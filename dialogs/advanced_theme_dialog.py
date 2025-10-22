import tkinter as tk
from tkinter import ttk, colorchooser, font, messagebox
import os
from typing import Dict, Any, MutableMapping

# --- 1. Dicionário Completo de Temas ---
# Todos os temas do seu editor web, mapeados para a
# estrutura do settings.json (custom_colors, font_family, etc.)
PRESET_THEMES = {
    "☀️ Temas Claros": {
        "Padrão Streamlit": {
            "font_family": "Segoe UI", "font_size": 10, "border_width": 1, "border_radius": 4,
            "custom_colors": {
                "primary": "#FF4B4B", "secondary": "#F0F2F6", "success": "#28a745",
                "info": "#17a2b8", "warning": "#ffc107", "danger": "#FF4B4B"
            }
        },
        "Menta Suave": {
            "font_family": "Segoe UI", "font_size": 10, "border_width": 1, "border_radius": 6,
            "custom_colors": {
                "primary": "#1FAB89", "secondary": "#9DF3C4", "success": "#1FAB89",
                "info": "#3C8DAD", "warning": "#F39C12", "danger": "#E74C3C"
            }
        },
        "Algodão Doce": {
            "font_family": "Segoe UI", "font_size": 10, "border_width": 1, "border_radius": 8,
            "custom_colors": {
                "primary": "#F76B8A", "secondary": "#FAD2E1", "success": "#5CDB95",
                "info": "#5B86E5", "warning": "#FCA311", "danger": "#F76B8A"
            }
        },
        "Areia e Céu": {
            "font_family": "Segoe UI", "font_size": 10, "border_width": 1, "border_radius": 4,
            "custom_colors": {
                "primary": "#3C8DAD", "secondary": "#D4C7B0", "success": "#28a745",
                "info": "#3C8DAD", "warning": "#E6AF2E", "danger": "#C0392B"
            }
        },
        "Lavanda": {
            "font_family": "Georgia", "font_size": 10, "border_width": 1, "border_radius": 8,
            "custom_colors": {
                "primary": "#7F5A83", "secondary": "#DCD6F7", "success": "#5CDB95",
                "info": "#A0C4FF", "warning": "#FCA311", "danger": "#E63946"
            }
        },
        "Limão Siciliano": {
            "font_family": "Segoe UI", "font_size": 10, "border_width": 1, "border_radius": 4,
            "custom_colors": {
                "primary": "#D4E157", "secondary": "#FFFACD", "success": "#4CAF50",
                "info": "#00BFFF", "warning": "#D4E157", "danger": "#F44336"
            }
        },
        "Pêssego": {
            "font_family": "Georgia", "font_size": 10, "border_width": 1, "border_radius": 6,
            "custom_colors": {
                "primary": "#FF8A65", "secondary": "#FFE0B2", "success": "#8BC34A",
                "info": "#4FC3F7", "warning": "#FF8A65", "danger": "#E57373"
            }
        },
        "Céu de Inverno": {
            "font_family": "Segoe UI", "font_size": 10, "border_width": 1, "border_radius": 4,
            "custom_colors": {
                "primary": "#4FC3F7", "secondary": "#B3E5FC", "success": "#81C784",
                "info": "#4FC3F7", "warning": "#FFEE58", "danger": "#EF5350"
            }
        },
    },
    "🌙 Temas Escuros": {
        "Drácula": {
            "font_family": "Consolas", "font_size": 10, "border_width": 1, "border_radius": 2,
            "custom_colors": {
                "primary": "#bd93f9", "secondary": "#6272a4", "success": "#50fa7b",
                "info": "#8be9fd", "warning": "#f1fa8c", "danger": "#ff5555"
            }
        },
        "Monokai Pro": {
            "font_family": "Consolas", "font_size": 10, "border_width": 1, "border_radius": 2,
            "custom_colors": {
                "primary": "#ff6188", "secondary": "#78dce8", "success": "#a9dc76",
                "info": "#78dce8", "warning": "#ffd866", "danger": "#ff6188"
            }
        },
        "Nord": {
            "font_family": "Segoe UI", "font_size": 10, "border_width": 1, "border_radius": 4,
            "custom_colors": {
                "primary": "#88C0D0", "secondary": "#5E81AC", "success": "#A3BE8C",
                "info": "#8FBCBB", "warning": "#EBCB8B", "danger": "#BF616A"
            }
        },
        "Synthwave '84": {
            "font_family": "Consolas", "font_size": 11, "border_width": 1, "border_radius": 0,
            "custom_colors": {
                "primary": "#f92aad", "secondary": "#72f1b8", "success": "#39FF14",
                "info": "#00F2FF", "warning": "#F9E000", "danger": "#f92aad"
            }
        },
        "One Dark Pro": {
            "font_family": "Consolas", "font_size": 10, "border_width": 1, "border_radius": 2,
            "custom_colors": {
                "primary": "#61AFEF", "secondary": "#56B6C2", "success": "#98C379",
                "info": "#61AFEF", "warning": "#E5C07B", "danger": "#E06C75"
            }
        },
        "Meia-noite na Floresta": {
            "font_family": "Segoe UI", "font_size": 10, "border_width": 1, "border_radius": 4,
            "custom_colors": {
                "primary": "#4DB6AC", "secondary": "#2C3E50", "success": "#4DB6AC",
                "info": "#5DADE2", "warning": "#F39C12", "danger": "#E74C3C"
            }
        },
        "Café Expresso": {
            "font_family": "Georgia", "font_size": 10, "border_width": 1, "border_radius": 2,
            "custom_colors": {
                "primary": "#A1887F", "secondary": "#3E2723", "success": "#8BC34A",
                "info": "#6D4C41", "warning": "#FFB74D", "danger": "#D9534F"
            }
        },
        "Retrô Sombrio (Gruvbox)": {
            "font_family": "Consolas", "font_size": 10, "border_width": 1, "border_radius": 2,
            "custom_colors": {
                "primary": "#FABD2F", "secondary": "#b8bb26", "success": "#b8bb26",
                "info": "#83a598", "warning": "#FABD2F", "danger": "#fb4934"
            }
        },
    },
    "🌈 Temas Vibrantes": {
        "Pôr do Sol Tropical": {
            "font_family": "Segoe UI", "font_size": 10, "border_width": 1, "border_radius": 8,
            "custom_colors": {
                "primary": "#FF6B6B", "secondary": "#FFE69A", "success": "#06D6A0",
                "info": "#118AB2", "warning": "#FFD166", "danger": "#FF6B6B"
            }
        },
        "Cyberpunk Neon": {
            "font_family": "Consolas", "font_size": 10, "border_width": 2, "border_radius": 0,
            "custom_colors": {
                "primary": "#00F2FF", "secondary": "#7B00E0", "success": "#39FF14",
                "info": "#00F2FF", "warning": "#F9E000", "danger": "#FF0054"
            }
        },
        "Vaporwave": {
            "font_family": "Consolas", "font_size": 11, "border_width": 1, "border_radius": 0,
            "custom_colors": {
                "primary": "#F92AAD", "secondary": "#34294F", "success": "#72F1B8",
                "info": "#00F2FF", "warning": "#F9E000", "danger": "#F92AAD"
            }
        },
        "Arco-íris Pastel": {
            "font_family": "Georgia", "font_size": 10, "border_width": 1, "border_radius": 10,
            "custom_colors": {
                "primary": "#ff8b94", "secondary": "#f8e0e2", "success": "#c1fba4",
                "info": "#b2e0ff", "warning": "#fff5b2", "danger": "#ff8b94"
            }
        },
        "Magma": {
            "font_family": "Consolas", "font_size": 10, "border_width": 1, "border_radius": 2,
            "custom_colors": {
                "primary": "#FF3D00", "secondary": "#F57C00", "success": "#4CAF50",
                "info": "#FF6E40", "warning": "#FFC107", "danger": "#FF3D00"
            }
        },
        "Oceano Elétrico": {
            "font_family": "Segoe UI", "font_size": 10, "border_width": 1, "border_radius": 0,
            "custom_colors": {
                "primary": "#00E5FF", "secondary": "#02162B", "success": "#76FF03",
                "info": "#00E5FF", "warning": "#FFEA00", "danger": "#FF3D00"
            }
        },
        "Verde Limão Neon": {
            "font_family": "Segoe UI", "font_size": 10, "border_width": 1, "border_radius": 0,
            "custom_colors": {
                "primary": "#76FF03", "secondary": "#2C2C2C", "success": "#76FF03",
                "info": "#00E5FF", "warning": "#FFEA00", "danger": "#FF1744"
            }
        },
    },
    "💼 Temas Corporativos": {
        "Azul Executivo": {
            "font_family": "Segoe UI", "font_size": 10, "border_width": 1, "border_radius": 4,
            "custom_colors": {
                "primary": "#005A9E", "secondary": "#E1EBF5", "success": "#28a745",
                "info": "#005A9E", "warning": "#ffc107", "danger": "#dc3545"
            }
        },
        "Grafite Sóbrio": {
            "font_family": "Segoe UI", "font_size": 10, "border_width": 1, "border_radius": 4,
            "custom_colors": {
                "primary": "#4A4A4A", "secondary": "#EAEAEA", "success": "#28a745",
                "info": "#17a2b8", "warning": "#ffc107", "danger": "#dc3545"
            }
        },
        "Verde Confiança": {
            "font_family": "Segoe UI", "font_size": 10, "border_width": 1, "border_radius": 4,
            "custom_colors": {
                "primary": "#007A5E", "secondary": "#E6F2F0", "success": "#007A5E",
                "info": "#00A0B0", "warning": "#F39C12", "danger": "#C0392B"
            }
        },
        "Bordô Elegante": {
            "font_family": "Georgia", "font_size": 10, "border_width": 1, "border_radius": 6,
            "custom_colors": {
                "primary": "#800020", "secondary": "#FBEAEF", "success": "#4F7942",
                "info": "#5B86E5", "warning": "#F39C12", "danger": "#800020"
            }
        },
        "Cinza Tecnológico": {
            "font_family": "Segoe UI", "font_size": 10, "border_width": 1, "border_radius": 4,
            "custom_colors": {
                "primary": "#0078D4", "secondary": "#E1E1E1", "success": "#28a745",
                "info": "#0078D4", "warning": "#ffc107", "danger": "#dc3545"
            }
        },
        "Ouro e Petróleo (Finanças)": {
            "font_family": "Georgia", "font_size": 10, "border_width": 1, "border_radius": 2,
            "custom_colors": {
                "primary": "#B8860B", "secondary": "#282828", "success": "#9ACD32",
                "info": "#4682B4", "warning": "#B8860B", "danger": "#D2691E"
            }
        },
        "Azul Saúde": {
            "font_family": "Segoe UI", "font_size": 10, "border_width": 1, "border_radius": 6,
            "custom_colors": {
                "primary": "#00A0B0", "secondary": "#EDF8F9", "success": "#4CAF50",
                "info": "#00A0B0", "warning": "#FF9800", "danger": "#F44336"
            }
        },
    }
}


