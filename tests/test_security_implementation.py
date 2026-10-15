import hashlib
import hmac
import json
import os
import sqlite3
import time
import uuid
from datetime import timedelta
from pathlib import Path
import bcrypt
import httpx
import pytest
from sqlalchemy import select, update, insert, func
import config
from persistencia import auth, mfa, passwords, security, audit
from persistencia.schema import usuarios, auth_state, user_security, api_sessions, audit_outbox, external_identities
from persistencia.database import DatabaseManager
PASSWORD = 'Teste seguro do template 2026!'


@pytest.fixture
def private_keys(tmp_path, monkeypatch):
    monkeypatch.delenv('NEXLIFY_SECRET_KEY', raising=False)
    monkeypatch.setattr(security, 'KEY_PATH', tmp_path / '.secrets' / 'secret.key')


def test_argon_upgrade_preserves_account_and_revokes_old_session(administrator):
    legacy = bcrypt.hashpw(PASSWORD.encode(), bcrypt.gensalt(12)).decode()
    with administrator.begin() as conn:
        conn.execute(update(usuarios).values(senha_criptografada=legacy))
    assert auth.verify_user_credentials('admin', PASSWORD)
    with administrator.connect() as conn:
        upgraded = conn.execute(select(usuarios.c.senha_criptografada)).scalar_one()
    assert upgraded.startswith('$argon2id$')
    assert passwords.verify(PASSWORD, upgraded)
    assert not passwords.needs_upgrade(upgraded)
    assert passwords.verify('Uma frase bastante longa com acentos çã é! ' * 5,
                            auth.hash_password('Uma frase bastante longa com acentos çã é! ' * 5))


def test_hibp_only_prefix_and_fails_closed(monkeypatch):
    monkeypatch.setattr(config, 'PASSWORD_BREACH_MODE', 'hibp')
    digest = hashlib.sha1(PASSWORD.encode(), usedforsecurity=False).hexdigest().upper()
    calls = []
    def get(url, **kwargs):
        calls.append((url, kwargs))
        return httpx.Response(200, text=digest[5:] + ':42\r\n', request=httpx.Request('GET', url))
    monkeypatch.setattr(httpx, 'get', get)
    with pytest.raises(ValueError, match='comprometidas'):
        auth.hash_password(PASSWORD)
    assert calls[0][0].endswith('/' + digest[:5])
    assert PASSWORD not in str(calls) and digest[5:] not in str(calls)
    assert calls[0][1]['headers']['Add-Padding'] == 'true'
    monkeypatch.setattr(httpx, 'get', lambda *a, **k: (_ for _ in ()).throw(httpx.ConnectError('offline')))
    with pytest.raises(ValueError):
        auth.hash_password(PASSWORD)


def test_mfa_enrollment_replay_recovery_and_production_gate(administrator, email_enabled, monkeypatch):
    original_session = auth._session.get()
    monkeypatch.setattr(config, 'ENVIRONMENT', 'production')
    with pytest.raises(PermissionError, match='MFA'):
        auth.authorize('vegetais')
    mfa.begin_enrollment('admin@example.org')
    enrollment_code = email_enabled[-1][1]
    codes = mfa.confirm_enrollment(enrollment_code)
    assert len(codes) == 8 and len(set(codes)) == 8
    auth._session.set(original_session)
    with pytest.raises(PermissionError, match='revogada'):
        auth.current_session()
    assert auth.verify_user_credentials('admin', PASSWORD, enrollment_code) is None
    assert auth.verify_user_credentials('admin', PASSWORD, codes[0])
    assert auth.authorize('vegetais')
    with pytest.raises(PermissionError):
        mfa.disable()
    assert auth.verify_user_credentials('admin', PASSWORD, codes[0]) is None
    assert auth.verify_user_credentials('admin', PASSWORD, codes[1])
    with administrator.connect() as conn:
        row = conn.execute(select(user_security)).mappings().one()
        assert row['mfa_secret'] is None
        assert codes[0] not in row['recovery_hashes']


def test_mfa_enrollment_failures_persist(administrator, email_enabled):
    mfa.begin_enrollment('admin@example.org')
    for _ in range(5):
        with pytest.raises(ValueError):
            mfa.confirm_enrollment('wrong')
    assert auth._session.get() is None
    with administrator.connect() as conn:
        state = conn.execute(select(auth_state)).mappings().one()
        assert state['failed_attempts'] == 5 and state['locked_until'] > auth.utcnow()


