import tkinter as tk
from tkinter import ttk, messagebox
import logging
import time

import config
from persistencia import auth

class LoginDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.user_info = None
        self.attempts = 0
        self.max_attempts = config.MAX_LOGIN_ATTEMPTS
        self.login_logger = logging.getLogger("login_attempts")

        self.title("Login do Sistema")

        self.grab_set()
        self.resizable(False, False)

        self.password_visible = tk.BooleanVar(value=False)

        self._setup_widgets()

        self.deiconify()

        self._center_window()

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.user_entry.focus_set()

    def _setup_widgets(self):
        main_frame = ttk.Frame(self, padding="20 15 20 20")
        main_frame.pack(fill="both", expand=True)

        credentials_frame = ttk.LabelFrame(main_frame, text=" Credenciais de Acesso ", padding=15)
        credentials_frame.pack(fill="x")

        ttk.Label(credentials_frame, text="Usuário:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.user_entry = ttk.Entry(credentials_frame, width=30)
        self.user_entry.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(credentials_frame, text="Senha:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.pass_entry = ttk.Entry(credentials_frame, show="*", width=30)
        self.pass_entry.grid(row=1, column=1, pady=5, padx=5, sticky="ew")

        self.otp_label = ttk.Label(credentials_frame, text="Código do e-mail / recuperação:")
        self.otp_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.otp_entry = ttk.Entry(credentials_frame, show="*", width=30)
        self.otp_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.otp_label.grid_remove()
        self.otp_entry.grid_remove()
        self.mfa_status = ttk.Label(main_frame, text="", wraplength=420)
        self.mfa_status.pack(fill="x")
        self.resend_btn = ttk.Button(main_frame, text="Reenviar código por e-mail", command=self._resend_code)
        self.otp_entry.bind("<Return>", lambda e: self._on_login())
        credentials_frame.columnconfigure(1, weight=1)

        show_pass_check = ttk.Checkbutton(main_frame, text="Mostrar senha", variable=self.password_visible,
                                          command=self._toggle_password_visibility)
        show_pass_check.pack(anchor="w", pady=(5, 10), padx=5)

        self.user_entry.bind("<Return>", lambda e: self.pass_entry.focus_set())
        self.pass_entry.bind("<Return>", lambda e: self._on_login())

        if config.API_MODE == 'client':
            ttk.Button(main_frame, text='Entrar com SSO', command=self._on_sso).pack(fill='x', pady=5)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(10, 0))
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        login_btn = ttk.Button(btn_frame, text="Entrar", command=self._on_login, style='Success.TButton')
        login_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        cancel_btn = ttk.Button(btn_frame, text="Cancelar", command=self._on_cancel, style='Secondary.TButton')
        cancel_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def _on_sso(self):
        import webbrowser
        from services.client import request
        try:
            result = request('POST', '/sso/start')
            from urllib.parse import urlsplit
            if urlsplit(result['authorization_url']).scheme not in {'https', 'http'}:
                raise ValueError('Endereço SSO inválido.')
            self._sso_handle = result['handle']
            self._sso_deadline = time.monotonic() + 600
            webbrowser.open(result['authorization_url'])
            self.after(3000, self._poll_sso)
        except (ValueError, PermissionError, ConnectionError) as error:
            messagebox.showerror('SSO', str(error), parent=self)

    def _poll_sso(self):
        from services.client import sso_poll
        if time.monotonic() >= self._sso_deadline:
            return
        try:
            user = sso_poll(self._sso_handle, self.otp_entry.get().strip())
            if user and user.get('mfa_required'):
                self._show_challenge(user)
                self._sso_waiting = True
                return
            if user:
                self.user_info = user
                self.destroy()
                return
            self.after(3000, self._poll_sso)
        except (ValueError, PermissionError, ConnectionError) as error:
            messagebox.showerror('SSO', str(error), parent=self)

    def _show_challenge(self, result):
        self.otp_label.grid()
        self.otp_entry.grid()
        self.mfa_status.configure(text='Código enviado para ' + result.get('masked_email', '') +
                                  '. Válido por cinco minutos. Digite e clique em Entrar.')
        if result.get('delivery') == 'recovery':
            self.mfa_status.configure(text='Use um código de recuperação do cadastro antigo para migrar para e-mail.')
            self.resend_btn.pack_forget()
        else:
            if result.get('delivery') == 'unavailable':
                self.mfa_status.configure(text='Não foi possível enviar agora. Aguarde um minuto e tente reenviar, '
                                          'ou use um código de recuperação. Se persistir, verifique o SMTP.')
            self.resend_btn.pack(fill='x', pady=5)
        self.otp_entry.focus_set()
        self._center_window()

    def _resend_code(self):
        self.otp_entry.delete(0, 'end')
        self._on_login()

    def _toggle_password_visibility(self):
        self.pass_entry.config(show="" if self.password_visible.get() else "*")

    def _on_login(self, event=None):
        if getattr(self, '_sso_waiting', False):
            self._poll_sso()
            return
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()
        if not username or not password:
            messagebox.showwarning("Campos Vazios", "Por favor, preencha usuário e senha.", parent=self)
            self._shake_window()
            return

        try:
            user_data = auth.verify_user_credentials(username, password, self.otp_entry.get().strip())
        except (ValueError, PermissionError, ConnectionError) as error:
            messagebox.showerror('Autenticação', str(error), parent=self)
            return

        if user_data == "connection_error":
            messagebox.showerror("Problema de Conexão",
                                 "Não foi possível conectar ao banco de dados.\n\nVerifique sua rede, o servidor do banco e tente novamente mais tarde.",
                                 parent=self)
            self.user_info = "connection_error"
            self.destroy()
        elif isinstance(user_data, dict) and user_data.get('mfa_required'):
            self._show_challenge(user_data)
        elif user_data:
            self.login_logger.info('SUCESSO - Login para: %r', username)
            self.user_info = user_data
            self.destroy()
        else:
            self.attempts += 1
            remaining = self.max_attempts - self.attempts
            self.login_logger.warning('FALHA - Tentativa %s/%s para: %r', self.attempts, self.max_attempts, username)
            self._shake_window()
            if remaining > 0:
                messagebox.showwarning("Login Inválido",
                                       f"Usuário, senha ou código inválidos.\nTentativas restantes: {remaining}", parent=self)
                self.otp_entry.delete(0, 'end')
                if self.otp_entry.winfo_ismapped():
                    self.otp_entry.focus_set()
                else:
                    self.pass_entry.delete(0, 'end')
                    self.pass_entry.focus_set()
            else:
                self.login_logger.error("BLOQUEIO - Máximo de tentativas excedido.")
                messagebox.showerror("Acesso Bloqueado", "Número máximo de tentativas excedido.", parent=self)
                self.user_info = "max_attempts_failed"
                self.destroy()

    def _on_cancel(self):
        self.login_logger.info("CANCELADO - Login cancelado pelo usuário.")
        self.user_info = None
        self.destroy()

    def _shake_window(self):
        self.lift()
        x, y = self.winfo_x(), self.winfo_y()
        for _ in range(2):
            self.geometry(f"{x + 5:+d}{y:+d}")
            self.update_idletasks()
            time.sleep(0.04)
            self.geometry(f"{x - 5:+d}{y:+d}")
            self.update_idletasks()
            time.sleep(0.04)
        self.geometry(f"{x:+d}{y:+d}")

    def _center_window(self):
        """Centraliza a janela de login na tela principal do sistema operacional."""
        self.update_idletasks()

        window_width = self.winfo_width()
        window_height = self.winfo_height()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        center_x = (screen_width // 2) - (window_width // 2)
        center_y = (screen_height // 2) - (window_height // 2)

        self.geometry(f"{center_x:+d}{center_y:+d}")
