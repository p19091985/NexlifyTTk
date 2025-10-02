# config.py
from typing import Dict, Tuple
import os

# --- Flags de Controle ---
# Ativa/Desativa a tela de login. False inicia com um usuário 'Desenvolvedor'.
USE_LOGIN = True
# Ativa/Desativa a inicialização do banco de dados.
USE_DATABASE = True
# Se True, redireciona todas as saídas do console (print, erros) para o arquivo de log.
REDIRECT_CONSOLE_TO_LOG = True


# --- Aparência e Estilo ---
FONT_FAMILY = "Segoe UI" # Fonte mais moderna para Windows, com fallback
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
LOG_FORMAT = "%(asctime)s [%(levelname)-8s] %(name)-15s - %(message)s"