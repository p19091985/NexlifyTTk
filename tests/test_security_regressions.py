"""Security regressions use isolated databases; never the installation database."""
from datetime import timedelta
import os
from pathlib import Path

import pytest
from sqlalchemy import select, literal_column, text, Table, Column, MetaData, String, func, update

from persistencia import auth
from persistencia.repository import GenericRepository as Repository
from persistencia.schema import usuarios, vegetais, tipos_vegetais


@pytest.mark.parametrize('query', [
    select(usuarios.c.senha_criptografada),
    select(literal_column('(SELECT senha_criptografada FROM usuarios LIMIT 1)')).select_from(vegetais),
    select(vegetais.c.nome).where(text('1=1')),
    select(func.load_file('/etc/passwd')).select_from(vegetais),
    select(Table('vegetais', MetaData(), Column('nome', String), schema='other').c.nome),
    select(vegetais.c.nome).add_cte(usuarios.delete().cte('erase_users')),
])
def test_generic_select_rejects_unsafe_expressions_before_sql(administrator, query):
    with pytest.raises((ValueError, PermissionError)):
        Repository.execute_query_to_dataframe(query)


def test_filter_cannot_be_an_expression(administrator):
    with pytest.raises(ValueError):
        Repository.delete_from_table('tipos_vegetais', {'id': tipos_vegetais.c.id})


def test_write_value_cannot_be_an_expression(administrator):
    with pytest.raises(ValueError):
        Repository.update_table('vegetais', {'nome': text("'injected'")}, {'id': 1})


def test_role_change_revokes_existing_session(administrator):
    with administrator.begin() as connection:
        connection.execute(update(usuarios).where(usuarios.c.login_usuario == 'admin').values(tipo_acesso='Auditor Externo'))
    with pytest.raises(PermissionError, match='revogada'):
        auth.current_session()


@pytest.mark.parametrize('url', [
    'mysql+pymysql://u:p@localhost/test?ssl_disabled=true',
    'mariadb+pymysql://u:p@localhost/test?local_infile=1',
    'mssql+pyodbc://u:p@localhost/test?odbc_connect=Encrypt%3Dno',
    'mssql+pyodbc://u:p@localhost/test?TrustServerCertificate=yes',
    'oracle+oracledb://u:p@localhost/unsafe_dsn',
    'sqlite:///test.db?uri=true',
])
def test_database_url_cannot_override_security_policy(monkeypatch, url):
    from persistencia.database import create_database_engine
    monkeypatch.setenv('NEXLIFY_DATABASE_URL', url)
    with pytest.raises(ValueError):
        create_database_engine()


def test_dev_bypass_requires_explicit_dev_profile(monkeypatch):
    import config
    import utils.installation_profile as profiles
    monkeypatch.setattr(config, 'USE_LOGIN', False)
    monkeypatch.setattr(config, 'ENVIRONMENT', 'development')
    monkeypatch.setattr(profiles, 'load_installation_profile', lambda root: {'id': 'core'})
    with pytest.raises((PermissionError, ValueError)):
        auth.authorize('vegetais', write=True)


def test_safe_join_alias_and_bound_string_remain_supported(administrator):
    import pandas as pd
    value = "Aspas '); DROP TABLE usuarios; --"
    Repository.write_dataframe_to_table(pd.DataFrame([{'nome': value}]), 'tipos_vegetais')
    alias = tipos_vegetais.alias('t')
    result = Repository.execute_query_to_dataframe(select(alias.c.nome).where(alias.c.nome == value))
    assert result.iloc[0]['nome'] == value
    assert Repository.read_vegetais_com_tipo().empty
    assert len(Repository.read_table_to_dataframe('usuarios')) == 1


def test_write_rechecks_authorization_inside_transaction(administrator, monkeypatch):
    import persistencia.repository as repository
    original = repository.authorize
    def revoke_between_checks(table_name, write=False, *, connection=None):
        if connection is not None:
            auth.clear_session()
        return original(table_name, write, connection=connection)
    monkeypatch.setattr(repository, 'authorize', revoke_between_checks)
    with pytest.raises(PermissionError):
        Repository.update_table('usuarios', {'nome_completo': 'Should not change'}, {'login_usuario': 'admin'})
    with administrator.connect() as connection:
        assert connection.execute(select(usuarios.c.nome_completo)).scalar_one() == 'Administrador'


def test_idle_timeout_is_not_extended_by_session_polling(administrator, monkeypatch):
    import config
    now = auth.time.monotonic()
    monkeypatch.setattr(auth.time, 'monotonic', lambda: now + config.SESSION_IDLE_SECONDS - 1)
    auth.current_session()
    monkeypatch.setattr(auth.time, 'monotonic', lambda: now + config.SESSION_IDLE_SECONDS + 1)
    with pytest.raises(PermissionError, match='expirada'):
        auth.current_session()
    with pytest.raises(PermissionError):
        Repository.read_table_to_dataframe('vegetais')


def test_activity_does_not_bypass_absolute_timeout(administrator, monkeypatch):
    import config
    now = auth.time.monotonic()
    session = dict(auth._session.get(), _created_at=now - config.SESSION_MAX_SECONDS - 1)
    auth._session.set(session)
    with pytest.raises(PermissionError, match='expirada'):
        auth.touch_session_activity()


