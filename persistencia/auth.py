"""Autenticação local, limitação persistente de tentativas e autorização."""
from contextvars import ContextVar
from contextlib import nullcontext
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import logging
import time
import bcrypt
from sqlalchemy import select, update, insert, func
from sqlalchemy.exc import SQLAlchemyError
import config
from .database import DatabaseManager
from .schema import usuarios, auth_state, log_alteracoes, user_security, ROLES
from .legacy_hashes import LEGACY_HASH_DIGESTS
from . import passwords, mfa, audit
from .access_policy import ADMIN, WRITERS, PAGE_RULES, PageAccessDenied, can_access_page, can_access_table

_session = ContextVar('nexlify_session', default=None)
_dummy_hash = passwords.HASHER.hash('nexlify invalid account timing')
logger = logging.getLogger('authentication')


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def password_validation_error(password, confirmation=None):
    if not isinstance(password, str):
        return 'Informe uma senha em texto.'
    if confirmation is not None and password != confirmation:
        return 'A senha e a confirmação não coincidem.'
    if len(password) < 15:
        return 'Use uma frase-senha com pelo menos 15 caracteres.'
    try:
        encoded = password.encode('utf-8')
    except UnicodeError:
        return 'A senha contém caracteres inválidos.'
    if len(encoded) > 1024:
        return 'A senha deve ter no máximo 1024 bytes UTF-8.'
    if len(set(password)) < 5 or password.casefold() in {'admin1234567890!', 'password123456789', '123456789012345'}:
        return 'Escolha uma frase-senha menos previsível.'
    return None


def hash_password(password):
    error = password_validation_error(password)
    if error:
        raise ValueError(error)
    if passwords.compromised(password):
        raise ValueError('Senha encontrada na lista de senhas comprometidas. Escolha outra.')
    return passwords.HASHER.hash(password)


def check_password_hash(password, hashed_password):
    return passwords.verify(password, hashed_password)


