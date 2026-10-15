"""OIDC authorization code + PKCE. Provider tokens never reach the desktop.

One server worker owns short-lived flows. Restart cancels outstanding logins.
Identities must be bound explicitly by an installation administrator.
"""
import base64
import hashlib
import os
import secrets
import threading
import time
from urllib.parse import urlencode
import httpx
from joserfc import jwt
from joserfc.jwk import KeySet
from joserfc.errors import JoseError
from sqlalchemy import select, update
from persistencia import auth, mfa, audit
from persistencia.database import DatabaseManager
from persistencia.schema import external_identities, usuarios, auth_state, ROLES
from .transport import validate_service_url, tls_context
from . import sessions
import config

_flows = {}
_lock = threading.Lock()


def settings():
    issuer = os.environ.get('NEXLIFY_OIDC_ISSUER', '')
    client = os.environ.get('NEXLIFY_OIDC_CLIENT_ID', '')
    callback = os.environ.get('NEXLIFY_OIDC_REDIRECT_URI', '')
    if not issuer or not client or not callback:
        raise PermissionError('SSO não configurado nesta instalação.')
    validate_service_url(issuer)
    validate_service_url(callback)
    return issuer, client, callback


def provider_request(method, url, **kwargs):
    validate_service_url(url)
    with httpx.Client(verify=tls_context(os.environ.get('NEXLIFY_OIDC_CA', '')), timeout=15,
                      follow_redirects=False, trust_env=False) as client:
        with client.stream(method, url, **kwargs) as response:
            response.raise_for_status()
            body = bytearray()
            for chunk in response.iter_bytes():
                body.extend(chunk)
                if len(body) > 1048576:
                    raise ValueError('Resposta SSO excede o limite.')
            import json
            return json.loads(body)


def discovery(issuer):
    data = provider_request('GET', issuer.rstrip('/') + '/.well-known/openid-configuration')
    if data.get('issuer') != issuer or 'S256' not in data.get('code_challenge_methods_supported', []):
        raise ValueError('Provedor deve corresponder ao issuer e suportar PKCE S256.')
    for key in ('authorization_endpoint', 'token_endpoint', 'jwks_uri'):
        validate_service_url(data[key])
    return data


def start():
    issuer, client, callback = settings()
    data = discovery(issuer)
    handle, state, nonce, verifier = (secrets.token_urlsafe(32) for _ in range(4))
    now = time.monotonic()
    with _lock:
        for key in list(_flows):
            if _flows[key]['expires'] <= now:
                del _flows[key]
        if len(_flows) >= 256:
            raise PermissionError('Muitos logins SSO em andamento. Aguarde.')
        _flows[hashlib.sha256(handle.encode()).hexdigest()] = {
            'state': state, 'nonce': nonce, 'verifier': verifier, 'provider': data,
            'expires': now + 600, 'created': time.time(), 'identity': None, 'consumed': False,
            'issuer': issuer, 'client': client, 'callback': callback}
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode()
    query = urlencode({'client_id': client, 'redirect_uri': callback, 'response_type': 'code',
        'scope': 'openid', 'state': state, 'nonce': nonce, 'code_challenge': challenge,
        'code_challenge_method': 'S256', 'max_age': '300', 'prompt': 'login'})
    return {'handle': handle, 'authorization_url': data['authorization_endpoint'] + '?' + query}


def validate_token(encoded, flow, keys):
    if not isinstance(encoded, str) or len(encoded) > 32768:
        raise ValueError('Token SSO inválido.')
    token = jwt.decode(encoded, KeySet.import_key_set(keys), algorithms=['RS256', 'ES256'])
    jwt.JWTClaimsRegistry(leeway=30, iss={'essential': True, 'value': flow['issuer']},
        aud={'essential': True, 'value': flow['client']}, nonce={'essential': True, 'value': flow['nonce']},
        exp={'essential': True}, iat={'essential': True}, sub={'essential': True},
        auth_time={'essential': True}).validate(token.claims)
    claims = token.claims
    if not isinstance(claims['sub'], str) or len(claims['sub']) > 255:
        raise ValueError('Identidade SSO inválida.')
    if claims.get('azp', flow['client']) != flow['client']:
        raise ValueError('Cliente autorizado inválido.')
    if isinstance(claims['aud'], list) and len(claims['aud']) > 1 and claims.get('azp') != flow['client']:
        raise ValueError('Cliente autorizado ausente.')
    if not isinstance(claims['auth_time'], (int, float)) or not time.time() - 330 <= claims['auth_time'] <= time.time() + 30:
        raise ValueError('Autenticação SSO não é recente.')
    return (claims['iss'], claims['sub'], claims['exp'])


