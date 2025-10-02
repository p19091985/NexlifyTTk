# painel_02.py (CORRIGIDO)
import tkinter as tk
from tkinter import ttk, messagebox
from persistencia.base_panel import BasePanel
import config  # <--- IMPORTAÇÃO ADICIONADA

class PainelWidgetsBasicos(BasePanel):
    PANEL_NAME = "Widgets Básicos"
    PANEL_ICON = "🧱"
    ALLOWED_ACCESS = []

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        title_label = ttk.Label(main_frame, text="Demonstração de Widgets ttk", font=config.FONTS["section_title"])
        title_label.pack(pady=(0, 20))

        # --- Frame para Interação ---
        interaction_frame = ttk.LabelFrame(main_frame, text=" Interação com o Usuário ", padding=15)
        interaction_frame.pack(pady=10, fill="x")

        ttk.Label(interaction_frame, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(interaction_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(interaction_frame, text="Idade:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.age_spinbox = ttk.Spinbox(interaction_frame, from_=18, to=100, width=5)
        self.age_spinbox.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.age_spinbox.set(25)

        action_button = ttk.Button(interaction_frame, text="Saudação", command=self._show_greeting)
        action_button.grid(row=0, column=2, rowspan=2, padx=10, pady=5, sticky="ns")
        interaction_frame.columnconfigure(1, weight=1)

        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=15)

        # --- Frame para Opções ---
        options_frame = ttk.LabelFrame(main_frame, text=" Widgets de Seleção ", padding=15)
        options_frame.pack(pady=10, fill="x")

        self.check_var = tk.BooleanVar()
        checkbutton = ttk.Checkbutton(options_frame, text="Ativar modo avançado", variable=self.check_var, style='TCheckbutton')
        checkbutton.pack(anchor="w")

        self.radio_var = tk.StringVar(value="email")
        ttk.Label(options_frame, text="\nForma de contato preferida:").pack(anchor="w")
        radio_email = ttk.Radiobutton(options_frame, text="E-mail", variable=self.radio_var, value="email")
        radio_email.pack(anchor="w", padx=20)
        radio_phone = ttk.Radiobutton(options_frame, text="Telefone", variable=self.radio_var, value="telefone")
        radio_phone.pack(anchor="w", padx=20)

        choices_button = ttk.Button(options_frame, text="Mostrar Escolhas", command=self._show_choices)
        choices_button.pack(pady=10)

    def _show_greeting(self):
        name = self.name_entry.get()
        age = self.age_spinbox.get()
        if not name:
            messagebox.showwarning("Entrada Inválida", "Por favor, digite seu nome.")
            return
        if not age.isdigit():
            messagebox.showwarning("Entrada Inválida", "Por favor, insira uma idade válida.")
            return
        messagebox.showinfo("Saudação", f"Olá, {name}! Você tem {age} anos.")

    def _show_choices(self):
        advanced = "Ativado" if self.check_var.get() else "Desativado"
        contact = self.radio_var.get()
        messagebox.showinfo("Suas Escolhas", f"Modo Avançado: {advanced}\nContato Preferido: {contact.capitalize()}")