def is_legacy_hash(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest() in LEGACY_HASH_DIGESTS


def _state(connection, username):
    row = connection.execute(select(auth_state).where(auth_state.c.login_usuario == username)).mappings().first()
    if row is None:
        connection.execute(insert(auth_state).values(login_usuario=username, failed_attempts=0, must_change=0))
        return {'failed_attempts': 0, 'locked_until': None, 'must_change': 0}
    return row


def lock_authentication_transaction(connection):
    # SQLite ignores SELECT FOR UPDATE. Acquire its writer lock before reading
    # the attempt counter so concurrent processes cannot lose failed attempts.
    if connection.dialect.name == 'sqlite' and not connection.connection.driver_connection.in_transaction:
        connection.exec_driver_sql('BEGIN IMMEDIATE')


def locked_users_query():
    return select(usuarios).with_for_update().with_hint(usuarios, 'WITH (UPDLOCK, ROWLOCK)', dialect_name='mssql')


def verify_user_credentials(username, password, otp=''):
    if config.API_MODE == 'client':
        from services.client import login
        return login(username, password, otp)
    clear_session()
    if not isinstance(username, str) or not isinstance(password, str) or not username or len(username) > 100:
        return None
    try:
        if len(password.encode('utf-8')) > 1024:
            return None
    except UnicodeError:
        return None
    try:
        engine = DatabaseManager.get_engine()
        if engine is None:
            return 'connection_error'
        with engine.begin() as connection:
            lock_authentication_transaction(connection)
            user = connection.execute(locked_users_query().where(usuarios.c.login_usuario == username)).mappings().first()
            if user is None:
                passwords.verify(password, _dummy_hash)
                audit.record(connection, None, 'Falha de autenticação; conta inexistente.')
                return None
            username = user['login_usuario']
            state = _state(connection, username)
            if state['locked_until'] and state['locked_until'] > utcnow():
                return None
            security = mfa.state(connection, username)
            valid = check_password_hash(password, user['senha_criptografada'])
            if valid and not is_legacy_hash(user['senha_criptografada']) and user['tipo_acesso'] in ROLES:
                if not otp:
                    challenge = mfa.challenge(connection, username, 'login', security)
                    if challenge:
                        return challenge
                valid = mfa.consume(connection, username, otp, security)
            if not valid or is_legacy_hash(user['senha_criptografada']) or user['tipo_acesso'] not in ROLES:
                attempts = (0 if state['locked_until'] else state['failed_attempts']) + 1
                lock = utcnow() + timedelta(seconds=config.LOGIN_LOCK_SECONDS) if attempts >= config.MAX_LOGIN_ATTEMPTS else None
                connection.execute(update(auth_state).where(auth_state.c.login_usuario == username).values(failed_attempts=attempts, locked_until=lock))
                if lock:
                    revoke_account_sessions(connection, username)
                audit.record(connection, username, 'Falha de autenticação; contador persistente atualizado.')
                logger.warning('Falha de autenticação; contador persistente atualizado.')
                return None
            connection.execute(update(auth_state).where(auth_state.c.login_usuario == username).values(failed_attempts=0, locked_until=None))
            credential = user['senha_criptografada']
            if passwords.needs_upgrade(credential):
                credential = passwords.HASHER.hash(password)
                connection.execute(update(usuarios).where(usuarios.c.login_usuario == username).values(senha_criptografada=credential))
            audit.record(connection, username, 'Sessão autenticada por senha e segundo fator quando habilitado.')
            result = {'username': username, 'name': user['nome_completo'], 'access_level': user['tipo_acesso'],
                      'must_change_password': bool(state['must_change']), '_credential_hash': credential,
                      '_security_version': security['security_version'],
                      'must_setup_mfa': mfa.needs_setup(connection, username, user['tipo_acesso'], security),
                      'mfa_available': config.MFA_ENABLED, '_mfa_policy': config.MFA_ENABLED,
                      '_reauthenticated_at': time.monotonic(),
                      '_created_at': time.monotonic(), '_last_activity': time.monotonic()}
        _session.set(result)
        logger.info('Sessão autenticada.')
        return {key: value for key, value in result.items() if not key.startswith('_')}
    except SQLAlchemyError:
        logger.error('Falha de acesso ao banco durante autenticação.')
        return 'connection_error'


def clear_session():
    _session.set(None)
    if config.API_MODE == 'client':
        from services.client import logout
        logout()


def _timed_session():
    session = _session.get()
    if not session:
        raise PermissionError('Entre no sistema antes de acessar os dados.')
    now = time.monotonic()
    if now - session['_last_activity'] >= config.SESSION_IDLE_SECONDS or now - session['_created_at'] >= config.SESSION_MAX_SECONDS:
        clear_session()
        raise PermissionError('Sessão expirada. Entre novamente.')
    return session


def touch_session_activity():
    if config.API_MODE == 'client':
        from services.client import activity
        return activity()
    session = _timed_session()
    _session.set(dict(session, _last_activity=time.monotonic()))


def current_session(require_password_change=False, *, connection=None, touch=False, lock=False, allow_mfa_setup=False):
    if config.API_MODE == 'client':
        from services.client import request
        return request('GET', '/session')
    session = _timed_session()
    with nullcontext(connection) if connection is not None else DatabaseManager.get_engine().connect() as active:
        if lock:
            lock_authentication_transaction(active)
        query = locked_users_query() if lock else select(usuarios)
        user = active.execute(query.where(usuarios.c.login_usuario == session['username'])).mappings().first()
        if (not user or not hmac.compare_digest(user['senha_criptografada'], session['_credential_hash'])
                or user['tipo_acesso'] != session['access_level'] or user['tipo_acesso'] not in ROLES):
            clear_session()
            raise PermissionError('Sessão revogada. Entre novamente.')
        state = active.execute(select(auth_state.c.must_change).where(auth_state.c.login_usuario == session['username'])).scalar()
        if state is None:
            clear_session()
            raise PermissionError('Sessão revogada. Entre novamente.')
        security = mfa.state(active, session['username'])
        if security['security_version'] != session.get('_security_version', 0) or session.get('_mfa_policy', False) != config.MFA_ENABLED:
            clear_session()
            raise PermissionError('Sessão revogada. Entre novamente.')
        if mfa.needs_setup(active, session['username'], session['access_level'], security) and not allow_mfa_setup:
            raise PermissionError('Habilite MFA antes de acessar os dados.')
        if state and not require_password_change:
            raise PermissionError('Troque a senha temporária antes de continuar.')
        if touch:
            session = dict(session, _last_activity=time.monotonic())
            _session.set(session)
    return session


def page_session():
    """Também valida o modo sem login; nunca confia no perfil informado pela UI."""
    if not config.USE_LOGIN:
        config.validate()
        require_dev_mode()
        return {'username': None, 'access_level': ADMIN}
    return current_session(touch=True)


def authorize_page(page, *, project_root=None):
    from utils.installation_profile import load_installation_profile
    from utils.paths import PROJECT_ROOT
    if config.API_MODE == 'client':
        from services.client import request
        session = request('POST', '/pages/authorize', {'page': page})
    else:
        session = page_session()
    if not can_access_page(session['access_level'], page,
                           profile_id=load_installation_profile(project_root or PROJECT_ROOT)['id'],
                           environment=config.ENVIRONMENT, api_mode=config.API_MODE):
        raise PageAccessDenied('Seu perfil não permite acessar esta página nesta instalação.')
    return {'username': session['username'], 'access_level': session['access_level'],
            'read_only': session['access_level'] in PAGE_RULES[page].read_only_roles}


def authorize(table_name, write=False, *, connection=None):
    if table_name not in {'usuarios', 'vegetais', 'tipos_vegetais', 'especie_gatos', 'log_alteracoes'}:
        raise PermissionError('Tabela não autorizada.')
    if not config.USE_LOGIN:
        config.validate()
        if config.ENVIRONMENT == 'development':
            require_dev_mode()
            session = {'username': None, 'access_level': ADMIN}
        else:
            raise PermissionError('Login obrigatório.')
    else:
        session = current_session(connection=connection, touch=True, lock=write and connection is not None)
    role = session['access_level']
    if table_name == 'usuarios' and role != ADMIN:
        raise PermissionError('Somente o Administrador Global pode gerenciar usuários.')
    if not can_access_table(role, table_name, write=write):
        raise PermissionError('Seu perfil não permite esta operação nesta página.')
    if table_name == 'usuarios' and write and config.USE_LOGIN:
        require_recent_auth(session)
    return session


def bootstrap_admin(password):
    hashed = hash_password(password)
    with DatabaseManager.get_engine().begin() as connection:
        lock_authentication_transaction(connection)
        if connection.execute(select(func.count()).select_from(usuarios)).scalar_one():
            raise PermissionError('A criação inicial só está disponível em um banco sem usuários.')
        connection.execute(insert(usuarios).values(login_usuario='admin', senha_criptografada=hashed,
                           nome_completo='Administrador', tipo_acesso=ADMIN))
        connection.execute(insert(auth_state).values(login_usuario='admin', failed_attempts=0, must_change=0))
        audit.record(connection, 'admin', 'Administrador inicial criado.')


def require_dev_mode():
    from utils.installation_profile import load_installation_profile
    from utils.paths import PROJECT_ROOT
    if config.ENVIRONMENT != 'development' or load_installation_profile(PROJECT_ROOT)['id'] != 'dev':
        raise PermissionError('Ferramenta exclusiva do perfil Desenvolvimento com environment = development.')


def reset_admin_password(password):
    require_dev_mode()
    hashed = hash_password(password)
    with DatabaseManager.get_engine().begin() as connection:
        lock_authentication_transaction(connection)
        user = connection.execute(locked_users_query().where(usuarios.c.login_usuario == 'admin')).mappings().first()
        if not user or user['tipo_acesso'] != ADMIN:
            raise ValueError('Administrador admin não encontrado. Use a criação inicial para bancos vazios.')
        if check_password_hash(password, user['senha_criptografada']):
            raise ValueError('Escolha uma senha diferente da atual.')
        _state(connection, 'admin')
        connection.execute(update(usuarios).where(usuarios.c.login_usuario == 'admin').values(senha_criptografada=hashed))
        connection.execute(update(auth_state).where(auth_state.c.login_usuario == 'admin').values(failed_attempts=0, locked_until=None, must_change=1))
        audit.record(connection, 'admin', 'Senha administrativa redefinida pela ferramenta local de desenvolvimento.')
    clear_session()


def change_own_password(old_password, new_password):
    if config.API_MODE == 'client':
        from services.client import request
        request('POST', '/password', {'old_password': old_password, 'new_password': new_password})
        clear_session()
        return
    session = current_session(require_password_change=True, allow_mfa_setup=True)
    if old_password == new_password:
        raise ValueError('Escolha uma senha diferente da atual.')
    validation = password_validation_error(new_password)
    if validation:
        raise ValueError(validation)
    username = session['username']
    denied = False
    with DatabaseManager.get_engine().begin() as connection:
        current_session(require_password_change=True, allow_mfa_setup=True, connection=connection, lock=True)
        state = _state(connection, username)
        if state['locked_until'] and state['locked_until'] > utcnow():
            clear_session()
            raise PermissionError('Conta temporariamente bloqueada. Aguarde antes de entrar novamente.')
        if not check_password_hash(old_password, session['_credential_hash']):
            attempts = (0 if state['locked_until'] else state['failed_attempts']) + 1
            until = utcnow() + timedelta(seconds=config.LOGIN_LOCK_SECONDS) if attempts >= config.MAX_LOGIN_ATTEMPTS else None
            connection.execute(update(auth_state).where(auth_state.c.login_usuario == username).values(failed_attempts=attempts, locked_until=until))
            if until:
                revoke_account_sessions(connection, session['username'])
                clear_session()
            denied = True
        else:
            hashed = hash_password(new_password)
            connection.execute(update(usuarios).where(usuarios.c.login_usuario == username).values(senha_criptografada=hashed))
            connection.execute(update(auth_state).where(auth_state.c.login_usuario == username).values(must_change=0, failed_attempts=0, locked_until=None))
            audit.record(connection, username, 'Senha alterada pelo titular.')
    if denied:
        raise ValueError('Senha atual incorreta ou limite de tentativas atingido.')
    clear_session()


def require_recent_auth(session=None):
    if config.API_MODE == 'client':
        from services.client import request
        request('GET', '/reauth/status')
        return
    session = session or current_session(allow_mfa_setup=True)
    if time.monotonic() - session.get('_reauthenticated_at', 0) > config.REAUTH_SECONDS:
        raise PermissionError('Confirme sua identidade antes da operação administrativa.')


def reauthenticate(password, otp=''):
    if config.API_MODE == 'client':
        from services.client import request
        return request('POST', '/reauth', {'password': password, 'otp': otp})
    session = current_session(require_password_change=True, allow_mfa_setup=True)
    denied = False
    with DatabaseManager.get_engine().begin() as connection:
        current_session(require_password_change=True, allow_mfa_setup=True, connection=connection, lock=True)
        state = _state(connection, session['username'])
        if state['locked_until'] and state['locked_until'] > utcnow():
            clear_session()
            raise PermissionError('Conta temporariamente bloqueada.')
        valid = check_password_hash(password, session['_credential_hash'])
        if valid:
            if not otp:
                challenge = mfa.challenge(connection, session['username'], 'reauth')
                if challenge:
                    return challenge
            valid = mfa.consume(connection, session['username'], otp, purpose='reauth')
        if not valid:
            attempts = (0 if state['locked_until'] else state['failed_attempts']) + 1
            until = utcnow() + timedelta(seconds=config.LOGIN_LOCK_SECONDS) if attempts >= config.MAX_LOGIN_ATTEMPTS else None
            connection.execute(update(auth_state).where(auth_state.c.login_usuario == session['username']).values(failed_attempts=attempts, locked_until=until))
            if until:
                revoke_account_sessions(connection, session['username'])
                clear_session()
            denied = True
        else:
            connection.execute(update(auth_state).where(auth_state.c.login_usuario == session['username']).values(failed_attempts=0, locked_until=None))
    if denied:
        raise PermissionError('Credenciais de confirmação inválidas.')
    _session.set(dict(session, _reauthenticated_at=time.monotonic(), _last_activity=time.monotonic()))


def prepare_user_password(password):
    if config.API_MODE == 'client':
        error = password_validation_error(password)
        if error:
            raise ValueError(error)
        return {'password': password}
    return {'senha_criptografada': hash_password(password)}


def revoke_account_sessions(connection, username):
    mfa.state(connection, username)
    connection.execute(update(user_security).where(user_security.c.login_usuario == username).values(
        security_version=user_security.c.security_version + 1))
