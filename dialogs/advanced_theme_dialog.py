import tkinter as tk
from tkinter import ttk, colorchooser, font, messagebox
import os


class ScrolledFrame(ttk.Frame):
    """Um frame com uma barra de rolagem vertical que funciona com a roda do mouse."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.canvas = tk.Canvas(self, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(self, event):
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")


class AdvancedThemeDialog(tk.Toplevel):
    """
    Uma janela de diálogo avançada para personalização do tema,
    usando apenas componentes padrão do Tkinter.
    """

    def __init__(self, parent, settings_manager):
        super().__init__(parent)
        self.title("Painel de Personalização Avançada")
        self.transient(parent)

        # --- INÍCIO DA CORREÇÃO ---
        # Adiciona a mesma lógica de centralização do about_dialog.py

        # 1. Força a atualização para obter a geometria correta do 'parent'
        self.update_idletasks()

        # 2. Define o tamanho desejado para este diálogo
        self_width = 850
        self_height = 700

        # 3. Obtém a geometria da janela principal (que está maximizada)
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        # 4. Calcula a posição central
        pos_x = parent_x + (parent_width // 2) - (self_width // 2)
        pos_y = parent_y + (parent_height // 2) - (self_height // 2)

        # 5. Define a geometria (tamanho + posição) e impede redimensionamento
        self.geometry(f"{self_width}x{self_height}+{pos_x}+{pos_y}")
        self.resizable(False, False)
        # --- FIM DA CORREÇÃO ---

        # A linha original self.geometry("850x700") foi substituída pela lógica acima.

        self.app = parent
        self.settings_manager = settings_manager
        self.current_settings = self.settings_manager.load_settings()

        self.font_family_var = tk.StringVar(value=self.current_settings.get('font_family', 'Segoe UI'))
        self.font_size_var = tk.IntVar(value=self.current_settings.get('font_size', 10))
        self.border_width_var = tk.IntVar(value=self.current_settings.get('border_width', 1))
        self.border_radius_var = tk.IntVar(value=self.current_settings.get('border_radius', 0))

        self.preview_scale_var = tk.DoubleVar(value=75)
        self.preview_check_var = tk.BooleanVar(value=False)
        self.color_vars = {}

        default_colors = {
            'primary': '#007bff', 'secondary': '#6c757d', 'success': '#28a745',
            'info': '#17a2b8', 'warning': '#ffc107', 'danger': '#dc3545'
        }

        saved_colors = self.current_settings.get('custom_colors', {})
        for name, color in default_colors.items():
            self.color_vars[name] = tk.StringVar(value=saved_colors.get(name) or color)

        self._create_widgets()
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self._update_preview()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)

        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill='x', pady=(0, 10))
        ttk.Button(action_frame, text="Restaurar Padrões", command=self._restore_defaults,
                   style="Warning.TButton").pack(side='left')
        ttk.Button(action_frame, text="Cancelar", command=self._on_cancel, style="Secondary.TButton").pack(side='right')
        ttk.Button(action_frame, text="Salvar e Fechar", command=self._save_and_close, style="Success.TButton").pack(
            side='right', padx=5)

        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True)

        settings_container = ttk.Frame(paned, padding=5)
        paned.add(settings_container, weight=1)

        notebook = ttk.Notebook(settings_container)
        notebook.pack(fill="both", expand=True)

        self._create_colors_tab(notebook)
        self._create_typography_tab(notebook)
        self._create_fine_tuning_tab(notebook)

        preview_container = ttk.LabelFrame(paned, text=" Pré-visualização em Tempo Real ", padding=15)
        paned.add(preview_container, weight=2)
        self._create_preview_widgets(preview_container)

    def _create_preview_widgets(self, parent):
        f_buttons = ttk.Frame(parent)
        f_buttons.pack(fill='x', pady=5)

        self.preview_success_btn = ttk.Button(f_buttons, text="Success", style="Success.TButton")
        self.preview_success_btn.pack(side='left', fill='x', expand=True, padx=2)

        self.preview_danger_btn = ttk.Button(f_buttons, text="Danger", style="Danger.TButton")
        self.preview_danger_btn.pack(side='left', fill='x', expand=True, padx=2)

        self.preview_info_btn = ttk.Button(f_buttons, text="Info", style="Info.TButton")
        self.preview_info_btn.pack(side='left', fill='x', expand=True, padx=2)

        ttk.Label(parent, text="Campo de Entrada:").pack(anchor='w', pady=(10, 5))
        self.preview_entry = ttk.Entry(parent)
        self.preview_entry.pack(fill='x', expand=True)

        ttk.Label(parent, text="Controle Deslizante (Scale):").pack(anchor='w', pady=(10, 5))
        ttk.Scale(parent, from_=0, to=100, variable=self.preview_scale_var).pack(fill='x', expand=True)

        check = ttk.Checkbutton(parent, text="Desativar botão 'Success'",
                                variable=self.preview_check_var, command=self._toggle_preview_button_state)
        check.pack(pady=10)

        self.preview_label = ttk.Label(parent, text="Este texto reflete a fonte e o tamanho escolhidos.",
                                       wraplength=400, justify='center')
        self.preview_label.pack(pady=20, fill='x', expand=True)

    def _toggle_preview_button_state(self):
        self.preview_success_btn.config(state="disabled" if self.preview_check_var.get() else "normal")

    def _create_colors_tab(self, notebook):
        tab_container = ttk.Frame(notebook)
        notebook.add(tab_container, text="Cores")

        scrolled_content = ScrolledFrame(tab_container)
        scrolled_content.pack(fill="both", expand=True)
        tab = scrolled_content.scrollable_frame

        for color_name in self.color_vars:
            f = ttk.Frame(tab)
            f.pack(fill='x', pady=4, padx=5)
            ttk.Label(f, text=f"{color_name.replace('_', ' ').title()}:", width=12).pack(side='left')

            color_btn = ttk.Button(f, text="Escolher...", command=lambda cn=color_name: self._choose_color(cn))
            color_btn.pack(side='left', padx=5)

            color_preview = tk.Frame(f, width=100, height=20, relief='sunken', borderwidth=1)
            color_preview.pack(side='left', fill='x', expand=True)

            self.color_vars[color_name].trace_add('write',
                                                  lambda name, index, mode, var=self.color_vars[color_name],
                                                         frame=color_preview:
                                                  self._update_color_previews(frame, var.get()))
            self._update_color_previews(color_preview, self.color_vars[color_name].get())

    def _create_typography_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=10)
        notebook.add(tab, text="Tipografia")

        ttk.Label(tab, text="Família da Fonte:").pack(anchor='w')
        available_fonts = sorted([f for f in font.families() if not f.startswith('@')])
        font_combo = ttk.Combobox(tab, textvariable=self.font_family_var, values=available_fonts, state='readonly')
        font_combo.pack(fill='x', pady=5)
        font_combo.bind('<<ComboboxSelected>>', self._update_preview)

        ttk.Label(tab, text="Tamanho da Fonte Base:").pack(anchor='w', pady=(10, 0))
        font_size_spin = ttk.Spinbox(tab, from_=8, to=16, textvariable=self.font_size_var, command=self._update_preview)
        font_size_spin.pack(fill='x', pady=5)

    def _create_fine_tuning_tab(self, notebook):
        """Cria a aba de ajustes finos para bordas."""
        tab = ttk.Frame(notebook, padding=10)
        notebook.add(tab, text="Ajustes")

        ttk.Label(tab, text=f"Espessura da Borda: {self.border_width_var.get()}px").pack(anchor='w')
        ttk.Scale(tab, from_=0, to=5, variable=self.border_width_var, command=self._update_preview).pack(
            fill='x', pady=5)

        ttk.Label(tab, text=f"Arredondamento dos Cantos (Radius): {self.border_radius_var.get()}px").pack(anchor='w',
                                                                                                          pady=(10, 0))
        ttk.Scale(tab, from_=0, to=20, variable=self.border_radius_var, command=self._update_preview).pack(
            fill='x', pady=5)

    def _update_color_previews(self, frame, color):
        try:
            frame.config(bg=color if color else "white")
        except tk.TclError:
            frame.config(bg="white")

    def _choose_color(self, color_name):
        initial_color = self.color_vars[color_name].get()
        color_code = colorchooser.askcolor(title=f"Escolha a cor para '{color_name}'", initialcolor=initial_color,
                                           parent=self)
        if color_code and color_code[1]:
            self.color_vars[color_name].set(color_code[1])
            self._update_preview()

    def _update_preview(self, *args):
        preview_settings = {
            "font_family": self.font_family_var.get(),
            "font_size": self.font_size_var.get(),
            "custom_colors": {name: var.get() for name, var in self.color_vars.items()}
        }
        self.app._apply_theme_settings(self.app.style, preview_settings)

        try:
            for child in self.winfo_children():
                if isinstance(child, ttk.PanedWindow):
                    pass
        except Exception:
            pass

        self.app.style.configure('TButton', borderwidth=self.border_width_var.get())
        self.app.style.configure('TEntry', borderwidth=self.border_width_var.get())

        try:
            font_config = (self.font_family_var.get(), self.font_size_var.get())
            self.preview_label.config(font=font_config)
        except tk.TclError:
            font_config = ('TkDefaultFont', self.font_size_var.get())
            self.preview_label.config(font=font_config)

    def _save_and_close(self):
        new_settings = {
            "font_family": self.font_family_var.get(),
            "font_size": self.font_size_var.get(),
            "custom_colors": {name: (var.get() or None) for name, var in self.color_vars.items()},
            "border_width": self.border_width_var.get(),
            "border_radius": self.border_radius_var.get(),
        }
        self.settings_manager.save_settings(new_settings)
        self.app._apply_theme_settings(self.app.style, new_settings)
        messagebox.showinfo("Configurações Salvas", "O novo tema e as personalizações foram aplicados.", parent=self)
        self.destroy()

    def _on_cancel(self):
        """Restaura o tema salvo e fecha a janela."""
        last_saved_settings = self.settings_manager.load_settings()
        self.app._apply_theme_settings(self.app.style, last_saved_settings)
        self.destroy()

    def _restore_defaults(self):
        if messagebox.askyesno("Confirmar", "Tem certeza de que deseja restaurar as configurações padrão?",
                               parent=self):
            try:
                if os.path.exists(self.settings_manager.filepath):
                    os.remove(self.settings_manager.filepath)
            except OSError as e:
                messagebox.showerror("Erro", f"Não foi possível remover o arquivo de configurações:\n{e}", parent=self)
                return

            default_settings = self.settings_manager.load_settings()
            self.app._apply_theme_settings(self.app.style, default_settings)
            messagebox.showinfo("Sucesso",
                                "As configurações padrão foram restauradas. Pode ser necessário reiniciar a aplicação para que todas as alterações tenham efeito.",
                                parent=self)
            self.destroy()