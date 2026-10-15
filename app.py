import tkinter as tk
from tkinter import ttk, messagebox, font
import logging
import re
from typing import Dict, Any, Optional
import platform
import subprocess
import sys
from importlib import import_module
from functools import wraps
from persistencia.access_policy import can_access_page, PageAccessDenied
from panels.base_panel import BasePanel
from panels import ALL_PANELS
from settings_manager import SettingsManager
from utils.window_icon import apply_window_icon
from utils.installation_profile import (
    CAPABILITY_VISUAL_TESTS,
    load_installation_profile,
    panel_visible_for_profile,
    profile_info_has_capability,
)
from theme import COLORS as C, apply_dark_theme, get_contrasting_text, style_menu
from utils.ui_components import Tooltip, center_window
import os
import glob


GEOMETRY_PATTERN = re.compile(r"^(?P<width>\d+)x(?P<height>\d+)(?P<x>[+-]\d+)(?P<y>[+-]\d+)$")


def protected_page(page):
    """Protege callbacks, mesmo quando chamados sem passar pelo menu."""
    def decorate(method):
        @wraps(method)
        def guarded(self, *args, **kwargs):
            if self._guard_page(page):
                return method(self, *args, **kwargs)
        return guarded
    return decorate


class AplicacaoPrincipal(tk.Tk):
    def __init__(self, project_root: str) -> None:
        super().__init__()

        self.settings_manager = SettingsManager(project_root=project_root)
        self._last_normal_geometry = ""
        self._restore_geometry_job = None
        self._geometry_snapshot_job = None
        self._capturing_window_geometry = False

        self.withdraw()

        self._configure_styles()
        self.settings = self.settings_manager.load_settings()
        self._apply_font_settings(self.style, self.settings)

        self.logger = logging.getLogger("main_app")
        self.project_root = project_root
        self.installation_profile_info = load_installation_profile(project_root)
        self.active_installation_profile_id = self.installation_profile_info["id"]

        # Helper state for intelligent live-theming
        self._last_theme_colors = dict(C)

        from persistencia import auth
        import config
        self.current_user = None
        if config.USE_LOGIN:
            from dialogs.login_ui import LoginDialog
            dialog = LoginDialog(self)
            self.wait_window(dialog)
            user = dialog.user_info
            if not isinstance(user, dict):
                self.destroy()
                return
            if user.get('must_change_password'):
                from dialogs.password_dialog import PasswordDialog
                change = PasswordDialog(self, mode='change')
                self.wait_window(change)
                if not change.success:
                    auth.clear_session()
                    self.destroy()
                    return
                self._restart_requested = True
                self.destroy()
                return
            if user.get('must_setup_mfa'):
                from dialogs.mfa_dialog import MfaDialog
                enrollment = MfaDialog(self)
                self.wait_window(enrollment)
                auth.clear_session()
                self._restart_requested = enrollment.success
                self.destroy()
                return
            self.current_user = user
        else:
            config.validate()
            self.current_user = {'username': None, 'name': 'Desenvolvimento', 'access_level': auth.ADMIN}
        self._initialize_ui()
        if config.USE_LOGIN:
            self.bind_all('<KeyPress>', self._record_session_activity, add='+')
            self.bind_all('<ButtonPress>', self._record_session_activity, add='+')
            self.after(15000, self._check_session)


    def _configure_styles(self):
        """Configure ttk styles using the centralized dark theme."""
        self.style = ttk.Style(self)
        apply_dark_theme(self.style)

    def _apply_font_settings(self, style_obj: ttk.Style, settings: Dict[str, Any]):
        """
        Apply font settings from settings.json to the ttk style object.
        Color configuration is now handled by theme.py.
        """
        font_family = settings.get('font_family', 'Segoe UI')
        font_size = settings.get('font_size', 10)
        default_font_tuple = (font_family, font_size)

        try:
            font.Font(family=font_family, size=font_size)
            style_obj.configure('.', font=default_font_tuple)
            style_obj.configure('Treeview', font=default_font_tuple)
            style_obj.configure('Treeview.Heading', font=(font_family, font_size, 'bold'))
            logging.debug(f"Font applied: {font_family}, {font_size}pt")
        except tk.TclError:
            logging.warning(f"Font '{font_family}' not found. Using 'TkDefaultFont'.")
            default_font_tuple = ('TkDefaultFont', font_size)
            style_obj.configure('.', font=default_font_tuple)
            style_obj.configure('Treeview', font=default_font_tuple)
            style_obj.configure('Treeview.Heading', font=('TkDefaultFont', font_size, 'bold'))

    def _initialize_ui(self):
        """Build the main application UI."""
        self.title("NexlifyTTk — Painel de Controle")
        apply_window_icon(self, self.project_root, default=True, logger=self.logger)
        self.configure(bg=C["bg_dark"])
        self._set_initial_geometry()

        self.panels: Dict[str, Optional[BasePanel]] = {}
        self.panel_specs: Dict[str, Dict[str, Any]] = {}
        self.sidebar_buttons: Dict[str, ttk.Button] = {}
        self.topbar_buttons: Dict[str, tk.Menubutton] = {}
        self.topbar_menus: Dict[str, tk.Menu] = {}
        self.current_panel_name: str = ""

        self._setup_ui()

        if self.sidebar_buttons:
            first_button_name = next(iter(self.sidebar_buttons))
            self.switch_panel_by_name(first_button_name)
            self.update_idletasks()
            self._fit_window_to_content()

        self.protocol("WM_DELETE_WINDOW", self._confirm_exit)
        self.bind("<<AppThemeChanged>>", self._on_theme_changed)
        self.bind("<Configure>", self._queue_window_geometry_snapshot, add="+")
        self.deiconify()
        self.after_idle(self._restore_saved_window_geometry)

    def _on_theme_changed(self, event=None):
        """Handle <<AppThemeChanged>> by updating the root window and all children."""
        self.logger.info("Live theme update requested. Propagating colors...")
        self.configure(bg=C["bg_dark"])

        # Keep in-memory settings in sync so _save_window_position won't overwrite the new theme
        self.settings = self.settings_manager.load_settings(force_reload=True)

        # 1. Update ttk Styles
        self._configure_styles()

        # 2. Update standard tk widgets recursively
        self._apply_theme_to_widgets(self)

        # 3. Update specific components that might need manual intervention
        self._refresh_topbar_theme()

        # The sidebar
        self.sidebar_frame.configure(style='Sidebar.TFrame')
        for child in self.sidebar_frame.winfo_children():
            if isinstance(child, tk.Label):
                child.configure(bg=C["sidebar_bg"], fg=C["accent_blue"])

        # Ensure the currently active sidebar button stays highlighted correctly
        if self.current_panel_name in self.sidebar_buttons:
            self.sidebar_buttons[self.current_panel_name].configure(
                bg=C["sidebar_active"],
                fg=get_contrasting_text(C["sidebar_active"], dark=C["bg_darkest"]),
            )

        self.update_idletasks()

        # After propagation, remember the new colors for next time
        self._last_theme_colors = dict(C)

    def _update_menu_colors(self, menu_widget):
        """Recursively update tk.Menu widgets"""
        from theme import style_menu
        style_menu(menu_widget)
        for child in menu_widget.winfo_children():
            if isinstance(child, tk.Menu):
                self._update_menu_colors(child)

    def _apply_theme_to_widgets(self, root_widget):
        """Recursively updates the bg/fg of Tkinter widgets using a smart reverse-lookup."""
        # Build reverse lookup map from old hex value to theme key.
        # We sort keys to prioritize more semantic ones if there are duplicates.
        reverse_map = {}
        for k, v in self._last_theme_colors.items():
            # Lowercase for robust hex comparison
            if isinstance(v, str) and v.startswith("#"):
                reverse_map[v.lower()] = k

        for child in root_widget.winfo_children():
            wtype = child.winfo_class()

            try:
                # ── INTELLIGENT REVERSE LOOKUP MAPPING ──
                # If we know the widget's current bg/fg matches one of our old theme hexes,
                # we seamlessly graduate it to the new theme's corresponding hex.

                # Try handling Background
                if "background" in child.keys():
                    old_bg = child.cget("background")
                    if isinstance(old_bg, str) and old_bg.startswith("#"):
                        key = reverse_map.get(old_bg.lower())
                        if key and key in C:
                            child.configure(background=C[key])

                # Try handling Foreground
                if "foreground" in child.keys():
                    old_fg = child.cget("foreground")
                    if isinstance(old_fg, str) and old_fg.startswith("#"):
                        key = reverse_map.get(old_fg.lower())
                        if key and key in C:
                            child.configure(foreground=C[key])

                # Try handling ActiveBackground
                if "activebackground" in child.keys():
                    old_abg = child.cget("activebackground")
                    if isinstance(old_abg, str) and old_abg.startswith("#"):
                        key = reverse_map.get(old_abg.lower())
                        if key and key in C:
                            child.configure(activebackground=C[key])

                # Try handling ActiveForeground
                if "activeforeground" in child.keys():
                    old_afg = child.cget("activeforeground")
                    if isinstance(old_afg, str) and old_afg.startswith("#"):
                        key = reverse_map.get(old_afg.lower())
                        if key and key in C:
                            child.configure(activeforeground=C[key])

                # Try handling SelectBackground
                if "selectbackground" in child.keys():
                    old_sbg = child.cget("selectbackground")
                    if isinstance(old_sbg, str) and old_sbg.startswith("#"):
                        key = reverse_map.get(old_sbg.lower())
                        if key and key in C:
                            child.configure(selectbackground=C[key])

                # Try handling SelectForeground
                if "selectforeground" in child.keys():
                    old_sfg = child.cget("selectforeground")
                    if isinstance(old_sfg, str) and old_sfg.startswith("#"):
                        key = reverse_map.get(old_sfg.lower())
                        if key and key in C:
                            child.configure(selectforeground=C[key])

                # Try handling insertbackground (caret color)
                if "insertbackground" in child.keys():
                    old_ibg = child.cget("insertbackground")
                    if isinstance(old_ibg, str) and old_ibg.startswith("#"):
                        key = reverse_map.get(old_ibg.lower())
                        if key and key in C:
                            child.configure(insertbackground=C[key])

                if "highlightbackground" in child.keys():
                    old_hbg = child.cget("highlightbackground")
                    if isinstance(old_hbg, str) and old_hbg.startswith("#"):
                        key = reverse_map.get(old_hbg.lower())
                        if key and key in C:
                            child.configure(highlightbackground=C[key])

                if "highlightcolor" in child.keys():
                    old_hc = child.cget("highlightcolor")
                    if isinstance(old_hc, str) and old_hc.startswith("#"):
                        key = reverse_map.get(old_hc.lower())
                        if key and key in C:
                            child.configure(highlightcolor=C[key])

                if "disabledforeground" in child.keys():
                    old_dfg = child.cget("disabledforeground")
                    if isinstance(old_dfg, str) and old_dfg.startswith("#"):
                        key = reverse_map.get(old_dfg.lower())
                        if key and key in C:
                            child.configure(disabledforeground=C[key])

                if "selectcolor" in child.keys():
                    old_sc = child.cget("selectcolor")
                    if isinstance(old_sc, str) and old_sc.startswith("#"):
                        key = reverse_map.get(old_sc.lower())
                        if key and key in C:
                            child.configure(selectcolor=C[key])

                # Normalize entries that were created with named colors like "white".
                if wtype == "Entry":
                    bg = child.cget("background") if "background" in child.keys() else ""
                    fg = str(child.cget("foreground")).lower() if "foreground" in child.keys() else ""
                    if isinstance(bg, str) and bg.startswith("#") and fg in {"white", "#ffffff", "black", "#000000"}:
                        child.configure(foreground=C["fg_primary"])
                    if "insertbackground" in child.keys():
                        ibg = str(child.cget("insertbackground")).lower()
                        if ibg in {"white", "#ffffff", "black", "#000000"}:
                            child.configure(insertbackground=C["fg_primary"])

                # Keep button labels readable even when they were created with hardcoded white/black.
                if wtype == "Button":
                    bg = child.cget("background") if "background" in child.keys() else ""
                    fg = str(child.cget("foreground")).lower() if "foreground" in child.keys() else ""
                    if isinstance(bg, str) and bg.startswith("#") and fg in {"white", "#ffffff", "black", "#000000"}:
                        child.configure(
                            foreground=get_contrasting_text(bg, dark=C["bg_darkest"])
                        )
                    if "activebackground" in child.keys() and "activeforeground" in child.keys():
                        active_bg = child.cget("activebackground")
                        active_fg = str(child.cget("activeforeground")).lower()
                        if isinstance(active_bg, str) and active_bg.startswith("#") and active_fg in {"white", "#ffffff", "black", "#000000"}:
                            child.configure(
                                activeforeground=get_contrasting_text(active_bg, dark=C["bg_darkest"])
                            )

            except tk.TclError:
                pass # Widget might not support one of the properties

            # Recursive call
            self._apply_theme_to_widgets(child)

            # ── CUSTOM THEME HOOK (Post-order) ──
            # Let the widget's own _apply_theme method run custom logic (like updating images/canvases).
            if hasattr(child, "_apply_theme") and callable(getattr(child, "_apply_theme")):
                try:
                    child._apply_theme()
                except Exception as e:
                    self.logger.warning(f"Error calling _apply_theme on {wtype}: {e}")

    def _setup_ui(self) -> None:
        """Create the main UI structure (topbar, sidebar and content area)."""
        self.topbar_frame = tk.Frame(self, bg=C["bg_darker"])
        self.topbar_frame.pack(side="top", fill="x")

        self.topbar_inner = tk.Frame(self.topbar_frame, bg=C["bg_darker"])
        self.topbar_inner.pack(side="left", fill="y", padx=10)

        self.topbar_separator = tk.Frame(self, bg=C["bg_toolbar"], height=1)
        self.topbar_separator.pack(side="top", fill="x")

        self.body_frame = tk.Frame(self, bg=C["bg_dark"])
        self.body_frame.pack(side="top", fill="both", expand=True)

        self.sidebar_frame = ttk.Frame(
            self.body_frame,
            width=self._compute_sidebar_width(),
            style='Sidebar.TFrame',
        )
        self.sidebar_frame.pack(side="left", fill="y", padx=(0, 0), pady=0)
        self.sidebar_frame.pack_propagate(False)

        title_lbl = tk.Label(self.sidebar_frame,
                             text="  📐  NexlifyTTk",
                             font=("Arial", 12, "bold"),
                             bg=C["sidebar_bg"], fg=C["accent_blue"],
                             anchor="w", pady=12, padx=8)
        title_lbl.pack(fill="x")
        tk.Label(self.sidebar_frame, text=f"{self.current_user['name']}\n{self.current_user['access_level']}",
                 bg=C['sidebar_bg'], fg=C['fg_secondary'], anchor='w', justify='left',
                 wraplength=270, padx=16, pady=8).pack(fill='x')

        tk.Frame(self.sidebar_frame, bg=C["bg_toolbar"], height=1).pack(fill="x")

        self.content_frame = tk.Frame(self.body_frame, bg=C["bg_dark"])
        self.content_frame.pack(side="right", fill="both", expand=True, padx=0, pady=0)

        self._load_and_create_panels()
        self._build_topbar()

        logout_btn = tk.Button(self.sidebar_frame,
                               text="🚪  Sair da Aplicação",
                               font=("Arial", 10),
                               bg=C["accent_red"], fg=get_contrasting_text(C["accent_red"], dark=C["bg_darkest"]),
                               activebackground=C["accent_red_h"],
                               activeforeground=get_contrasting_text(C["accent_red_h"], dark=C["bg_darkest"]),
                               relief=tk.FLAT, cursor="hand2", pady=6)
        logout_btn.configure(command=self._confirm_exit)
        logout_btn.pack(side="bottom", fill="x", pady=10, padx=10)
        Tooltip(logout_btn, "Fechar o sistema")
        self._fit_sidebar_width_to_content()

    def _compute_sidebar_width(self) -> int:
        """Size the sidebar so panel names fit without clipping."""
        screen_w = self.winfo_screenwidth()

        title_font = font.Font(family="Arial", size=12, weight="bold")
        button_font = font.Font(family="Arial", size=10)

        labels = [
            "  📐  NexlifyTTk",
            "🚪  Sair da Aplicação",
        ]
        labels.extend(
            f"  {panel_spec['icon']}  {panel_spec['name']}"
            for panel_spec in self._allowed_panel_specs()
        )

        max_text_width = max(
            title_font.measure(labels[0]),
            *(button_font.measure(label) for label in labels[1:]),
        )

        horizontal_padding = 44
        desired_width = max_text_width + horizontal_padding
        min_width = 280
        max_width = max(300, int(screen_w * 0.32))
        return max(min_width, min(desired_width, max_width))

    def _fit_sidebar_width_to_content(self) -> None:
        """Expand the sidebar when labels require more horizontal space."""
        self.update_idletasks()

        required_width = 0
        for child in self.sidebar_frame.winfo_children():
            if not child.winfo_ismapped():
                continue

            child_required = child.winfo_reqwidth()
            if child.winfo_manager() == "pack":
                pack_info = child.pack_info()
                child_required += self._pack_padding_total(pack_info.get("padx", 0))

            required_width = max(required_width, child_required)

        required_width += 12
        screen_w = self.winfo_screenwidth()
        min_width = 300
        max_width = max(340, int(screen_w * 0.36))
        self.sidebar_frame.configure(width=max(min_width, min(required_width, max_width)))

    def _pack_padding_total(self, padding_value) -> int:
        """Convert Tk pack padding values into total horizontal pixels."""
        if padding_value in ("", None):
            return 0

        if isinstance(padding_value, (int, float)):
            parts = [int(float(padding_value))]
        elif isinstance(padding_value, (tuple, list)):
            try:
                parts = [int(float(value)) for value in padding_value]
            except (TypeError, ValueError):
                return 0
        else:
            try:
                parts = [int(float(value)) for value in self.tk.splitlist(padding_value)]
            except (tk.TclError, TypeError, ValueError):
                try:
                    parts = [int(float(padding_value))]
                except (TypeError, ValueError):
                    return 0

        if len(parts) == 1:
            return parts[0] * 2
        return sum(parts[:2])

    def _build_topbar(self):
        import config
        app_menu = self._create_topbar_menu('Aplicação')
        app_menu.add_command(label='Salvar posição da janela', command=self._save_window_position)
        if config.USE_LOGIN:
            app_menu.add_command(label='Trocar senha', command=self._change_password)
            if self.current_user.get('mfa_available', config.MFA_ENABLED):
                app_menu.add_command(label='Ativar MFA por e-mail', command=self._enable_mfa)
            app_menu.add_command(label='Trocar usuário', command=self._switch_user)
        app_menu.add_command(label='Sair', command=self._confirm_exit)
        panels = self._create_topbar_menu('Painéis')
        for name in self.sidebar_buttons:
            panels.add_command(label=name, command=lambda n=name: self.switch_panel_by_name(n))
        settings = self._create_topbar_menu('Configurações')
        if config.ENABLE_THEME_MENU:
            settings.add_command(label='Seleção de tema', command=self._open_theme_selector)
            settings.add_command(label='Fontes e preferências', command=self._open_font_settings)
        if self._can_access_page('settings.computer'):
            settings.add_command(label='Informações do computador', command=self._open_computer_info)
        if self._can_access_page('settings.diagnostics'):
            settings.add_command(label='Diagnóstico da instalação', command=self._open_diagnostics)
        if self._can_access_page('settings.smtp'):
            settings.add_command(label='Envio de e-mail / SMTP', command=self._open_email_settings)
        if self._can_access_page('settings.types'):
            settings.add_command(label='Tipos de vegetais', command=self._open_tipos_vegetais_modal)
        help_menu = self._create_topbar_menu('Ajuda')
        help_menu.add_command(label='Sobre', command=self._show_about_dialog)
        help_menu.add_command(label='Tipo de instalação ativo', command=self._open_installation_profile_info)
        if self._can_access_page('dev.tests'):
            dev = self._create_topbar_menu('Desenvolvimento')
            dev.add_command(label='Central de testes', command=self._open_visual_test)
            dev.add_command(label='Monitor de processos', command=self._open_process_monitor)
            dev.add_command(label='Ferramentas de configuração', command=self._open_devtools)
            dev.add_command(label='Restaurar preferências visuais', command=self._open_factory_reset)

    def _create_topbar_menu(self, label: str) -> tk.Menu:
        """Create a styled dropdown button and return its menu."""
        btn = tk.Menubutton(
            self.topbar_inner,
            text=label,
            font=("Arial", 10),
            bg=C["bg_darker"],
            fg=C["fg_primary"],
            activebackground=C["bg_button"],
            activeforeground=get_contrasting_text(C["bg_button"], dark=C["bg_darkest"]),
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            indicatoron=False,
            direction="below",
            padx=10,
            pady=8,
            cursor="hand2",
        )
        btn.pack(side="left", padx=(0, 2))

        menu = tk.Menu(btn, tearoff=0)
        style_menu(menu)
        btn.configure(menu=menu)

        self.topbar_buttons[label] = btn
        self.topbar_menus[label] = menu
        return menu

    def _refresh_topbar_theme(self) -> None:
        """Refresh the custom topbar colors after theme changes."""
        if hasattr(self, "topbar_frame"):
            self.topbar_frame.configure(bg=C["bg_darker"])
        if hasattr(self, "topbar_inner"):
            self.topbar_inner.configure(bg=C["bg_darker"])
        if hasattr(self, "topbar_separator"):
            self.topbar_separator.configure(bg=C["bg_toolbar"])

        for btn in self.topbar_buttons.values():
            btn.configure(
                bg=C["bg_darker"],
                fg=C["fg_primary"],
                activebackground=C["bg_button"],
                activeforeground=get_contrasting_text(C["bg_button"], dark=C["bg_darkest"]),
            )

        for menu in self.topbar_menus.values():
            self._update_menu_colors(menu)

    def _load_and_create_panels(self):
        """Register visible panels and create only their navigation buttons."""
        for panel_spec in self._allowed_panel_specs():
            name = panel_spec["name"]
            icon = panel_spec["icon"]
            self.panel_specs[name] = panel_spec
            self.panels[name] = None

            btn = tk.Button(
                self.sidebar_frame,
                text=f"  {icon}  {name}",
                font=("Arial", 10),
                bg=C["sidebar_bg"], fg=C["fg_primary"],
                activebackground=C["sidebar_active"],
                activeforeground=get_contrasting_text(C["sidebar_active"], dark=C["bg_darkest"]),
                relief=tk.FLAT, anchor="w",
                padx=12, pady=8, cursor="hand2",
                command=lambda n=name: self.switch_panel_by_name(n),
            )
            btn.pack(fill="x", pady=1, padx=5)
            self.sidebar_buttons[name] = btn
            Tooltip(btn, f"Abrir painel de {name}")

    def _allowed_panel_specs(self):
        return [spec for spec in ALL_PANELS
                if panel_visible_for_profile(spec, self.active_installation_profile_id)
                and self._can_access_page(spec['name'])]

    def _can_access_page(self, page):
        """Só para exibição; a abertura sempre consulta a sessão validada."""
        import config
        return can_access_page(self.current_user.get('access_level'), page,
                               profile_id=self.active_installation_profile_id,
                               environment=config.ENVIRONMENT, api_mode=config.API_MODE)

    def _guard_page(self, page):
        from persistencia.auth import authorize_page
        try:
            session = authorize_page(page, project_root=self.project_root)
            if any(session[key] != self.current_user.get(key) for key in ('username', 'access_level')):
                raise PermissionError('Sessão alterada.')
        except PageAccessDenied:
            self.logger.warning('Acesso a página negado: %s', page)
            messagebox.showwarning('Acesso negado', 'Seu perfil não permite acessar esta página.', parent=self)
            return False
        except Exception:
            self.logger.info('Não foi possível validar a sessão ao abrir uma página.')
            self._switch_user()
            return False
        return True

    def _profile_has_capability(self, capability: str) -> bool:
        """Return whether the active installation profile exposes a capability."""
        return profile_info_has_capability(self.installation_profile_info, capability)

    def _instantiate_panel(self, panel_name: str) -> Optional[BasePanel]:
        """Import and create a panel only when it is first opened."""
        if not self._guard_page(panel_name):
            return None
        panel_spec = self.panel_specs.get(panel_name)
        if not panel_spec:
            return None

        try:
            module = import_module(panel_spec["module"])
            PanelClass = getattr(module, panel_spec["class_name"])
            panel_instance = PanelClass(self.content_frame, self)
            self.panels[panel_name] = panel_instance
            return panel_instance
        except (PermissionError, ConnectionError):
            # A sessão pode ser revogada entre a navegação e a construção.
            self._switch_user()
            return None
        except Exception as e:
            self.panels[panel_name] = None
            messagebox.showerror(
                "Erro ao Carregar Painel",
                f"Falha crítica ao carregar o painel '{panel_name}':\n\n{e}",
                parent=self,
            )
            self.logger.critical("Failed to load panel %s: %s", panel_name, e, exc_info=True)
            return None

    def switch_panel_by_name(self, panel_name: str):
        """Show the selected panel and highlight the sidebar button."""
        if not self._guard_page(panel_name):
            return
        if panel_name not in self.panel_specs:
            logging.warning(f"Attempted to switch to non-existent panel: {panel_name}")
            return

        if self.current_panel_name and self.current_panel_name in self.panels:
            current_panel = self.panels.get(self.current_panel_name)
            if current_panel is not None:
                current_panel.pack_forget()

        panel = self.panels.get(panel_name)
        if panel is None:
            panel = self._instantiate_panel(panel_name)
            if panel is None:
                return

        for name, btn in self.sidebar_buttons.items():
            if name == panel_name:
                btn.configure(
                    bg=C["sidebar_active"],
                    fg=get_contrasting_text(C["sidebar_active"], dark=C["bg_darkest"]),
                )
            else:
                btn.configure(bg=C["sidebar_bg"], fg=C["fg_primary"])

        self.current_panel_name = panel_name
        panel.pack(fill="both", expand=True)
        self.update_idletasks()
        self._fit_window_to_content()
        logging.debug(f"Switched to panel: {panel_name}")

    @protected_page('settings.theme')
    def _open_theme_selector(self):
        """Abre o diálogo de seleção de tema global."""
        from modals.theme_selector import ThemeSelectorDialog
        try:
            ThemeSelectorDialog(self, self.settings_manager)
        except Exception as e:
            self.logger.error(f"Erro ao abrir o seletor de tema: {e}", exc_info=True)
            messagebox.showerror("Erro", f"Não foi possível abrir o seletor de tema:\n{e}", parent=self)


    @protected_page('settings.computer')
    def _open_computer_info(self):
        """Abre o diálogo com relatório do computador."""
        try:
            from modals.computer_info_dialog import ComputerInfoDialog
            ComputerInfoDialog(self)
        except Exception as e:
            self.logger.error(f"Erro ao abrir as informações do computador: {e}", exc_info=True)
            messagebox.showerror(
                "Erro",
                f"Não foi possível abrir as informações do computador:\n{e}",
                parent=self,
            )

    @protected_page('dev.reset_preferences')
    def _open_factory_reset(self):
        if not messagebox.askyesno('Restaurar preferências', 'Restaurar tema, fontes e posição da janela?', parent=self):
            return
        settings = self.settings_manager.load_settings(force_reload=True)
        for key in ('active_theme', 'font_family', 'font_size', 'window_geometry', 'custom_colors'):
            settings.pop(key, None)
        self.settings_manager.save_settings(settings)
        self._restart_requested = True
        self.destroy()

    @protected_page('dev.tests')
    def _open_visual_test(self):
        if not self._profile_has_capability(CAPABILITY_VISUAL_TESTS):
            return
        from instalacao.diagnostics_gui import DiagnosticsDialog
        DiagnosticsDialog(self, run_tests=True)

    @protected_page('help.installation')
    def _open_installation_profile_info(self):
        from modals.installation_profile_dialog import InstallationProfileDialog
        InstallationProfileDialog(self, self.project_root)

    @protected_page('help.about')
    def _show_about_dialog(self):
        """Open the 'About' dialog."""
        from modals.about_dialog import AboutDialog
        AboutDialog(self)

    def _confirm_exit(self):
        """Ask for confirmation before closing the application."""
        dialog = tk.Toplevel(self)
        dialog.title("Confirmar Saída")
        dialog.configure(bg=C["bg_dark"])
        dialog.transient(self)
        dialog.resizable(False, False)

        dw, dh = 360, 150
        center_window(dialog, dw, dh, parent=self)

        tk.Label(dialog, text="⚠️", font=("Arial", 28),
                 bg=C["bg_dark"], fg=C["accent_orange"]).pack(pady=(15, 5))
        tk.Label(dialog, text="Deseja fechar a aplicação?",
                 font=("Arial", 11), bg=C["bg_dark"], fg=C["fg_primary"]).pack()

        btn_frame = tk.Frame(dialog, bg=C["bg_dark"])
        btn_frame.pack(pady=15)

        def do_exit():
            dialog.destroy()
            self.logger.info("Aplicação encerrada pelo usuário.")
            self._save_window_position(notify=False)
            self.destroy()

        btn_sim = tk.Button(btn_frame, text="  Sim  ", font=("Arial", 10),
                  bg=C["accent_red"], fg=get_contrasting_text(C["accent_red"], dark=C["bg_darkest"]),
                  activebackground=C["accent_red_h"],
                  activeforeground=get_contrasting_text(C["accent_red_h"], dark=C["bg_darkest"]),
                  relief=tk.FLAT, cursor="hand2",
                  command=do_exit)
        btn_sim.pack(side=tk.LEFT, padx=8)
        Tooltip(btn_sim, "Salvar configurações e fechar")

        btn_nao = tk.Button(btn_frame, text="  Não  ", font=("Arial", 10),
                  bg=C["bg_button"], fg=C["fg_primary"],
                  activebackground=C["bg_button_hover"],
                  activeforeground=get_contrasting_text(C["bg_button_hover"], dark=C["bg_darkest"]),
                  relief=tk.FLAT, cursor="hand2",
                  command=dialog.destroy)
        btn_nao.pack(side=tk.LEFT, padx=8)
        Tooltip(btn_nao, "Cancelar e voltar para a aplicação")

        dialog.bind("<Escape>", lambda _event: dialog.destroy())
        dialog.bind("<Return>", lambda _event: do_exit())

        dialog.update_idletasks()
        fitted_w = max(dw, dialog.winfo_reqwidth() + 12)
        fitted_h = max(dh, dialog.winfo_reqheight() + 12)
        center_window(dialog, fitted_w, fitted_h, parent=self)

        def _finalize_dialog():
            try:
                dialog.grab_set()
            except tk.TclError:
                pass

            try:
                btn_nao.focus_set()
            except tk.TclError:
                pass

        dialog.after_idle(_finalize_dialog)
        return dialog

    def _save_window_position(self, notify=True):
        """Salva a geometria atual da janela no arquivo de configurações."""
        # Não permite salvar se estiver em tela cheia (zoomed) ou minimizado (iconic)
        if self.state() != 'zoomed' and self.state() != 'iconic':
            # Reload latest settings from disk to avoid overwriting theme changes
            self.settings = self.settings_manager.load_settings(force_reload=True)
            self._remember_current_window_geometry()
            self.settings['window_geometry'] = self._last_normal_geometry or self._capture_current_window_geometry(flush_events=True)
            self.settings_manager.save_settings(self.settings)
            self.logger.info(f"Geometria da janela salva: {self.settings['window_geometry']}")
            if notify:
                messagebox.showinfo("Posição Salva", "A tela atual (incluindo em qual monitor e qual tamanho) abrirá neste mesmo local da próxima vez!", parent=self)
        else:
            if notify:
                messagebox.showwarning("Atenção", "Saia do modo Tela Cheia (Maximizado) ou Minimizado para salvar uma posição customizada.", parent=self)

    def _fit_window_to_content(self, padding: int = 24) -> None:
        """Ensure the root window is not smaller than the currently visible UI."""
        if self.state() == 'zoomed':
            return

        self.update_idletasks()
        req_w = self.winfo_reqwidth() + padding
        req_h = self.winfo_reqheight() + padding
        cur_w = max(self.winfo_width(), 1)
        cur_h = max(self.winfo_height(), 1)
        target_w = min(self.winfo_screenwidth(), max(cur_w, req_w))
        target_h = min(self.winfo_screenheight(), max(cur_h, req_h))

        if target_w == cur_w and target_h == cur_h:
            return

        x, y = self._get_window_position()
        self.geometry(f"{target_w}x{target_h}{x:+d}{y:+d}")

    def _get_window_position(self) -> tuple[int, int]:
        """Return the current top-left window position from the active geometry."""
        geometry = self.geometry()
        match = GEOMETRY_PATTERN.match(geometry)
        if match:
            return int(match.group("x")), int(match.group("y"))

        return max(self.winfo_x(), 0), max(self.winfo_y(), 0)

    def _capture_current_window_geometry(self, flush_events: bool = False) -> str:
        """Capture the effective window size plus the current geometry origin."""
        if flush_events and not self._capturing_window_geometry:
            self._capturing_window_geometry = True
            try:
                self.update_idletasks()
                self.update()
            except tk.TclError:
                pass
            finally:
                self._capturing_window_geometry = False
        else:
            try:
                self.update_idletasks()
            except tk.TclError:
                pass

        geometry = self.geometry()
        match = GEOMETRY_PATTERN.match(geometry)
        width = max(self.winfo_width(), 1)
        height = max(self.winfo_height(), 1)

        if match:
            x = int(match.group("x"))
            y = int(match.group("y"))
        else:
            x = self.winfo_x()
            y = self.winfo_y()

        return f"{width}x{height}{x:+d}{y:+d}"

    def _queue_window_geometry_snapshot(self, event=None):
        """Debounce configure events so the latest normal geometry is cached."""
        if not self.winfo_exists():
            return
        if self.state() in {"zoomed", "iconic"}:
            return

        if self._geometry_snapshot_job is not None:
            try:
                self.after_cancel(self._geometry_snapshot_job)
            except tk.TclError:
                pass

        self._geometry_snapshot_job = self.after_idle(self._remember_current_window_geometry)

    def _remember_current_window_geometry(self):
        """Store the most recent usable geometry for future restores."""
        self._geometry_snapshot_job = None
        if not self.winfo_exists():
            return
        if self.state() in {"zoomed", "iconic"}:
            return
        self._last_normal_geometry = self._capture_current_window_geometry(flush_events=True)

    def _restore_saved_window_geometry(self):
        """Re-apply the saved geometry after the window is mapped on screen."""
        self._restore_geometry_job = None
        saved_geometry = self.settings.get("window_geometry", "")
        if not saved_geometry or self.state() in {"zoomed", "iconic"}:
            return
        self.geometry(saved_geometry)
        self._remember_current_window_geometry()

    def _set_initial_geometry(self) -> None:
        import platform # Certifique-se de importar platform
        system_name = platform.system()
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        # Se houver uma geometria salva em múltiplos monitores, usa ela em vez de se auto-centralizar.
        saved_geometry = self.settings.get('window_geometry', "")

        if saved_geometry:
            self.geometry(saved_geometry)
            self._last_normal_geometry = saved_geometry
            self.logger.info(f"Geometria restaurada: {saved_geometry}")
        else:
            # Lógica padrão (abrir maximizado no Windows ou centralizado no Linux/Mac)
            if system_name == "Windows":
                try:
                    self.state('zoomed')
                except tk.TclError:
                    self.geometry(f"{int(w * 0.9)}x{int(h * 0.9)}")
            else:
                self.geometry(f"{int(w * 0.9)}x{int(h * 0.9)}")

            self.update_idletasks()
            win_w = self.winfo_width()
            win_h = self.winfo_height()
            x = (w // 2) - (win_w // 2)
            y = (h // 2) - (win_h // 2)
            self.geometry(f"{win_w}x{win_h}{x:+d}{y:+d}")
            self._last_normal_geometry = self._capture_current_window_geometry()

    def get_current_user(self):
        return dict(self.current_user)

    def _check_session(self):
        from persistencia.auth import current_session
        try:
            session = current_session()
            if session['access_level'] != self.current_user['access_level']:
                raise PermissionError('Perfil alterado.')
        except Exception:
            # Close protected windows immediately; a blocking message box would
            # leave their contents visible until someone acknowledged it.
            self.logger.info('Sessão encerrada por expiração, revogação ou falha de validação.')
            self._switch_user()
            return
        self.after(15000, self._check_session)

    def _record_session_activity(self, event=None):
        from persistencia.auth import touch_session_activity
        try:
            touch_session_activity()
        except (PermissionError, ConnectionError, ValueError):
            self._switch_user()

    def _switch_user(self):
        from persistencia.auth import clear_session
        self._restart_requested = True
        self.destroy()
        clear_session()

    @protected_page('settings.smtp')
    def _open_email_settings(self):
        from dialogs.email_settings_dialog import EmailSettingsDialog
        dialog = EmailSettingsDialog(self)
        self.wait_window(dialog)

    def _enable_mfa(self):
        from dialogs.mfa_dialog import MfaDialog
        dialog = MfaDialog(self)
        self.wait_window(dialog)
        if dialog.success:
            self._restart_requested = True
            self.destroy()

    def _change_password(self):
        from dialogs.password_dialog import PasswordDialog
        dialog = PasswordDialog(self, mode='change')
        self.wait_window(dialog)
        if dialog.success:
            self._switch_user()

    @protected_page('settings.types')
    def _open_tipos_vegetais_modal(self):
        from modals.tipos_vegetais_controller import TiposVegetaisController
        TiposVegetaisController(self).show()

    @protected_page('settings.theme')
    def _open_font_settings(self):
        from dialogs.advanced_theme_dialog import AdvancedThemeDialog
        AdvancedThemeDialog(self, self.settings_manager)

    def _apply_theme_settings(self, style, settings):
        self._apply_font_settings(style, settings)
        for color_key, style_name in [('danger', 'Danger'), ('success', 'Success'), ('info', 'Info'),
                                       ('warning', 'Warning'), ('secondary', 'Secondary')]:
            color = settings.get('custom_colors', {}).get(color_key)
            if color:
                style.configure(f'{style_name}.TButton', background=color, foreground=get_contrasting_text(color))

    @protected_page('settings.diagnostics')
    def _open_diagnostics(self):
        from instalacao.diagnostics_gui import DiagnosticsDialog
        DiagnosticsDialog(self)

    @protected_page('dev.processes')
    def _open_process_monitor(self):
        from instalacao.monitor_processo import ProcessMonitor
        ProcessMonitor(self)

    @protected_page('dev.tools')
    def _open_devtools(self):
        subprocess.Popen([sys.executable, os.path.join(self.project_root, 'instalacao', 'launch_devtools.py')], cwd=self.project_root)

    def show_placeholder_alert(self):
        messagebox.showinfo('Template', 'Implemente aqui a regra de negócio da sua aplicação.', parent=self)
