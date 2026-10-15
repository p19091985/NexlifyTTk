"""Configuração local; valores inválidos interrompem a inicialização."""
import configparser
import logging
import os
from utils.paths import PROJECT_ROOT
_config_path = PROJECT_ROOT / 'config_settings.ini'
_parser = configparser.ConfigParser(interpolation=None)
_parser.read(_config_path, encoding='utf-8')
_parser.read(PROJECT_ROOT / 'config.local.ini', encoding='utf-8')
if not _parser.has_section('Settings'):
    _parser.add_section('Settings')
DATABASE_ENABLED = _parser.getboolean('Settings', 'database_enabled', fallback=True)
INITIALIZE_DATABASE_ON_STARTUP = _parser.getboolean('Settings', 'initialize_database_on_startup', fallback=True)
USE_LOGIN = _parser.getboolean('Settings', 'use_login', fallback=True)
_mfa_value = os.environ.get('NEXLIFY_MFA_ENABLED', _parser.get('Settings', 'mfa_enabled', fallback='false')).lower()
if _mfa_value not in configparser.ConfigParser.BOOLEAN_STATES:
    raise ValueError('mfa_enabled deve ser True ou False.')
MFA_ENABLED = configparser.ConfigParser.BOOLEAN_STATES[_mfa_value]
REDIRECT_CONSOLE_TO_LOG = _parser.getboolean('Settings', 'redirect_console_to_log', fallback=False)
ENABLE_THEME_MENU = _parser.getboolean('Settings', 'enable_theme_menu', fallback=True)
LOGGING_ENABLED = _parser.getboolean('Settings', 'logging_enabled', fallback=True)
ENVIRONMENT = os.environ.get('NEXLIFY_ENV', _parser.get('Settings', 'environment', fallback='production'))
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCK_SECONDS = 300
SESSION_IDLE_SECONDS = _parser.getint('Settings', 'session_idle_seconds', fallback=900)
SESSION_MAX_SECONDS = _parser.getint('Settings', 'session_max_seconds', fallback=28800)
REAUTH_SECONDS = 300
API_MODE = os.environ.get('NEXLIFY_API_MODE', _parser.get('Settings', 'api_mode', fallback='local'))
API_URL = os.environ.get('NEXLIFY_API_URL', _parser.get('Settings', 'api_url', fallback=''))
API_CA = os.environ.get('NEXLIFY_API_CA', '')
PASSWORD_BREACH_MODE = os.environ.get('NEXLIFY_PASSWORD_BREACH_MODE', 'hibp' if ENVIRONMENT == 'production' else 'local')
PASSWORD_BLOCKLIST_PATH = os.environ.get('NEXLIFY_PASSWORD_BLOCKLIST', '')
LOG_LEVEL = getattr(logging, _parser.get('Settings', 'log_level', fallback='INFO').upper(), logging.INFO)
LOG_FORMAT = _parser.get('Settings', 'log_format', fallback='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
def validate():
    if API_MODE not in {'local', 'client', 'server'} or PASSWORD_BREACH_MODE not in {'local', 'hibp'}:
        raise ValueError('Modo de API ou verificação de senhas inválido.')
    if API_MODE == 'client':
        from services.transport import validate_service_url
        validate_service_url(API_URL)
    if ENVIRONMENT not in {'development', 'production'}:
        raise ValueError('environment deve ser development ou production.')
    if USE_LOGIN and not DATABASE_ENABLED:
        raise ValueError('O login requer o banco de dados habilitado.')
    if INITIALIZE_DATABASE_ON_STARTUP and not DATABASE_ENABLED:
        raise ValueError('A inicialização do banco requer database_enabled = True.')
    if ENVIRONMENT == 'production' and (not USE_LOGIN or not LOGGING_ENABLED):
        raise ValueError('Em produção, login e logs são obrigatórios.')
    if not 60 <= SESSION_IDLE_SECONDS <= 3600 or not SESSION_IDLE_SECONDS <= SESSION_MAX_SECONDS <= 86400:
        raise ValueError('Sessão: inatividade deve ficar entre 60 e 3600 segundos; duração máxima entre a inatividade e 86400 segundos.')
    if not USE_LOGIN:
        from utils.installation_profile import load_installation_profile
        if load_installation_profile(PROJECT_ROOT)['id'] != 'dev':
            raise ValueError('Desabilitar login exige instalação com perfil Desenvolvimento.')
