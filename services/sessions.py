"""Opaque API tokens, stored only as digests; expiry shared across workers."""
import hashlib
import hmac
import secrets
import time
from datetime import timedelta
from sqlalchemy import select, insert, update, delete
from persistencia import auth, mfa
from persistencia.database import DatabaseManager
from persistencia.schema import api_sessions, usuarios
import config


def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def credential_digest(value):
    return digest(value + '|email-mfa-v1:' + str(config.MFA_ENABLED))


def issue():
    session = auth._session.get()
    token = secrets.token_urlsafe(32)
    now = auth.utcnow()
    with DatabaseManager.get_engine().begin() as connection:
        connection.execute(delete(api_sessions).where(api_sessions.c.created_at < now - timedelta(seconds=config.SESSION_MAX_SECONDS)))
        connection.execute(insert(api_sessions).values(token_hash=digest(token), login_usuario=session['username'],
            credential_digest=credential_digest(session['_credential_hash']), access_level=session['access_level'],
            security_version=session['_security_version'], created_at=now, last_activity=now, reauthenticated_at=now))
    return token


def load(token):
    if not token or len(token) > 128:
        raise PermissionError('Sessão inválida.')
    now = auth.utcnow()
    with DatabaseManager.get_engine().begin() as connection:
        row = connection.execute(select(api_sessions).where(api_sessions.c.token_hash == digest(token))).mappings().first()
        if (not row or (now-row['created_at']).total_seconds() >= config.SESSION_MAX_SECONDS
                or (now-row['last_activity']).total_seconds() >= config.SESSION_IDLE_SECONDS):
            raise PermissionError('Sessão expirada. Entre novamente.')
        user = connection.execute(select(usuarios).where(usuarios.c.login_usuario == row['login_usuario'])).mappings().first()
        security = mfa.state(connection, row['login_usuario']) if user else None
        if (not user or not hmac.compare_digest(credential_digest(user['senha_criptografada']), row['credential_digest'])
                or user['tipo_acesso'] != row['access_level'] or security['security_version'] != row['security_version']):
            connection.execute(delete(api_sessions).where(api_sessions.c.token_hash == digest(token)))
            raise PermissionError('Sessão revogada. Entre novamente.')
        state = auth._state(connection, row['login_usuario'])
        setup = mfa.needs_setup(connection, row['login_usuario'], user['tipo_acesso'], security)
    current = time.monotonic()
    auth._session.set({'username': user['login_usuario'], 'name': user['nome_completo'], 'access_level': user['tipo_acesso'],
        'must_change_password': bool(state['must_change']),
        'must_setup_mfa': setup, 'mfa_available': config.MFA_ENABLED, '_mfa_policy': config.MFA_ENABLED,
        '_credential_hash': user['senha_criptografada'], '_security_version': security['security_version'],
        '_created_at': current - (now-row['created_at']).total_seconds(),
        '_last_activity': current - (now-row['last_activity']).total_seconds(),
        '_reauthenticated_at': current - (now-row['reauthenticated_at']).total_seconds()})


def refresh(token, active=False):
    session = auth._session.get()
    if session is None:
        revoke(token)
        return
    now = auth.utcnow()
    values = {'reauthenticated_at': now - timedelta(seconds=time.monotonic()-session['_reauthenticated_at'])}
    if active:
        values['last_activity'] = now
    with DatabaseManager.get_engine().begin() as connection:
        connection.execute(update(api_sessions).where(api_sessions.c.token_hash == digest(token)).values(**values))


def revoke(token):
    if token:
        with DatabaseManager.get_engine().begin() as connection:
            connection.execute(delete(api_sessions).where(api_sessions.c.token_hash == digest(token)))
