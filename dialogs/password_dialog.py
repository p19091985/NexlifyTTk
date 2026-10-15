"""Criação inicial e troca de senha sem gravar ou registrar o texto informado."""
import tkinter as tk
from tkinter import ttk, messagebox
from persistencia import auth


class PasswordDialog(tk.Toplevel):
    def __init__(self, parent, mode='change'):
        super().__init__(parent)
        self.mode = mode
        self.success = False
        self.title({'bootstrap': 'Criar administrador', 'reset': 'DEV — Reset do administrador',
                    'change': 'Trocar senha'}[mode])
        self.resizable(False, False)
        frame = ttk.Frame(self, padding=24)
        frame.pack(fill='both', expand=True)
        title = 'Definir senha do admin' if mode != 'change' else 'Definir sua nova senha'
        ttk.Label(frame, text=title, font=('Segoe UI', 15, 'bold')).pack(anchor='w')
        text = 'Use uma frase-senha de 15 caracteres ou mais, até 1024 bytes UTF-8.'
        if mode == 'reset':
            text += '\nA senha atual será substituída e será exigida uma nova troca no login.\nAs sessões existentes serão revogadas.'
        ttk.Label(frame, text=text, wraplength=480, justify='left').pack(anchor='w', pady=12)
        self.old = tk.StringVar(self)
        self.password = tk.StringVar(self)
        self.confirmation = tk.StringVar(self)
        self.fields = []
        pairs = [('Senha atual / temporária', self.old)] if mode == 'change' else []
        pairs += [('Nova senha', self.password), ('Confirmação', self.confirmation)]
        for label, variable in pairs:
            ttk.Label(frame, text=label).pack(anchor='w')
            entry = ttk.Entry(frame, textvariable=variable, show='•', width=48)
            entry.pack(fill='x', pady=(2, 10))
            self.fields.append(entry)
        self.reveal = tk.BooleanVar(self, False)
        ttk.Checkbutton(frame, text='Mostrar senhas', variable=self.reveal,
                        command=lambda: [field.configure(show='' if self.reveal.get() else '•') for field in self.fields]).pack(anchor='w')
        buttons = ttk.Frame(frame)
        buttons.pack(fill='x', pady=(16, 0))
        ttk.Button(buttons, text='Cancelar', command=self.destroy).pack(side='left')
        ttk.Button(buttons, text='Salvar senha', command=self.submit).pack(side='right')
        self.bind('<Return>', lambda event: self.submit())
        self.bind('<Escape>', lambda event: self.destroy())
        self.update_idletasks()
        width, height = self.winfo_reqwidth(), self.winfo_reqheight()
        self.geometry(f'+{max(0,(self.winfo_screenwidth()-width)//2)}+{max(0,(self.winfo_screenheight()-height)//2)}')
        self.grab_set()
        self.fields[0].focus_set()

    def submit(self):
        password = self.password.get()
        error = auth.password_validation_error(password, self.confirmation.get())
        if error:
            messagebox.showwarning('Senha inválida', error, parent=self)
            return
        if self.mode == 'reset' and not messagebox.askyesno('Confirmar reset', 'Substituir a senha do admin neste banco?', parent=self):
            return
        try:
            if self.mode == 'bootstrap':
                auth.bootstrap_admin(password)
            elif self.mode == 'reset':
                auth.reset_admin_password(password)
            else:
                auth.change_own_password(self.old.get(), password)
        except (ValueError, PermissionError) as error:
            messagebox.showerror('Não foi possível salvar', str(error), parent=self)
            return
        except Exception:
            messagebox.showerror('Erro', 'Falha ao acessar o banco. Nenhuma senha foi confirmada.', parent=self)
            return
        self.old.set('')
        self.password.set('')
        self.confirmation.set('')
        self.success = True
        messagebox.showinfo('Senha salva', 'Senha definida. Entre no sistema com a nova senha.', parent=self)
        self.destroy()
