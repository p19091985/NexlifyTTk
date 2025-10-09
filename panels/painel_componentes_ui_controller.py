# panels/painel_componentes_ui_controller.py
import tkinter as tk
from ttkbootstrap.toast import ToastNotification
from panels.base_panel import BasePanel
from .painel_componentes_ui_view import ComponentesUIView

class PainelComponentesUI(BasePanel):
    PANEL_NAME = "Componentes UI"
    PANEL_ICON = "🎨"
    ALLOWED_ACCESS = []

    def __init__(self, parent, app_controller, **kwargs):
        self.scale_var = tk.DoubleVar(value=75)
        super().__init__(parent, app_controller, **kwargs)
        self.scale_var.trace_add("write", self._update_meter)

    def create_widgets(self):
        self.view = ComponentesUIView(self, controller=self)
        self.view.pack(fill="both", expand=True)

    def _update_meter(self, *args):
        current_value = self.scale_var.get()
        if self.view.meter:
            self.view.meter.configure(amountused=current_value)

    def _show_toast(self):
        toast = ToastNotification(
            title="Notificação de Exemplo",
            message="Esta é uma notificação 'toast'.\nExcelente para feedback não-bloqueante.",
            duration=3000,
            bootstyle="info",
            position=(20, 20, 'se')
        )
        toast.show_toast()