# --- 2. Funções Auxiliares ---

def deep_merge(source, destination):
    """Faz um merge recursivo de dicionários."""
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            deep_merge(value, node)
        else:
            destination[key] = value
    return destination


class ScrolledFrame(ttk.Frame):
    """Um frame com uma barra de rolagem vertical que funciona com a roda do mouse."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_windows)  # Windows
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)  # Linux (scroll up)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)  # Linux (scroll down)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _on_mousewheel_windows(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")


class AdvancedThemeDialog(tk.Toplevel):
    """
    Uma janela de diálogo avançada para personalização do tema,
    usando apenas componentes padrão do Tkinter.
    """

    def __init__(self, parent, settings_manager):
        super().__init__(parent)
        self.title("Painel de Personalização Avançada")
        self.transient(parent)

        self.update_idletasks()

        self_width = 850
        self_height = 700

        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        pos_x = parent_x + (parent_width // 2) - (self_width // 2)
        pos_y = parent_y + (parent_height // 2) - (self_height // 2)

        self.geometry(f"{self_width}x{self_height}+{pos_x}+{pos_y}")
        self.resizable(False, False)

        self.app = parent
        self.settings_manager = settings_manager
        self.current_settings = self.settings_manager.load_settings()

        # --- Variáveis de Estado (Originais) ---
        self.font_family_var = tk.StringVar()
        self.font_size_var = tk.IntVar()
        self.border_width_var = tk.IntVar()
        self.border_radius_var = tk.IntVar()
        self.preview_scale_var = tk.DoubleVar(value=75)
        self.preview_check_var = tk.BooleanVar(value=False)
        self.color_vars = {}

        # --- Variáveis de Estado (Novas para a Galeria) ---
        self.theme_category_var = tk.StringVar()
        self.theme_name_var = tk.StringVar()

        try:
            self.available_fonts = sorted([f for f in font.families() if not f.startswith('@')])
        except Exception:
            self.available_fonts = ['Segoe UI', 'Arial', 'Times New Roman', 'Courier New', 'Georgia', 'Verdana',
                                    'Consolas']

        default_colors = {
            'primary': '#007bff', 'secondary': '#6c757d', 'success': '#28a745',
            'info': '#17a2b8', 'warning': '#ffc107', 'danger': '#dc3545'
        }
        for name in default_colors.keys():
            self.color_vars[name] = tk.StringVar()

        # Carrega os valores iniciais do settings.json para as vars
        self._populate_vars_from_settings()

        self._create_widgets()
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self._update_preview()

        # Seleciona a primeira categoria por padrão
        first_category = list(PRESET_THEMES.keys())[0]
        self.theme_category_var.set(first_category)
        self._on_category_select()

    def _populate_vars_from_settings(self):
        """Atualiza as variáveis do Tkinter com base no dicionário current_settings."""
        settings = self.current_settings
        self.font_family_var.set(settings.get('font_family', 'Segoe UI'))
        self.font_size_var.set(settings.get('font_size', 10))
        self.border_width_var.set(settings.get('border_width', 1))
        self.border_radius_var.set(settings.get('border_radius', 0))

        saved_colors = settings.get('custom_colors', {})
        defaults = self.settings_manager.default_settings['custom_colors']
        for name, var in self.color_vars.items():
            var.set(saved_colors.get(name) or defaults.get(name))

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

        # --- INJEÇÃO DA GALERIA DE TEMAS ---
        gallery_frame = ttk.LabelFrame(settings_container, text="🎨 Galeria de Temas Predefinidos", padding=15)
        gallery_frame.pack(fill="x", pady=(0, 10))
        gallery_frame.columnconfigure(1, weight=1)

        ttk.Label(gallery_frame, text="Categoria:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.category_combo = ttk.Combobox(
            gallery_frame, textvariable=self.theme_category_var,
            values=list(PRESET_THEMES.keys()), state="readonly"
        )
        self.category_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.category_combo.bind("<<ComboboxSelected>>", self._on_category_select)

        ttk.Label(gallery_frame, text="Tema:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.theme_combo = ttk.Combobox(
            gallery_frame, textvariable=self.theme_name_var, state="disabled"
        )
        self.theme_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Button(
            gallery_frame, text="Aplicar Tema da Galeria",
            command=self._apply_gallery_theme, style="Success.TButton"
        ).grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=(5, 0))

        ttk.Separator(settings_container, orient="horizontal").pack(fill='x', pady=10)
        # --- FIM DA INJEÇÃO ---

        notebook = ttk.Notebook(settings_container)
        notebook.pack(fill="both", expand=True)

        self._create_colors_tab(notebook)
        self._create_typography_tab(notebook)
        self._create_fine_tuning_tab(notebook)

        preview_container = ttk.LabelFrame(paned, text=" Pré-visualização em Tempo Real ", padding=15)
        paned.add(preview_container, weight=2)
        self._create_preview_widgets(preview_container)

    # --- Funções da Galeria (Novas) ---

    def _on_category_select(self, event=None):
        """Atualiza o combobox de temas quando uma categoria é selecionada."""
        category = self.theme_category_var.get()
        if category in PRESET_THEMES:
            theme_names = list(PRESET_THEMES[category].keys())
            self.theme_combo.config(values=theme_names, state="readonly")
            self.theme_name_var.set(theme_names[0])
        else:
            self.theme_combo.config(values=[], state="disabled")
            self.theme_name_var.set("")

    def _apply_gallery_theme(self):
        """Aplica um tema da galeria."""
        category = self.theme_category_var.get()
        theme_name = self.theme_name_var.get()
        if not category or not theme_name:
            messagebox.showwarning("Seleção Vazia", "Por favor, selecione uma categoria e um tema.", parent=self)
            return

        theme_settings = PRESET_THEMES[category][theme_name]

        # Faz um merge para não perder chaves desconhecidas (ex: "theme", "focus_ring")
        new_settings = self.settings_manager.load_settings()
        new_settings = deep_merge(theme_settings, new_settings)

        self.current_settings = new_settings
        self._populate_vars_from_settings()  # Atualiza todas as TK Vars
        self._update_preview()  # Atualiza a UI
        messagebox.showinfo("Tema Aplicado", f"O tema '{theme_name}' foi carregado no editor.", parent=self)

    # --- Funções Originais (Sem modificação de propósito) ---

    def _create_preview_widgets(self, parent):
        f_buttons = ttk.Frame(parent)
        f_buttons.pack(fill='x', pady=5)

        self.preview_success_btn = ttk.Button(f_buttons, text="Success", style="Success.TButton")
        self.preview_success_btn.pack(side='left', fill='x', expand=True, padx=2)

        self.preview_danger_btn = ttk.Button(f_buttons, text="Danger", style="Danger.TButton")
        self.preview_danger_btn.pack(side='left', fill='x', expand=True, padx=2)

        self.preview_info_btn = ttk.Button(f_buttons, text="Info", style="Info.TButton")
        self.preview_info_btn.pack(side='left', fill='x', expand=True, padx=2)

        self.preview_warning_btn = ttk.Button(f_buttons, text="Warning", style="Warning.TButton")
        self.preview_warning_btn.pack(side='left', fill='x', expand=True, padx=2)

        self.preview_secondary_btn = ttk.Button(f_buttons, text="Secondary", style="Secondary.TButton")
        self.preview_secondary_btn.pack(side='left', fill='x', expand=True, padx=2)

        ttk.Label(parent, text="Campo de Entrada:").pack(anchor='w', pady=(10, 5))
        self.preview_entry = ttk.Entry(parent)
        self.preview_entry.pack(fill='x', expand=True)

        ttk.Label(parent, text="Controle Deslizante (Scale):").pack(anchor='w', pady=(10, 5))
        ttk.Scale(parent, from_=0, to=100, variable=self.preview_scale_var, orient='horizontal').pack(fill='x',
                                                                                                      expand=True)

        check = ttk.Checkbutton(parent, text="Desativar botão 'Success'",
                                variable=self.preview_check_var, command=self._toggle_preview_button_state)
        check.pack(pady=10)

        self.preview_label = ttk.Label(parent, text="Este texto reflete a fonte e o tamanho escolhidos.",
                                       wraplength=400, justify='center', anchor='center')
        self.preview_label.pack(pady=20, fill='both', expand=True)

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
            f.columnconfigure(2, weight=1)

            ttk.Label(f, text=f"{color_name.replace('_', ' ').title()}:", width=12).pack(side='left')

            color_btn = ttk.Button(f, text="Escolher...", width=10,
                                   command=lambda cn=color_name: self._choose_color(cn))
            color_btn.pack(side='left', padx=5)

            color_preview = tk.Frame(f, width=100, height=24, relief='sunken', borderwidth=1)
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
        font_combo = ttk.Combobox(tab, textvariable=self.font_family_var, values=self.available_fonts, state='readonly')
        font_combo.pack(fill='x', pady=5)
        font_combo.bind('<<ComboboxSelected>>', self._update_preview)

        ttk.Label(tab, text="Tamanho da Fonte Base:").pack(anchor='w', pady=(10, 0))
        font_size_spin = ttk.Spinbox(tab, from_=8, to=16, textvariable=self.font_size_var, command=self._update_preview)
        font_size_spin.pack(fill='x', pady=5)
        self.font_size_var.trace_add('write', self._update_preview)  # Para digitação

    def _create_fine_tuning_tab(self, notebook):
        """Cria a aba de ajustes finos para bordas."""
        tab = ttk.Frame(notebook, padding=10)
        notebook.add(tab, text="Ajustes")

        ttk.Label(tab, text=f"Espessura da Borda (px):").pack(anchor='w')
        ttk.Scale(tab, from_=0, to=5, variable=self.border_width_var, command=self._update_preview,
                  orient='horizontal').pack(
            fill='x', pady=5)
        self.border_width_var.trace_add('write', self._update_preview)

        ttk.Label(tab, text=f"Arredondamento dos Cantos (Radius):").pack(anchor='w',
                                                                         pady=(10, 0))
        ttk.Scale(tab, from_=0, to=20, variable=self.border_radius_var, command=self._update_preview,
                  orient='horizontal').pack(
            fill='x', pady=5)
        self.border_radius_var.trace_add('write', self._update_preview)

    def _update_color_previews(self, frame, color):
        try:
            frame.config(bg=color if (color and color != "None") else "white")
        except tk.TclError:
            frame.config(bg="white")

    def _choose_color(self, color_name):
        initial_color = self.color_vars[color_name].get()
        try:
            color_code = colorchooser.askcolor(title=f"Escolha a cor para '{color_name}'", initialcolor=initial_color,
                                               parent=self)
            if color_code and color_code[1]:
                self.color_vars[color_name].set(color_code[1])
                self._update_preview()
        except tk.TclError:
            messagebox.showwarning("Erro de Cor", "Não foi possível abrir o seletor de cores.", parent=self)

    def _update_preview(self, *args):
        preview_settings = {
            "font_family": self.font_family_var.get(),
            "font_size": self.font_size_var.get(),
            "custom_colors": {name: var.get() for name, var in self.color_vars.items()}
        }
        # Aplica o preview no estilo da *aplicação principal*
        self.app._apply_theme_settings(self.app.style, preview_settings)

        # Define os estilos dos botões de preview (que são filhos deste dialog)
        self._apply_preview_styles()

        try:
            font_config = (self.font_family_var.get(), self.font_size_var.get())
            self.preview_label.config(font=font_config)
        except tk.TclError:
            font_config = ('TkDefaultFont', self.font_size_var.get())
            self.preview_label.config(font=font_config)

        self.update_idletasks()

    def _apply_preview_styles(self):
        """Aplica os estilos de preview nos botões dentro do Toplevel."""
        # Esta função é necessária porque o preview está dentro do Toplevel,
        # mas os estilos são aplicados no self.app.style (o root).
        # Precisamos garantir que os estilos deste Toplevel também sejam atualizados.

        style = self.app.style  # Usa o style da app principal

        colors = {name: var.get() for name, var in self.color_vars.items()}
        button_styles = {
            'Danger.TButton': {'background': colors.get('danger') or '#dc3545', 'active': '#c82333'},
            'Success.TButton': {'background': colors.get('success') or '#28a745', 'active': '#218838'},
            'Warning.TButton': {'background': colors.get('warning') or '#ffc107', 'active': '#e0a800',
                                'foreground': 'black'},
            'Info.TButton': {'background': colors.get('info') or '#17a2b8', 'active': '#138496'},
            'Secondary.TButton': {'background': colors.get('secondary') or '#6c757d', 'active': '#5a6268'},
        }
        for style_name, colors_dict in button_styles.items():
            fg = colors_dict.get('foreground', 'white')
            try:
                style.configure(style_name, foreground=fg, background=colors_dict['background'])
                style.map(style_name, background=[('active', colors_dict['active'])])
            except tk.TclError:
                pass  # Ignora cores inválidas

        border_w = self.border_width_var.get()
        style.configure('TButton', borderwidth=border_w)
        style.configure('TEntry', borderwidth=border_w)

    def _save_and_close(self):
        # Carrega o arquivo mais recente para preservar chaves desconhecidas
        latest_settings = self.settings_manager.load_settings()

        new_settings = {
            "font_family": self.font_family_var.get(),
            "font_size": self.font_size_var.get(),
            "custom_colors": {name: (var.get() or None) for name, var in self.color_vars.items()},
            "border_width": self.border_width_var.get(),
            "border_radius": self.border_radius_var.get(),
        }

        # Faz o merge para preservar chaves como 'theme' e 'focus_ring'
        final_settings = deep_merge(new_settings, latest_settings)

        self.settings_manager.save_settings(final_settings)
        # Aplica as configurações salvas permanentemente
        self.app._apply_theme_settings(self.app.style, final_settings)
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
            # Preserva o nome do tema original (ex: 'lumen'), mas reseta o resto
            default_settings['theme'] = self.current_settings.get('theme', 'lumen')
            self.settings_manager.save_settings(default_settings)

            self.app._apply_theme_settings(self.app.style, default_settings)
            messagebox.showinfo("Sucesso",
                                "As configurações padrão foram restauradas. Pode ser necessário reiniciar a aplicação para que todas as alterações tenham efeito.",
                                parent=self)
            self.destroy()