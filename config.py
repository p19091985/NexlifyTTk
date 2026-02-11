import configparser
from pathlib import Path
import logging
import sys

_config_path = Path(__file__).parent / "config_settings.ini"
_parser = configparser.ConfigParser()

if not _config_path.is_file():
    print(f"Aviso: '{_config_path.name}' não encontrado. Criando arquivo padrão.", file=sys.stderr)
    default_ini_content = """[Settings]
redirect_console_to_log = False
log_level = DEBUG
log_format = [%(asctime)s] [%(name)s] [%(levelname)-8s] - %(message)s
"""
    try:
        with open(_config_path, 'w', encoding='utf-8') as f:
            f.write(default_ini_content)
    except Exception as e:
        print(f"Erro crítico: Não foi possível criar '{_config_path}': {e}", file=sys.stderr)
        sys.exit(1)

try:
    _parser.read(_config_path, encoding='utf-8')
    if 'Settings' not in _parser:
        print("Aviso: Seção [Settings] não encontrada. Usando padrões.", file=sys.stderr)
        _parser['Settings'] = {}
except Exception as e:
    print(f"Erro ao ler .ini: {e}. Usando padrões.", file=sys.stderr)
    _parser['Settings'] = {}

def _get_boolean_setting(key, default=False):
    try:
        return _parser.getboolean('Settings', key, fallback=default)
    except (configparser.Error, ValueError):
        return default

def _get_string_setting(key, default=""):
    try:
        return _parser.get('Settings', key, fallback=default)
    except (configparser.Error, ValueError):
        return default

REDIRECT_CONSOLE_TO_LOG = _get_boolean_setting('redirect_console_to_log', default=False)

LOG_LEVEL_STR = _get_string_setting('log_level', default="INFO").upper()
LOG_FORMAT = _get_string_setting('log_format', default="[%(asctime)s] [%(name)s] [%(levelname)-8s] - %(message)s")

LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)