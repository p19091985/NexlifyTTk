"""Optional email verification: short-lived, purpose-bound, single-use codes."""
import hashlib
import hmac
import json
import secrets
from datetime import timedelta
from sqlalchemy import insert, select, update, delete
import config
from .schema import user_security, auth_state, email_mfa
from .security import load_key, load_keys
from services.email_delivery import send_code, validate_address


def state(connection, username):
    row = connection.execute(select(user_security).where(user_security.c.login_usuario == username)).mappings().first()
    if row is None:
        connection.execute(insert(user_security).values(login_usuario=username, mfa_enabled=0, last_counter=-1, security_version=0))
        return {'mfa_enabled': 0, 'mfa_secret': None, 'pending_secret': None, 'pending_until': None,
                'last_counter': -1, 'recovery_hashes': None, 'security_version': 0}
    return row


def email_state(connection, username):
    return connection.execute(select(email_mfa).where(email_mfa.c.login_usuario == username)).mappings().first()


def active(connection, username, row=None):
    row = row if row is not None else state(connection, username)
    email = email_state(connection, username) if config.MFA_ENABLED and row['mfa_enabled'] else None
    return bool(email and email['email'])


def needs_setup(connection, username, role, row=None):
    from .auth import ADMIN
    row = row if row is not None else state(connection, username)
    return bool(config.MFA_ENABLED and not active(connection, username, row)
                and (row['mfa_enabled'] or (config.ENVIRONMENT == 'production' and role == ADMIN)))


def challenge(connection, username, purpose, row=None):
    row = row if row is not None else state(connection, username)
    if not config.MFA_ENABLED or not row['mfa_enabled']:
        return None
    if active(connection, username, row):
        try:
            return issue(connection, username, purpose)
        except (ConnectionError, ValueError):
            # Keep recovery entry available without authenticating when SMTP is down.
            return {'mfa_required': True, 'delivery': 'unavailable'}
    # A legacy TOTP enrollment requires its existing recovery code before conversion.
    return {'mfa_required': True, 'delivery': 'recovery'}


def _digest(key, username, purpose, nonce, code):
    payload = json.dumps(['email-mfa-v1', username, purpose, nonce, code], ensure_ascii=True).encode()
    return hmac.new(key, payload, hashlib.sha256).hexdigest()


def issue(connection, username, purpose, address=None):
    from .auth import utcnow
    if not config.MFA_ENABLED:
        raise PermissionError('MFA está desabilitado nesta instalação.')
    if purpose not in {'enroll', 'login', 'reauth', 'sso'}:
        raise ValueError('Finalidade MFA inválida.')
    row = email_state(connection, username)
    address = validate_address(address if purpose == 'enroll' else (row['email'] if row else ''))
    now = utcnow()
    result = {'mfa_required': True, 'delivery': 'email', 'masked_email': address[0] + '***@' + address.rsplit('@', 1)[1]}
    if row and row['sent_at'] and (now-row['sent_at']).total_seconds() < 60:
        same = row['purpose'] == purpose and (purpose != 'enroll' or row['pending_email'] == address)
        if same and row['code_digest'] and row['code_until'] and row['code_until'] > now:
            return result
        raise ValueError('Aguarde 60 segundos entre envios de códigos por e-mail.')
    code, nonce = f'{secrets.randbelow(1000000):06d}', secrets.token_hex(16)
    values = dict(code_digest=_digest(load_key(create=True), username, purpose, nonce, code),
                  nonce=nonce, code_until=now+timedelta(minutes=5), purpose=purpose, sent_at=now,
                  pending_email=address if purpose == 'enroll' else None)
    # Do not replace a previous challenge if delivery fails.
    send_code(address, code)
    if row:
        connection.execute(update(email_mfa).where(email_mfa.c.login_usuario == username).values(**values))
    else:
        connection.execute(insert(email_mfa).values(login_usuario=username, **values))
    # Caller owns the account lock and transaction.
    return result


def _consume_code(connection, username, code, purpose):
    from .auth import utcnow
    row = email_state(connection, username)
    if (not isinstance(code, str) or len(code) != 6 or not code.isascii() or not code.isdigit()
            or not row or row['purpose'] != purpose or not row['code_digest']
            or not row['code_until'] or row['code_until'] <= utcnow()):
        return False
    valid = any(hmac.compare_digest(_digest(key, username, purpose, row['nonce'], code), row['code_digest'])
                for key in load_keys())
    if valid:
        connection.execute(update(email_mfa).where(email_mfa.c.login_usuario == username).values(
            code_digest=None, code_until=None, nonce=None, purpose=None))
    return valid


