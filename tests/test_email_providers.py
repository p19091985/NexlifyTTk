import json
import os
import ssl
import time
from pathlib import Path
import pytest
import config
from services import email_settings, email_delivery, email_oauth
from services.email_providers import PROVIDERS, defaults
from persistencia import security


@pytest.fixture
def mail_store(tmp_path, monkeypatch):
    for key in list(os.environ):
        if key.startswith('NEXLIFY_SMTP_') or key == 'NEXLIFY_SECRET_KEY':
            monkeypatch.delenv(key)
    monkeypatch.setattr(config, 'API_MODE', 'local')
    monkeypatch.setattr(security, 'KEY_PATH', tmp_path / '.secrets' / 'secret.key')
    email_oauth._tokens.clear()
    return tmp_path


def settings(provider='gmail'):
    data = defaults(provider)
    data.update(enabled=True, sender='sender@example.org', username='sender@example.org', password='test-app-password')
    if provider == 'custom':
        data['host'] = 'smtp.example.org'
    if provider == 'outlook':
        data.update(password='', client_id='00000000-0000-0000-0000-000000000001', refresh_token='test-refresh-token')
    return data


def test_ten_presets_and_custom_defaults():
    assert len(PROVIDERS) == 11 and 'custom' in PROVIDERS
    for provider in PROVIDERS:
        preset = defaults(provider)
        assert preset['enabled'] is False
        assert preset['security'] in {'starttls', 'ssl'}
        if provider != 'custom':
            assert preset['host'] and PROVIDERS[provider]['source'].startswith('https://')


def test_saved_credentials_are_encrypted_and_blank_preserves_only_same_identity(mail_store):
    original = settings()
    result = email_settings.save(original)
    assert not email_settings.SECRETS.intersection(result)
    content = email_settings.path().read_text()
    assert original['password'] not in content and original['sender'] not in content
    assert email_settings.effective() == original
    email_settings.save(dict(original, password=''))
    assert email_settings.effective()['password'] == original['password']
    with pytest.raises(ValueError, match='senha'):
        email_settings.save(dict(original, host='different.example.org', password=''))
    assert email_settings.effective() == original


def test_environment_is_complete_and_never_inherits_saved_secrets(mail_store, monkeypatch):
    email_settings.save(settings())
    monkeypatch.setenv('NEXLIFY_SMTP_HOST', 'another.example.org')
    with pytest.raises(ValueError):
        email_settings.effective()
    monkeypatch.setenv('NEXLIFY_SMTP_FROM', 'test@example.org')
    monkeypatch.setenv('NEXLIFY_SMTP_USER', 'test@example.org')
    monkeypatch.setenv('NEXLIFY_SMTP_PASSWORD', 'environment-password')
    result = email_settings.effective()
    assert result['host'] == 'another.example.org' and result['password'] == 'environment-password'
    with pytest.raises(ValueError, match='ambiente'):
        email_settings.save(settings())


def test_corrupt_or_wrong_key_never_reverts_to_defaults(mail_store, monkeypatch):
    from cryptography.fernet import Fernet
    email_settings.save(settings())
    monkeypatch.setenv('NEXLIFY_SECRET_KEY', Fernet.generate_key().decode())
    with pytest.raises(ValueError, match='chave'):
        email_settings.load_saved()


def test_client_cannot_read_write_or_send_smtp(mail_store, monkeypatch):
    email_settings.save(settings())
    monkeypatch.setattr(config, 'API_MODE', 'client')
    for call in (email_settings.load_saved, email_settings.effective, lambda: email_settings.save(settings()),
                 lambda: email_delivery.send_test('test@example.org')):
        with pytest.raises(PermissionError):
            call()


@pytest.mark.parametrize('change', [{'host': 'smtp.example.org\r\nNOOP'}, {'host': 'https://smtp.example.org'},
    {'port': 0}, {'port': True}, {'security': 'plain'}, {'username': 'sender\x01auth=Bearer'},
    {'sender': 'a@example.org\r\nBcc: b@example.org'}, {'auth': 'anonymous'}, {'token_url': 'http://localhost/token'}])
