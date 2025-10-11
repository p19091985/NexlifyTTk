# panels/painel_componentes_ui_view.py
import tkinter as tk
from tkinter import ttk


class ScrolledFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.canvas = tk.Canvas(self, borderwidth=0)
        self.viewPort = ttk.Frame(self.canvas)
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas_window = self.canvas.create_window((4, 4), window=self.viewPort, anchor="nw", tags="self.viewPort")

        self.viewPort.bind("<Configure>", self.onFrameConfigure)
        self.canvas.bind("<Configure>", self.onCanvasConfigure)

    def onFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def onCanvasConfigure(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)


class ComponentesUIView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        scrolled_frame = ScrolledFrame(self)
        scrolled_frame.pack(fill="both", expand=True)

        main_container = scrolled_frame.viewPort

        btn_frame = ttk.LabelFrame(main_container, text=" 1. Botões e Estilos ", padding=10)
        btn_frame.pack(fill="x", expand=True, pady=(0, 15), padx=10)
        self._create_buttons(btn_frame)

        input_frame = ttk.LabelFrame(main_container, text=" 2. Entrada de Dados (Inputs) ", padding=10)
        input_frame.pack(fill="x", expand=True, pady=(0, 15), padx=10)
        self._create_inputs(input_frame)

        options_frame = ttk.LabelFrame(main_container, text=" 3. Seletores e Opções ", padding=10)
        options_frame.pack(fill="x", expand=True, pady=(0, 15), padx=10)
        self._create_selectors(options_frame)

        sync_frame = ttk.LabelFrame(main_container, text=" 4. Controles Sincronizados ", padding=10)
        sync_frame.pack(fill="x", expand=True, pady=(0, 15), padx=10)
        self._create_synced_controls(sync_frame)

        toast_frame = ttk.LabelFrame(main_container, text=" 5. Notificações ", padding=10)
        toast_frame.pack(fill="x", expand=True, pady=(0, 15), padx=10)
        self._create_notifications(toast_frame)

    def _create_buttons(self, parent):
        ttk.Label(parent, text="Estilos podem ser aplicados a botões ttk.").pack(anchor="w", pady=(0, 5))
        subframe = ttk.Frame(parent)
        subframe.pack(fill="x")
        ttk.Button(subframe, text="Success", style="Success.TButton").pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(subframe, text="Info", style="Info.TButton").pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(subframe, text="Warning", style="Warning.TButton").pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(subframe, text="Danger", style="Danger.TButton").pack(side="left", expand=True, fill="x", padx=2)
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

    def _create_selectors(self, parent):
        ttk.Label(parent, text="Checkbuttons:").pack(anchor="w")
        ttk.Checkbutton(parent, text="Opção independente 1").pack(anchor="w", padx=20)
        ttk.Checkbutton(parent, text="Opção 2").pack(anchor="w", padx=20, pady=5)

        ttk.Label(parent, text="\nRadiobuttons:").pack(anchor="w")
        radio_var = tk.StringVar(value="rb2")
        ttk.Radiobutton(parent, text="Escolha X", variable=radio_var, value="rb1").pack(anchor="w", padx=20)
        ttk.Radiobutton(parent, text="Escolha Y", variable=radio_var, value="rb2").pack(anchor="w", padx=20)

    def _create_synced_controls(self, parent):
        ttk.Label(parent, text="Arraste o Scale para ver a Progressbar e o contador se atualizarem:").pack(anchor="w",
                                                                                                           pady=(0, 10))
        scale = ttk.Scale(parent, from_=0, to=100, orient="horizontal", variable=self.controller.scale_var)
        scale.pack(fill="x", expand=True, pady=5)

        progressbar = ttk.Progressbar(parent, orient="horizontal", variable=self.controller.scale_var)
        progressbar.pack(fill="x", expand=True, pady=10)

        meter_frame = ttk.Frame(parent)
        meter_frame.pack(pady=10)
        ttk.Label(meter_frame, text="Nível: ").pack(side="left")
        self.meter_label = ttk.Label(meter_frame, text="75%", font=("-size", 14, "-weight", "bold"))
        self.meter_label.pack(side="left")

    def _create_notifications(self, parent):
        ttk.Button(parent, text="Exibir Notificação 'Toast'", command=self.controller._show_toast,
                   style="Info.TButton").pack(pady=5)