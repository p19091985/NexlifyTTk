# login_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import logging
import time

try:
    from . import auth
except ImportError:
    import auth

import config


class LoginDialog(tk.Toplevel):
    """
    Janela de diálogo de login com funcionalidades de UX aprimoradas,
    como visibilidade de senha e feedback visual de erro.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.user_info = None
        self.attempts = 0
        self.max_attempts = 3
        self.login_logger = logging.getLogger("login_attempts")

        self.title("Login do Sistema")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        self.password_visible = tk.BooleanVar(value=False)

        self._setup_widgets()
        self._center_window()

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.user_entry.focus_set()
        self.deiconify()

    def _setup_widgets(self):
        main_frame = ttk.Frame(self, padding="20 15 20 20")
        main_frame.pack(fill="both", expand=True)

        # Frame para os campos de entrada
        credentials_frame = ttk.LabelFrame(main_frame, text=" Credenciais de Acesso ", padding=15)
        credentials_frame.pack(fill="x")

        ttk.Label(credentials_frame, text="Usuário:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.user_entry = ttk.Entry(credentials_frame, width=30)
        self.user_entry.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(credentials_frame, text="Senha:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.pass_entry = ttk.Entry(credentials_frame, show="*", width=30)
        self.pass_entry.grid(row=1, column=1, pady=5, padx=5, sticky="ew")

        credentials_frame.columnconfigure(1, weight=1)

        # NOVO: Checkbutton para mostrar/ocultar a senha
        show_pass_check = ttk.Checkbutton(main_frame, text="Mostrar senha",
                                          variable=self.password_visible,
                                          command=self._toggle_password_visibility)
        show_pass_check.pack(anchor="w", pady=(5, 10), padx=5)

        # Binds de teclado
        self.user_entry.bind("<Return>", lambda e: self.pass_entry.focus_set())
        self.pass_entry.bind("<Return>", lambda e: self._on_login())

        # Frame para os botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(10, 0))
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        login_btn = ttk.Button(btn_frame, text="Entrar", command=self._on_login, style='Accent.TButton')
        login_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        cancel_btn = ttk.Button(btn_frame, text="Cancelar", command=self._on_cancel)
        cancel_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        s = ttk.Style()
        s.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'))

    def _toggle_password_visibility(self):
        if self.password_visible.get():
            self.pass_entry.config(show="")
        else:
            self.pass_entry.config(show="*")

    def _on_login(self, event=None):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()

        if not username or not password:
            messagebox.showwarning("Campos Vazios", "Por favor, preencha usuário e senha.", parent=self)
            self._shake_window()
            return

        user_data = auth.verify_user_credentials(username, password)
        if user_data:
            self.login_logger.info(f"SUCESSO - Login para: '{username}'")
            self.user_info = user_data
            self.destroy()
        else:
            self.attempts += 1
            remaining = self.max_attempts - self.attempts
            self.login_logger.warning(f"FALHA - Tentativa {self.attempts}/{self.max_attempts} para: '{username}'")

            self._shake_window()  # Feedback visual de erro

            if remaining > 0:
                messagebox.showwarning("Login Inválido",
                                       f"Usuário ou senha inválidos.\nTentativas restantes: {remaining}", parent=self)
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
        """ NOVO: Efeito de 'shake' para feedback de erro. """
        self.lift()
        x, y = self.winfo_x(), self.winfo_y()
        shake_intensity = 5
        shake_duration_ms = 40

        for _ in range(2):
            self.geometry(f"+{x + shake_intensity}+{y}")
            self.update_idletasks()
            time.sleep(shake_duration_ms / 1000)
            self.geometry(f"+{x - shake_intensity}+{y}")
            self.update_idletasks()
            time.sleep(shake_duration_ms / 1000)

        self.geometry(f"+{x}+{y}")  # Retorna à posição original

    def _center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        parent_x, parent_y = self.parent.winfo_rootx(), self.parent.winfo_rooty()
        parent_w, parent_h = self.parent.winfo_width(), self.parent.winfo_height()
        x = parent_x + (parent_w // 2) - (w // 2)
        y = parent_y + (parent_h // 2) - (h // 2)
        self.geometry(f"+{x}+{y}")