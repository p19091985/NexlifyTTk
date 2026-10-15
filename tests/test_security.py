import pytest
from cryptography.fernet import Fernet
from sqlalchemy import select, insert, update
from persistencia import auth
from persistencia.schema import usuarios, auth_state
from persistencia.security import encrypt_message, decrypt_message
PASSWORD = 'Teste seguro do template 2026!'


def test_encryption_fails_closed():
    key = Fernet.generate_key()
    token = encrypt_message('secret value', key)
    assert token.startswith('ENC:')
    assert decrypt_message(token, key) == 'secret value'
    with pytest.raises(ValueError):
        decrypt_message(token, Fernet.generate_key())
    with pytest.raises(ValueError):
        decrypt_message('plaintext is not a token', key)


@pytest.mark.parametrize('password', ['short', 'x'*20, 'é'*37])
def test_rejects_weak_or_overlong_password(password):
    with pytest.raises(ValueError):
        auth.hash_password(password)


def test_persistent_lockout(administrator):
    for _ in range(5):
        assert auth.verify_user_credentials('admin', 'wrong') is None
    assert auth.verify_user_credentials('admin', PASSWORD) is None
    with administrator.connect() as connection:
        state = connection.execute(select(auth_state)).mappings().one()
        assert state['failed_attempts'] == 5
        assert state['locked_until'] is not None


def test_concurrent_failures_are_counted(administrator):
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(lambda _: auth.verify_user_credentials('admin', 'wrong'), range(5)))
    assert results == [None] * 5
    with administrator.connect() as connection:
        assert connection.execute(select(auth_state.c.failed_attempts)).scalar_one() == 5


def test_public_legacy_password_hash_is_rejected(administrator, monkeypatch):
    monkeypatch.setattr(auth, 'is_legacy_hash', lambda value: True)
    assert auth.verify_user_credentials('admin', PASSWORD) is None


def test_reset_is_development_only(administrator, monkeypatch):
    import config
    monkeypatch.setattr(config, 'ENVIRONMENT', 'production')
    with pytest.raises(PermissionError):
        auth.reset_admin_password('Outra frase de teste 2026!')


def test_reset_requires_change_and_revokes_old_session(administrator, monkeypatch):
    import utils.installation_profile as profiles
    monkeypatch.setattr(profiles, 'load_installation_profile', lambda root: {'id':'dev'})
    session = auth._session.get()
    new_password = 'Temporaria segura de teste 2026!'
    auth.reset_admin_password(new_password)
    auth._session.set(session)
    with pytest.raises(PermissionError, match='revogada'):
        auth.current_session()
    user = auth.verify_user_credentials('admin', new_password)
    assert user['must_change_password']
    with pytest.raises(PermissionError, match='Troque'):
        auth.authorize('vegetais', write=True)
    auth.change_own_password(new_password, 'Permanente segura de teste 2026!')
    assert not auth.verify_user_credentials('admin', 'Permanente segura de teste 2026!')['must_change_password']


def test_unknown_account_and_invalid_input(database):
    assert auth.verify_user_credentials('absent', PASSWORD) is None
    assert auth.verify_user_credentials('absent', 'é'*40) is None
    assert auth.verify_user_credentials('absent', None) is None


def test_production_cannot_disable_login(monkeypatch):
    import config
    monkeypatch.setattr(config, 'ENVIRONMENT', 'production')
    monkeypatch.setattr(config, 'USE_LOGIN', False)
    with pytest.raises(ValueError):
        config.validate()
