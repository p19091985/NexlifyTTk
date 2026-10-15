"""
Centralized dark theme for the NexlifyTTk application.
"""
import tkinter as tk
from tkinter import ttk
import platform

# ── DPI Scaling ──────────────────────────────────────────────────────
_dpi_scale_cache = None


def get_dpi_scale(root=None):
    """Return DPI scale factor (1.0 = standard 96 DPI).

    On Windows without SetProcessDpiAwareness, tkinter auto-scales
    so we return 1.0. On Linux/Mac, detect from winfo_fpixels.
    """
    global _dpi_scale_cache
    if _dpi_scale_cache is not None:
        return _dpi_scale_cache
    try:
        if platform.system() == "Windows":
            # tkinter handles DPI scaling internally on Windows
            _dpi_scale_cache = 1.0
        elif root:
            _dpi_scale_cache = root.winfo_fpixels('1i') / 96.0
        else:
            _dpi_scale_cache = 1.0
    except Exception:
        _dpi_scale_cache = 1.0
    return _dpi_scale_cache


def scaled(value, scale=None):
    """Scale a pixel value by the DPI factor."""
    if scale is None:
        scale = get_dpi_scale()
    return int(value * scale)


def scaled_font(family, size, *modifiers, scale=None):
    """Return a DPI-scaled font tuple, e.g. scaled_font('Arial', 10, 'bold')."""
    if scale is None:
        scale = get_dpi_scale()
    return (family, int(size * scale), *modifiers)


# Default dark theme (Original)
_GATO_A_NOITE = {
    "bg_dark":          "#2b2b2b",
    "bg_darker":        "#1e1e1e",
    "bg_darkest":       "#202020",
    "bg_widget":        "#383838",
    "bg_toolbar":       "#333333",
    "bg_button":        "#444444",
    "bg_button_hover":  "#555555",
    "bg_subtle":        "#3e3e3e",
    "bg_subtle_hover":  "#4e4e4e",
    "bg_result":        "#1a1a2e",

    "fg_primary":       "#e0e0e0",
    "fg_secondary":     "#aaaaaa",
    "fg_muted":         "#888888",
    "fg_dim":           "#666666",

    "accent_blue":      "#4fc3f7",
    "accent_blue_h":    "#039be5",
    "accent_orange":    "#FF9800",
    "accent_green":     "#4CAF50",
    "accent_green_h":   "#66BB6A",
    "accent_purple":    "#AB47BC",
    "accent_red":       "#dc3545",
    "accent_red_h":     "#c82333",

    "sidebar_bg":       "#1e1e1e",
    "sidebar_active":   "#333333",

    "select_bg":        "#37474f",
    "select_fg":        "#ffffff",

    "border":           "#555555",
    "error_red":        "#dc3545",
    "error_red_h":      "#c82333",
    "accent_blue_hover": "#039be5",
}

_DRACULA = {
    "bg_dark":          "#282a36",
    "bg_darker":        "#21222c",
    "bg_darkest":       "#1e1f29",
    "bg_widget":        "#44475a",
    "bg_toolbar":       "#44475a",
    "bg_button":        "#6272a4",
    "bg_button_hover":  "#7182b8",
    "bg_subtle":        "#44475a",
    "bg_subtle_hover":  "#6272a4",
    "bg_result":        "#282a36",

    "fg_primary":       "#f8f8f2",
    "fg_secondary":     "#e2e2dc",
    "fg_muted":         "#bfbfb9",
    "fg_dim":           "#8b8b85",

    "accent_blue":      "#8be9fd",   # Cyan
    "accent_blue_h":    "#9dedff",
    "accent_orange":    "#ffb86c",
    "accent_green":     "#50fa7b",
    "accent_green_h":   "#69ff91",
    "accent_purple":    "#bd93f9",
    "accent_red":       "#ff5555",
    "accent_red_h":     "#ff6e6e",

    "sidebar_bg":       "#21222c",
    "sidebar_active":   "#44475a",

    "select_bg":        "#bd93f9",
    "select_fg":        "#282a36",

    "border":           "#6272a4",
    "error_red":        "#ff5555",
    "error_red_h":      "#ff6e6e",
    "accent_blue_hover": "#9dedff",
}

