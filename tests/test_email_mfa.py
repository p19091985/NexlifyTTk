from datetime import timedelta
import hashlib
import json
import ssl
import time

import pytest
from sqlalchemy import select, update, insert, func
import config
from persistencia import auth, mfa
from persistencia.schema import email_mfa, user_security, auth_state, api_sessions, external_identities
from services import email_delivery, sessions

PASSWORD = 'Teste seguro do template 2026!'


def enroll(sent):
    result = mfa.begin_enrollment('admin@example.org')
    assert result['delivery'] == 'email' and 'secret' not in result
    return mfa.confirm_enrollment(sent[-1][1])


def age_delivery(engine):
    with engine.begin() as connection:
        connection.execute(update(email_mfa).values(sent_at=auth.utcnow()-timedelta(seconds=61)))


def test_default_is_off_in_production_and_does_not_send(administrator, monkeypatch):
    from configparser import ConfigParser
    from utils.paths import PROJECT_ROOT
    settings = ConfigParser()
    settings.read(PROJECT_ROOT / 'config_settings.ini')
    assert settings.getboolean('Settings', 'mfa_enabled') is False
    monkeypatch.setattr(config, 'ENVIRONMENT', 'production')
    monkeypatch.setattr(mfa, 'send_code', lambda *args: pytest.fail('Disabled MFA sent an email'))
    with administrator.begin() as connection:
        connection.execute(update(user_security).values(mfa_enabled=1))
    user = auth.verify_user_credentials('admin', PASSWORD)
    assert not user['must_setup_mfa'] and not user['mfa_available']
    assert auth.authorize('vegetais')
    auth.reauthenticate(PASSWORD)
    with pytest.raises(PermissionError, match='desabilitado'):
        mfa.begin_enrollment('admin@example.org')


def test_enrollment_login_cooldown_replay_and_no_cleartext(administrator, email_enabled):
    enroll(email_enabled)
    assert auth.verify_user_credentials('admin', 'wrong') is None
    assert len(email_enabled) == 1
    result = auth.verify_user_credentials('admin', PASSWORD)
    assert result['mfa_required'] and auth._session.get() is None
    address, code = email_enabled[-1]
    assert len(code) == 6 and code.isascii() and code.isdigit()
    assert auth.verify_user_credentials('admin', PASSWORD) == result
    assert len(email_enabled) == 2
    with administrator.connect() as connection:
        row = connection.execute(select(email_mfa)).mappings().one()
        assert row['code_digest'] != hashlib.sha256(code.encode()).hexdigest()
        assert row['code_digest'] != code and row['purpose'] == 'login'
    assert auth.verify_user_credentials('admin', PASSWORD, code)['username'] == 'admin'
    assert auth.verify_user_credentials('admin', PASSWORD, code) is None


def test_expiration_and_purpose_binding(administrator, email_enabled):
    codes = enroll(email_enabled)
    auth.verify_user_credentials('admin', PASSWORD)
    code = email_enabled[-1][1]
    with administrator.begin() as connection:
        assert not mfa.consume(connection, 'admin', code, purpose='reauth')
        connection.execute(update(email_mfa).values(code_until=auth.utcnow()-timedelta(seconds=1)))
    assert auth.verify_user_credentials('admin', PASSWORD, code) is None
    assert auth.verify_user_credentials('admin', PASSWORD, codes[0])
    assert auth.verify_user_credentials('admin', PASSWORD, codes[0]) is None


def test_incorrect_codes_persist_lockout(administrator, email_enabled):
    enroll(email_enabled)
    auth.verify_user_credentials('admin', PASSWORD)
    for _ in range(5):
        assert auth.verify_user_credentials('admin', PASSWORD, 'bad-code') is None
    assert auth.verify_user_credentials('admin', PASSWORD, email_enabled[-1][1]) is None
    with administrator.connect() as connection:
        row = connection.execute(select(auth_state)).mappings().one()
        assert row['failed_attempts'] == 5 and row['locked_until'] > auth.utcnow()


def test_reauth_requires_new_email_code(administrator, email_enabled):
    codes = enroll(email_enabled)
    auth.verify_user_credentials('admin', PASSWORD, codes[0])
    original = dict(auth._session.get(), _reauthenticated_at=time.monotonic()-301)
    auth._session.set(original)
    assert auth.reauthenticate(PASSWORD)['mfa_required']
    with pytest.raises(PermissionError):
        auth.authorize('usuarios', write=True)
    assert auth._session.get()['_reauthenticated_at'] == original['_reauthenticated_at']
    auth.reauthenticate(PASSWORD, email_enabled[-1][1])
    assert auth.authorize('usuarios', write=True)


