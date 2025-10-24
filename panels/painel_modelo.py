import tkinter as tk
from tkinter import ttk, messagebox
from panels.base_panel import BasePanel

class PainelModelo(BasePanel):
    """
    Painel modelo unificado (View + Controller).
    Serve como template para criar novos painéis na aplicação.
    Demonstra a estrutura básica e interação com o controlador principal (app).
    """
    PANEL_NAME = "Painel Modelo"
    PANEL_ICON = "📋"
    ALLOWED_ACCESS = []                    

    def __init__(self, parent, app_controller, **kwargs):
                                                                                   
        super().__init__(parent, app_controller, **kwargs)

    def create_widgets(self):
        """
        Método principal que constrói a UI do painel.
        Deve chamar métodos auxiliares (_build_*) para organizar a criação.
        """
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        titulo = ttk.Label(main_frame, text="Estrutura de um Novo Painel (Unificado)",
                           font=("-size", 16, "-weight", "bold"))
        titulo.pack(pady=(0, 20))

        self._build_content(main_frame)

    def _build_content(self, parent):
        """ Constrói a área de conteúdo principal do painel modelo. """
        conteudo_frame = ttk.LabelFrame(parent, text=" Guia Rápido (Padrão Simplificado) ", padding=15)
        conteudo_frame.pack(fill="both", expand=True, pady=10)

        instrucoes_texto = (
            "Este painel demonstra a estrutura recomendada para novos painéis.\n\n"
            "Passos Sugeridos:\n"
            "1. Copie este arquivo (`painel_modelo.py`) para `painel_meu_painel.py`.\n\n"
            "2. Renomeie a classe para `PainelMeuPainel`.\n\n"
            "3. Defina `PANEL_NAME`, `PANEL_ICON`, `ALLOWED_ACCESS`.\n\n"
            "4. No `__init__`: inicialize `tk.StringVar`s e guarde refs de widgets (ex: `self.tree = None`).\n\n"
            "5. No `create_widgets`: Configure o layout principal e chame métodos auxiliares\n"
            "   para construir a UI (ex: `self._build_form(frame)`, `self._build_table(frame)`).\n\n"
            "6. Crie métodos `_build_*`: para encapsular a criação de widgets e layout (`.grid`, `.pack`).\n\n"
            "7. Crie métodos `_load_*` ou `_get_*`: para buscar dados (ex: `_load_data_into_table`)\n"
            "   ou pegar dados do formulário (ex: `_get_data_from_form`).\n\n"
            "8. Crie métodos `_on_*`: para tratar eventos (cliques, seleções).\n"
            "   (ex: `_on_save_button_click`, `_on_table_select`).\n"
            "   Estes métodos chamam validações, métodos de dados e atualizam a UI.\n\n"
            "9. Adicione comentários explicando o propósito de cada seção.\n\n"
            "10. Registre `PainelMeuPainel` em `panels/__init__.py`."
        )
        instrucoes_label = ttk.Label(conteudo_frame, text=instrucoes_texto, justify="left")
        instrucoes_label.pack(pady=10)

        botao_exemplo = ttk.Button(conteudo_frame, text="Testar Interação",
                                   command=self._on_test_button_click, style="Success.TButton")
        botao_exemplo.pack(pady=20)

    def _on_test_button_click(self):
        """ Lógica de exemplo chamada pelo botão 'Testar Interação'. """

        usuario_atual = self.app.get_current_user()

        messagebox.showinfo(
            "Interação Funcionou!",
            f"Olá, {usuario_atual['name']}!\n\n"
            f"O painel '{self.PANEL_NAME}' está funcionando corretamente.\n"
            "Ele pode acessar dados da aplicação principal.",
            parent=self                                                     
        )