def test_invalid_configuration_is_rejected(mail_store, change):
    with pytest.raises(ValueError):
        email_settings.save(dict(settings(), **change))
    assert not email_settings.path().exists()


def test_outlook_does_not_fall_back_to_password(mail_store):
    with pytest.raises(ValueError, match='OAuth2'):
        email_settings.save(dict(settings('outlook'), auth='password'))


@pytest.mark.parametrize('provider', list(PROVIDERS))
def test_all_presets_deliver_through_verified_tls(mail_store, monkeypatch, provider):
    data = settings(provider)
    email_settings.save(data)
    events = []
    class SMTP:
        def __init__(self, host, port, timeout, context=None):
            assert (host, port) == (data['host'], data['port'])
            self.secure = context is not None
            if context:
                assert context.verify_mode == ssl.CERT_REQUIRED and context.check_hostname
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def ehlo(self):
            pass
        def starttls(self, context):
            assert context.verify_mode == ssl.CERT_REQUIRED and context.check_hostname
            self.secure = True
        def login(self, username, password):
            assert self.secure and (username, password) == (data['username'], data['password'])
            events.append('password')
        def auth(self, method, callback):
            assert self.secure and method == 'XOAUTH2'
            assert callback() == 'user=sender@example.org\x01auth=Bearer test-access-token\x01\x01'
            assert callback(b'error') == ''
            events.append('oauth2')
        def send_message(self, message):
            assert self.secure
            assert message['To'] == 'recipient@example.org'
            assert 'teste' in message['Subject']
            events.append('send')
            return {}
    monkeypatch.setattr(email_delivery.smtplib, 'SMTP', SMTP)
    monkeypatch.setattr(email_delivery.smtplib, 'SMTP_SSL', SMTP)
    monkeypatch.setattr(email_oauth, 'access_token', lambda config: 'test-access-token')
    email_delivery.send_test('recipient@example.org')
    assert events == [data['auth'], 'send']


def test_unconfigured_email_is_disabled_without_network(mail_store, monkeypatch):
    monkeypatch.setattr(email_delivery.smtplib, 'SMTP', lambda *a, **k: pytest.fail('Unexpected connection'))
    with pytest.raises(ValueError, match='desabilitado'):
        email_delivery.send_test('recipient@example.org')
    assert not email_settings.path().exists()


def test_refresh_rotates_persisted_token_and_caches_access(mail_store, monkeypatch):
    data = settings('outlook')
    email_settings.save(data)
    calls = []
    def post(url, fields):
        calls.append(fields)
        return {'access_token': 'test-access-token', 'token_type': 'Bearer', 'expires_in': 3600,
                'refresh_token': 'rotated-refresh-token'}
    monkeypatch.setattr(email_oauth, 'post', post)
    assert email_oauth.access_token(email_settings.effective()) == 'test-access-token'
    assert email_settings.effective()['refresh_token'] == 'rotated-refresh-token'
    assert email_oauth.access_token(email_settings.effective()) == 'test-access-token'
    assert len(calls) == 1
    assert 'rotated-refresh-token' not in email_settings.path().read_text()
    email_settings.save(dict(data, username='other@example.org', refresh_token='another-refresh-token'))
    email_oauth.access_token(email_settings.effective())
    assert len(calls) == 2


def test_refresh_does_not_overwrite_concurrent_config_change(mail_store):
    original = settings('outlook')
    email_settings.save(original)
    changed = dict(original, username='other@example.org', refresh_token='new-refresh-token')
    email_settings.save(changed)
    email_settings.remember_refresh_token(original, 'late-refresh-token')
    assert email_settings.effective() == changed