def test_admin_reauth_is_required(administrator):
    session = auth._session.get()
    auth._session.set(dict(session, _reauthenticated_at=time.monotonic() - 301))
    with pytest.raises(PermissionError, match='Confirme'):
        auth.authorize('usuarios', write=True)
    auth.reauthenticate(PASSWORD)
    assert auth.authorize('usuarios', write=True)


@pytest.fixture
def api(administrator, monkeypatch):
    from fastapi.testclient import TestClient
    from services.api import app, _limits
    monkeypatch.setattr(config, 'API_MODE', 'server')
    _limits.clear()
    with TestClient(app, base_url='https://testserver') as client:
        yield client


def call(api, method, params=None, token=None):
    return api.post('/rpc', json={'method': method, 'params': params or {}},
                    headers={'Authorization': 'Bearer ' + token} if token else {})


def login(api):
    response = call(api, 'login', {'username': 'admin', 'password': PASSWORD})
    assert response.status_code == 200, response.text
    return response.json()['token']


def test_api_boundary_tokens_privileges_hashes_and_revocation(api, administrator):
    assert call(api, 'read', {'table': 'usuarios'}).status_code == 403
    token = login(api)
    response = call(api, 'read', {'table': 'usuarios'}, token)
    assert response.status_code == 200
    assert 'senha_criptografada' not in response.text
    for field in ('senha_criptografada', 'SENHA_CRIPTOGRAFADA'):
        assert call(api, 'update', {'table': 'usuarios', 'values': {field: 'fake'}, 'where': {'login_usuario': 'admin'}}, token).status_code == 400
    for table in ('api_sessions', 'user_security', 'audit_outbox', 'external_identities', 'email_mfa'):
        assert call(api, 'read', {'table': table}, token).status_code == 400
    with administrator.connect() as conn:
        row = conn.execute(select(api_sessions)).mappings().one()
        assert row['token_hash'] == hashlib.sha256(token.encode()).hexdigest()
        assert token not in str(row)
    assert call(api, 'insert', {'table': 'usuarios', 'rows': [{'login_usuario': 'auditor', 'nome_completo': 'Auditor',
        'tipo_acesso': 'Auditor Externo', 'password': 'Auditor seguro com senha única 2026!'}]}, token).status_code == 200
    other = call(api, 'login', {'username': 'auditor', 'password': 'Auditor seguro com senha única 2026!'}).json()['token']
    assert call(api, 'read', {'table': 'vegetais'}, other).status_code == 403  # temporary password
    assert call(api, 'password', {'old_password': 'Auditor seguro com senha única 2026!', 'new_password': 'Auditor definitivo e seguro 2026!'}, other).status_code == 200
    other = call(api, 'login', {'username': 'auditor', 'password': 'Auditor definitivo e seguro 2026!'}).json()['token']
    assert call(api, 'read', {'table': 'vegetais'}, other).status_code == 200
    assert call(api, 'read', {'table': 'usuarios'}, other).status_code == 403
    assert call(api, 'insert', {'table': 'tipos_vegetais', 'rows': [{'nome': 'forbidden'}]}, other).status_code == 403
    with administrator.begin() as conn:
        conn.execute(update(usuarios).where(usuarios.c.login_usuario == 'admin').values(senha_criptografada=auth.hash_password('Senha alterada fora da sessão 2026!')))
    assert call(api, 'session', token=token).status_code == 403


def test_api_idle_poll_does_not_extend_session_and_reauth(api, administrator):
    token = login(api)
    old = auth.utcnow() - timedelta(seconds=301)
    with administrator.begin() as conn:
        conn.execute(update(api_sessions).values(last_activity=old, reauthenticated_at=old))
    assert call(api, 'session', token=token).status_code == 200
    with administrator.connect() as conn:
        assert conn.execute(select(api_sessions.c.last_activity)).scalar_one() == old
    assert call(api, 'update', {'table': 'usuarios', 'values': {'nome_completo': 'Changed'}, 'where': {'login_usuario': 'admin'}}, token).status_code == 403
    assert call(api, 'reauth', {'password': PASSWORD}, token).status_code == 200
    with administrator.begin() as conn:
        conn.execute(update(api_sessions).values(last_activity=auth.utcnow()-timedelta(seconds=901)))
    assert call(api, 'session', token=token).status_code == 403


