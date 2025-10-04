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

from dialogs.advanced_theme_dialog import AdvancedThemeDialog
from dialogs.login_ui import LoginDialog

from modals.tipos_linguagem_modal import TiposLinguagemModal


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

            try:
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

        if config.USE_LOGIN:
            user_info = self._run_login_process()
            if not user_info or user_info == "max_attempts_failed":
                self.destroy()
                return
        else:
            user_info = {"name": "Desenvolvedor", "access_level": "Administrador Global", "username": "dev"}

        self.title("Painel de Controlo Moderno")
        try:
            self.logger = logging.getLogger("main_app")
            self.current_user = user_info
            self._set_initial_geometry()
            self.panels: Dict[str, BasePanel] = {}
            self.sidebar_buttons: Dict[str, ttk.Button] = {}
            self.current_panel_name: str = ""
            self._setup_ui()
            self.config(menu=self._create_menubar())
            if self.sidebar_buttons:
                first_button_name = next(iter(self.sidebar_buttons))
                self.switch_panel_by_name(first_button_name)
            self.deiconify()
        except Exception as e:
            logging.error(f"Erro na inicialização da aplicação: {e}", exc_info=True)
            self.destroy()
            raise

    def _run_login_process(self) -> dict | None:
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
        ttk.Separator(self.sidebar_frame, orient="horizontal").pack(fill='x', pady=5, padx=10)
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self._load_and_create_panels()
        logout_btn = ttk.Button(self.sidebar_frame, text="🚪 Sair", command=self.destroy, style="danger.TButton")
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
                # --- MODIFICAÇÃO: Adiciona uma notificação de erro visual ---
                error_message = f"Erro fatal ao carregar o painel '{PanelClass.__name__}':\n\n{e}"
                self.logger.error(error_message, exc_info=True)
                messagebox.showerror("Erro de Carregamento de Painel", error_message)

    def switch_panel_by_name(self, panel_name: str):
        if self.current_panel_name:
            self.panels[self.current_panel_name].pack_forget()
        self.current_panel_name = panel_name
        panel = self.panels[panel_name]
        panel.pack(fill="both", expand=True)
        self.logger.info(f"Utilizador trocou para o painel: '{panel_name}'")

    def _create_menubar(self) -> tk.Menu:
        menubar = tk.Menu(self)
        cadastros_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Cadastros", menu=cadastros_menu)
        for name in self.sidebar_buttons.keys():
            if "gestão" in name.lower():
                cadastros_menu.add_command(label=name, command=lambda n=name: self.switch_panel_by_name(n))
        cadastros_menu.add_separator()
        cadastros_menu.add_command(label="Tipos de Linguagem...", command=self._open_tipos_linguagem_modal)

        navegacao_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Navegação", menu=navegacao_menu)
        for name in self.sidebar_buttons.keys():
            if "gestão" not in name.lower():
                navegacao_menu.add_command(label=name, command=lambda n=name: self.switch_panel_by_name(n))

        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Configurações", menu=settings_menu)
        settings_menu.add_command(label="Aparência e Tema", command=self._open_advanced_theme_dialog)
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre", command=self._show_about_dialog)
        menubar.add_command(label="Sair", command=self.destroy)
        return menubar

    def _open_tipos_linguagem_modal(self):
        try:
            callback = None
            current_panel = self.panels.get(self.current_panel_name)
            if current_panel and hasattr(current_panel, '_carregar_tipos_linguagem'):
                callback = current_panel._carregar_tipos_linguagem
                self.logger.info(f"Callback de atualização definido para o painel '{self.current_panel_name}'.")
            modal = TiposLinguagemModal(self, on_close_callback=callback)
            modal.wait_window()
        except Exception as e:
            self.logger.error(f"Erro ao abrir a janela modal: {e}", exc_info=True)
            messagebox.showerror("Erro Crítico", f"Não foi possível abrir a janela de gestão: {e}")

    def _open_advanced_theme_dialog(self):
        AdvancedThemeDialog(self, self.settings_manager)

    def _show_about_dialog(self):
        messagebox.showinfo("Sobre",
                            "Painel de Controlo Moderno v1.0\n\nDesenvolvido com Python, Tkinter e ttkbootstrap.")

    def _set_initial_geometry(self) -> None:
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        width = int(w * config.MAIN_WINDOW_RATIO)
        height = int(h * config.MAIN_WINDOW_RATIO)
        self.geometry(f"{width}x{height}+{(w - width) // 2}+{(h - height) // 2}")
        self.minsize(int(width * config.MAIN_WINDOW_MIN_SIZE_RATIO), int(height * config.MAIN_WINDOW_MIN_SIZE_RATIO))