_OCEANO_ELETRICO = {
    "bg_dark":          "#010a14",
    "bg_darker":        "#00050a",
    "bg_darkest":       "#000000",
    "bg_widget":        "#02162b",
    "bg_toolbar":       "#02162b",
    "bg_button":        "#032242",
    "bg_button_hover":  "#043363",
    "bg_subtle":        "#02162b",
    "bg_subtle_hover":  "#032242",
    "bg_result":        "#010a14",

    "fg_primary":       "#e0ffff",
    "fg_secondary":     "#bfefff",
    "fg_muted":         "#8cb8c9",
    "fg_dim":           "#5c8a9e",

    "accent_blue":      "#00e5ff",
    "accent_blue_h":    "#33ebff",
    "accent_orange":    "#ffab40",
    "accent_green":     "#00e676",
    "accent_green_h":   "#33eb89",
    "accent_purple":    "#d500f9",
    "accent_red":       "#f50057",
    "accent_red_h":     "#ff4081",

    "sidebar_bg":       "#00050a",
    "sidebar_active":   "#02162b",

    "select_bg":        "#00e5ff",
    "select_fg":        "#000000",

    "border":           "#043363",
    "error_red":        "#f50057",
    "error_red_h":      "#ff4081",
    "accent_blue_hover": "#33ebff",
}

_AREIA_E_CEU = {
    "bg_dark":          "#f0ebe3",
    "bg_darker":        "#e3dcd1",
    "bg_darkest":       "#d1c7b8",
    "bg_widget":        "#ffffff",
    "bg_toolbar":       "#ffffff",
    "bg_button":        "#d4c7b0",
    "bg_button_hover":  "#c0b298",
    "bg_subtle":        "#e6dfd5",
    "bg_subtle_hover":  "#d4c7b0",
    "bg_result":        "#f8f5f0",

    "fg_primary":       "#1e3c4a",
    "fg_secondary":     "#3a5a6b",
    "fg_muted":         "#6c8b9c",
    "fg_dim":           "#8b9ca6",

    "accent_blue":      "#3c8dad",
    "accent_blue_h":    "#4a9fbf",
    "accent_orange":    "#d68945",
    "accent_green":     "#5b9c5f",
    "accent_green_h":   "#6eb872",
    "accent_purple":    "#876391",
    "accent_red":       "#c45353",
    "accent_red_h":     "#db6565",

    "sidebar_bg":       "#e3dcd1",
    "sidebar_active":   "#d4c7b0",

    "select_bg":        "#3c8dad",
    "select_fg":        "#ffffff",

    "border":           "#c0b298",
    "error_red":        "#c45353",
    "error_red_h":      "#db6565",
    "accent_blue_hover": "#4a9fbf",
}

_LIMAO_SICILIANO = {
    "bg_dark":          "#fffde7",
    "bg_darker":        "#fff9c4",
    "bg_darkest":       "#fff59d",
    "bg_widget":        "#ffffff",
    "bg_toolbar":       "#ffffff",
    "bg_button":        "#fff59d",
    "bg_button_hover":  "#fff176",
    "bg_subtle":        "#fffde7",
    "bg_subtle_hover":  "#fff59d",
    "bg_result":        "#ffffff",

    "fg_primary":       "#4e342e",
    "fg_secondary":     "#5d4037",
    "fg_muted":         "#8d6e63",
    "fg_dim":           "#bcaaa4",

    "accent_blue":      "#29b6f6",
    "accent_blue_h":    "#4fc3f7",
    "accent_orange":    "#ffa726",
    "accent_green":     "#66bb6a",
    "accent_green_h":   "#81c784",
    "accent_purple":    "#ab47bc",
    "accent_red":       "#ef5350",
    "accent_red_h":     "#e57373",

    "sidebar_bg":       "#fff9c4",
    "sidebar_active":   "#fff59d",

    "select_bg":        "#4e342e",
    "select_fg":        "#ffffff",

    "border":           "#fff176",
    "error_red":        "#ef5350",
    "error_red_h":      "#e57373",
    "accent_blue_hover": "#4fc3f7",
}

THEMES = {
    "Gato a Noite": _GATO_A_NOITE,
    "Drácula": _DRACULA,
    "Oceano Elétrico": _OCEANO_ELETRICO,
    "Areia e Céu": _AREIA_E_CEU,
    "Limão Siciliano": _LIMAO_SICILIANO,
}