def consume(connection, username, code, row=None, *, purpose='login'):
    row = row if row is not None else state(connection, username)
    if not config.MFA_ENABLED or not row['mfa_enabled']:
        return True
    if not isinstance(code, str) or len(code) > 100:
        return False
    if _consume_code(connection, username, code, purpose):
        return True
    hashes = json.loads(row['recovery_hashes'] or '[]')
    digest = hashlib.sha256(code.encode('utf-8')).hexdigest()
    if digest in hashes:
        hashes.remove(digest)
        connection.execute(update(user_security).where(user_security.c.login_usuario == username).values(recovery_hashes=json.dumps(hashes)))
        connection.execute(update(email_mfa).where(email_mfa.c.login_usuario == username).values(
            code_digest=None, code_until=None, nonce=None, purpose=None))
        return True
    return False


def begin_enrollment(email):
    from . import auth
    from .database import DatabaseManager
    if config.API_MODE == 'client':
        from services.client import request
        return request('POST', '/mfa/enroll', {'email': email})
    if not config.MFA_ENABLED:
        raise PermissionError('MFA está desabilitado nesta instalação.')
    email = validate_address(email)
    with DatabaseManager.get_engine().begin() as connection:
        session = auth.current_session(allow_mfa_setup=True, connection=connection, lock=True)
        auth.require_recent_auth(session)
        if active(connection, session['username']):
            raise ValueError('MFA já habilitado. Desabilite com reautenticação antes de substituir.')
        return issue(connection, session['username'], 'enroll', email)


def confirm_enrollment(code):
    from . import auth, audit
    from .database import DatabaseManager
    if config.API_MODE == 'client':
        from services.client import request
        result = request('POST', '/mfa/confirm', {'code': code})
        auth.clear_session()
        return result['recovery_codes']
    if not config.MFA_ENABLED:
        raise PermissionError('MFA está desabilitado nesta instalação.')
    with DatabaseManager.get_engine().begin() as connection:
        session = auth.current_session(allow_mfa_setup=True, connection=connection, lock=True)
        auth.require_recent_auth(session)
        username = session['username']
        attempts_state = auth._state(connection, username)
        if attempts_state['locked_until'] and attempts_state['locked_until'] > auth.utcnow():
            raise PermissionError('Conta temporariamente bloqueada.')
        row, pending = state(connection, username), email_state(connection, username)
        if not pending or not pending['pending_email'] or pending['purpose'] != 'enroll':
            raise ValueError('Solicite um código de cadastro por e-mail.')
        denied = not _consume_code(connection, username, code, 'enroll')
        if denied:
            attempts = (0 if attempts_state['locked_until'] else attempts_state['failed_attempts']) + 1
            until = auth.utcnow() + timedelta(seconds=config.LOGIN_LOCK_SECONDS) if attempts >= config.MAX_LOGIN_ATTEMPTS else None
            connection.execute(update(auth_state).where(auth_state.c.login_usuario == username).values(failed_attempts=attempts, locked_until=until))
            if until:
                auth.revoke_account_sessions(connection, username)
                auth.clear_session()
        else:
            codes = [secrets.token_urlsafe(18) for _ in range(8)]
            connection.execute(update(user_security).where(user_security.c.login_usuario == username).values(
                mfa_secret=None, mfa_enabled=1, pending_secret=None, pending_until=None,
                last_counter=-1, security_version=row['security_version'] + 1,
                recovery_hashes=json.dumps([hashlib.sha256(item.encode()).hexdigest() for item in codes])))
            connection.execute(update(email_mfa).where(email_mfa.c.login_usuario == username).values(
                email=pending['pending_email'], pending_email=None, sent_at=None))
            connection.execute(update(auth_state).where(auth_state.c.login_usuario == username).values(failed_attempts=0, locked_until=None))
            audit.record(connection, username, 'MFA por e-mail habilitado; sessões anteriores revogadas.')
    if denied:
        raise ValueError('Código MFA inválido ou expirado.')
    auth.clear_session()
    return codes


def disable():
    from . import auth, audit
    from .database import DatabaseManager
    if config.API_MODE == 'client':
        from services.client import request
        request('POST', '/mfa/disable', {})
        auth.clear_session()
        return
    with DatabaseManager.get_engine().begin() as connection:
        session = auth.current_session(connection=connection, lock=True)
        auth.require_recent_auth(session)
        if config.MFA_ENABLED and config.ENVIRONMENT == 'production' and session['access_level'] == auth.ADMIN:
            raise PermissionError('Com MFA ativo na instalação, administradores em produção devem mantê-lo habilitado.')
        row = state(connection, session['username'])
        connection.execute(update(user_security).where(user_security.c.login_usuario == session['username']).values(
            mfa_enabled=0, mfa_secret=None, recovery_hashes=None, pending_secret=None, pending_until=None,
            security_version=row['security_version'] + 1))
        connection.execute(delete(email_mfa).where(email_mfa.c.login_usuario == session['username']))
        audit.record(connection, session['username'], 'MFA desabilitado pelo titular.')
    auth.clear_session()
