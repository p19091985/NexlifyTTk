import tkinter as tk
from tkinter import ttk, font
from tkinter import scrolledtext
from panels.base_panel import BasePanel

class PainelGuiaConfig(BasePanel):
    """
    Painel unificado (View + Controller) que exibe um guia formatado
    sobre as configurações e modos de operação da aplicação.
    O conteúdo é estático e lido diretamente do código.
    """
    PANEL_NAME = "Guia de Configuração"
    PANEL_ICON = "📚"

    def __init__(self, parent, app_controller, **kwargs):
        super().__init__(parent, app_controller, **kwargs)

    def create_widgets(self):
        """
        Método principal que constrói a UI do painel.
        Cria uma área de texto formatada (ScrolledText) para exibir o guia.
        """
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        titulo = ttk.Label(main_frame, text="⚙️ Guia de Configuração e Modos de Operação",
                           font=("-size", 18, "-weight", "bold"))
        titulo.pack(pady=(0, 20), anchor="w")

        text_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=20,
                                              font=("Segoe UI", 10), bd=0, relief=tk.FLAT,
                                              padx=15, pady=15, background="white")
        text_area.pack(fill="both", expand=True, pady=10)

        code_font = "Consolas" if "Consolas" in font.families() else "Courier New"
        header_font_family = "Segoe UI Semibold" if "Segoe UI Semibold" in font.families() else "Segoe UI"
        subheader_font_family = "Segoe UI Semibold" if "Segoe UI Semibold" in font.families() else "Segoe UI"

        text_area.tag_configure("h1", font=(header_font_family, 16, "bold"), spacing1=20, spacing3=10, foreground="#003366")
        text_area.tag_configure("h2", font=(subheader_font_family, 13, "bold"), spacing1=15, spacing3=8, foreground="#005a9e")
        text_area.tag_configure("h3", font=("Segoe UI", 11, "bold"), spacing1=10, spacing3=5, foreground="#333333")
        text_area.tag_configure("code", font=(code_font, 9), background="#f5f5f5", wrap=tk.NONE,
                                lmargin1=25, lmargin2=25, borderwidth=1, relief=tk.SOLID,
                                spacing1=8, spacing3=8, tabs=("1c", "2c", "3c"))
        text_area.tag_configure("bold", font=("Segoe UI", 10, "bold"))
        text_area.tag_configure("italic", font=("Segoe UI", 10, "italic"))
        text_area.tag_configure("body", lmargin1=10, lmargin2=10, spacing3=6)
        text_area.tag_configure("note", lmargin1=20, lmargin2=20, foreground="#555555", font=("Segoe UI", 9, "italic"), spacing3=8)
        text_area.tag_configure("flag", font=(code_font, 10, "bold"), foreground="#cc0000")
        text_area.tag_configure("success", foreground="#155724", font=("Segoe UI", 10, "bold"))
        text_area.tag_configure("info", foreground="#004085")

        text_area.insert(tk.END, "Guia de Configuração da Aplicação\n", "h1")
        text_area.insert(tk.END,
                         "Esta aplicação é um template/boilerplate de referência, construído com Tkinter e o estilo ttk. "
                         "As configurações, localizadas no arquivo ", "body")
        text_area.insert(tk.END, "config_settings.ini", "code")
        text_area.insert(tk.END,
                         ", permitem ajustar o comportamento do sistema.\n\n", "body")

        text_area.insert(tk.END, "1. Detalhamento das Configurações (`config_settings.ini`)\n", "h2")
        text_area.insert(tk.END,
                         "Para alterar o modo de operação, edite os valores no arquivo ", "body")
        text_area.insert(tk.END, "config_settings.ini", "code")
        text_area.insert(tk.END, " e reinicie a aplicação.\n\n", "body")

        text_area.insert(tk.END, "REDIRECT_CONSOLE_TO_LOG\n", "flag")
        text_area.insert(tk.END, "   ↳ Direcionamento de Saída (Logs)\n", "italic")
        text_area.insert(tk.END, "   ▪ ", "body")
        text_area.insert(tk.END, "True:", "bold")
        text_area.insert(tk.END,
                         " (Produção / Debug Centralizado) Saídas do console (`print`, erros) são redirecionadas para os arquivos de log rotativos em ", "body")
        text_area.insert(tk.END, "logs/", "code")
        text_area.insert(tk.END, ". Mantém o terminal limpo.\n", "body")
        text_area.insert(tk.END, "   ▪ ", "body")
        text_area.insert(tk.END, "False:", "bold")
        text_area.insert(tk.END,
                         " (Debug Rápido) As saídas aparecem diretamente no terminal onde a aplicação foi iniciada. Útil para visibilidade imediata.\n\n", "body")

        text_area.insert(tk.END, "ENABLE_THEME_MENU\n", "flag")
        text_area.insert(tk.END, "   ↳ Controla a Exibição do Menu de Temas\n", "italic")
        text_area.insert(tk.END, "   ▪ ", "body")
        text_area.insert(tk.END, "True:", "bold")
        text_area.insert(tk.END, " Exibe opções de personalização de tema no menu de configurações.\n", "body")
        text_area.insert(tk.END, "   ▪ ", "body")
        text_area.insert(tk.END, "False:", "bold")
        text_area.insert(tk.END, " Oculta as opções de tema.\n\n", "body")

        text_area.insert(tk.END, "2. Configurações de Estilo (`settings.json`)\n", "h2")
        text_area.insert(tk.END,
                         "O arquivo ", "body")
        text_area.insert(tk.END, "settings.json", "code")
        text_area.insert(tk.END,
                         " permite personalizar a aparência da aplicação:\n\n", "body")
        text_area.insert(tk.END, "   ▪ ", "body")
        text_area.insert(tk.END, "font_family:", "bold")
        text_area.insert(tk.END, " Família da fonte (ex: 'Segoe UI', 'Arial').\n", "body")
        text_area.insert(tk.END, "   ▪ ", "body")
        text_area.insert(tk.END, "font_size:", "bold")
        text_area.insert(tk.END, " Tamanho da fonte em pontos.\n", "body")
        text_area.insert(tk.END, "   ▪ ", "body")
        text_area.insert(tk.END, "custom_colors:", "bold")
        text_area.insert(tk.END, " Cores personalizadas para os estilos de botão (danger, success, warning, etc.).\n\n", "body")

        text_area.insert(tk.END, "3. Configuração de Logging\n", "h2")
        text_area.insert(tk.END,
                         "O sistema de logging é configurado em ", "body")
        text_area.insert(tk.END, "config_settings.ini", "code")
        text_area.insert(tk.END, " com as seguintes opções:\n\n", "body")
        text_area.insert(tk.END, "   ▪ ", "body")
        text_area.insert(tk.END, "log_level:", "bold")
        text_area.insert(tk.END, " Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL).\n", "body")
        text_area.insert(tk.END, "   ▪ ", "body")
        text_area.insert(tk.END, "log_format:", "bold")
        text_area.insert(tk.END, " Formato das mensagens de log.\n\n", "body")

        text_area.insert(tk.END, "4. Como Adicionar Novos Painéis\n", "h2")
        text_area.insert(tk.END,
                         "Use o Painel Modelo como referência. Os passos são:\n\n", "body")
        text_area.insert(tk.END,
                         "1. Copie `painel_modelo.py` para um novo arquivo.\n"
                         "2. Renomeie a classe e defina PANEL_NAME, PANEL_ICON.\n"
                         "3. Implemente `create_widgets()` com sua UI.\n"
                         "4. Registre o novo painel em `panels/__init__.py`.\n", "code")
        text_area.insert(tk.END, "\n", "body")

        text_area.insert(tk.END, "--- Fim do Guia ---\n", ("italic", "body"))

        text_area.config(state="disabled")