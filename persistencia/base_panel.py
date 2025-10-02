import tkinter as tk

class BasePanel(tk.Frame):
    """
    A classe base para todos os painéis de conteúdo da aplicação.
    """
    # NOME E ÍCONE EXIBIDOS NA BARRA LATERAL
    PANEL_NAME = "Nome do Painel"
    PANEL_ICON = "❓"

    # LISTA DE NÍVEIS DE ACESSO QUE PODEM VER ESTE PAINEL.
    # Se a lista estiver vazia, todos os usuários podem ver.
    # Exemplo: ALLOWED_ACCESS = ["Administrador Global", "Gerente de TI"]
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
