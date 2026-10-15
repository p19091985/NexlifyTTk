"""Local administrative SMTP editor; network calls never block Tk's main thread."""
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from services import email_settings, email_oauth
from services.email_providers import PROVIDERS, defaults
from services.email_delivery import send_test, validate_address


def authorize_admin(parent):
    from persistencia import auth
    from .mfa_dialog import ensure_recent_auth
    email_settings.require_server()
    if auth.current_session(allow_mfa_setup=True)['access_level'] != auth.ADMIN:
        raise PermissionError('Somente o Administrador Global pode configurar o envio de e-mail.')
    return ensure_recent_auth(parent)


class EmailSettingsDialog(tk.Toplevel):
    def __init__(self, parent, *, authorize=None):
        super().__init__(parent)
        self.authorize = authorize or authorize_admin
        self.title('Configurar envio de e-mail')
        self.resizable(True, False)
        self.flow = None
        self.timers = set()
        self.busy = False
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.grab_set()
        try:
            if not self.authorize(self):
                self.after_idle(self.destroy)
                return
            data = email_settings.load_saved()
        except (ValueError, PermissionError, OSError) as error:
            messagebox.showerror('E-mail', str(error), parent=self)
            self.after_idle(self.destroy)
            return
        self.vars = {key: tk.StringVar(self, '' if key in email_settings.SECRETS else str(value))
                     for key, value in data.items() if key != 'enabled'}
        self.enabled = tk.BooleanVar(self, data['enabled'])
        outer = ttk.Frame(self, padding=16)
        outer.pack(fill='both', expand=True)
        ttk.Label(outer, text='Conta remetente do servidor').pack(anchor='w')
        self.provider = ttk.Combobox(outer, state='readonly', values=[p['name'] for p in PROVIDERS.values()], width=60)
        self.provider.set(PROVIDERS[data['provider']]['name'])
        self.provider.bind('<<ComboboxSelected>>', self.select_provider)
        self.provider.pack(fill='x', pady=6)
        self.note = ttk.Label(outer, text=PROVIDERS[data['provider']]['note'], wraplength=590)
        self.note.pack(anchor='w', pady=6)
        ttk.Checkbutton(outer, text='Habilitar envio por esta conta (não ativa o MFA)', variable=self.enabled).pack(anchor='w')
        notebook = ttk.Notebook(outer)
        notebook.pack(fill='both', expand=True, pady=10)
        general, authentication = ttk.Frame(notebook, padding=12), ttk.Frame(notebook, padding=12)
        notebook.add(general, text='Servidor SMTP')
        notebook.add(authentication, text='Autenticação')
        self.entries = {}
        for row, (key, title) in enumerate((('host', 'Servidor'), ('port', 'Porta'), ('security', 'Segurança'),
                ('sender', 'E-mail remetente'), ('username', 'Usuário SMTP'), ('ca', 'Arquivo de CA privada (opcional)'))):
            self.field(general, row, key, title, ('starttls', 'ssl') if key == 'security' else None)
        for row, (key, title) in enumerate((('auth', 'Método'), ('password', 'Senha / senha de aplicativo'),
                ('client_id', 'OAuth2: Application (client) ID'), ('token_url', 'OAuth2: endpoint de token'),
                ('scope', 'OAuth2: escopos'), ('client_secret', 'OAuth2: segredo do aplicativo (opcional)'),
                ('refresh_token', 'OAuth2: refresh token'))):
            self.field(authentication, row, key, title, ('password', 'oauth2') if key == 'auth' else None)
        ttk.Label(authentication, text='Credenciais salvas não são exibidas. Em branco mantém a credencial somente\n'
                  'se conta e servidor continuarem iguais. Mudanças exigem nova autenticação.').grid(row=7, column=0, columnspan=2, pady=8)
        self.connect_button = ttk.Button(authentication, text='Conectar conta Outlook à Microsoft', command=self.connect)
        self.connect_button.grid(row=8, column=0, columnspan=2, sticky='ew')
        self.oauth_status = ttk.Label(authentication, text='', wraplength=570)
        self.oauth_status.grid(row=9, column=0, columnspan=2, pady=5)
        self.test_address = tk.StringVar(self, data['sender'])
        test_row = ttk.Frame(outer)
        test_row.pack(fill='x')
        ttk.Label(test_row, text='Destinatário do teste:').pack(side='left')
        ttk.Entry(test_row, textvariable=self.test_address, width=36).pack(side='left', fill='x', expand=True, padx=8)
        self.status = ttk.Label(outer, wraplength=590, text=('Variáveis de ambiente SMTP estão ativas; remova-as para salvar pela tela.'
            if email_settings.environment_active() else 'Configuração exclusiva desta máquina; credenciais criptografadas no servidor.'))
        self.status.pack(anchor='w', pady=8)
        actions = ttk.Frame(outer)
        actions.pack(fill='x')
        self.save_button = ttk.Button(actions, text='Salvar configuração', command=self.save)
        self.save_button.pack(side='left', padx=4)
        self.test_button = ttk.Button(actions, text='Enviar e-mail de teste', command=self.test)
        self.test_button.pack(side='left', padx=4)
        ttk.Button(actions, text='Fechar', command=self.close).pack(side='right')
        self.actions = (self.save_button, self.test_button, self.connect_button, self.provider)

    def field(self, parent, row, key, title, choices=None):
        parent.columnconfigure(1, weight=1)
        ttk.Label(parent, text=title+':').grid(row=row, column=0, sticky='w', padx=(0, 10), pady=4)
        entry = (ttk.Combobox(parent, textvariable=self.vars[key], values=choices, state='readonly') if choices else
                 ttk.Entry(parent, textvariable=self.vars[key], show='*' if key in email_settings.SECRETS else '', width=42))
        entry.grid(row=row, column=1, sticky='ew', pady=4)
        self.entries[key] = entry

    def select_provider(self, event=None):
        provider = next(key for key, value in PROVIDERS.items() if value['name'] == self.provider.get())
        self.flow = None
        self.oauth_status.configure(text='')
        for key, value in defaults(provider).items():
            if key not in {'enabled', 'sender', 'username'}:
                self.vars[key].set(str(value))
        self.note.configure(text=PROVIDERS[provider]['note'])

    def values(self):
        return dict({key: variable.get() if key in email_settings.SECRETS else variable.get().strip()
                     for key, variable in self.vars.items()}, enabled=self.enabled.get())

    def save(self):
        try:
            if self.busy or not self.authorize(self):
                return
            email_settings.save(self.values())
            for key in email_settings.SECRETS:
                self.vars[key].set('')
            self.status.configure(text='Configuração salva. Os próximos envios usarão esta conta. O estado do MFA não foi alterado.')
        except (ValueError, PermissionError, OSError) as error:
            messagebox.showerror('E-mail', str(error), parent=self)

    def work(self, operation, done):
        if self.busy:
            return
        self.busy = True
        for widget in self.actions:
            widget.configure(state='disabled')
        results = queue.Queue()
        def run():
            try:
                results.put((True, operation()))
            except (ValueError, PermissionError, ConnectionError, OSError):
                # Provider responses and credentials never enter UI messages or logs.
                results.put((False, 'Operação não concluída. Confira a conexão, TLS, credenciais e permissões do provedor.'))
        threading.Thread(target=run, daemon=True).start()
        def collect():
            if not self.winfo_exists():
                return
            try:
                ok, result = results.get_nowait()
            except queue.Empty:
                self.schedule(100, collect)
                return
            self.busy = False
            for widget in self.actions:
                widget.configure(state='readonly' if widget is self.provider else 'normal')
            if ok:
                done(result)
            else:
                self.flow = None
                self.status.configure(text=result)
        self.schedule(100, collect)

    def test(self):
        try:
            if self.busy or not self.authorize(self):
                return
            if email_settings.environment_active():
                raise ValueError('As variáveis SMTP estão ativas. Teste pelo utilitário do servidor ou remova-as para usar esta tela.')
            settings = email_settings.prepare(self.values())
            if not settings['enabled']:
                raise ValueError('Marque Habilitar envio para testar esta configuração.')
            address = validate_address(self.test_address.get().strip())
        except (ValueError, PermissionError, OSError) as error:
            messagebox.showerror('Teste de e-mail', str(error), parent=self)
            return
        self.status.configure(text='Enviando uma mensagem de teste para o destinatário informado…')
        self.work(lambda: send_test(address, settings=settings),
                  lambda result: self.status.configure(text='Mensagem aceita pelo servidor SMTP. Confira a caixa de entrada e o spam.'))

    def connect(self):
        try:
            if self.busy or not self.authorize(self):
                return
            if self.vars['provider'].get() != 'outlook':
                raise ValueError('Selecione Outlook / Hotmail / Live para usar este assistente.')
            client_id = self.vars['client_id'].get().strip()
        except (ValueError, PermissionError) as error:
            messagebox.showerror('OAuth2', str(error), parent=self)
            return
        def started(flow):
            self.flow = flow
            self.oauth_status.configure(text='Abra '+flow['verification_uri']+' no navegador e informe o código '+flow['user_code']+
                '. Autorize o envio SMTP. Esta tela aguardará a confirmação.')
            self.schedule(1000, self.poll)
        self.work(lambda: email_oauth.start_microsoft(client_id), started)

    def poll(self):
        if not self.flow or not self.winfo_exists():
            return
        if self.busy:
            self.schedule(1000, self.poll)
            return
        flow = self.flow
        def received(token):
            if self.flow is not flow:
                return
            if token:
                self.vars['refresh_token'].set(token)
                self.vars['client_id'].set(flow['client_id'])
                self.vars['token_url'].set(email_oauth.MICROSOFT+'token')
                self.vars['scope'].set(email_oauth.SCOPE)
                self.vars['auth'].set('oauth2')
                self.flow = None
                self.oauth_status.configure(text='Conta autorizada. Salve a configuração e envie um teste.')
            else:
                self.schedule(1000, self.poll)
        self.work(lambda: email_oauth.poll_microsoft(flow), received)

    def close(self):
        self.flow = None
        self.destroy()

    def schedule(self, milliseconds, callback):
        def invoke():
            self.timers.discard(timer)
            callback()
        timer = self.after(milliseconds, invoke)
        self.timers.add(timer)
        return timer

    def destroy(self):
        self.flow = None
        for timer in getattr(self, 'timers', ()):
            self.after_cancel(timer)
        self.timers = set()
        super().destroy()
