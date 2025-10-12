                      
from tkinter import ttk

class BasePanel(ttk.Frame):
    PANEL_NAME = "Nome do Painel"
    PANEL_ICON = "❓"
    ALLOWED_ACCESS = []

    def __init__(self, parent, app_controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app_controller
        self.create_widgets()

    def create_widgets(self):
        raise NotImplementedError("Cada painel deve implementar o método 'create_widgets'.")

    def show_placeholder_alert(self):
        self.app.show_placeholder_alert()