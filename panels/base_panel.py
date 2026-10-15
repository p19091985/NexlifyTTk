                      
from tkinter import ttk
from persistencia.auth import authorize_page

class BasePanel(ttk.Frame):
    PANEL_NAME = "Nome do Painel"
    PANEL_ICON = "❓"

    def __init__(self, parent, app_controller, **kwargs):
        access = authorize_page(self.PANEL_NAME, project_root=app_controller.project_root)
        self.read_only = access['read_only']
        super().__init__(parent, **kwargs)
        self.app = app_controller
        self.create_widgets()

    def create_widgets(self):
        raise NotImplementedError("Cada painel deve implementar o método 'create_widgets'.")

    def show_placeholder_alert(self):
        self.app.show_placeholder_alert()