_SL_PRESET_THEMES = {'☀️ Temas Claros': {'Padrão Streamlit': {'primaryColor': '#FF4B4B', 'backgroundColor': '#FFFFFF', 'secondaryBackgroundColor': '#F0F2F6', 'textColor': '#31333F', 'font': 'sans serif'}, 'Menta Suave': {'primaryColor': '#1FAB89', 'backgroundColor': '#D7FBE8', 'secondaryBackgroundColor': '#9DF3C4', 'textColor': '#042F1A', 'font': 'sans serif'}, 'Algodão Doce': {'primaryColor': '#F76B8A', 'backgroundColor': '#FDECF2', 'secondaryBackgroundColor': '#FAD2E1', 'textColor': '#5E2E3B', 'font': 'sans serif'}, 'Areia e Céu': {'primaryColor': '#3C8DAD', 'backgroundColor': '#F0EBE3', 'secondaryBackgroundColor': '#D4C7B0', 'textColor': '#1E3C4A', 'font': 'sans serif'}, 'Lavanda': {'primaryColor': '#7F5A83', 'backgroundColor': '#F4EEFF', 'secondaryBackgroundColor': '#DCD6F7', 'textColor': '#2B192E', 'font': 'serif'}, 'Limão Siciliano': {'primaryColor': '#D4E157', 'backgroundColor': '#FFFDE7', 'secondaryBackgroundColor': '#FFFACD', 'textColor': '#4E342E', 'font': 'sans serif'}, 'Pêssego': {'primaryColor': '#FF8A65', 'backgroundColor': '#FFF3E0', 'secondaryBackgroundColor': '#FFE0B2', 'textColor': '#4E342E', 'font': 'serif'}, 'Céu de Inverno': {'primaryColor': '#4FC3F7', 'backgroundColor': '#E1F5FE', 'secondaryBackgroundColor': '#B3E5FC', 'textColor': '#1A237E', 'font': 'sans serif'}}, '🌙 Temas Escuros': {'Drácula': {'primaryColor': '#bd93f9', 'backgroundColor': '#282a36', 'secondaryBackgroundColor': '#44475a', 'textColor': '#f8f8f2', 'font': 'sans serif'}, 'Monokai Pro': {'primaryColor': '#ff6188', 'backgroundColor': '#2D2A2E', 'secondaryBackgroundColor': '#403E41', 'textColor': '#FCFCFA', 'font': 'monospace'}, 'Nord': {'primaryColor': '#88C0D0', 'backgroundColor': '#2E3440', 'secondaryBackgroundColor': '#3B4252', 'textColor': '#ECEFF4', 'font': 'sans serif'}, "Synthwave '84": {'primaryColor': '#f92aad', 'backgroundColor': '#2b213a', 'secondaryBackgroundColor': '#34294f', 'textColor': '#f8f8f2', 'font': 'sans serif'}, 'One Dark Pro': {'primaryColor': '#61AFEF', 'backgroundColor': '#282C34', 'secondaryBackgroundColor': '#31353F', 'textColor': '#ABB2BF', 'font': 'monospace'}, 'Meia-noite na Floresta': {'primaryColor': '#4DB6AC', 'backgroundColor': '#1B2631', 'secondaryBackgroundColor': '#2C3E50', 'textColor': '#E0E0E0', 'font': 'sans serif'}, 'Café Expresso': {'primaryColor': '#A1887F', 'backgroundColor': '#211F1F', 'secondaryBackgroundColor': '#3E2723', 'textColor': '#D7CCC8', 'font': 'serif'}, 'Retrô Sombrio (Gruvbox)': {'primaryColor': '#FABD2F', 'backgroundColor': '#282828', 'secondaryBackgroundColor': '#3C3836', 'textColor': '#EBDBB2', 'font': 'monospace'}}, '🌈 Temas Vibrantes': {'Pôr do Sol Tropical': {'primaryColor': '#FF6B6B', 'backgroundColor': '#FFF1C9', 'secondaryBackgroundColor': '#FFE69A', 'textColor': '#8B4513', 'font': 'sans serif'}, 'Cyberpunk Neon': {'primaryColor': '#00F2FF', 'backgroundColor': '#0C0032', 'secondaryBackgroundColor': '#1D004D', 'textColor': '#F0F0F0', 'font': 'monospace'}, 'Vaporwave': {'primaryColor': '#F92AAD', 'backgroundColor': '#2B213A', 'secondaryBackgroundColor': '#34294F', 'textColor': '#F8F8f2', 'font': 'sans serif'}, 'Arco-íris Pastel': {'primaryColor': '#ff8b94', 'backgroundColor': '#fcefee', 'secondaryBackgroundColor': '#f8e0e2', 'textColor': '#683135', 'font': 'serif'}, 'Magma': {'primaryColor': '#FF3D00', 'backgroundColor': '#212121', 'secondaryBackgroundColor': '#303030', 'textColor': '#F5F5F5', 'font': 'monospace'}, 'Oceano Elétrico': {'primaryColor': '#00E5FF', 'backgroundColor': '#010A14', 'secondaryBackgroundColor': '#02162B', 'textColor': '#E0FFFF', 'font': 'sans serif'}, 'Verde Limão Neon': {'primaryColor': '#76FF03', 'backgroundColor': '#1B1B1B', 'secondaryBackgroundColor': '#2C2C2C', 'textColor': '#E6FEE9', 'font': 'sans serif'}}, '💼 Temas Corporativos': {'Azul Executivo': {'primaryColor': '#005A9E', 'backgroundColor': '#F5F5F5', 'secondaryBackgroundColor': '#E1EBF5', 'textColor': '#212121', 'font': 'sans serif'}, 'Grafite Sóbrio': {'primaryColor': '#4A4A4A', 'backgroundColor': '#FFFFFF', 'secondaryBackgroundColor': '#EAEAEA', 'textColor': '#333333', 'font': 'sans serif'}, 'Verde Confiança': {'primaryColor': '#007A5E', 'backgroundColor': '#F7F9F9', 'secondaryBackgroundColor': '#E6F2F0', 'textColor': '#1D1C1D', 'font': 'sans serif'}, 'Bordô Elegante': {'primaryColor': '#800020', 'backgroundColor': '#FDF6F7', 'secondaryBackgroundColor': '#FBEAEF', 'textColor': '#33000A', 'font': 'serif'}, 'Cinza Tecnológico': {'primaryColor': '#0078D4', 'backgroundColor': '#F3F3F3', 'secondaryBackgroundColor': '#E1E1E1', 'textColor': '#141414', 'font': 'sans serif'}, 'Ouro e Petróleo (Finanças)': {'primaryColor': '#B8860B', 'backgroundColor': '#121212', 'secondaryBackgroundColor': '#282828', 'textColor': '#E5E5E5', 'font': 'serif'}, 'Azul Saúde': {'primaryColor': '#00A0B0', 'backgroundColor': '#FFFFFF', 'secondaryBackgroundColor': '#EDF8F9', 'textColor': '#4A4A4A', 'font': 'sans serif'}}}

