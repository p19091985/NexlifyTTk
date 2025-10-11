# panels/painel_modelo_controller.py
from tkinter import messagebox
from panels.base_panel import BasePanel
from .painel_modelo_view import ModeloView

class PainelModelo(BasePanel):
    PANEL_NAME = "Painel Modelo"
    PANEL_ICON = "📋"
    ALLOWED_ACCESS = []

    def __init__(self, parent, app_controller, **kwargs):
        super().__init__(parent, app_controller, **kwargs)

    def create_widgets(self):
        self.view = ModeloView(self, controller=self)
        self.view.pack(fill="both", expand=True)

    def _on_botao_click(self):
        usuario_atual = self.app.get_current_user()
        messagebox.showinfo(
            "Interação Funcionou!",
            f"Olá, {usuario_atual['name']}!\n\nO painel modelo no padrão MVC está funcionando corretamente.",
            parent=self
        )