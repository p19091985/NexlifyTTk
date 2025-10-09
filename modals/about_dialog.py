# modals/about_dialog.py
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as bstrap


class AboutDialog(bstrap.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Sobre a Aplicação")

        # Configuração para tornar a janela modal
        self.transient(parent)
        self.grab_set()

        # Centralizar a janela em relação ao pai
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        self_width = 350
        self_height = 220

        pos_x = parent_x + (parent_width // 2) - (self_width // 2)
        pos_y = parent_y + (parent_height // 2) - (self_height // 2)

        self.geometry(f"{self_width}x{self_height}+{pos_x}+{pos_y}")
        self.resizable(False, False)

        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        app_icon_label = ttk.Label(main_frame, text="🚀", font=("-size", 36))
        app_icon_label.pack()

        title_label = ttk.Label(
            main_frame,
            text="Sistema de Demonstração",
            font=("-size", 14, "-weight", "bold")
        )
        title_label.pack(pady=(10, 5))

        version_label = ttk.Label(
            main_frame,
            text="Versão 1.0.0",
            font=("-size", 9),
            style="secondary.TLabel"
        )
        version_label.pack()

        description_label = ttk.Label(
            main_frame,
            text="Este é um exemplo de aplicação construído com Tkinter e ttkbootstrap,\n"
                 "demonstrando padrões de arquitetura como MVC.",
            justify="center",
            wraplength=300
        )
        description_label.pack(pady=10)

        ok_button = ttk.Button(main_frame, text="OK", command=self.destroy, style="primary.TButton")
        ok_button.pack(pady=(10, 0))
        ok_button.focus_set()

        # Esperar até que a janela seja fechada
        self.wait_window(self)