def _adjust_hex_lightness(hex_color, amount):
    import colorsys
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6: return '#' + hex_color
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)
    l = max(0, min(1, l + amount))
    rr, gg, bb = colorsys.hls_to_rgb(h, l, s)
    return f"#{int(rr*255):02x}{int(gg*255):02x}{int(bb*255):02x}"


def get_contrasting_text(hex_color, dark="#1e1e1e", light="#ffffff"):
    """Return a readable foreground color for a given hex background."""
    if not isinstance(hex_color, str) or not hex_color.startswith("#"):
        return light

    color = hex_color.lstrip("#")
    if len(color) != 6:
        return light

    r, g, b = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return dark if brightness >= 160 else light

def _generate_tk_theme(stream_theme):
    bg = stream_theme.get("backgroundColor", "#FFFFFF")
    bg_sec = stream_theme.get("secondaryBackgroundColor", "#F0F2F6")
    text = stream_theme.get("textColor", "#31333F")
    primary = stream_theme.get("primaryColor", "#FF4B4B")

    r, g, b = tuple(int(bg.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    brightness = (r*299 + g*587 + b*114) / 1000
    is_dark = brightness < 128

    if is_dark:
        bg_darker = _adjust_hex_lightness(bg, -0.04)
        bg_darkest = _adjust_hex_lightness(bg, -0.08)
        btn_hover = _adjust_hex_lightness(bg_sec, 0.08)
        fg_sec = _adjust_hex_lightness(text, -0.2)
        fg_mut = _adjust_hex_lightness(text, -0.4)
    else:
        bg_darker = _adjust_hex_lightness(bg, -0.05)
        bg_darkest = _adjust_hex_lightness(bg, -0.1)
        btn_hover = _adjust_hex_lightness(bg_sec, -0.05)
        fg_sec = _adjust_hex_lightness(text, 0.2)
        fg_mut = _adjust_hex_lightness(text, 0.4)

    return {
        "bg_dark":          bg,
        "bg_darker":        bg_darker,
        "bg_darkest":       bg_darkest,
        "bg_widget":        bg_sec,
        "bg_toolbar":       bg_sec,
        "bg_button":        bg_sec,
        "bg_button_hover":  btn_hover,
        "bg_subtle":        bg,
        "bg_subtle_hover":  btn_hover,
        "bg_result":        bg,

        "fg_primary":       text,
        "fg_secondary":     fg_sec,
        "fg_muted":         fg_mut,
        "fg_dim":           fg_mut,

        "accent_blue":      primary,
        "accent_blue_h":    _adjust_hex_lightness(primary, 0.1 if is_dark else -0.1),

        "accent_orange":    "#FF9800" if is_dark else "#F57C00",
        "accent_green":     "#4CAF50" if is_dark else "#4CAF50",
        "accent_green_h":   "#66BB6A" if is_dark else "#388E3C",
        "accent_purple":    "#AB47BC" if is_dark else "#8E24AA",
        "accent_red":       "#dc3545" if is_dark else "#d32f2f",
        "accent_red_h":     "#c82333" if is_dark else "#b71c1c",

        "sidebar_bg":       bg_darker,
        "sidebar_active":   bg_sec,

        "select_bg":        primary,
        "select_fg":        bg if is_dark else "#ffffff",

        "border":           btn_hover,
        "error_red":        "#dc3545" if is_dark else "#d32f2f",
        "error_red_h":      "#c82333" if is_dark else "#b71c1c",
        "accent_blue_hover": _adjust_hex_lightness(primary, 0.1 if is_dark else -0.1),
    }

# Inject generated themes if they aren't manually defined
for _cat, _cat_themes in _SL_PRESET_THEMES.items():
    for _t_name, _t_colors in _cat_themes.items():
        if _t_name not in THEMES:
            THEMES[_t_name] = _generate_tk_theme(_t_colors)

# Load active theme from settings.json
def _load_active_theme_colors():
    import json
    import os
    try:
        # Resolve path to settings.json relative to this file
        project_root = os.path.dirname(os.path.abspath(__file__))
        settings_path = os.path.join(project_root, "settings.json")
        if os.path.exists(settings_path):
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
                theme_name = settings.get("active_theme", "Gato a Noite")
                return THEMES.get(theme_name, THEMES["Gato a Noite"]).copy()
    except Exception:
        pass

    return THEMES["Gato a Noite"].copy()

COLORS = _load_active_theme_colors()

def set_active_theme_colors(theme_name: str, style=None):
    """
    Updates the global COLORS dictionary in-place with the given theme
    and optionally immediately updates the ttk.Style.
    In-place update is crucial so that import references `from theme import C`
    keep pointing to the same dictionary object in memory.
    """
    new_colors = THEMES.get(theme_name, THEMES["Gato a Noite"]).copy()
    COLORS.clear()
    COLORS.update(new_colors)

    if style:
        apply_dark_theme(style)

C = COLORS


def apply_dark_theme(style: ttk.Style) -> None:
    """
    Configure all ttk styles to use the dark colour scheme.
    Call this once after creating the ttk.Style object.
    """
    style.theme_use("clam")

    style.configure(".",
        background=C["bg_dark"],
        foreground=C["fg_primary"],
        fieldbackground=C["bg_widget"],
        insertcolor=C["fg_primary"],
        borderwidth=0,
        relief="flat",
    )
    style.map(".",
        background=[("active", C["bg_button_hover"])],
        foreground=[("disabled", C["fg_dim"])],
    )

    style.configure("TFrame", background=C["bg_dark"])

    style.configure("TLabel",
        background=C["bg_dark"],
        foreground=C["fg_primary"],
    )

    style.configure("TLabelframe",
        background=C["bg_dark"],
        foreground=C["accent_blue"],
        bordercolor=C["bg_toolbar"],
    )
    style.configure("TLabelframe.Label",
        background=C["bg_dark"],
        foreground=C["accent_blue"],
    )

    style.configure("TEntry",
        fieldbackground=C["bg_widget"],
        foreground=C["fg_primary"],
        insertcolor=C["fg_primary"],
        bordercolor=C["bg_button"],
    )

    style.configure("TButton",
        background=C["bg_button"],
        foreground=C["fg_primary"],
        padding=6,
        relief="flat",
    )
    style.map("TButton",
        background=[("active", C["bg_button_hover"])],
        foreground=[("active", "#ffffff")],
    )

    style.configure("Sidebar.TFrame", background=C["sidebar_bg"])
    style.configure("Sidebar.TLabel", background=C["sidebar_bg"], foreground=C["fg_primary"])
    style.configure("Sidebar.TButton",
        background=C["sidebar_bg"],
        foreground=C["fg_primary"],
        borderwidth=0,
        anchor="w",
        padding=(10, 8),
    )
    style.map("Sidebar.TButton",
        background=[("active", C["sidebar_active"])],
        foreground=[("active", "#ffffff")],
    )

    _semantic = {
        "Danger.TButton":    (C["accent_red"],    C["accent_red_h"],    "#ffffff"),
        "Success.TButton":   (C["accent_green"],  C["accent_green_h"],  "#ffffff"),
        "Warning.TButton":   (C["accent_orange"], "#e0a800",            "#1e1e1e"),
        "Info.TButton":      (C["accent_blue"],   "#039be5",            "#1e1e1e"),
        "Secondary.TButton": (C["bg_subtle"],     C["bg_subtle_hover"], C["fg_primary"]),
    }
    for name, (bg, active_bg, fg) in _semantic.items():
        style.configure(name, background=bg, foreground=fg, padding=6, relief="flat")
        style.map(name, background=[("active", active_bg)])

    style.configure("TCombobox",
        fieldbackground=C["bg_widget"],
        background=C["bg_button"],
        foreground=C["fg_primary"],
        arrowcolor=C["fg_primary"],
    )
    style.map("TCombobox",
        fieldbackground=[("readonly", C["bg_widget"])],
        foreground=[("readonly", C["fg_primary"])],
    )

    style.configure("TNotebook",
        background=C["bg_dark"],
        borderwidth=0,
    )
    style.configure("TNotebook.Tab",
        background=C["bg_toolbar"],
        foreground=C["fg_secondary"],
        padding=(12, 6),
    )
    style.map("TNotebook.Tab",
        background=[("selected", C["bg_darker"]), ("active", C["bg_button"])],
        foreground=[("selected", C["accent_blue"]), ("active", C["fg_primary"])],
    )

    style.configure("TSeparator", background=C["bg_toolbar"])

    # ── Additional widgets (fixes white areas on Xubuntu/XFCE) ──
    style.configure("TCheckbutton",
        background=C["bg_dark"],
        foreground=C["fg_primary"],
        indicatorcolor=C["bg_widget"],
    )
    style.map("TCheckbutton",
        background=[("active", C["bg_dark"])],
        indicatorcolor=[("selected", C["accent_blue"])],
    )

    style.configure("TRadiobutton",
        background=C["bg_dark"],
        foreground=C["fg_primary"],
        indicatorcolor=C["bg_widget"],
    )
    style.map("TRadiobutton",
        background=[("active", C["bg_dark"])],
        indicatorcolor=[("selected", C["accent_blue"])],
    )

    style.configure("TSpinbox",
        fieldbackground=C["bg_widget"],
        background=C["bg_button"],
        foreground=C["fg_primary"],
        arrowcolor=C["fg_primary"],
        insertcolor=C["fg_primary"],
    )

    style.configure("TMenubutton",
        background=C["bg_button"],
        foreground=C["fg_primary"],
    )
    style.map("TMenubutton",
        background=[("active", C["bg_button_hover"])],
    )

    style.configure("TScale",
        background=C["bg_dark"],
        troughcolor=C["bg_darker"],
    )

    style.configure("TProgressbar",
        background=C["accent_blue"],
        troughcolor=C["bg_darker"],
    )

    style.configure("TPanedwindow", background=C["bg_dark"])

    style.configure("Treeview",
        background=C["bg_darker"],
        fieldbackground=C["bg_darker"],
        foreground=C["fg_primary"],
    )
    style.configure("Treeview.Heading",
        background=C["bg_toolbar"],
        foreground=C["fg_primary"],
    )
    style.map("Treeview",
        background=[("selected", C["select_bg"])],
        foreground=[("selected", C["select_fg"])],
    )

    style.configure("TScrollbar",
        background=C["bg_toolbar"],
        troughcolor=C["bg_darker"],
        arrowcolor=C["fg_muted"],
    )


def style_menu(menu: tk.Menu) -> None:
    """Apply dark colors to a tk.Menu widget (recursively)."""
    menu.configure(
        bg=C["bg_darker"],
        fg=C["fg_primary"],
        activebackground=C["bg_button"],
        activeforeground="#ffffff",
        relief="flat",
        borderwidth=0,
    )
