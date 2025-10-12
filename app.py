        
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, Any

import config
from panels.base_panel import BasePanel
from panels import ALL_PANELS
from settings_manager import SettingsManager
from dialogs.login_ui import LoginDialog
                                                      
from modals.tipos_vegetais_controller import TiposVegetaisController
from modals.about_dialog import AboutDialog


class AplicacaoPrincipal(tk.Tk):
    def __init__(self, project_root: str) -> None:
        super().__init__()
        self.settings_manager = SettingsManager(project_root=project_root)

        self.withdraw()

        self._configure_styles()
        current_settings = self.settings_manager.load_settings()
        self._apply_font_settings(current_settings)

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

    def _configure_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        self.style.configure('TButton', padding=6, relief="flat", background="#ccc")
        self.style.map('TButton', background=[('active', '#e0e0e0')])

        self.style.configure('Danger.TButton', foreground='white', background='#dc3545')
        self.style.map('Danger.TButton', background=[('active', '#c82333')])

        self.style.configure('Success.TButton', foreground='white', background='#28a745')
        self.style.map('Success.TButton', background=[('active', '#218838')])

        self.style.configure('Warning.TButton', foreground='black', background='#ffc107')
        self.style.map('Warning.TButton', background=[('active', '#e0a800')])

        self.style.configure('Info.TButton', foreground='white', background='#17a2b8')
        self.style.map('Info.TButton', background=[('active', '#138496')])

        self.style.configure('Secondary.TButton', foreground='white', background='#6c757d')
        self.style.map('Secondary.TButton', background=[('active', '#5a6268')])

        self.style.configure('Sidebar.TFrame', background='#f0f0f0')
        self.style.configure('Sidebar.TLabel', background='#f0f0f0')
        self.style.configure('Sidebar.TButton', background='#f0f0f0', borderwidth=0, anchor='w')
        self.style.map('Sidebar.TButton', background=[('active', '#dcdcdc')])

    def _apply_font_settings(self, settings: Dict[str, Any]):
        font_family = settings.get('font_family', 'Segoe UI')
        font_size = settings.get('font_size', 10)
        default_font = (font_family, font_size)
        self.style.configure('.', font=default_font)
        self.style.configure('Treeview', font=default_font)
        self.style.configure('Treeview.Heading', font=(font_family, font_size, 'bold'))

    def _initialize_session_for_user(self, user_info: Dict[str, Any]):
        for widget in self.winfo_children():
            widget.destroy()

        self.current_user = user_info
        self.title("Painel de Controle")
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
        self.sidebar_frame = ttk.Frame(self, width=250, style='Sidebar.TFrame')
        self.sidebar_frame.pack(side="left", fill="y", padx=(5, 0), pady=5)
        self.sidebar_frame.pack_propagate(False)

        user_info_frame = ttk.Frame(self.sidebar_frame, style='Sidebar.TFrame')
        user_info_frame.pack(fill="x", pady=10, padx=10)

        ttk.Label(user_info_frame, text=f"Utilizador: {self.current_user['name']}", anchor="w",
                  style='Sidebar.TLabel').pack(fill="x")
        ttk.Label(user_info_frame, text=f"Perfil: {self.current_user['access_level']}", anchor="w",
                  style='Sidebar.TLabel').pack(fill="x")

        ttk.Button(user_info_frame, text="Trocar de Usuário", command=self._switch_user).pack(fill="x", pady=(5, 0))

        ttk.Separator(self.sidebar_frame, orient="horizontal").pack(fill='x', pady=5, padx=10)

        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self._load_and_create_panels()

        logout_btn = ttk.Button(self.sidebar_frame, text="🚪 Sair da Aplicação", command=self._confirm_exit,
                                style="Danger.TButton")
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
                                     style="Sidebar.TButton")
                    btn.pack(fill="x", pady=2, padx=10)
                    self.sidebar_buttons[name] = btn
            except Exception as e:
                messagebox.showerror("Erro de Carregamento de Painel",
                                     f"Erro fatal ao carregar o painel '{PanelClass.__name__}':\n\n{e}")

    def switch_panel_by_name(self, panel_name: str):
        if panel_name not in self.panels: return
        if self.current_panel_name and self.current_panel_name in self.panels:
            self.panels[self.current_panel_name].pack_forget()
        self.current_panel_name = panel_name
        self.panels[panel_name].pack(fill="both", expand=True)

    def _create_menubar(self) -> tk.Menu:
        menubar = tk.Menu(self)

        cadastros_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Cadastros", menu=cadastros_menu)
        for name in self.sidebar_buttons.keys():
            if "gestão" in name.lower() or "catálogo" in name.lower():
                cadastros_menu.add_command(label=name, command=lambda n=name: self.switch_panel_by_name(n))
        cadastros_menu.add_separator()
                                                               
        cadastros_menu.add_command(label="Tipos de Vegetais...", command=self._open_tipos_vegetais_modal)

        config_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Configurações", menu=config_menu)

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

                                                                           
    def _open_tipos_vegetais_modal(self):
        try:
            callback = None
            current_panel = self.panels.get(self.current_panel_name)
                                                               
            if current_panel and hasattr(current_panel, '_carregar_tipos_vegetais'):
                callback = current_panel._carregar_tipos_vegetais

                                            
            controller = TiposVegetaisController(self, on_close_callback=callback)
            controller.show()
        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Não foi possível abrir a janela de gestão: {e}")

    def _show_about_dialog(self):
        AboutDialog(self)

    def _confirm_exit(self):
        if messagebox.askyesno("Confirmar Saída", "Tem certeza que deseja fechar a aplicação?", icon='warning',
                               parent=self):
            self.destroy()

    def _set_initial_geometry(self) -> None:
        try:
            self.attributes('-zoomed', True)
        except tk.TclError:
            w, h = self.winfo_screenwidth(), self.winfo_screenheight()
            self.geometry(f"{w}x{h}+0+0")

        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.minsize(int(w * 0.5), int(h * 0.5))