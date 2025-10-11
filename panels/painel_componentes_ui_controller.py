# panels/painel_componentes_ui_controller.py
import tkinter as tk
from tkinter import Toplevel, Label
from panels.base_panel import BasePanel
from .painel_componentes_ui_view import ComponentesUIView


class ToastNotification(Toplevel):
    def __init__(self, parent, title, message, duration=3000):
        super().__init__(parent)
        self.overrideredirect(True)

        Label(self, text=title, font=("-weight", "bold"), padx=10, pady=5, anchor='w', background='#333',
              foreground='white').pack(fill='x')
        Label(self, text=message, padx=10, pady=10, wraplength=250, justify='left').pack(fill='x')

        self.update_idletasks()

        parent.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()

        x = parent_x + parent_width - self.winfo_width() - 20
        y = parent_y + parent.winfo_height() - self.winfo_height() - 20

        self.geometry(f"+{x}+{y}")
        self.after(duration, self.destroy)


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
        self._update_meter()

    def _update_meter(self, *args):
        current_value = self.scale_var.get()
        if self.view.meter_label:
            self.view.meter_label.config(text=f"{current_value:.0f}%")

    def _show_toast(self):
        ToastNotification(
            self,
            title="Notificação de Exemplo",
            message="Esta é uma notificação 'toast'.\nExcelente para feedback não-bloqueante.",
            duration=3000
        )