def test_microsoft_device_flow_polling_slowdown_and_one_use(mail_store, monkeypatch):
    clock = [100.0]
    monkeypatch.setattr(email_oauth.time, 'monotonic', lambda: clock[0])
    responses = [dict(verification_uri='https://microsoft.com/devicelogin', user_code='TEST-CODE', device_code='private-device-code', expires_in=900, interval=5),
                 {'error': 'authorization_pending'}, {'error': 'slow_down'}, {'refresh_token': 'test-refresh-token'}]
    calls = []
    def post(url, data):
        calls.append((url, data))
        return responses.pop(0)
    monkeypatch.setattr(email_oauth, 'post', post)
    flow = email_oauth.start_microsoft(settings('outlook')['client_id'])
    assert email_oauth.poll_microsoft(flow) is None and len(calls) == 1
    clock[0] += 5
    assert email_oauth.poll_microsoft(flow) is None
    clock[0] += 5
    assert email_oauth.poll_microsoft(flow) is None and flow['interval'] == 10
    clock[0] += 10
    assert email_oauth.poll_microsoft(flow) == 'test-refresh-token'
    with pytest.raises(ValueError, match='expirou'):
        email_oauth.poll_microsoft(flow)
    assert not email_settings.path().exists()


@pytest.mark.parametrize('error', ['authorization_declined', 'expired_token', 'invalid_grant'])
def test_microsoft_denial_does_not_save_tokens(mail_store, monkeypatch, error):
    monkeypatch.setattr(email_oauth, 'post', lambda *a: {'error': error})
    flow = {'client_id': 'id', 'device_code': 'code', 'expires_at': time.monotonic()+300, 'next_poll': 0, 'interval': 5}
    with pytest.raises(ValueError, match='recusada'):
        email_oauth.poll_microsoft(flow)
    assert not email_settings.path().exists()


def test_oauth_transport_blocks_redirect_and_redacts_response(mail_store, monkeypatch):
    import httpx
    real_client = httpx.Client
    def transport(request):
        assert request.url.scheme == 'https'
        return httpx.Response(302, headers={'Location': 'https://untrusted.example'}, text='secret-token')
    def client(**kwargs):
        assert kwargs['verify'] is True and kwargs['trust_env'] is False and kwargs['follow_redirects'] is False
        return real_client(transport=httpx.MockTransport(transport), **kwargs)
    monkeypatch.setattr(httpx, 'Client', client)
    with pytest.raises(ConnectionError) as error:
        email_oauth.post('https://login.microsoftonline.com/token', {'refresh_token': 'secret-token'})
    assert 'secret-token' not in str(error.value)


def test_rotation_reencrypts_smtp_configuration(administrator, mail_store, tmp_path):
    from instalacao.rotate_key import rotate
    email_settings.save(settings())
    old_key = security.load_key()
    old_payload = json.loads(email_settings.path().read_text())['payload']
    rotate(tmp_path/'database.ini')
    new_payload = json.loads(email_settings.path().read_text())['payload']
    assert email_settings.effective() == settings()
    assert security.decrypt_message(old_payload)
    with pytest.raises(ValueError):
        security.decrypt_message(new_payload, old_key)


def test_packages_include_smtp_modules_but_no_configuration(mail_store, tmp_path):
    import zipfile
    from instalacao.package_release import build
    email_settings.save(settings())
    for mode in ('local', 'server', 'client'):
        target = tmp_path/(mode+'.zip')
        build(target, mode=mode, api_url='https://api.example' if mode == 'client' else '')
        with zipfile.ZipFile(target) as archive:
            assert 'services/email_settings.py' in archive.namelist()
            assert 'services/email_providers.py' in archive.namelist()
            assert 'services/email_oauth.py' in archive.namelist()
            assert ('instalacao/config_email.py' in archive.namelist()) == (mode != 'client')
            assert not any(name.startswith('.secrets/') for name in archive.namelist())


