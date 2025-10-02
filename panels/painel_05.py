# painel_05.py
import tkinter as tk
from tkinter import ttk, messagebox
from persistencia.base_panel import BasePanel
import config

class PainelFormularios(BasePanel):
    PANEL_NAME = "Entrada de Dados"
    PANEL_ICON = "📝"
    ALLOWED_ACCESS = [
        'Administrador Global', 'Gerente de TI',
        'Supervisor de Produção', 'Operador de Linha'
    ]

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="x", expand=False)

        title_label = ttk.Label(main_frame, text="Exemplo de Formulário com ttk", font=config.FONTS["section_title"])
        title_label.pack(pady=(0, 20), padx=0)

        # --- Frame de Informações do Usuário ---
        input_frame = ttk.LabelFrame(main_frame, text=" Informações do Usuário ", padding=15)
        input_frame.pack(fill="x", pady=10)

        ttk.Label(input_frame, text="Nome de usuário:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry = ttk.Entry(input_frame, width=30)
        self.entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(input_frame, text="País:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.combo = ttk.Combobox(input_frame, values=["Brasil", "Portugal", "Angola", "Moçambique"], state="readonly")
        self.combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.combo.set("Brasil")
        input_frame.columnconfigure(1, weight=1)

        # --- Frame de Opções Adicionais ---
        options_frame = ttk.LabelFrame(main_frame, text=" Opções Adicionais ", padding=15)
        options_frame.pack(fill="x", pady=10)

        self.check_var = tk.BooleanVar()
        check = ttk.Checkbutton(options_frame, text="Ativar notificação por e-mail", variable=self.check_var)
        check.pack(anchor="w")

        self.radio_var = tk.StringVar(value="diario")
        ttk.Label(options_frame, text="\nFrequência do relatório:").pack(anchor="w", pady=(5, 0))
        ttk.Radiobutton(options_frame, text="Diário", variable=self.radio_var, value="diario").pack(anchor="w", padx=15)
        ttk.Radiobutton(options_frame, text="Semanal", variable=self.radio_var, value="semanal").pack(anchor="w", padx=15)
        ttk.Radiobutton(options_frame, text="Mensal", variable=self.radio_var, value="mensal").pack(anchor="w", padx=15)

        action_button = ttk.Button(self, text="Enviar Dados", command=self.show_form_data, style='Accent.TButton')
        action_button.pack(pady=20)
        # Estilo para botão de destaque (opcional)
        s = ttk.Style()
        s.configure('Accent.TButton', font = ('Segoe UI', 10, 'bold'))


    def show_form_data(self):
        notification = "Ativada" if self.check_var.get() else "Desativada"
        frequency = self.radio_var.get().capitalize()
        username = self.entry.get()
        country = self.combo.get()

        if not username or not country:
            messagebox.showwarning("Dados Incompletos", "Por favor, preencha o nome de usuário e o país.")
            return

        message = (
            f"--- Dados Enviados ---\n\n"
            f"Nome de Usuário: {username}\n"
            f"País: {country}\n"
            f"Notificação por E-mail: {notification}\n"
            f"Frequência do Relatório: {frequency}"
        )
        messagebox.showinfo("Confirmação", message)