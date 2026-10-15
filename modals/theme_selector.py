import tkinter as tk
from tkinter import ttk, messagebox
import logging
from theme import COLORS as C, THEMES
from settings_manager import SettingsManager
from modals.dialog_utils import prepare_modal, wait_for_modal
from utils.ui_components import Tooltip

class ThemeSelectorDialog(tk.Toplevel):
    def __init__(self, parent, settings_manager: SettingsManager):
        super().__init__(parent)
        self.parent = parent
        self.settings_manager = settings_manager

        self.title("Seleção de Tema")
        self.configure(bg=C["bg_dark"])

        self.settings = self.settings_manager.load_settings()
        self.current_theme = self.settings.get("active_theme", "Gato a Noite")

        self._setup_ui()
        prepare_modal(self, parent=parent, width=400, height=300)
        wait_for_modal(self, self)

    def _setup_ui(self):
        main_frame = tk.Frame(self, bg=C["bg_dark"], padx=30, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        lbl_title = tk.Label(
            main_frame,
            text="🎨 Escolha o Visual do Sistema",
            font=("Arial", 14, "bold"),
            bg=C["bg_dark"],
            fg=C["accent_blue"]
        )
        lbl_title.pack(pady=(0, 5))

        lbl_desc = tk.Label(
            main_frame,
            text="Selecione um tema abaixo para personalizar as cores\nde todas as telas e painéis da aplicação.",
            font=("Arial", 10),
            bg=C["bg_dark"],
            fg=C["fg_secondary"],
            justify=tk.CENTER
        )
        lbl_desc.pack(pady=(0, 20))

        # Combobox
        cb_frame = tk.Frame(main_frame, bg=C["bg_dark"])
        cb_frame.pack(fill=tk.X, pady=10)

        lbl_tema = tk.Label(cb_frame, text="Tema Global:", font=("Arial", 11, "bold"), bg=C["bg_dark"], fg=C["fg_primary"])
        lbl_tema.pack(side=tk.LEFT, padx=(0, 10))

        self.var_theme = tk.StringVar(value=self.current_theme)
        theme_names = list(THEMES.keys())

        self.cb_theme = ttk.Combobox(
            cb_frame,
            textvariable=self.var_theme,
            values=theme_names,
            state="readonly",
            font=("Arial", 11),
            width=20
        )
        self.cb_theme.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Buttons
        btn_frame = tk.Frame(main_frame, bg=C["bg_dark"])
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        btn_frame.grid_columnconfigure(0, weight=1, uniform="theme_actions")
        btn_frame.grid_columnconfigure(1, weight=1, uniform="theme_actions")

        btn_save = tk.Button(
            btn_frame,
            text="💾 Salvar",
            font=("Arial", 11, "bold"),
            bg=C["accent_green"],
            fg="#ffffff",
            activebackground=C["accent_green_h"],
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._save_theme
        )
        btn_save.grid(row=0, column=0, sticky="ew", padx=(0, 5), ipady=5)

        btn_cancel = tk.Button(
            btn_frame,
            text="Cancelar",
            font=("Arial", 11),
            bg=C["bg_button"],
            fg=C["fg_primary"],
            activebackground=C["bg_button_hover"],
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.destroy
        )
        btn_cancel.grid(row=0, column=1, sticky="ew", padx=(5, 0), ipady=5)

    def _save_theme(self):
        new_theme = self.var_theme.get()
        if new_theme not in THEMES:
            messagebox.showerror("Erro", "Tema inválido selecionado.", parent=self)
            return

        if new_theme == self.current_theme:
            self.destroy()
            return

        # Save to settings.json
        self.settings["active_theme"] = new_theme
        self.settings_manager.save_settings(self.settings)
        logging.info(f"Theme changed to: {new_theme}")

        # Inform the user that the app will restart
        messagebox.showinfo(
            "Tema Alterado",
            f"O tema foi alterado para \"{new_theme}\".\n\n"
            f"A aplicação será reiniciada automaticamente\n"
            f"para aplicar o novo tema completamente.",
            parent=self
        )

        # Close the dialog first
        self.destroy()

        # Signal the app to restart
        root = self.parent
        if root:
            root._restart_requested = True
            root.after(100, root.destroy)
