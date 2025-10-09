# dialogs/advanced_theme_dialog.py
import tkinter as tk
from tkinter import ttk, colorchooser, font, messagebox
import ttkbootstrap as bstrap
from ttkbootstrap.scrolled import ScrolledFrame
import os


class AdvancedThemeDialog(bstrap.Toplevel):
    """
    Uma janela de diálogo avançada para personalização completa do tema,
    com pré-visualização em tempo real e ajustes finos.
    """

    def __init__(self, parent, settings_manager):
        super().__init__(parent)
        self.title("Painel de Personalização Avançada")
        self.transient(parent)
        self.geometry("850x700")

        self.app = parent
        self.settings_manager = settings_manager
        self.preview_style = bstrap.Style()
        self.current_settings = self.settings_manager.load_settings()

        #  Variáveis de Controlo da UI 
        self.theme_var = tk.StringVar(value=self.current_settings['theme'])
        self.font_family_var = tk.StringVar(value=self.current_settings.get('font_family', 'Segoe UI'))
        self.font_size_var = tk.IntVar(value=self.current_settings.get('font_size', 10))
        self.border_width_var = tk.IntVar(value=self.current_settings.get('border_width', 1))
        self.border_radius_var = tk.IntVar(value=self.current_settings.get('border_radius', 8))
        self.focus_ring_var = tk.BooleanVar(value=self.current_settings.get('focus_ring', True))
        self.preview_scale_var = tk.DoubleVar(value=75)
        self.preview_check_var = tk.BooleanVar(value=False)
        self.color_vars = {}
        for name, color in self.current_settings['custom_colors'].items():
            self.color_vars[name] = tk.StringVar(value=color if color else "")

        self._create_widgets()
        self.position_center()
        self.grab_set()

        #Garante que o cancelamento restaure o tema salvo 
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill='x', pady=(0, 10))
        ttk.Button(action_frame, text="Restaurar Padrões", command=self._restore_defaults,
                   style="warning.TButton").pack(side='left')
        #Botão Cancelar agora chama _on_cancel 
        ttk.Button(action_frame, text="Cancelar", command=self._on_cancel, style="secondary.TButton").pack(side='right')
        ttk.Button(action_frame, text="Salvar e Fechar", command=self._save_and_close, style="success.TButton").pack(
            side='right', padx=5)
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True)
        settings_container = ttk.Frame(paned, padding=5)
        paned.add(settings_container, weight=1)
        notebook = ttk.Notebook(settings_container, bootstyle="primary")
        notebook.pack(fill="both", expand=True)
        self._create_general_tab(notebook)
        self._create_colors_tab(notebook)
        self._create_typography_tab(notebook)
        self._create_fine_tuning_tab(notebook)
        preview_container = ttk.LabelFrame(paned, text=" Pré-visualização em Tempo Real ", padding=15)
        paned.add(preview_container, weight=2)
        self._create_preview_widgets(preview_container)

    def _create_preview_widgets(self, parent):
        f_buttons = ttk.Frame(parent);
        f_buttons.pack(fill='x', pady=5)
        self.preview_primary_btn = ttk.Button(f_buttons, text="Primary", style="primary.TButton")
        self.preview_primary_btn.pack(side='left', fill='x', expand=True, padx=2)
        ttk.Button(f_buttons, text="Success", style="success.TButton").pack(side='left', fill='x', expand=True, padx=2)
        ttk.Button(f_buttons, text="Danger (Outline)", style="danger.Outline.TButton").pack(side='left', fill='x',
                                                                                            expand=True, padx=2)
        ttk.Label(parent, text="Campo de Entrada (Info):").pack(anchor='w', pady=(10, 5))
        ttk.Entry(parent, style="info.TEntry").pack(fill='x', expand=True)
        ttk.Label(parent, text="Controlo Deslizante (Warning):").pack(anchor='w', pady=(10, 5))
        ttk.Scale(parent, from_=0, to=100, style="warning.Horizontal.TScale", variable=self.preview_scale_var).pack(
            fill='x', expand=True)
        check = ttk.Checkbutton(parent, text="Desativar botão 'Primary'", style="secondary.TCheckbutton",
                                variable=self.preview_check_var, command=self._toggle_preview_button_state)
        check.pack(pady=10)
        self.preview_label = ttk.Label(parent, text="Este texto reflete a fonte e o tamanho escolhidos.",
                                       wraplength=400, justify='center')
        self.preview_label.pack(pady=20, fill='x', expand=True)
        self.after(50, self._update_preview)

    def _toggle_preview_button_state(self):
        self.preview_primary_btn.config(state="disabled" if self.preview_check_var.get() else "normal")

    def _create_general_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=10);
        notebook.add(tab, text="Geral")
        ttk.Label(tab, text="Tema Base:").pack(anchor='w')
        theme_combo = ttk.Combobox(tab, textvariable=self.theme_var, values=sorted(self.preview_style.theme_names()),
                                   state='readonly')
        theme_combo.pack(fill='x', pady=(5, 0))
        theme_combo.bind('<<ComboboxSelected>>', self._update_preview)

    def _create_colors_tab(self, notebook):
        tab_container = ttk.Frame(notebook, padding=0);
        notebook.add(tab_container, text="Cores")
        scrolled_content = ScrolledFrame(tab_container, padding=10, autohide=True);
        scrolled_content.pack(fill="both", expand=True)
        for color_name in self.color_vars:
            f = ttk.Frame(scrolled_content);
            f.pack(fill='x', pady=4)
            ttk.Label(f, text=f"{color_name.capitalize()}:", width=12).pack(side='left')
            color_btn = ttk.Button(f, text="Escolher...", command=lambda cn=color_name: self._choose_color(cn));
            color_btn.pack(side='left', padx=5)
            color_preview = tk.Frame(f, width=100, height=20, relief='sunken', borderwidth=1);
            color_preview.pack(side='left', fill='x', expand=True)
            self.color_vars[color_name].trace_add('write', lambda *args, frame=color_preview, var=self.color_vars[
                color_name]: self._update_color_previews(frame, var.get()))
            self._update_color_previews(color_preview, self.color_vars[color_name].get())

    def _create_typography_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=10);
        notebook.add(tab, text="Tipografia")
        ttk.Label(tab, text="Família da Fonte:").pack(anchor='w')
        available_fonts = sorted([f for f in font.families() if not f.startswith('@')])
        font_combo = ttk.Combobox(tab, textvariable=self.font_family_var, values=available_fonts);
        font_combo.pack(fill='x', pady=5)
        font_combo.bind('<<ComboboxSelected>>', self._update_preview)
        ttk.Label(tab, text="Tamanho da Fonte Base:").pack(anchor='w', pady=(10, 0))
        font_size_spin = ttk.Spinbox(tab, from_=8, to=16, textvariable=self.font_size_var,
                                     command=self._update_preview);
        font_size_spin.pack(fill='x', pady=5)

    def _create_fine_tuning_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=10);
        notebook.add(tab, text="Ajustes")
        ttk.Label(tab, text=f"Arredondamento dos Cantos (Radius):").pack(anchor='w')
        ttk.Scale(tab, from_=0, to=20, variable=self.border_radius_var, command=self._update_preview).pack(fill='x',
                                                                                                           pady=5)
        ttk.Label(tab, text=f"Espessura da Borda:").pack(anchor='w', pady=(10, 0))
        ttk.Scale(tab, from_=0, to=5, variable=self.border_width_var, command=self._update_preview).pack(fill='x',
                                                                                                         pady=5)
        ttk.Checkbutton(tab, text="Ativar anel de foco visual", variable=self.focus_ring_var,
                        command=self._update_preview, style='primary.TCheckbutton').pack(pady=15)

    def _update_color_previews(self, frame, color):
        try:
            frame.config(bg=color if color else "white")
        except tk.TclError:
            frame.config(bg="white")

    def _choose_color(self, color_name):
        initial_color = self.preview_style.colors.get(color_name)
        color_code = colorchooser.askcolor(title=f"Escolha a cor para '{color_name}'", initialcolor=initial_color,
                                           parent=self)
        if color_code and color_code[1]: self.color_vars[color_name].set(color_code[1]); self._update_preview()

    def _update_preview(self, event=None):
        style = self.preview_style
        style.theme_use(self.theme_var.get())
        for name, var in self.color_vars.items():
            if var.get(): style.colors.set(name, var.get())
        try:
            font_config = (self.font_family_var.get(), self.font_size_var.get());
            style.configure('.', font=font_config);
            self.preview_label.config(font=font_config)
        except tk.TclError:
            font_config = ('TkDefaultFont', self.font_size_var.get());
            style.configure('.', font=font_config);
            self.preview_label.config(font=font_config)
        # Aplica espessura da borda na pré-visualização de forma segura
        style.configure('TButton', borderwidth=self.border_width_var.get());
        style.configure('Outline.TButton', borderwidth=self.border_width_var.get());
        style.configure('TEntry', borderwidth=self.border_width_var.get())

    def _save_and_close(self):
        new_settings = {
            "theme": self.theme_var.get(), "font_family": self.font_family_var.get(),
            "font_size": self.font_size_var.get(),
            "custom_colors": {name: var.get() if var.get() else None for name, var in self.color_vars.items()},
            "border_width": self.border_width_var.get(), "border_radius": self.border_radius_var.get(),
            "focus_ring": self.focus_ring_var.get()
        }
        self.settings_manager.save_settings(new_settings)
        #  Usa a função centralizada para aplicar o tema
        self.app._apply_theme_settings(self.app.style, new_settings)
        messagebox.showinfo("Configurações Salvas", "O novo tema e as personalizações foram aplicados.", parent=self)
        self.destroy()

    def _on_cancel(self):
        """Restaura o tema salvo e fecha a janela."""
        last_saved_settings = self.settings_manager.load_settings()
        self.app._apply_theme_settings(self.app.style, last_saved_settings)
        self.destroy()

    def _restore_defaults(self):
        if messagebox.askyesno("Confirmar", "Tem a certeza de que deseja restaurar as configurações padrão?",
                               parent=self):
            try:
                os.remove(self.settings_manager.filepath)
            except FileNotFoundError:
                pass
            # Carrega e aplica os padrões imediatamente
            default_settings = self.settings_manager.load_settings()
            self.app._apply_theme_settings(self.app.style, default_settings)
            messagebox.showinfo("Sucesso", "As configurações padrão foram restauradas.", parent=self)
            self.destroy()