def test_api_body_limits_no_error_echo_and_https(api, monkeypatch):
    assert api.post('/rpc', content=b'x' * 65537).status_code == 413
    response = api.post('/rpc', json={'method': 'login', 'params': [], 'password': PASSWORD})
    assert response.status_code == 400 and PASSWORD not in response.text
    monkeypatch.setattr(config, 'ENVIRONMENT', 'production')
    assert api.get('http://testserver/health').status_code == 400


def test_lockout_revokes_existing_api_sessions_even_after_unlock(api, administrator):
    token = login(api)
    for _ in range(5):
        assert call(api, 'login', {'username': 'admin', 'password': 'wrong'}).status_code == 401
    with administrator.begin() as connection:
        connection.execute(update(auth_state).values(locked_until=None, failed_attempts=0))
    assert call(api, 'session', token=token).status_code == 403


def test_client_installer_refuses_folder_with_server_secrets(tmp_path):
    from instalacao.install import install
    (tmp_path/'banco.local.ini').touch()
    with pytest.raises(ValueError, match='pasta limpa'):
        install('core', 'sqlite', root=tmp_path, mode='client', api_url='https://api.example')


def test_client_never_opens_database(monkeypatch):
    monkeypatch.setattr(config, 'API_MODE', 'client')
    with pytest.raises(PermissionError):
        DatabaseManager.get_engine()


def test_outbox_is_atomic_and_collector_refuses_overwrite(administrator, tmp_path):
    from services.audit_receiver import store_event
    with administrator.connect() as conn:
        before = conn.execute(select(func.count()).select_from(audit_outbox)).scalar_one()
    with pytest.raises(RuntimeError):
        with administrator.begin() as conn:
            audit.record(conn, 'admin', 'Must roll back')
            raise RuntimeError()
    with administrator.connect() as conn:
        assert conn.execute(select(func.count()).select_from(audit_outbox)).scalar_one() == before
    event_id = str(uuid.uuid4())
    body = json.dumps({'event_id': event_id, 'action': 'tested'}).encode()
    key = os.urandom(32)
    signature = hmac.new(key, body, hashlib.sha256).hexdigest()
    first = store_event(body, signature, event_id, tmp_path/'remote', key)
    assert store_event(body, signature, event_id, tmp_path/'remote', key) == first
    with pytest.raises(PermissionError):
        store_event(body, 'wrong', event_id, tmp_path/'remote', key)
    altered = body.replace(b'tested', b'changed')
    with pytest.raises(ValueError):
        store_event(altered, hmac.new(key, altered, hashlib.sha256).hexdigest(), event_id, tmp_path/'remote', key)


def test_audit_delivery_receipt_and_retry(administrator, monkeypatch):
    from services import audit_delivery
    monkeypatch.setenv('NEXLIFY_AUDIT_URL', 'https://logs.example/events')
    monkeypatch.setenv('NEXLIFY_AUDIT_KEY', 'random-test-key-with-more-than-32-bytes')
    real_client = httpx.Client
    def transport(request):
        data = json.loads(request.content)
        return httpx.Response(200, json={'event_id': data['event_id'], 'sha256': hashlib.sha256(request.content).hexdigest()})
    monkeypatch.setattr(httpx, 'Client', lambda **kwargs: real_client(transport=httpx.MockTransport(transport)))
    result = audit_delivery.deliver_once()
    assert result['delivered'] > 0 and result['pending'] == 0
    with administrator.begin() as conn:
        audit.record(conn, 'admin', 'retry')
    monkeypatch.setattr(httpx, 'Client', lambda **kwargs: real_client(transport=httpx.MockTransport(lambda r: httpx.Response(503))))
    assert audit_delivery.deliver_once()['pending'] == 1
    with administrator.connect() as conn:
        event = conn.execute(select(audit_outbox).where(audit_outbox.c.delivered_at.is_(None))).mappings().one()
        assert event['attempts'] == 1 and event['next_attempt'] > auth.utcnow()


