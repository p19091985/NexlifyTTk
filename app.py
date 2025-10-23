import tkinter as tk
from tkinter import ttk, messagebox, font
import logging
from typing import Dict, Any
import platform
import config
from panels.base_panel import BasePanel
from panels import ALL_PANELS
from settings_manager import SettingsManager
from dialogs.login_ui import LoginDialog
from modals.tipos_vegetais_manager import TiposVegetaisManagerDialog
from modals.about_dialog import AboutDialog


class AplicacaoPrincipal(tk.Tk):
    def __init__(self, project_root: str) -> None:
        super().__init__()

        self.settings_manager = SettingsManager(project_root=project_root)

        self.withdraw()

        self._configure_styles()
        current_settings = self.settings_manager.load_settings()
        self._apply_theme_settings(self.style, current_settings)

        self.logger = logging.getLogger("main_app")
        self.project_root = project_root

        self.current_user = None

        if config.USE_LOGIN:
            self.logger.info("Sistema de login ATIVO.")
            user_info = self._run_login_process()

            if not user_info or user_info in ["max_attempts_failed", "connection_error"]:
                self.logger.warning("Falha no login ou cancelado. Encerrando aplicação.")
                self.destroy()
                return
        else:
            self.logger.warning("Sistema de login DESABILITADO. Usando usuário de desenvolvimento.")
            user_info = {"name": "Usuário de Desenvolvimento", "access_level": "Administrador Global",
                         "username": "dev_user"}

        self._initialize_session_for_user(user_info)

    def _configure_styles(self):
        """Configurações básicas do estilo ttk."""
        self.style = ttk.Style(self)
        self.style.theme_use('clam')

    def _apply_theme_settings(self, style_obj: ttk.Style, settings: Dict[str, Any]):
        """
        Aplica as configurações de fonte e cor lidas do settings.json
        ao objeto de estilo ttk.
        """
        font_family = settings.get('font_family', 'Segoe UI')
        font_size = settings.get('font_size', 10)
        default_font_tuple = (font_family, font_size)

        try:
            font.Font(family=font_family, size=font_size)
            style_obj.configure('.', font=default_font_tuple)
            style_obj.configure('Treeview', font=default_font_tuple)
            style_obj.configure('Treeview.Heading', font=(font_family, font_size, 'bold'))
            logging.debug(f"Fonte aplicada: {font_family}, {font_size}pt")
        except tk.TclError:
            logging.warning(f"Fonte '{font_family}' não encontrada ou inválida. Usando 'TkDefaultFont'.")
            default_font_tuple = ('TkDefaultFont', font_size)
            style_obj.configure('.', font=default_font_tuple)
            style_obj.configure('Treeview', font=default_font_tuple)
            style_obj.configure('Treeview.Heading', font=('TkDefaultFont', font_size, 'bold'))

        custom_colors = settings.get('custom_colors', {})
        logging.debug(f"Cores carregadas do settings: {custom_colors}")

        button_styles_config = {
            'Danger.TButton': {'key': 'danger', 'default_bg': '#dc3545', 'active': '#c82333'},
            'Success.TButton': {'key': 'success', 'default_bg': '#28a745', 'active': '#218838'},
            'Warning.TButton': {'key': 'warning', 'default_bg': '#ffc107', 'active': '#e0a800', 'fg': 'black'},
            'Info.TButton': {'key': 'info', 'default_bg': '#17a2b8', 'active': '#138496'},
            'Secondary.TButton': {'key': 'secondary', 'default_bg': '#6c757d', 'active': '#5a6268'},
        }

        for style_name, config_data in button_styles_config.items():
                                        
                                                                                                 
            bg_color = custom_colors.get(config_data['key'], config_data['default_bg']) or config_data['default_bg']

            fg_color = config_data.get('fg', 'white')

                                                                                                                
            active_bg = config_data.get('active', bg_color) or bg_color
                                     

            try:
                style_obj.configure(style_name, foreground=fg_color, background=bg_color, padding=6, relief="flat")
                style_obj.map(style_name, background=[('active', active_bg)])
                logging.debug(f"Aplicado estilo '{style_name}': BG={bg_color}, FG={fg_color}, ActiveBG={active_bg}")
            except tk.TclError as e:
                logging.warning(f"Erro ao aplicar estilo '{style_name}' com cor {bg_color}: {e}. Usando fallback.")
                try:
                    style_obj.configure(style_name, foreground=fg_color, background=config_data['default_bg'], padding=6,
                                        relief="flat")
                    style_obj.map(style_name, background=[('active', config_data['active'])])
                except tk.TclError:
                    logging.error(f"Falha crítica ao aplicar fallback para '{style_name}'.")

        style_obj.configure('TButton', padding=6, relief="flat")
        style_obj.configure('Sidebar.TFrame', background='#f0f0f0')
        style_obj.configure('Sidebar.TLabel', background='#f0f0f0')
        style_obj.configure('Sidebar.TButton', background='#f0f0f0', borderwidth=0, anchor='w')
        style_obj.map('Sidebar.TButton', background=[('active', '#dcdcdc')])

    def _initialize_session_for_user(self, user_info: Dict[str, Any]):
        """Limpa a UI antiga (se houver) e constrói a nova com base no usuário."""
        for widget in self.winfo_children():
            widget.destroy()

        self.current_user = user_info
        self.title("Painel de Controle nexlifyttk")
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
        """Abre o diálogo de login e aguarda o resultado."""
        login_dialog = LoginDialog(self)
        self.wait_window(login_dialog)
        return login_dialog.user_info

    def get_current_user(self) -> dict:
        """Método público para outros painéis acessarem dados do usuário logado."""
        return self.current_user

    def _setup_ui(self) -> None:
        """Cria a estrutura da UI principal (sidebar e área de conteúdo)."""
        self.sidebar_frame = ttk.Frame(self, width=250, style='Sidebar.TFrame')
        self.sidebar_frame.pack(side="left", fill="y", padx=(5, 0), pady=5)
        self.sidebar_frame.pack_propagate(False)

        user_info_frame = ttk.Frame(self.sidebar_frame, style='Sidebar.TFrame')
        user_info_frame.pack(fill="x", pady=10, padx=10)

        ttk.Label(user_info_frame, text=f"Usuário: {self.current_user['name']}", anchor="w",
                  style='Sidebar.TLabel').pack(fill="x")
        ttk.Label(user_info_frame, text=f"Perfil: {self.current_user['access_level']}", anchor="w",
                  style='Sidebar.TLabel').pack(fill="x")

        if config.USE_LOGIN:
            ttk.Button(user_info_frame, text="Trocar de Usuário", command=self._switch_user).pack(fill="x", pady=(5, 0))

        ttk.Separator(self.sidebar_frame, orient="horizontal").pack(fill='x', pady=5, padx=10)

        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self._load_and_create_panels()

        logout_btn = ttk.Button(self.sidebar_frame, text="🚪 Sair da Aplicação", command=self._confirm_exit,
                                style="Danger.TButton")
        logout_btn.pack(side="bottom", fill="x", pady=10, padx=10)

    def _load_and_create_panels(self):
        """Carrega painéis da lista ALL_PANELS verificando permissões."""
        user_access_level = self.current_user.get('access_level', 'Desenvolvedor')

        for PanelClass in ALL_PANELS:
            try:
                if not PanelClass.ALLOWED_ACCESS or user_access_level in PanelClass.ALLOWED_ACCESS:
                    name, icon = PanelClass.PANEL_NAME, PanelClass.PANEL_ICON
                    panel_instance = PanelClass(self.content_frame, self)
                    self.panels[name] = panel_instance

                    btn = ttk.Button(self.sidebar_frame, text=f" {icon} {name}", compound="left",
                                     command=lambda n=name: self.switch_panel_by_name(n),
                                     style="Sidebar.TButton")

                    btn.pack(fill="x", pady=2, padx=10)
                    self.sidebar_buttons[name] = btn
            except Exception as e:
                messagebox.showerror("Erro de Carregamento de Painel",
                                     f"Erro fatal ao carregar o painel '{PanelClass.__name__}':\n\n{e}", parent=self)
                logging.critical(f"Falha ao carregar painel {PanelClass.__name__}: {e}", exc_info=True)

    def switch_panel_by_name(self, panel_name: str):
        """Mostra o painel selecionado."""
        if panel_name not in self.panels:
            logging.warning(f"Tentativa de trocar para painel inexistente: {panel_name}")
            return

        if self.current_panel_name and self.current_panel_name in self.panels:
            self.panels[self.current_panel_name].pack_forget()

        self.current_panel_name = panel_name
        self.panels[panel_name].pack(fill="both", expand=True)
        logging.debug(f"Trocado para o painel: {panel_name}")

    def _create_menubar(self) -> tk.Menu:
        """Cria a barra de menus superior (sem a opção de personalizar tema)."""
        menubar = tk.Menu(self)

        paineis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Painéis", menu=paineis_menu)
        for name in self.sidebar_buttons.keys():
            paineis_menu.add_command(label=name, command=lambda n=name: self.switch_panel_by_name(n))

        cadastros_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Cadastros Auxiliares", menu=cadastros_menu)
        cadastros_menu.add_command(label="Tipos de Vegetais...", command=self._open_tipos_vegetais_modal)

        config_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Configurações", menu=config_menu)

        if not config_menu.index("end"):
            config_menu.add_command(label="(Nenhuma opção)", state="disabled")

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre", command=self._show_about_dialog)

        menubar.add_command(label="Sair", command=self._confirm_exit)
        return menubar

    def _switch_user(self):
        """Reinicia a aplicação para permitir a troca de usuário."""
        self.logger.info(f"Usuário '{self.current_user['username']}' iniciou a troca de sessão.")
        self.withdraw()

        new_user_info = self._run_login_process()
        if new_user_info and new_user_info not in ["max_attempts_failed", "connection_error"]:
            self.logger.info(f"Login bem-sucedido para '{new_user_info['username']}'. Reconstruindo UI.")
            self._initialize_session_for_user(new_user_info)
        else:
            self.logger.warning("Troca de usuário falhou ou foi cancelada. Fechando a aplicação.")
            self.destroy()

    def _open_tipos_vegetais_modal(self):
        """Abre o diálogo unificado para gerenciar tipos de vegetais."""
        if not config.DATABASE_ENABLED:
            messagebox.showwarning("Funcionalidade Indisponível",
                                 "O banco de dados está desabilitado.", parent=self)
            return
        try:
            callback = None
            current_panel = self.panels.get(self.current_panel_name)
            if current_panel and hasattr(current_panel, '_carregar_tipos_vegetais'):
                callback = getattr(current_panel, '_carregar_tipos_vegetais')

            dialog = TiposVegetaisManagerDialog(self, on_close_callback=callback)
            dialog.wait_window()
        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Não foi possível abrir a janela de gestão: {e}", parent=self)
            logging.critical(f"Falha ao abrir TiposVegetaisManagerDialog: {e}", exc_info=True)

    def _show_about_dialog(self):
        """Abre o diálogo 'Sobre'."""
        AboutDialog(self)

    def _confirm_exit(self):
        """Pede confirmação antes de fechar a aplicação."""
        if messagebox.askyesno("Confirmar Saída", "Deseja fechar a aplicação?", icon='warning', parent=self):
            self.logger.info("Aplicação encerrada pelo usuário.")
            self.destroy()

    def _set_initial_geometry(self) -> None:
        system_name = platform.system()

        if system_name == "Windows":
            try:
                self.state('zoomed')
            except tk.TclError:
                w, h = self.winfo_screenwidth(), self.winfo_screenheight()
                self.geometry(f"{int(w * 0.9)}x{int(h * 0.9)}")
        else:
            w, h = self.winfo_screenwidth(), self.winfo_screenheight()
            self.geometry(f"{int(w * 0.9)}x{int(h * 0.9)}")

        self.update_idletasks()
        win_w = self.winfo_width()
        win_h = self.winfo_height()
        x = (w // 2) - (win_w // 2)
        y = (h // 2) - (win_h // 2)
        self.geometry(f'+{x}+{y}')