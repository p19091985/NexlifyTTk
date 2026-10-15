"""MFA enrollment and explicit confirmation before sensitive actions."""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from persistencia import auth, mfa


def ensure_recent_auth(parent):
    import config
    if not config.USE_LOGIN:
        auth.require_dev_mode()
        return True
    try:
        auth.require_recent_auth()
        return True
    except PermissionError:
        password = simpledialog.askstring('Confirmar identidade', 'Senha atual:', show='*', parent=parent)
        if password is None:
            return False
        try:
            result = auth.reauthenticate(password)
            if result and result.get('mfa_required'):
                prompt = ('Digite o código enviado ao e-mail cadastrado (ou um código de recuperação):'
                          if result.get('delivery') == 'email' else
                          'Envio por e-mail indisponível. Digite um código de recuperação ou cancele e tente novamente:')
                otp = simpledialog.askstring('Código por e-mail', prompt, parent=parent)
                if not otp:
                    return False
                auth.reauthenticate(password, otp.strip())
            return True
        except (ValueError, PermissionError, ConnectionError) as error:
            messagebox.showerror('Confirmação', str(error), parent=parent)
            return False


class MfaDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.success = False
        self.title('Autenticação em dois fatores')
        self.resizable(False, False)
        self.grab_set()
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill='both', expand=True)
        if not ensure_recent_auth(self):
            self.after_idle(self.destroy)
            return
        ttk.Label(frame, text='Cadastre seu e-mail para receber os códigos de acesso.').pack(anchor='w')
        self.email = ttk.Entry(frame, width=52)
        self.email.pack(fill='x', pady=8)
        self.send_button = ttk.Button(frame, text='Enviar código por e-mail', command=self.send)
        self.send_button.pack(fill='x')
        self.status = ttk.Label(frame, text='', wraplength=420)
        self.status.pack(anchor='w', pady=8)
        ttk.Label(frame, text='Código de seis dígitos recebido por e-mail:').pack(anchor='w')
        self.code = ttk.Entry(frame)
        self.code.pack(fill='x', pady=8)
        self.button = ttk.Button(frame, text='Ativar MFA', command=self.confirm)
        self.button.pack(fill='x')
        self.recovery = tk.Text(frame, width=54, height=12, wrap='word')
        self.recovery.pack(fill='x', pady=10)
        self.recovery.configure(state='disabled')
        ttk.Button(frame, text='Fechar', command=self.destroy).pack()

    def send(self):
        try:
            result = mfa.begin_enrollment(self.email.get().strip())
        except (ValueError, PermissionError, ConnectionError) as error:
            messagebox.showerror('MFA por e-mail', str(error), parent=self)
            return
        self.status.configure(text='Código enviado para ' + result['masked_email'] + '. Válido por cinco minutos.')
        self.code.focus_set()

    def confirm(self):
        try:
            codes = mfa.confirm_enrollment(self.code.get().strip())
        except (ValueError, PermissionError, ConnectionError) as error:
            messagebox.showerror('MFA', str(error), parent=self)
            return
        self.success = True
        self.button.configure(state='disabled')
        self.send_button.configure(state='disabled')
        self.email.configure(state='disabled')
        self.code.delete(0, 'end')
        self.recovery.configure(state='normal')
        self.recovery.insert('1.0', 'MFA ativado. Guarde estes códigos de uso único em seu cofre.\nEles serão exibidos somente agora. No próximo login, você receberá um novo código por e-mail.\n\n' + '\n'.join(codes))
        self.recovery.configure(state='disabled')