def test_failed_delivery_rolls_back_and_never_opens_session(administrator, email_enabled, monkeypatch):
    enroll(email_enabled)
    def offline(*args):
        raise ConnectionError('offline')
    monkeypatch.setattr(mfa, 'send_code', offline)
    assert auth.verify_user_credentials('admin', PASSWORD) == {'mfa_required': True, 'delivery': 'unavailable'}
    assert auth._session.get() is None
    with administrator.connect() as connection:
        assert connection.execute(select(email_mfa.c.code_digest)).scalar_one() is None


def test_resend_replaces_code_and_enrollment_address(administrator, email_enabled):
    mfa.begin_enrollment('first@example.org')
    first = email_enabled[-1][1]
    with pytest.raises(ValueError, match='60 segundos'):
        mfa.begin_enrollment('second@example.org')
    age_delivery(administrator)
    mfa.begin_enrollment('second@example.org')
    # Random codes could coincide, but the nonce and recipient change on every send.
    if first != email_enabled[-1][1]:
        with pytest.raises(ValueError):
            mfa.confirm_enrollment(first)
    mfa.confirm_enrollment(email_enabled[-1][1])
    with administrator.connect() as connection:
        assert connection.execute(select(email_mfa.c.email)).scalar_one() == 'second@example.org'


def test_enrollment_expired_code_counts_failure(administrator, email_enabled):
    mfa.begin_enrollment('admin@example.org')
    with administrator.begin() as connection:
        connection.execute(update(email_mfa).values(code_until=auth.utcnow()-timedelta(seconds=1)))
    with pytest.raises(ValueError, match='expirado'):
        mfa.confirm_enrollment(email_enabled[-1][1])
    with administrator.connect() as connection:
        assert connection.execute(select(auth_state.c.failed_attempts)).scalar_one() == 1
        assert not connection.execute(select(user_security.c.mfa_enabled)).scalar_one()


def test_policy_change_revokes_local_and_api_sessions(administrator, monkeypatch):
    token = sessions.issue()
    monkeypatch.setattr(config, 'MFA_ENABLED', True)
    with pytest.raises(PermissionError, match='revogada'):
        auth.current_session()
    with pytest.raises(PermissionError, match='revogada'):
        sessions.load(token)


def test_legacy_authenticator_requires_recovery_before_email_setup(administrator, email_enabled):
    recovery = 'existing-recovery-test-value'
    with administrator.begin() as connection:
        connection.execute(update(user_security).values(mfa_enabled=1,
            recovery_hashes=json.dumps([hashlib.sha256(recovery.encode()).hexdigest()])))
    result = auth.verify_user_credentials('admin', PASSWORD)
    assert result == {'mfa_required': True, 'delivery': 'recovery'}
    assert auth._session.get() is None
    assert auth.verify_user_credentials('admin', PASSWORD, '123456') is None
    assert auth.verify_user_credentials('admin', PASSWORD, recovery)['must_setup_mfa']
    with pytest.raises(PermissionError, match='MFA'):
        auth.authorize('vegetais')
    enroll(email_enabled)


def test_api_issues_token_only_after_email_and_reauth(administrator, email_enabled, monkeypatch):
    from fastapi.testclient import TestClient
    from services.api import app, _limits
    enroll(email_enabled)
    monkeypatch.setattr(config, 'API_MODE', 'server')
    _limits.clear()
    def call(client, method, params, token=None):
        return client.post('/rpc', json={'method': method, 'params': params},
            headers={'Authorization': 'Bearer '+token} if token else {}).json()
    with TestClient(app, base_url='https://testserver') as client:
        params = {'username': 'admin', 'password': PASSWORD}
        result = call(client, 'login', params)
        assert result['mfa_required'] and 'token' not in result and 'user' not in result
        with administrator.connect() as connection:
            assert connection.execute(select(func.count()).select_from(api_sessions)).scalar_one() == 0
        result = call(client, 'login', dict(params, otp=email_enabled[-1][1]))
        token = result['token']
        age_delivery(administrator)
        with administrator.begin() as connection:
            connection.execute(update(api_sessions).values(reauthenticated_at=auth.utcnow()-timedelta(seconds=301)))
        assert call(client, 'reauth', {'password': PASSWORD}, token)['mfa_required']
        with administrator.connect() as connection:
            assert (auth.utcnow()-connection.execute(select(api_sessions.c.reauthenticated_at)).scalar_one()).total_seconds() > 300
        assert call(client, 'reauth', {'password': PASSWORD, 'otp': email_enabled[-1][1]}, token)['ok']


def test_sso_keeps_flow_until_email_confirmation(administrator, email_enabled):
    from services import sso
    enroll(email_enabled)
    handle = 'a-random-handle-from-start'
    key = hashlib.sha256(handle.encode()).hexdigest()
    with administrator.begin() as connection:
        connection.execute(insert(external_identities).values(issuer='https://id.example', subject='known', login_usuario='admin'))
    sso._flows[key] = {'identity': ('https://id.example', 'known', time.time()+300), 'expires': time.monotonic()+300}
    try:
        assert sso.poll(handle)['mfa_required']
        assert key in sso._flows
        assert sso.poll(handle, email_enabled[-1][1])['token']
        with pytest.raises(PermissionError):
            sso.poll(handle, email_enabled[-1][1])
    finally:
        sso._flows.pop(key, None)


