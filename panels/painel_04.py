# painel_04.py (CORRIGIDO E COMPLETO)
import tkinter as tk
from tkinter import ttk, colorchooser
from panels.base_panel import BasePanel


class PainelWidgetsVisuais(BasePanel):
    PANEL_NAME = "Widgets Visuais"
    PANEL_ICON = "🎨"
    ALLOWED_ACCESS = []

    def create_widgets(self):
        self.draw_color = "black"
        self.old_x, self.old_y = None, None

        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        paned_window = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        paned_window.pack(fill="both", expand=True)

        canvas_frame = ttk.LabelFrame(paned_window, text=" Canvas Interativo ", padding=10)
        paned_window.add(canvas_frame, weight=3)

        self.canvas = tk.Canvas(canvas_frame, bg="white", cursor="cross", relief="sunken", borderwidth=1)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<B1-Motion>", self._desenhar_no_canvas)
        self.canvas.bind("<ButtonRelease-1>", self._resetar_desenho)

        controls_canvas_frame = ttk.Frame(canvas_frame)
        controls_canvas_frame.pack(fill="x", pady=(10, 0))

        color_button = ttk.Button(controls_canvas_frame, text="Mudar Cor", command=self._choose_color)
        color_button.pack(side="left", padx=(0, 10))

        clear_button = ttk.Button(controls_canvas_frame, text="Limpar Tela", command=lambda: self.canvas.delete("all"))
        clear_button.pack(side="left")

        bottom_frame = ttk.Frame(paned_window)
        paned_window.add(bottom_frame, weight=1)

        controls_left_frame = ttk.LabelFrame(bottom_frame, text=" Controles Sincronizados ", padding=10)
        controls_left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=10)

        self.scale_var = tk.DoubleVar(value=50)

        scale_label = ttk.Label(controls_left_frame, textvariable=self.scale_var, font=("Courier", 12, "bold"))
        scale_label.pack(pady=5)

        scale = ttk.Scale(controls_left_frame, from_=0, to=100, orient="horizontal", variable=self.scale_var)
        scale.pack(fill="x", expand=True, pady=5)

        progressbar = ttk.Progressbar(controls_left_frame, orient="horizontal", variable=self.scale_var,
                                      mode="determinate")
        progressbar.pack(fill="x", expand=True, pady=10)

    def _choose_color(self):
        color_code = colorchooser.askcolor(title="Escolha uma cor")
        if color_code and color_code[1]:
            self.draw_color = color_code[1]

    def _desenhar_no_canvas(self, event):
        if self.old_x and self.old_y:
            self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                    width=2, fill=self.draw_color,
                                    capstyle=tk.ROUND, smooth=tk.TRUE, splinesteps=36)
        self.old_x = event.x
        self.old_y = event.y

    def _resetar_desenho(self, event):
        self.old_x, self.old_y = None, None