@pytest.mark.gui
def test_configuration_dialog_presets_save_and_async_test(administrator, mail_store, monkeypatch):
    import tkinter as tk
    from dialogs import email_settings_dialog as ui
    from tkinter import messagebox
    def fail(title, message, **kwargs):
        raise AssertionError(message)
    monkeypatch.setattr(messagebox, 'showerror', fail)
    observed = []
    monkeypatch.setattr(ui, 'send_test', lambda address, settings: observed.append((address, settings['host'])))
    root = tk.Tk()
    root.withdraw()
    try:
        dialog = ui.EmailSettingsDialog(root)
        root.update()
        assert len(dialog.provider.cget('values')) == 11
        dialog.provider.set(PROVIDERS['yahoo']['name'])
        dialog.select_provider()
        assert dialog.vars['host'].get() == 'smtp.mail.yahoo.com'
        assert dialog.vars['port'].get() == '465'
        dialog.enabled.set(True)
        dialog.vars['sender'].set('sender@example.org')
        dialog.vars['username'].set('sender@example.org')
        dialog.vars['password'].set('gui-test-app-password')
        dialog.save()
        assert email_settings.effective()['password'] == 'gui-test-app-password'
        assert dialog.vars['password'].get() == ''
        dialog.test_address.set('recipient@example.org')
        dialog.test()
        deadline = time.monotonic()+5
        while dialog.busy and time.monotonic() < deadline:
            root.update()
            time.sleep(0.01)
        assert not dialog.busy and observed == [('recipient@example.org', 'smtp.mail.yahoo.com')]
        assert 'aceita' in dialog.status.cget('text')
        dialog.provider.set(PROVIDERS['outlook']['name'])
        dialog.select_provider()
        assert dialog.vars['auth'].get() == 'oauth2'
        dialog.provider.set(PROVIDERS['custom']['name'])
        dialog.select_provider()
        assert dialog.vars['host'].get() == '' and dialog.vars['password'].get() == ''
        dialog.close()
    finally:
        root.destroy()


@pytest.mark.gui
def test_configuration_dialog_microsoft_authorization_is_not_saved_until_save(administrator, mail_store, monkeypatch):
    import tkinter as tk
    from dialogs import email_settings_dialog as ui
    flow = {'client_id': settings('outlook')['client_id'], 'user_code': 'TEST-CODE', 'device_code': 'not-displayed',
            'verification_uri': 'https://microsoft.com/devicelogin', 'next_poll': 0, 'expires_at': time.monotonic()+300, 'interval': 5}
    monkeypatch.setattr(email_oauth, 'start_microsoft', lambda client: flow)
    monkeypatch.setattr(email_oauth, 'poll_microsoft', lambda current: 'gui-test-refresh-token')
    root = tk.Tk()
    root.withdraw()
    try:
        dialog = ui.EmailSettingsDialog(root)
        dialog.provider.set(PROVIDERS['outlook']['name'])
        dialog.select_provider()
        dialog.vars['client_id'].set(flow['client_id'])
        dialog.connect()
        deadline = time.monotonic()+5
        while not dialog.vars['refresh_token'].get() and time.monotonic() < deadline:
            root.update()
            time.sleep(0.01)
        assert dialog.vars['refresh_token'].get() == 'gui-test-refresh-token'
        assert not email_settings.path().exists()
        assert 'gui-test-refresh-token' not in dialog.oauth_status.cget('text')
        dialog.close()
    finally:
        root.destroy()


def test_configuration_authorization_requires_local_recent_admin(administrator, mail_store, monkeypatch):
    from persistencia import auth
    from dialogs.email_settings_dialog import authorize_admin
    from dialogs import mfa_dialog
    monkeypatch.setattr(mfa_dialog, 'ensure_recent_auth', lambda parent: True)
    assert authorize_admin(None)
    monkeypatch.setattr(auth, 'current_session', lambda **kwargs: {'access_level': 'Auditor Externo'})
    with pytest.raises(PermissionError):
        authorize_admin(None)


def test_config_lock_serializes_separate_processes(mail_store):
    import subprocess
    import sys
    script = """from pathlib import Path
import sys
from persistencia import security
from services import email_settings
security.KEY_PATH = Path(sys.argv[1]) / '.secrets' / 'secret.key'
(Path(sys.argv[1]) / 'ready').touch()
with email_settings.file_lock():
    (Path(sys.argv[1]) / 'acquired').touch()
"""
    child = None
    try:
        with email_settings.file_lock():
            child = subprocess.Popen([sys.executable, '-c', script, str(mail_store)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            deadline = time.monotonic()+10
            while not (mail_store/'ready').exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            assert (mail_store/'ready').exists()
            time.sleep(0.1)
            assert not (mail_store/'acquired').exists()
        output, errors = child.communicate(timeout=10)
        assert child.returncode == 0, errors.decode(errors='replace')
        assert (mail_store/'acquired').exists()
    finally:
        if child and child.poll() is None:
            child.kill()
            child.communicate()
