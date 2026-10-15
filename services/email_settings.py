"""Server-local SMTP configuration, encrypted at rest; never returned through RPC."""
import ipaddress
import json
import os
import re
import threading
import time
from contextlib import contextmanager
from urllib.parse import urlsplit
import config
from persistencia import security
from utils.secure_files import private_directory, atomic_write_private, reject_link_path, restrict_permissions
from .email_providers import defaults, PROVIDERS

LOCK = threading.RLock()
SECRETS = {'password', 'refresh_token', 'client_secret'}
IDENTITY = ('provider', 'host', 'port', 'security', 'username', 'sender', 'auth', 'client_id', 'token_url', 'scope')
ENV_FIELDS = {'provider': 'PROVIDER', 'host': 'HOST', 'port': 'PORT', 'security': 'SECURITY',
              'sender': 'FROM', 'username': 'USER', 'password': 'PASSWORD', 'auth': 'AUTH',
              'client_id': 'CLIENT_ID', 'client_secret': 'CLIENT_SECRET', 'refresh_token': 'REFRESH_TOKEN',
              'token_url': 'TOKEN_URL', 'scope': 'SCOPE', 'ca': 'CA'}


def require_server():
    if config.API_MODE == 'client':
        raise PermissionError('Configure e envie e-mails na máquina do servidor; clientes não guardam credenciais SMTP.')


def path():
    return security.KEY_PATH.parent / 'email.json'


@contextmanager
def file_lock():
    """Serialize CLI edits and token refresh across processes on Windows and Linux."""
    private_directory(path().parent)
    target = reject_link_path(path().with_suffix('.lock'))
    descriptor = os.open(target, os.O_RDWR | os.O_CREAT, 0o600)
    with os.fdopen(descriptor, 'r+b', buffering=0) as stream:
        restrict_permissions(target)
        if os.fstat(stream.fileno()).st_size == 0:
            stream.write(b'0')
        deadline = time.monotonic() + 5
        while True:
            try:
                stream.seek(0)
                if os.name == 'nt':
                    import msvcrt
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise ValueError('Configuração de e-mail ocupada. Tente novamente.') from None
                time.sleep(0.05)
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == 'nt':
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def environment_active():
    return any('NEXLIFY_SMTP_'+field in os.environ for field in ENV_FIELDS.values())


def load_saved():
    require_server()
    with LOCK:
        target = reject_link_path(path())
        if not target.exists():
            return defaults()
        restrict_permissions(target)
        try:
            envelope = json.loads(target.read_text(encoding='utf-8'))
            if envelope['version'] != 1 or not envelope['payload'].startswith('ENC:'):
                raise ValueError()
            data = json.loads(security.decrypt_message(envelope['payload']))
            return validate(data, require_credentials=False)
        except (KeyError, TypeError, ValueError, UnicodeError):
            raise ValueError('Configuração de e-mail inválida ou chave incorreta. Restaure a configuração e o chaveiro.') from None


def effective():
    require_server()
    if not environment_active():
        return validate(load_saved())
    # Environment configuration is independent; never send a saved secret to an overridden host.
    data = defaults(os.environ.get('NEXLIFY_SMTP_PROVIDER', 'custom'))
    data['enabled'] = True
    for field, variable in ENV_FIELDS.items():
        if 'NEXLIFY_SMTP_'+variable in os.environ:
            data[field] = os.environ['NEXLIFY_SMTP_'+variable]
    if 'NEXLIFY_SMTP_PORT' not in os.environ:
        data['port'] = 465 if data['security'] == 'ssl' else 587
    return validate(data)


def validate(data, *, require_credentials=True):
    from .email_delivery import validate_address
    if not isinstance(data, dict) or set(data) - set(defaults()):
        raise ValueError('Campos de configuração SMTP inválidos.')
    result = defaults(data.get('provider', 'custom'))
    result.update(data)
    if not isinstance(result['enabled'], bool):
        raise ValueError('Estado de envio inválido.')
    for key, value in result.items():
        if key not in {'enabled', 'port'} and (not isinstance(value, str) or len(value) > 16384):
            raise ValueError('Campo SMTP inválido.')
    if result['security'] not in {'ssl', 'starttls'}:
        raise ValueError('SMTP exige TLS: selecione starttls ou ssl.')
    if result['auth'] not in {'password', 'oauth2'}:
        raise ValueError('Autenticação deve ser password ou oauth2.')
    try:
        if isinstance(result['port'], bool):
            raise ValueError()
        result['port'] = int(str(result['port']))
    except (TypeError, ValueError):
        raise ValueError('Porta SMTP inválida.') from None
    if not 1 <= result['port'] <= 65535:
        raise ValueError('Porta SMTP inválida.')
    if result['host']:
        host = result['host']
        try:
            ipaddress.ip_address(host)
        except ValueError:
            if len(host) > 253 or not all(re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?', part) for part in host.split('.')):
                raise ValueError('Informe apenas o hostname ou IP SMTP, sem URL ou porta.') from None
    for name in ('username', 'client_id'):
        if any(ord(char) < 32 or ord(char) == 127 for char in result[name]):
            raise ValueError('Usuário ou identificador contém caracteres inválidos.')
    if result['sender']:
        result['sender'] = validate_address(result['sender'])
    if result['token_url']:
        url = urlsplit(result['token_url'])
        if url.scheme != 'https' or not url.hostname or url.username or url.password or url.query or url.fragment:
            raise ValueError('Endpoint OAuth2 exige HTTPS sem credenciais, query ou fragmento.')
    if result['provider'] == 'outlook' and result['auth'] != 'oauth2':
        raise ValueError('Outlook/Hotmail exige OAuth2. Use Conectar à Microsoft.')
    if result['enabled'] and require_credentials:
        if not result['host'] or not result['sender'] or not result['username']:
            raise ValueError('Configure servidor SMTP, remetente e usuário.')
        if result['auth'] == 'password' and not result['password']:
            raise ValueError('Informe a senha SMTP ou a senha de aplicativo.')
        if result['auth'] == 'oauth2' and not all(result[key] for key in ('client_id', 'token_url', 'refresh_token')):
            raise ValueError('Conecte a conta OAuth2 ou configure client ID, endpoint e refresh token.')
    return result


def prepare(values):
    """Blank secrets preserve credentials only when their account/destination is unchanged."""
    require_server()
    previous = load_saved()
    data = validate(values, require_credentials=False)
    if all(data[key] == previous[key] for key in IDENTITY):
        for key in SECRETS:
            if not data[key]:
                data[key] = previous[key]
    return validate(data)


def _write(data):
    private_directory(path().parent)
    envelope = {'version': 1, 'payload': security.encrypt_message(json.dumps(data, ensure_ascii=True))}
    atomic_write_private(path(), json.dumps(envelope))


def save(values):
    require_server()
    if environment_active():
        raise ValueError('SMTP está configurado por variáveis de ambiente. Remova-as para usar a configuração salva.')
    with LOCK, file_lock():
        data = prepare(values)
        _write(data)
    return {key: value for key, value in data.items() if key not in SECRETS}


def remember_refresh_token(settings, token):
    """Do not overwrite an administrator edit or an environment-managed credential."""
    if environment_active():
        return
    with LOCK, file_lock():
        current = load_saved()
        if all(current[key] == settings[key] for key in IDENTITY) and current['refresh_token'] == settings['refresh_token']:
            current['refresh_token'] = token
            _write(current)


def rotate_encryption():
    if path().exists():
        with LOCK, file_lock():
            _write(load_saved())
        return 1
    return 0
