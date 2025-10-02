# app.py
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict
import platform
import os

import config
from persistencia.base_panel import BasePanel
from panels import ALL_PANELS


class AplicacaoPrincipal(tk.Tk):
    def __init__(self, user_info: Dict) -> None:
        try:
            super().__init__()
            self.logger = logging.getLogger("main_app")
            self.current_user = user_info

            self.style = ttk.Style(self)
            self._setup_style()  # Configura o tema de forma inteligente

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
            else:
                self.logger.warning("Nenhum painel disponível para o usuário.")
                messagebox.showwarning("Acesso Restrito", "Nenhum painel está disponível para o seu perfil de acesso.")

        except Exception as e:
            logging.error(f"Erro na inicialização da aplicação principal: {e}", exc_info=True)
            raise

    # --- MÉTODO ADICIONADO PARA CORRIGIR O ERRO ---
    def get_current_user(self) -> dict:
        """Retorna o dicionário de informações do usuário logado."""
        return self.current_user

    def _setup_style(self):
        """Configura o estilo dos widgets ttk com base no SO e temas disponíveis."""
        system = platform.system()
        available_themes = self.style.theme_names()
        self.logger.info(f"SO detectado: {system}. Temas disponíveis: {available_themes}")

        theme_to_use = None
        if system == "Windows":
            if 'vista' in available_themes:
                theme_to_use = 'vista'
            elif 'xpnative' in available_themes:
                theme_to_use = 'xpnative'
        elif system == "Darwin":
            if 'aqua' in available_themes: theme_to_use = 'aqua'

        if not theme_to_use:
            for theme in ("clam", "alt", "default"):
                if theme in available_themes:
                    theme_to_use = theme
                    break
        try:
            if theme_to_use:
                self.style.theme_use(theme_to_use)
                self.logger.info(f"Tema ttk aplicado com sucesso: '{theme_to_use}'")
            else:
                self.logger.warning("Nenhum tema ttk preferencial foi encontrado.")
        except tk.TclError as e:
            self.logger.error(f"Erro ao aplicar o tema ttk: {e}")

    def _setup_ui(self) -> None:
        # Sidebar
        self.sidebar_frame = ttk.Frame(self, width=250, style='TFrame')
        self.sidebar_frame.pack(side="left", fill="y", padx=(5, 0), pady=5)
        self.sidebar_frame.pack_propagate(False)

        # Info usuário
        user_info_frame = ttk.Frame(self.sidebar_frame, style='TFrame')
        user_info_frame.pack(fill="x", pady=10, padx=10)

        ttk.Label(user_info_frame, text=f"Usuário: {self.current_user['name']}",
                  anchor="w").pack(fill="x")
        ttk.Label(user_info_frame, text=f"Perfil: {self.current_user['access_level']}",
                  anchor="w").pack(fill="x")

        ttk.Separator(self.sidebar_frame, orient="horizontal").pack(fill='x', pady=5, padx=10)

        # Área de conteúdo
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self._load_and_create_panels()

        # Botão sair
        logout_btn = ttk.Button(
            self.sidebar_frame, text="🚪 Sair",
            command=self.destroy
        )
        logout_btn.pack(side="bottom", fill="x", pady=10, padx=10)

    def _load_and_create_panels(self):
        user_access_level = self.current_user.get('access_level', 'Desenvolvedor')

        for PanelClass in ALL_PANELS:
            try:
                allowed = PanelClass.ALLOWED_ACCESS
                if not allowed or user_access_level in allowed:
                    name = PanelClass.PANEL_NAME
                    icon = PanelClass.PANEL_ICON

                    panel_instance = PanelClass(self.content_frame, self)
                    self.panels[name] = panel_instance

                    btn = ttk.Button(
                        self.sidebar_frame, text=f" {icon} {name}",
                        compound="left",
                        command=lambda n=name: self.switch_panel_by_name(n),
                        style='TButton'
                    )
                    btn.pack(fill="x", pady=2, padx=10)
                    self.sidebar_buttons[name] = btn

            except Exception as e:
                self.logger.error(f"Erro ao carregar painel {PanelClass.__name__}: {e}", exc_info=True)

    def switch_panel_by_name(self, panel_name: str):
        if self.current_panel_name:
            self.panels[self.current_panel_name].pack_forget()

        self.current_panel_name = panel_name
        panel = self.panels[panel_name]
        panel.pack(fill="both", expand=True)
        self.logger.info(f"Usuário trocou para o painel: '{panel_name}'")

    def _create_menubar(self) -> tk.Menu:
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)

        for name in self.sidebar_buttons.keys():
            file_menu.add_command(
                label=f"Abrir {name}",
                command=lambda n=name: self.switch_panel_by_name(n)
            )
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.destroy)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre", command=self._show_about_dialog)

        return menubar

    def _show_about_dialog(self):
        messagebox.showinfo(
            "Sobre o Sistema",
            "Painel de Controle Moderno v1.0\n\n"
            "Este sistema é uma aplicação de demonstração construída com Python e Tkinter (ttk).\n\n"
            "Seu propósito é exibir diferentes funcionalidades, desde a visualização de dados e dashboards "
            "até formulários de entrada, com um sistema de acesso por perfil de usuário."
        )

    def _set_initial_geometry(self) -> None:
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        width = int(w * config.MAIN_WINDOW_RATIO)
        height = int(h * config.MAIN_WINDOW_RATIO)
        self.geometry(f"{width}x{height}+{(w - width) // 2}+{(h - height) // 2}")
        self.minsize(int(width * config.MAIN_WINDOW_MIN_SIZE_RATIO),
                     int(height * config.MAIN_WINDOW_MIN_SIZE_RATIO))
