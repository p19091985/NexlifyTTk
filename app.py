# app.py
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, Any
import ttkbootstrap as bstrap

# Imports locais da aplicação
import config
from panels.base_panel import BasePanel
from panels import ALL_PANELS
from settings_manager import SettingsManager

# Importa as janelas de diálogo (modais)
from dialogs.advanced_theme_dialog import AdvancedThemeDialog
from dialogs.login_ui import LoginDialog
from modals.tipos_linguagem_controller import TiposLinguagemController
from modals.about_dialog import AboutDialog


class AplicacaoPrincipal(bstrap.Window):
    """
    A classe principal da aplicação que gerencia a janela, o login,
    os painéis e a personalização de temas.
    """

    @staticmethod
    def _apply_theme_settings(style_object: bstrap.Style, settings: Dict[str, Any]):
        """Aplica um dicionário de configurações a um objeto de estilo."""
        try:
            style_object.theme_use(settings.get("theme", "litera"))
            custom_colors = settings.get("custom_colors", {})
            for name, color in custom_colors.items():
                if color:
                    style_object.colors.set(name, color)
            font_family = settings.get('font_family', 'Segoe UI')
            font_size = settings.get('font_size', 10)
            style_object.configure('.', font=(font_family, font_size))
            border_radius = settings.get('border_radius', 8)
            focus_ring_width = 1 if settings.get('focus_ring', True) else 0
            # Usar 'call' para variáveis de tema ttkbootstrap de forma segura
            style_object.master.tk.call('set_var', 'theme_borderradius', border_radius)
            style_object.master.tk.call('set_var', 'theme_focus_ring_width', focus_ring_width)
        except tk.TclError:
            logging.warning("Comandos 'set_var' não encontrados. Ajustes finos podem não ser aplicados.")
        except Exception as e:
            logging.error(f"Erro ao aplicar configurações de tema: {e}", exc_info=True)

    def __init__(self, project_root: str) -> None:
        self.settings_manager = SettingsManager(project_root=project_root)
        current_settings = self.settings_manager.load_settings()
        super().__init__(themename=current_settings.get("theme", "litera"))
        self._apply_theme_settings(self.style, current_settings)

        self.withdraw()
        self.logger = logging.getLogger("main_app")
        self.project_root = project_root

        if config.USE_LOGIN:
            user_info = self._run_login_process()
            if not user_info or user_info in ["max_attempts_failed", "connection_error"]:
                self.destroy()
                return
        else:
            user_info = {"name": "Desenvolvedor", "access_level": "Administrador Global", "username": "dev"}

        self._initialize_session_for_user(user_info)

    def _initialize_session_for_user(self, user_info: Dict[str, Any]):
        """
        Constrói ou reconstrói a UI completa para o usuário logado.
        """
        for widget in self.winfo_children():
            widget.destroy()

        self.current_user = user_info
        self.title("Painel de Controle Moderno")
        self._set_initial_geometry()

        self.panels: Dict[str, BasePanel] = {}
        self.sidebar_buttons: Dict[str, ttk.Button] = {}
        self.current_panel_name: str = ""

        self._setup_ui()
        self.config(menu=self._create_menubar())

        if self.sidebar_buttons:
            first_button_name = next(iter(self.sidebar_buttons))
            self.switch_panel_by_name(first_button_name)

        self.protocol("WM_DELETE_WINDOW", self._confirm_exit)
        self.deiconify()

    def _run_login_process(self) -> dict | str | None:
        login_dialog = LoginDialog(self)
        self.wait_window(login_dialog)
        return login_dialog.user_info

    def get_current_user(self) -> dict:
        return self.current_user

    def _setup_ui(self) -> None:
        self.sidebar_frame = ttk.Frame(self, width=250, style='secondary.TFrame')
        self.sidebar_frame.pack(side="left", fill="y", padx=(5, 0), pady=5)
        self.sidebar_frame.pack_propagate(False)

        user_info_frame = ttk.Frame(self.sidebar_frame, style='secondary.TFrame')
        user_info_frame.pack(fill="x", pady=10, padx=10)

        ttk.Label(user_info_frame, text=f"Utilizador: {self.current_user['name']}", anchor="w",
                  style="secondary.Inverse.TLabel").pack(fill="x")
        ttk.Label(user_info_frame, text=f"Perfil: {self.current_user['access_level']}", anchor="w",
                  style="secondary.Inverse.TLabel").pack(fill="x")

        ttk.Button(user_info_frame, text="Trocar de Usuário", command=self._switch_user,
                   style="info.Link.TButton").pack(fill="x", pady=(5, 0))

        ttk.Separator(self.sidebar_frame, orient="horizontal").pack(fill='x', pady=5, padx=10)

        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self._load_and_create_panels()

        logout_btn = ttk.Button(self.sidebar_frame, text="🚪 Sair da Aplicação", command=self._confirm_exit,
                                style="danger.TButton")
        logout_btn.pack(side="bottom", fill="x", pady=10, padx=10)

    def _load_and_create_panels(self):
        user_access_level = self.current_user.get('access_level', 'Desenvolvedor')
        for PanelClass in ALL_PANELS:
            try:
                if not PanelClass.ALLOWED_ACCESS or user_access_level in PanelClass.ALLOWED_ACCESS:
                    name, icon = PanelClass.PANEL_NAME, PanelClass.PANEL_ICON
                    panel_instance = PanelClass(self.content_frame, self)
                    self.panels[name] = panel_instance
                    btn = ttk.Button(self.sidebar_frame, text=f" {icon} {name}", compound="left",
                                     command=lambda n=name: self.switch_panel_by_name(n),
                                     style="primary.Outline.TButton")
                    btn.pack(fill="x", pady=2, padx=10)
                    self.sidebar_buttons[name] = btn
            except Exception as e:
                messagebox.showerror("Erro de Carregamento de Painel",
                                     f"Erro fatal ao carregar o painel '{PanelClass.__name__}':\n\n{e}")

    def switch_panel_by_name(self, panel_name: str):
        if panel_name not in self.panels: return
        if self.current_panel_name in self.panels:
            self.panels[self.current_panel_name].pack_forget()
        self.current_panel_name = panel_name
        self.panels[panel_name].pack(fill="both", expand=True)

    def _create_menubar(self) -> tk.Menu:
        menubar = tk.Menu(self)

        # Menu Cadastros
        cadastros_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Cadastros", menu=cadastros_menu)
        for name in self.sidebar_buttons.keys():
            if "gestão" in name.lower() or "catálogo" in name.lower():
                cadastros_menu.add_command(label=name, command=lambda n=name: self.switch_panel_by_name(n))
        cadastros_menu.add_separator()
        cadastros_menu.add_command(label="Tipos de Linguagem...", command=self._open_tipos_linguagem_modal)

        # Menu Configurações
        config_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Configurações", menu=config_menu)

        # Adiciona o item de menu para Aparência e Tema
        config_menu.add_command(label="Aparência e Tema...", command=self._open_theme_dialog)

        # Desabilita o item de menu se a flag em config.py for False
        if not config.ENABLE_THEME_MENU:
            config_menu.entryconfig("Aparência e Tema...", state="disabled")

        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre", command=self._show_about_dialog)

        menubar.add_command(label="Sair", command=self._confirm_exit)
        return menubar

    def _switch_user(self):
        self.logger.info(f"Usuário '{self.current_user['username']}' iniciou a troca de sessão.")
        self.withdraw()
        new_user_info = self._run_login_process()
        if new_user_info and new_user_info not in ["max_attempts_failed", "connection_error"]:
            self.logger.info(f"Login bem-sucedido para '{new_user_info['username']}'. Reconstruindo UI.")
            self._initialize_session_for_user(new_user_info)
        else:
            self.logger.warning("Troca de usuário falhou ou foi cancelada. Fechando a aplicação.")
            self.destroy()

    def _open_tipos_linguagem_modal(self):
        try:
            callback = None
            current_panel = self.panels.get(self.current_panel_name)
            if current_panel and hasattr(current_panel, '_carregar_tipos_linguagem'):
                callback = current_panel._carregar_tipos_linguagem
            controller = TiposLinguagemController(self, on_close_callback=callback)
            controller.show()
        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Não foi possível abrir a janela de gestão: {e}")

    def _open_theme_dialog(self):
        """Abre a janela de configuração de temas, passando o gerenciador de configurações."""
        AdvancedThemeDialog(self, self.settings_manager)

    def _show_about_dialog(self):
        AboutDialog(self)

    def _confirm_exit(self):
        if messagebox.askyesno("Confirmar Saída", "Tem certeza que deseja fechar a aplicação?", icon='warning',
                               parent=self):
            self.destroy()

        # app.py (versão corrigida e recomendada)

    def _set_initial_geometry(self) -> None:
        """Define a janela para iniciar maximizada de forma compatível."""
        try:
            # Tenta maximizar a janela usando o método mais moderno e compatível
            self.attributes('-zoomed', True)
        except tk.TclError:
            # Se o método acima falhar, usa um fallback para preencher a tela
            w, h = self.winfo_screenwidth(), self.winfo_screenheight()
            self.geometry(f"{w}x{h}+0+0")

        # Define um tamanho mínimo para o caso de o usuário redimensionar a janela
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.minsize(int(w * 0.5), int(h * 0.5))