@pytest.mark.parametrize('address', ['x@example.org\r\nBcc:victim@example.org', 'Display <x@example.org>',
                                   'missing-at', 'x@-bad.example', 'a..b@example.org', '.x@example.org'])
def test_reject_invalid_email(address):
    with pytest.raises(ValueError):
        email_delivery.validate_address(address)


@pytest.mark.parametrize('mode', ['starttls', 'ssl'])
def test_smtp_verifies_tls_and_never_sends_credentials_before_tls(monkeypatch, mode):
    for key, value in {'HOST': 'smtp.example.org', 'FROM': 'noreply@example.org',
                       'USER': 'test-user', 'PASSWORD': 'test-password', 'SECURITY': mode}.items():
        monkeypatch.setenv('NEXLIFY_SMTP_'+key, value)
    monkeypatch.delenv('NEXLIFY_SMTP_PORT', raising=False)
    monkeypatch.delenv('NEXLIFY_SMTP_CA', raising=False)
    events = []
    class SMTP:
        def __init__(self, host, port, timeout, context=None):
            assert timeout == 10 and port == (465 if mode == 'ssl' else 587)
            self.secure = mode == 'ssl'
            if context:
                assert context.verify_mode == ssl.CERT_REQUIRED and context.check_hostname
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def ehlo(self):
            events.append('ehlo')
        def starttls(self, context):
            assert context.verify_mode == ssl.CERT_REQUIRED and context.check_hostname
            self.secure = True
            events.append('tls')
        def login(self, user, password):
            assert self.secure
            events.append('login')
        def send_message(self, message):
            assert self.secure and message['To'] == 'admin@example.org'
            assert '012345' in message.get_content()
            events.append('send')
            return {}
    monkeypatch.setattr(email_delivery.smtplib, 'SMTP', SMTP)
    monkeypatch.setattr(email_delivery.smtplib, 'SMTP_SSL', SMTP)
    email_delivery.send_code('admin@example.org', '012345')
    assert events[-2:] == ['login', 'send']


def test_smtp_plaintext_is_rejected(monkeypatch):
    monkeypatch.setenv('NEXLIFY_SMTP_HOST', 'smtp.example.org')
    monkeypatch.setenv('NEXLIFY_SMTP_SECURITY', 'plain')
    with pytest.raises(ValueError, match='TLS'):
        email_delivery.send_code('admin@example.org', '012345')


@pytest.mark.parametrize('mode', ['local', 'client', 'server'])
def test_packaged_auth_imports_with_mfa_disabled(tmp_path, mode):
    import os
    import subprocess
    import sys
    import zipfile
    from instalacao.package_release import build
    archive = tmp_path / (mode+'.zip')
    build(archive, mode=mode, api_url='https://api.example.org' if mode == 'client' else '')
    target = tmp_path / 'Instalação com espaços'
    with zipfile.ZipFile(archive) as package:
        package.extractall(target)
    environment = {key: value for key, value in os.environ.items() if not key.startswith('NEXLIFY_')}
    subprocess.run([sys.executable, '-c', 'from persistencia import auth; import config; assert config.MFA_ENABLED is False'],
                   cwd=target, env=environment, check=True, capture_output=True, text=True, timeout=30)


def test_client_recognizes_challenge_without_session(monkeypatch):
    from services import client
    monkeypatch.setattr(client, '_token', None)
    challenge = {'mfa_required': True, 'delivery': 'email', 'masked_email': 'a***@example.org'}
    monkeypatch.setattr(client, 'request', lambda *args: challenge)
    assert client.login('admin', PASSWORD) == challenge
    assert client._token is None
    assert client.sso_poll('handle') == challenge
    assert client._token is None


def test_smtp_failed_tls_never_authenticates_or_sends(monkeypatch):
    for key, value in {'HOST': 'smtp.example.org', 'FROM': 'noreply@example.org', 'USER': 'test',
                       'PASSWORD': 'test', 'SECURITY': 'starttls'}.items():
        monkeypatch.setenv('NEXLIFY_SMTP_'+key, value)
    monkeypatch.delenv('NEXLIFY_SMTP_CA', raising=False)
    monkeypatch.delenv('NEXLIFY_SMTP_PORT', raising=False)
    class SMTP:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def ehlo(self):
            pass
        def starttls(self, context):
            raise ssl.SSLCertVerificationError('Untrusted certificate')
        def login(self, *args):
            pytest.fail('Credentials sent before verified TLS')
        def send_message(self, *args):
            pytest.fail('Code sent before verified TLS')
    monkeypatch.setattr(email_delivery.smtplib, 'SMTP', SMTP)
    with pytest.raises(ConnectionError, match='enviar'):
        email_delivery.send_code('admin@example.org', '123456')
