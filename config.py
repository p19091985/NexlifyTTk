           
from typing import Dict, Tuple
import os

DATABASE_ENABLED = True
INITIALIZE_DATABASE_ON_STARTUP =True
USE_LOGIN = True
REDIRECT_CONSOLE_TO_LOG =False

MAX_LOGIN_ATTEMPTS = 3

ENABLE_THEME_MENU = True

FONT_FAMILY = "Segoe UI"
FONTS: Dict[str, Tuple[str, int, str]] = {
    "default": (FONT_FAMILY, 10, "normal"),
    "sidebar_button": (FONT_FAMILY, 11, "normal"),
    "main_title": (FONT_FAMILY, 18, "bold"),
    "section_title": (FONT_FAMILY, 13, "bold"),
    "body": (FONT_FAMILY, 10, "normal"),
}

MAIN_WINDOW_RATIO = 0.7
MAIN_WINDOW_MIN_SIZE_RATIO = 0.5

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s [%(levelname)-8s] %(name)-15s - %(message)s"