import tkinter as tk
from tkinter import ttk

class AboutDialog(tk.Toplevel):
    """
    Exibe informações detalhadas sobre a arquitetura e propósito do sistema.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Sobre o nexlifyttk (v1.0.0)")

        self.transient(parent)
        self.grab_set()

        self.update_idletasks()

        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        self_width = 550
        self_height = 480

        pos_x = parent_x + (parent_width // 2) - (self_width // 2)
        pos_y = parent_y + (parent_height // 2) - (self_height // 2)

        self.geometry(f"{self_width}x{self_height}+{pos_x}+{pos_y}")
        self.resizable(False, False)

        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=1)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(pady=(0, 15))

        ttk.Label(header_frame, text="🚀", font=("-size", 36)).pack(side="left", padx=(0, 10))
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side="left")

        ttk.Label(title_frame, text="nexlifyttk", font=("-size", 16, "-weight", "bold")).pack(anchor="w")
        ttk.Label(title_frame, text="Versão 1.0.0 — Template Desktop Python com Painéis", font=("-size", 9)).pack(anchor="w")

        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=(0, 15))

        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 15))

        purpose_tab = ttk.Frame(notebook, padding=10)
        notebook.add(purpose_tab, text=" Propósito ")
        ttk.Label(purpose_tab, text=(
            "O nexlifyttk é um boilerplate/template de referência para aplicações\n"
            "desktop Python, construído com Tkinter e o estilo ttk.\n\n"
            "Seu objetivo é fornecer uma base limpa e extensível para\n"
            "o desenvolvimento de aplicações desktop, com foco na clareza\n"
            "da organização do código e na facilidade de adicionar novas\n"
            "funcionalidades através do sistema de painéis."
        ), wraplength=self_width - 60, justify="left").pack(anchor="w")

        arch_tab = ttk.Frame(notebook, padding=10)
        notebook.add(arch_tab, text=" Arquitetura ")
        ttk.Label(arch_tab, text=(
            "O sistema é estruturado em camadas simples:\n\n"
            "■ Ponto de Entrada (run.py):\n"
            "   ↳ Inicializa loggers e lança a aplicação.\n\n"
            "■ Controlador Principal (app.py):\n"
            "   ↳ Janela raiz, sidebar de navegação, menus,\n"
            "      aplicação de tema visual.\n\n"
            "■ Painéis (panels/):\n"
            "   ↳ Cada painel combina View + Controller em uma\n"
            "      classe que herda de BasePanel.\n\n"
            "■ Configuração (config_settings.ini, settings.json):\n"
            "   ↳ Comportamento e aparência personalizáveis.\n\n"
            "■ Logging (persistencia/logger.py):\n"
            "   ↳ Sistema de log rotativo com categorias separadas."
        ), wraplength=self_width - 60, justify="left").pack(anchor="w")

        features_tab = ttk.Frame(notebook, padding=10)
        notebook.add(features_tab, text=" Destaques ")
        ttk.Label(features_tab, text=(
            "Pontos Notáveis:\n\n"
            "▶ Arquitetura Limpa: Separação clara entre UI,\n"
            "   lógica e configuração.\n\n"
            "▶ Extensível: Novos painéis são fáceis de adicionar\n"
            "   seguindo o template do Painel Modelo.\n\n"
            "▶ Configurável: Comportamento via config_settings.ini\n"
            "   e aparência via settings.json.\n\n"
            "▶ Logging Robusto: Sistema de log rotativo com\n"
            "   múltiplos loggers e categorias.\n\n"
            "▶ Cross-Platform: Funciona em Windows, Linux e macOS."
        ), wraplength=self_width - 60, justify="left").pack(anchor="w")

        ok_button = ttk.Button(main_frame, text="OK", command=self.destroy, style="Success.TButton")
        ok_button.pack(pady=(10, 0))
        ok_button.focus_set()

        self.wait_window(self)