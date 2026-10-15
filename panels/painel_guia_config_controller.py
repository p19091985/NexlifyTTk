import webbrowser
from panels.base_panel import BasePanel
from .painel_guia_config_view import GuiaConfigView

class PainelGuiaConfig(BasePanel):
    """
    Controller para o painel que exibe o guia de configuração da aplicação.
    """
    PANEL_NAME = "Guia de Configuração"
    PANEL_ICON = "📚"

    def __init__(self, parent, app_controller, **kwargs):
        super().__init__(parent, app_controller, **kwargs)

    def create_widgets(self):
        """Cria a view e a exibe na tela."""
        self.view = GuiaConfigView(self, controller=self)
        self.view.pack(fill="both", expand=True)

    def _open_video_link(self):
        """Abre o link do vídeo de introdução no navegador."""
        url = "https://www.youtube.com/watch?v=zxA97KcUm1Q"
        webbrowser.open(url)