def callback(code, state):
    if not code or len(code) > 8192 or not state or len(state) > 128:
        raise ValueError('Retorno SSO inválido.')
    with _lock:
        flow = next((row for row in _flows.values() if secrets.compare_digest(row['state'], state)), None)
        if not flow or flow['expires'] <= time.monotonic() or flow['consumed']:
            raise PermissionError('Login SSO expirado ou já utilizado.')
        flow['consumed'] = True
    data = {'grant_type': 'authorization_code', 'code': code, 'redirect_uri': flow['callback'],
            'client_id': flow['client'], 'code_verifier': flow['verifier']}
    secret = os.environ.get('NEXLIFY_OIDC_CLIENT_SECRET')
    if secret:
        data['client_secret'] = secret
    try:
        tokens = provider_request('POST', flow['provider']['token_endpoint'], data=data)
        keys = provider_request('GET', flow['provider']['jwks_uri'])
        identity = validate_token(tokens['id_token'], flow, keys)
    except (httpx.HTTPError, JoseError, ValueError, KeyError, TypeError):
        raise PermissionError('Não foi possível validar o login SSO. Inicie novamente.') from None
    with _lock:
        flow['identity'] = identity
        flow['expires'] = min(flow['expires'], time.monotonic() + max(0, identity[2] - time.time()))


def poll(handle, otp=''):
    if not isinstance(handle, str) or len(handle) > 128:
        raise PermissionError('Login SSO inválido.')
    key = hashlib.sha256(handle.encode()).hexdigest()
    with _lock:
        flow = _flows.get(key)
        if not flow or flow['expires'] <= time.monotonic():
            raise PermissionError('Login SSO expirado.')
        if not flow['identity']:
            return {'pending': True}
    issuer, subject, _expiry = flow['identity']
    denied = False
    with DatabaseManager.get_engine().begin() as connection:
        auth.lock_authentication_transaction(connection)
        username = connection.execute(select(external_identities.c.login_usuario).where(
            external_identities.c.issuer == issuer, external_identities.c.subject == subject)).scalar_one_or_none()
        user = connection.execute(auth.locked_users_query().where(usuarios.c.login_usuario == username)).mappings().first()
        if not user or user['tipo_acesso'] not in ROLES or auth.is_legacy_hash(user['senha_criptografada']):
            raise PermissionError('Identidade não vinculada a uma conta ativa.')
        status = auth._state(connection, username)
        if status['locked_until'] and status['locked_until'] > auth.utcnow():
            raise PermissionError('Conta temporariamente bloqueada.')
        security = mfa.state(connection, username)
        with _lock:
            if key not in _flows or flow['expires'] <= time.monotonic():
                raise PermissionError('Login SSO expirado ou já utilizado.')
        # Account lock serializes attempts without holding the global flow lock during SMTP.
        if not otp:
            challenge = mfa.challenge(connection, username, 'sso', security)
            if challenge:
                return challenge
        with _lock:
            if key not in _flows or flow['expires'] <= time.monotonic():
                raise PermissionError('Login SSO expirado ou já utilizado.')
            del _flows[key]
        setup = mfa.needs_setup(connection, username, user['tipo_acesso'], security)
        if not mfa.consume(connection, username, otp, security, purpose='sso'):
            from datetime import timedelta
            attempts = (0 if status['locked_until'] else status['failed_attempts']) + 1
            until = auth.utcnow() + timedelta(seconds=config.LOGIN_LOCK_SECONDS) if attempts >= config.MAX_LOGIN_ATTEMPTS else None
            connection.execute(update(auth_state).where(auth_state.c.login_usuario == username).values(failed_attempts=attempts, locked_until=until))
            if until:
                auth.revoke_account_sessions(connection, username)
            denied = True
        else:
            connection.execute(update(auth_state).where(auth_state.c.login_usuario == username).values(failed_attempts=0, locked_until=None))
            audit.record(connection, username, 'Sessão iniciada por SSO.')
    if denied:
        raise PermissionError('Código MFA inválido. Inicie novamente.')
    now = time.monotonic()
    session = {'username': username, 'name': user['nome_completo'], 'access_level': user['tipo_acesso'],
        'must_change_password': bool(status['must_change']),
        'must_setup_mfa': setup, 'mfa_available': config.MFA_ENABLED, '_mfa_policy': config.MFA_ENABLED,
        '_credential_hash': user['senha_criptografada'], '_security_version': security['security_version'],
        '_created_at': now, '_last_activity': now, '_reauthenticated_at': now}
    auth._session.set(session)
    return {'token': sessions.issue(), 'user': {key: value for key, value in session.items() if not key.startswith('_')}}
