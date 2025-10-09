# config.py
from typing import Dict, Tuple
import os

# --- Flags de Controle ---
DATABASE_ENABLED = True
INITIALIZE_DATABASE_ON_STARTUP = True
USE_LOGIN = True
REDIRECT_CONSOLE_TO_LOG = True

# --- Segurança ---
MAX_LOGIN_ATTEMPTS = 3


# --- Aparência e Estilo ---
# ESTA É A FLAG QUE CONTROLA O ACESSO AO PAINEL DE TEMAS.
# Se False, o item de menu "Aparência e Tema..." será desabilitado.
ENABLE_THEME_MENU = True

FONT_FAMILY = "Segoe UI"
FONTS: Dict[str, Tuple[str, int, str]] = {
    "default": (FONT_FAMILY, 10, "normal"),
    "sidebar_button": (FONT_FAMILY, 11, "normal"),
    "main_title": (FONT_FAMILY, 18, "bold"),
    "section_title": (FONT_FAMILY, 13, "bold"),
    "body": (FONT_FAMILY, 10, "normal"),
}

# --- Geometria da Janela ---
MAIN_WINDOW_RATIO = 0.7
MAIN_WINDOW_MIN_SIZE_RATIO = 0.5

# --- Configurações de Log ---
LOG_LEVEL = "INFO"
# CORREÇÃO: Adicionada aspas duplas no final da string para fechá-la.
LOG_FORMAT = "%(asctime)s [%(levelname)-8s] %(name)-15s - %(message)s"