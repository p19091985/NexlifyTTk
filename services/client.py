"""Desktop remote mode: tokens in memory, no direct database connection."""
import io
import time
import json
import httpx
import pandas as pd
import config
from .transport import validate_service_url, tls_context

_token = None
_last_activity_sent = 0.0


def request(method, path, params=None):
    url = validate_service_url(config.API_URL)
    headers = {'Authorization': 'Bearer ' + _token} if _token else {}
    try:
        response = httpx.post(url + '/rpc', json={'method': path.strip('/'), 'params': params or {}}, headers=headers,
                              verify=tls_context(config.API_CA), timeout=5 if path.strip('/') in {'session', 'activity', 'logout'} else 20, follow_redirects=False, trust_env=False)
    except httpx.HTTPError:
        raise ConnectionError('API indisponível. Verifique a conexão e o certificado.') from None
    if response.status_code in {401, 403}:
        raise PermissionError(response.json().get('detail', 'Acesso negado.'))
    if response.is_error:
        raise ValueError('A API recusou a operação. Verifique os dados e as permissões.')
    return response.json()


def login(username, password, otp=''):
    global _token
    logout()
    try:
        result = request('POST', '/login', {'username': username, 'password': password, 'otp': otp})
    except (PermissionError, ValueError):
        return None
    except ConnectionError:
        return 'connection_error'
    if result.get('mfa_required'):
        return result
    _token = result['token']
    return result['user']


def logout():
    global _token
    if _token:
        try:
            request('POST', '/logout', {})
        except (ValueError, PermissionError, ConnectionError):
            pass  # Local logout still removes the token; server expiry remains.
        finally:
            _token = None


def activity():
    global _last_activity_sent
    if time.monotonic() - _last_activity_sent >= 15:
        request('POST', '/activity', {})
        _last_activity_sent = time.monotonic()


def dataframe(payload):
    return pd.read_json(io.StringIO(json.dumps(payload)), orient='table')


def sso_poll(handle, otp=''):
    global _token
    result = request('POST', '/sso/poll', {'handle': handle, 'otp': otp})
    if 'token' in result:
        _token = result['token']
        return result['user']
    return result if result.get('mfa_required') else None
