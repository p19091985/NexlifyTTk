# panels/painel_02.py
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as bstrap
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.toast import ToastNotification
from panels.base_panel import BasePanel


class PainelExemplosBootstrap(BasePanel):
    PANEL_NAME = "Exemplos ttkbootstrap"
    PANEL_ICON = "📚"
    ALLOWED_ACCESS = []  # Acessível a todos

    def create_widgets(self):
        # Frame principal com scroll para acomodar todos os exemplos
        scrolled_frame = ScrolledFrame(self, autohide=True, padding=15)
        scrolled_frame.pack(fill="both", expand=True)

        main_container = ttk.Frame(scrolled_frame)
        main_container.pack(fill="both", expand=True)
        main_container.columnconfigure(0, weight=1, uniform="group1")
        main_container.columnconfigure(1, weight=1, uniform="group1")

        # --- COLUNA DA ESQUERDA ---
        left_column = ttk.Frame(main_container)
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # --- Botões e Estilos ---
        btn_frame = ttk.LabelFrame(left_column, text=" Botões e Estilos ", padding=10)
        btn_frame.pack(fill="x", expand=True, pady=(0, 10))

        ttk.Button(btn_frame, text="Success (Sólido)", style="success.TButton").pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Info (Outline)", style="info.Outline.TButton").pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Danger (Link)", style="danger.Link.TButton").pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Desativado", style="secondary.TButton", state="disabled").pack(fill="x", pady=2)

        # --- Caixas de Seleção (Checkbuttons) ---
        check_frame = ttk.LabelFrame(left_column, text=" Caixas de Seleção ", padding=10)
        check_frame.pack(fill="x", expand=True, pady=(0, 10))

        ttk.Checkbutton(check_frame, text="Estilo Padrão").pack(anchor="w")
        ttk.Checkbutton(check_frame, text="Estilo 'Toolbutton'", style="info.Toolbutton").pack(anchor="w", pady=5)
        ttk.Checkbutton(check_frame, text="Estilo 'Round Toggle'", style="success.Roundtoggle.TCheckbutton").pack(
            anchor="w")

        # --- Botões de Opção (Radiobuttons) ---
        radio_frame = ttk.LabelFrame(left_column, text=" Botões de Opção ", padding=10)
        radio_frame.pack(fill="x", expand=True, pady=(0, 10))
        radio_var = tk.StringVar(value="opt1")
        ttk.Radiobutton(radio_frame, text="Opção Padrão 1", variable=radio_var, value="opt1").pack(anchor="w")
        ttk.Radiobutton(radio_frame, text="Opção Padrão 2", variable=radio_var, value="opt2").pack(anchor="w")
        ttk.Radiobutton(radio_frame, text="Estilo 'Toolbutton'", style="warning.Toolbutton", variable=radio_var,
                        value="opt3").pack(anchor="w", pady=5)

        # --- COLUNA DA DIREITA ---
        right_column = ttk.Frame(main_container)
        right_column.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # --- Medidores e Progresso (Interativos) ---
        meter_frame = ttk.LabelFrame(right_column, text=" Medidores e Progresso ", padding=10)
        meter_frame.pack(fill="x", expand=True, pady=(0, 10))

        self.meter_var = tk.IntVar(value=75)
        # MODIFICAÇÃO 1: Adiciona o trace na variável para chamar a função de atualização
        self.meter_var.trace_add("write", self._update_meter)


        self.meter = bstrap.Meter(meter_frame, metersize=180, padding=5, amountused=75,
                             metertype="semi", subtext="Nível de Bateria",
                             interactive=True, bootstyle="success")
        self.meter.pack()

        ttk.Label(meter_frame, text="Ajuste o valor:").pack(pady=(10, 0))
        scale = ttk.Scale(meter_frame, from_=0, to=100, variable=self.meter_var, style="success.Horizontal.TScale")
        scale.pack(fill="x", expand=True, pady=5)

        ttk.Progressbar(meter_frame, variable=self.meter_var, style="success-striped.Horizontal.TProgressbar").pack(
            fill="x", expand=True)

        # --- Widgets Avançados ---
        adv_frame = ttk.LabelFrame(right_column, text=" Widgets Avançados ", padding=10)
        adv_frame.pack(fill="x", expand=True, pady=(0, 10))

        ttk.Label(adv_frame, text="Seletor de Data (DateEntry):").pack(anchor="w")
        date_entry = bstrap.DateEntry(adv_frame, bootstyle="primary", firstweekday=0, dateformat="%d/%m/%Y")
        date_entry.pack(fill="x", pady=5)

        ttk.Label(adv_frame, text="Notificação Toast:").pack(anchor="w", pady=(10, 0))
        toast_btn = ttk.Button(adv_frame, text="Exibir Notificação", command=self._show_toast, style="info.TButton")
        toast_btn.pack(fill="x", pady=5)

        # --- Abas (Notebook) ---
        notebook_frame = ttk.LabelFrame(right_column, text=" Abas (Notebook) ", padding=10)
        notebook_frame.pack(fill="x", expand=True, pady=(0, 10))

        notebook = ttk.Notebook(notebook_frame, bootstyle="primary")
        notebook.pack(fill="x", expand=True, pady=5)

        tab1 = ttk.Frame(notebook, padding=10)
        ttk.Label(tab1, text="Conteúdo da primeira aba.").pack()
        notebook.add(tab1, text="Aba 1")

        tab2 = ttk.Frame(notebook, padding=10)
        ttk.Label(tab2, text="Conteúdo da segunda aba com um ícone.").pack()
        notebook.add(tab2, text="Aba 2 📄")


    def _update_meter(self, *args):
        """Atualiza a propriedade 'amountused' do Meter com o valor da variável."""
        current_value = self.meter_var.get()
        self.meter.configure(amountused=current_value)

    def _show_toast(self):
        """Exibe uma notificação flutuante (toast)."""
        toast = ToastNotification(
            title="Notificação de Exemplo",
            message="Esta é uma mensagem de toast do ttkbootstrap!",
            duration=3000,
            bootstyle="info",
            position=(20, 20, 'se')  # Canto inferior direito da tela
        )
        toast.show_toast()