# panels/painel_componentes_ui_view.py
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as bstrap
from ttkbootstrap.scrolled import ScrolledFrame


class ComponentesUIView(ttk.Frame):
    """A View para o painel de demonstração de componentes."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        scrolled_frame = ScrolledFrame(self, autohide=True, padding=15)
        scrolled_frame.pack(fill="both", expand=True)
        main_container = ttk.Frame(scrolled_frame)
        main_container.pack(fill="both", expand=True)

        # Seção 1: Botões
        btn_frame = ttk.LabelFrame(main_container, text=" 1. Botões e Estilos Semânticos ", padding=10)
        btn_frame.pack(fill="x", expand=True, pady=(0, 15))
        self._create_buttons(btn_frame)

        # Seção 2: Inputs
        input_frame = ttk.LabelFrame(main_container, text=" 2. Entrada de Dados (Inputs) ", padding=10)
        input_frame.pack(fill="x", expand=True, pady=(0, 15))
        self._create_inputs(input_frame)

        # Seção 3: Seletores
        options_frame = ttk.LabelFrame(main_container, text=" 3. Seletores e Opções ", padding=10)
        options_frame.pack(fill="x", expand=True, pady=(0, 15))
        self._create_selectors(options_frame)

        # Seção 4: Controles Sincronizados
        sync_frame = ttk.LabelFrame(main_container, text=" 4. Controles Sincronizados ", padding=10)
        sync_frame.pack(fill="x", expand=True, pady=(0, 15))
        self._create_synced_controls(sync_frame)

        # Seção 5: Notificações
        toast_frame = ttk.LabelFrame(main_container, text=" 5. Notificações ", padding=10)
        toast_frame.pack(fill="x", expand=True, pady=(0, 15))
        self._create_notifications(toast_frame)

    def _create_buttons(self, parent):
        ttk.Label(parent, text="ttkbootstrap oferece estilos baseados em cores (semântica).").pack(anchor="w",
                                                                                                   pady=(0, 5))
        subframe = ttk.Frame(parent)
        subframe.pack(fill="x")
        ttk.Button(subframe, text="Success", style="success.TButton").pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(subframe, text="Info (Outline)", style="info.Outline.TButton").pack(side="left", expand=True,
                                                                                       fill="x", padx=2)
        ttk.Button(subframe, text="Warning (Link)", style="warning.Link.TButton").pack(side="left", expand=True,
                                                                                       fill="x", padx=2)
        ttk.Button(subframe, text="Danger", style="danger.TButton").pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(subframe, text="Disabled", state="disabled").pack(side="left", expand=True, fill="x", padx=2)

    def _create_inputs(self, parent):
        parent.columnconfigure(1, weight=1)
        ttk.Label(parent, text="Entry:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        entry = ttk.Entry(parent)
        entry.insert(0, "Texto de exemplo")
        entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(parent, text="Combobox:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        combo = ttk.Combobox(parent, state="readonly", values=["Opção A", "Opção B", "Opção C"])
        combo.set("Opção B")
        combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(parent, text="DateEntry:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        date_entry = bstrap.DateEntry(parent, bootstyle="primary", firstweekday=0, dateformat="%d/%m/%Y")
        date_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

    def _create_selectors(self, parent):
        ttk.Label(parent, text="Checkbuttons:").pack(anchor="w")
        ttk.Checkbutton(parent, text="Opção independente 1").pack(anchor="w", padx=20)
        ttk.Checkbutton(parent, text="Opção 'Round Toggle'", style="success.Roundtoggle.TCheckbutton").pack(anchor="w",
                                                                                                            padx=20,
                                                                                                            pady=5)
        ttk.Label(parent, text="\nRadiobuttons:").pack(anchor="w")
        radio_var = tk.StringVar(value="rb2")
        ttk.Radiobutton(parent, text="Escolha X", variable=radio_var, value="rb1").pack(anchor="w", padx=20)
        ttk.Radiobutton(parent, text="Escolha Y", variable=radio_var, value="rb2").pack(anchor="w", padx=20)
        ttk.Radiobutton(parent, text="Escolha Z (Toolbutton)", style="info.Toolbutton", variable=radio_var,
                        value="rb3").pack(anchor="w", padx=20, pady=5)

    def _create_synced_controls(self, parent):
        ttk.Label(parent, text="Arraste o Scale para ver a Progressbar e o Meter se atualizarem:").pack(anchor="w",
                                                                                                        pady=(0, 10))
        scale = ttk.Scale(parent, from_=0, to=100, orient="horizontal", variable=self.controller.scale_var)
        scale.pack(fill="x", expand=True, pady=5)
        progressbar = ttk.Progressbar(parent, orient="horizontal", variable=self.controller.scale_var,
                                      style="success-striped.Horizontal.TProgressbar")
        progressbar.pack(fill="x", expand=True, pady=10)
        self.meter = bstrap.Meter(parent, metersize=150, padding=5, amountused=75, metertype="semi", subtext="Nível",
                                  interactive=False, bootstyle="success")
        self.meter.pack(pady=10)

    def _create_notifications(self, parent):
        ttk.Button(parent, text="Exibir Notificação 'Toast'", command=self.controller._show_toast,
                   style="info.TButton").pack(pady=5)