def test_actual_activity_extends_idle_timer(administrator, monkeypatch):
    import config
    now = auth.time.monotonic()
    monkeypatch.setattr(auth.time, 'monotonic', lambda: now + config.SESSION_IDLE_SECONDS - 1)
    auth.touch_session_activity()
    monkeypatch.setattr(auth.time, 'monotonic', lambda: now + config.SESSION_IDLE_SECONDS + 1)
    assert auth.current_session()['username'] == 'admin'


def test_private_configuration_does_not_reuse_predictable_temporary_file(tmp_path):
    from instalacao.config_banco_gui import save_database_config
    target = tmp_path / 'banco.local.ini'
    stale = target.with_suffix('.ini.tmp')
    stale.write_text('Do not overwrite', encoding='utf-8')
    save_database_config({'type': 'sqlite', 'path': 'local.db'}, path=target)
    assert stale.read_text(encoding='utf-8') == 'Do not overwrite'
    assert 'local.db' in target.read_text(encoding='utf-8')
    if os.name != 'nt':
        assert target.stat().st_mode & 0o777 == 0o600


def test_private_configuration_rejects_symbolic_links(tmp_path):
    from utils.secure_files import atomic_write_private
    outside = tmp_path / 'preserve.txt'
    outside.write_text('Preserve', encoding='utf-8')
    link = tmp_path / 'config.ini'
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip('Creating symlinks requires privileges on this Windows installation')
    with pytest.raises(ValueError):
        atomic_write_private(link, 'Changed')
    assert outside.read_text(encoding='utf-8') == 'Preserve'


def test_decrypt_missing_key_never_creates_replacement(tmp_path, monkeypatch):
    from persistencia import security
    from cryptography.fernet import Fernet
    monkeypatch.delenv('NEXLIFY_SECRET_KEY', raising=False)
    target = tmp_path / '.secrets' / 'secret.key'
    monkeypatch.setattr(security, 'KEY_PATH', target)
    token = security.encrypt_message('Isolated test', Fernet.generate_key())
    with pytest.raises(ValueError):
        security.decrypt_message(token)
    assert not target.exists()


def test_private_log_rotation_keeps_restrictive_permissions(tmp_path):
    import logging
    from persistencia.logger import PrivateRotatingFileHandler
    path = tmp_path / 'app.log'
    handler = PrivateRotatingFileHandler(path, maxBytes=30, backupCount=2, encoding='utf-8')
    try:
        for _ in range(3):
            handler.emit(logging.LogRecord('test', logging.INFO, '', 0, 'An isolated test message', (), None))
    finally:
        handler.close()
    assert (tmp_path / 'app.log.1').exists()
    if os.name != 'nt':
        assert all(item.stat().st_mode & 0o777 == 0o600 for item in tmp_path.glob('app.log*'))


def test_password_change_attempts_are_persistently_limited(administrator):
    from persistencia.schema import auth_state
    for _ in range(5):
        with pytest.raises(ValueError, match='Senha atual'):
            auth.change_own_password('wrong', 'Nova frase segura para teste 2026!')
    with administrator.connect() as connection:
        row = connection.execute(select(auth_state)).mappings().one()
        assert row['failed_attempts'] == 5
        assert row['locked_until'] is not None
    assert auth._session.get() is None
    assert auth.verify_user_credentials('admin', 'Teste seguro do template 2026!') is None


def test_production_refuses_start_without_file_logging(tmp_path, monkeypatch):
    import config
    import persistencia.logger as logging_config
    import logging
    monkeypatch.setattr(config, 'ENVIRONMENT', 'production')
    monkeypatch.setattr(logging_config, 'ENABLE_LOGGING', True)
    monkeypatch.setattr(logging_config, 'REDIRECT_CONSOLE_TO_LOG', False)
    def denied(path):
        raise PermissionError('test')
    monkeypatch.setattr(logging_config, 'private_directory', denied)
    # setup_loggers replaces root handlers; retain pytest's handlers intact.
    root = logging.getLogger()
    handlers = list(root.handlers)
    level = root.level
    root.handlers = []
    try:
        with pytest.raises(RuntimeError, match='log obrigatório'):
            logging_config.setup_loggers()
    finally:
        for handler in root.handlers:
            handler.close()
        root.handlers = handlers
        root.setLevel(level)


def test_invalid_unicode_input_fails_closed(database):
    assert auth.verify_user_credentials('admin', '\ud800') is None
    assert auth.password_validation_error(None)
    assert auth.password_validation_error('Um texto longo com \ud800')


def test_mysql_policy_requires_tls_before_sending_authentication(monkeypatch):
    import ssl
    pymysql = pytest.importorskip('pymysql')
    import persistencia.database as database
    captured = {}
    def capture(url, **kwargs):
        captured.update(kwargs)
        return object()
    monkeypatch.setattr(database, 'create_engine', capture)
    database.create_database_engine({'type': 'mysql', 'host': 'localhost', 'dbname': 'test', 'user': 'test'})
    connection = pymysql.Connection(user='test', defer_connect=True, **captured['connect_args'])
    assert connection.ctx.verify_mode == ssl.CERT_REQUIRED
    assert connection.ctx.check_hostname
    assert connection._ssl_required
    connection.server_version = '8.0'
    connection.server_capabilities = 0  # Server offers no TLS.
    with pytest.raises(pymysql.err.OperationalError, match='SSL is required'):
        connection._request_authentication()