def test_backup_restore_integrity_and_no_overwrite(administrator, tmp_path):
    from instalacao.backup import create_sqlite_backup, restore_to_new_file
    backup = create_sqlite_backup(Path(administrator.url.database), tmp_path/'backups')
    restored = restore_to_new_file(backup, tmp_path/'restored.db')
    with sqlite3.connect(restored) as conn:
        assert conn.execute('SELECT count(*) FROM usuarios').fetchone()[0] == 1
    with pytest.raises(FileExistsError):
        restore_to_new_file(backup, restored)
    manifest = json.loads(backup.with_suffix('.json').read_text())
    manifest['sha256'] = '0' * 64
    backup.with_suffix('.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match='Checksum'):
        restore_to_new_file(backup, tmp_path/'invalid.db')


def test_rotation_keeps_old_decrypts_and_reencrypts_mfa(administrator, private_keys, tmp_path):
    from instalacao.rotate_key import rotate
    seed = 'legacy-totp-key-for-rotation-test'
    with administrator.begin() as conn:
        mfa.state(conn, 'admin')
        conn.execute(update(user_security).values(pending_secret=security.encrypt_message(seed)))
    old_key = security.load_key()
    old_token = security.encrypt_message('backup credential')
    config_file = tmp_path/'database.ini'
    config_file.write_text('[database]\npassword = ' + old_token, encoding='utf-8')
    assert rotate(config_file)['rotated']
    assert security.load_key() != old_key
    assert security.decrypt_message(old_token) == 'backup credential'
    with administrator.connect() as conn:
        new_token = conn.execute(select(user_security.c.pending_secret)).scalar_one()
    assert security.decrypt_message(new_token) == seed
    with pytest.raises(ValueError):
        security.decrypt_message(new_token, old_key)


def test_package_excludes_secrets_dev_and_has_verifiable_manifest(tmp_path):
    from instalacao.package_release import build, verify
    import zipfile
    package = tmp_path/'client.zip'
    build(package, api_url='https://api.example')
    assert verify(package)
    with zipfile.ZipFile(package) as archive:
        files = archive.namelist()
        assert 'reset_admin.py' not in files and 'banco.local.ini' not in files and 'banco.ini' not in files
        assert 'instalacao/provision.py' not in files
        assert not any('/.venv/' in name or name.startswith('.secrets/') or name.endswith('.db') for name in files)
        assert b'api_mode = client' in archive.read('config_settings.ini')
        assert b'mfa_enabled = False' in archive.read('config_settings.ini')


def test_private_files_native_permissions(tmp_path):
    from utils.secure_files import atomic_write_private
    path = tmp_path/'private.txt'
    atomic_write_private(path, 'not a credential')
    if os.name == 'nt':
        import subprocess
        # Native ACL check; no broad Users or Everyone read grants.
        script = '$a=Get-Acl -LiteralPath $env:NEXLIFY_ACL_TEST; $a.AreAccessRulesProtected; $a.Access | ForEach-Object { $_.IdentityReference.Translate([System.Security.Principal.SecurityIdentifier]).Value }'
        result = subprocess.run(['powershell', '-NoProfile', '-Command', script], env=dict(os.environ, NEXLIFY_ACL_TEST=str(path)), capture_output=True, text=True, check=True)
        assert 'True' in result.stdout
        assert 'S-1-1-0' not in result.stdout and 'S-1-5-32-545' not in result.stdout
    else:
        assert path.stat().st_mode & 0o777 == 0o600


def test_oidc_signature_audience_nonce_and_expiration():
    from joserfc import jwt
    from joserfc.jwk import RSAKey
    from joserfc.errors import JoseError
    from services.sso import validate_token
    key = RSAKey.generate_key(2048)
    key.ensure_kid()
    jwks = {'keys': [key.as_dict(private=False)]}
    now = int(time.time())
    flow = {'issuer': 'https://id.example', 'client': 'nexlify', 'nonce': 'random-nonce'}
    claims = {'iss': flow['issuer'], 'aud': flow['client'], 'nonce': flow['nonce'], 'sub': 'user-subject',
              'iat': now, 'exp': now+300, 'auth_time': now}
    def encode(values):
        return jwt.encode({'alg': 'RS256', 'kid': key.kid}, values, key)
    assert validate_token(encode(claims), flow, jwks) == ('https://id.example', 'user-subject', now+300)
    for replacement in ({'aud': 'attacker'}, {'nonce': 'replay'}, {'exp': now-60}, {'iss': 'https://attacker.example'}, {'auth_time': now-600}, {'azp': 'attacker'}):
        with pytest.raises((ValueError, JoseError)):
            validate_token(encode(dict(claims, **replacement)), flow, jwks)


def test_sso_pkce_single_use_and_explicit_identity_binding(administrator, monkeypatch):
    from services import sso
    from joserfc import jwt
    from joserfc.jwk import RSAKey
    from urllib.parse import urlsplit, parse_qs
    monkeypatch.setenv('NEXLIFY_OIDC_ISSUER', 'https://id.example')
    monkeypatch.setenv('NEXLIFY_OIDC_CLIENT_ID', 'nexlify')
    monkeypatch.setenv('NEXLIFY_OIDC_REDIRECT_URI', 'https://api.example/sso/callback')
    key = RSAKey.generate_key(2048)
    key.ensure_kid()
    data = {'issuer': 'https://id.example', 'authorization_endpoint': 'https://id.example/authorize',
        'token_endpoint': 'https://id.example/token', 'jwks_uri': 'https://id.example/keys', 'code_challenge_methods_supported': ['S256']}
    observed = {}
    def provider(method, url, **kwargs):
        if url.endswith('openid-configuration'):
            return data
        if url.endswith('/keys'):
            return {'keys': [key.as_dict(private=False)]}
        assert kwargs['data']['code'] == 'provider-code'
        import base64
        verifier = kwargs['data']['code_verifier']
        assert base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode() == observed['code_challenge'][0]
        now = int(time.time())
        claims = {'iss': 'https://id.example', 'aud': 'nexlify', 'sub': 'known-subject',
            'nonce': observed['nonce'][0], 'exp': now+300, 'iat': now, 'auth_time': now}
        return {'id_token': jwt.encode({'alg': 'RS256', 'kid': key.kid}, claims, key)}
    monkeypatch.setattr(sso, 'provider_request', provider)
    with administrator.begin() as connection:
        connection.execute(insert(external_identities).values(issuer='https://id.example', subject='known-subject', login_usuario='admin'))
    flow = sso.start()
    observed.update(parse_qs(urlsplit(flow['authorization_url']).query))
    assert observed['code_challenge_method'] == ['S256']
    assert 'handle' not in flow['authorization_url']
    assert sso.poll(flow['handle']) == {'pending': True}
    with pytest.raises(PermissionError):
        sso.callback('provider-code', 'wrong-state')
    sso.callback('provider-code', observed['state'][0])
    with pytest.raises(PermissionError):
        sso.callback('provider-code', observed['state'][0])
    result = sso.poll(flow['handle'])
    assert result['user']['username'] == 'admin' and result['token']
    with pytest.raises(PermissionError):
        sso.poll(flow['handle'])


def test_revision_one_migration_preserves_rows_and_backup(tmp_path, monkeypatch):
    monkeypatch.setattr(config, 'PASSWORD_BREACH_MODE', 'local')
    from persistencia.database import create_database_engine
    from persistencia.schema import metadata, schema_versions
    from persistencia.migrations import REVISION_TABLES, current_version
    engine = create_database_engine({'type': 'sqlite', 'path': str(tmp_path/'v1.db')})
    with engine.begin() as connection:
        metadata.create_all(connection, tables=[table for table in metadata.sorted_tables if table.name in REVISION_TABLES[1]])
        connection.execute(insert(schema_versions).values(version=1, applied_at=auth.utcnow()))
        connection.execute(insert(usuarios).values(login_usuario='existing', nome_completo='Existing',
            senha_criptografada=auth.hash_password(PASSWORD), tipo_acesso='Auditor Externo'))
    DatabaseManager.initialize_database(engine)
    assert current_version(engine) == 3
    with engine.connect() as connection:
        assert connection.execute(select(usuarios.c.nome_completo)).scalar_one() == 'Existing'
    assert list((tmp_path/'.runtime/backups').glob('*.db'))
    engine.dispose()


@pytest.mark.parametrize('database', ['postgresql', 'mysql', 'mariadb', 'sqlserver', 'oracle', 'firebird'])
def test_runtime_grants_are_limited_and_quote_identifiers(database):
    from instalacao.db_permissions import grants
    sql = grants(database, 'runtime_app')
    assert 'GRANT ALL' not in sql and 'GRANT CREATE' not in sql
    assert 'SELECT, INSERT ON' in sql
    assert 'schema_versions' in sql.lower() and 'external_identities' in sql.lower()
    with pytest.raises(ValueError):
        grants(database, 'name; DROP DATABASE example')
