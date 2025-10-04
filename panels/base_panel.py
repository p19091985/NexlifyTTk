# panels/base_panel.py (CORRIGIDO)
from tkinter import ttk

# MODIFICAÇÃO: Herda de ttk.Frame para consistência com o ttkbootstrap
class BasePanel(ttk.Frame):
    """
    A classe base para todos os painéis de conteúdo da aplicação.
    Agora baseada em ttk.Frame para integração correta com temas.
    """
    # NOME E ÍCONE EXIBIDOS NA BARRA LATERAL
    PANEL_NAME = "Nome do Painel"
    PANEL_ICON = "❓"

    # LISTA DE NÍVEIS DE ACESSO QUE PODEM VER ESTE PAINEL.
    # Se a lista estiver vazia, todos os usuários podem ver.
    ALLOWED_ACCESS = []

    def __init__(self, parent, app_controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app_controller
        self.create_widgets()

    def create_widgets(self):
        """
        Método abstrato que deve ser implementado por cada painel filho
        para criar os widgets daquele painel.
        """
        raise NotImplementedError("Cada painel deve implementar o método 'create_widgets'.")

    def show_placeholder_alert(self):
        """ Atalho para chamar o alerta da aplicação principal. """
        self.app.show_placeholder_alert()