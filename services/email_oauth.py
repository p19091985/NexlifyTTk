"""SMTP OAuth2 refresh and Microsoft device authorization; tokens stay on the server."""
import hashlib
import json
import threading
import time
import uuid
from urllib.parse import urlsplit
import httpx

_lock = threading.Lock()
_tokens = {}
MICROSOFT = 'https://login.microsoftonline.com/consumers/oauth2/v2.0/'
SCOPE = 'https://outlook.office.com/SMTP.Send offline_access'


def post(url, data):
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('Endpoint OAuth2 inválido; use HTTPS.')
    try:
        with httpx.Client(timeout=15, verify=True, follow_redirects=False, trust_env=False) as client:
            with client.stream('POST', url, data=data) as response:
                body = bytearray()
                for chunk in response.iter_bytes():
                    body.extend(chunk)
                    if len(body) > 1048576:
                        raise ValueError()
                if response.status_code not in {200, 400, 401}:
                    raise ValueError()
                result = json.loads(body)
                if not isinstance(result, dict):
                    raise ValueError()
                if response.status_code != 200 and 'error' not in result:
                    raise ValueError()
                return result
    except (httpx.HTTPError, ValueError, UnicodeError):
        raise ConnectionError('Não foi possível consultar o provedor OAuth2. Verifique a conexão e o cadastro do aplicativo.') from None


def valid_token(value):
    if not isinstance(value, str) or not 1 <= len(value) <= 16384 or not value.isascii() or any(ord(c) <= 32 or ord(c) == 127 for c in value):
        raise ValueError('Token OAuth2 inválido. Reconecte a conta.')
    return value


def _cache_key(settings):
    # Bind cached access tokens to the complete SMTP and OAuth identity, never log this material.
    return hashlib.sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest()


def access_token(settings):
    from .email_settings import remember_refresh_token
    with _lock:
        key = _cache_key(settings)
        cached = _tokens.get(key)
        if cached and cached[1] > time.monotonic() + 60:
            return cached[0]
        data = {'grant_type': 'refresh_token', 'client_id': settings['client_id'],
                'refresh_token': settings['refresh_token']}
        if settings['scope']:
            data['scope'] = settings['scope']
        if settings['client_secret']:
            data['client_secret'] = settings['client_secret']
        result = post(settings['token_url'], data)
        if 'error' in result or result.get('token_type', '').lower() != 'bearer':
            raise ValueError('OAuth2 recusado. Reconecte a conta e confira as permissões SMTP.')
        token = valid_token(result.get('access_token'))
        try:
            lifetime = min(86400, max(0, int(result.get('expires_in', 0))))
        except (TypeError, ValueError):
            raise ValueError('Prazo do token OAuth2 inválido.') from None
        if len(_tokens) >= 16:
            _tokens.clear()
        _tokens[key] = token, time.monotonic() + lifetime
        if result.get('refresh_token'):
            refresh = valid_token(result['refresh_token'])
            remember_refresh_token(settings, refresh)
            _tokens[_cache_key(dict(settings, refresh_token=refresh))] = _tokens[key]
        return token


def start_microsoft(client_id):
    from .email_settings import require_server
    require_server()
    try:
        client_id = str(uuid.UUID(client_id))
    except (ValueError, TypeError, AttributeError):
        raise ValueError('Informe o Application (client) ID do aplicativo registrado na Microsoft.') from None
    result = post(MICROSOFT+'devicecode', {'client_id': client_id, 'scope': SCOPE})
    try:
        uri = urlsplit(result['verification_uri'])
        if (uri.scheme != 'https' or uri.hostname not in {'microsoft.com', 'www.microsoft.com', 'login.microsoftonline.com'}
                or uri.username or uri.password):
            raise ValueError()
        device_code = valid_token(result['device_code'])
        code = valid_token(result['user_code'])
        interval = max(5, min(60, int(result.get('interval', 5))))
        expiry = min(900, max(1, int(result['expires_in'])))
    except (ValueError, TypeError, KeyError):
        raise ValueError('Não foi possível iniciar OAuth2. Confira o client ID e a permissão de cliente público.') from None
    return {'client_id': client_id, 'device_code': device_code, 'user_code': code,
            'verification_uri': result['verification_uri'], 'interval': interval,
            'expires_at': time.monotonic()+expiry, 'next_poll': time.monotonic()+interval}


def poll_microsoft(flow):
    if time.monotonic() >= flow['expires_at']:
        raise ValueError('Autorização Microsoft expirou. Conecte novamente.')
    if time.monotonic() < flow['next_poll']:
        return None
    result = post(MICROSOFT+'token', {'client_id': flow['client_id'], 'device_code': flow['device_code'],
                                    'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'})
    error = result.get('error')
    if error in {'authorization_pending', 'slow_down'}:
        if error == 'slow_down':
            flow['interval'] += 5
        flow['next_poll'] = time.monotonic()+flow['interval']
        return None
    if error:
        flow['expires_at'] = 0
        raise ValueError('Autorização Microsoft recusada ou expirada. Conecte novamente.')
    flow['expires_at'] = 0  # Single-use flow; keep only the refresh token after confirmation.
    return valid_token(result.get('refresh_token'))
