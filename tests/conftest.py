import pytest
import config
from persistencia.database import DatabaseManager, create_database_engine
from persistencia import auth

PASSWORD = 'Teste seguro do template 2026!'


@pytest.fixture(params=[
    'Administrador Global', 'Diretor de Operações', 'Gerente de TI',
    'Supervisor de Produção', 'Operador de Linha', 'Analista de Dados', 'Auditor Externo',
])
def access_user(request, administrator):
    """Usuário real por perfil em banco temporário, sem senha provisória."""
    from sqlalchemy import insert, select
    from persistencia.schema import usuarios, auth_state
    role = request.param
    with administrator.begin() as connection:
        hashed = connection.execute(select(usuarios.c.senha_criptografada)).scalar_one()
        connection.execute(insert(usuarios).values(login_usuario='profile_test',
            senha_criptografada=hashed, nome_completo='Teste de perfil', tipo_acesso=role))
        connection.execute(insert(auth_state).values(login_usuario='profile_test', failed_attempts=0, must_change=0))
    user = auth.verify_user_credentials('profile_test', PASSWORD)
    assert user['access_level'] == role
    common = {'Gestão de Espécies (Gatos)', 'Guia de Configuração'}
    management = common | {'Cadastro de Vegetais', 'Vegetais e Auditoria'}
    expected = {
        'Administrador Global': management | {'Gestão de Usuários', 'Painel Modelo'},
        'Diretor de Operações': management,
        'Gerente de TI': management,
        'Supervisor de Produção': common,
        'Operador de Linha': common,
        'Analista de Dados': management,
        'Auditor Externo': common | {'Vegetais e Auditoria'},
    }
    return {'user': user, 'engine': administrator, 'pages': expected[role]}


@pytest.fixture
def database(tmp_path, monkeypatch):
    monkeypatch.delenv('NEXLIFY_DATABASE_URL', raising=False)
    monkeypatch.setattr(config, 'DATABASE_ENABLED', True)
    monkeypatch.setattr(config, 'USE_LOGIN', True)
    monkeypatch.setattr(config, 'MFA_ENABLED', False)
    monkeypatch.setattr(config, 'ENVIRONMENT', 'development')
    monkeypatch.setattr(config, 'PASSWORD_BREACH_MODE', 'local')
    engine = create_database_engine({'type': 'sqlite', 'path': str(tmp_path/'test.db')})
    monkeypatch.setattr(DatabaseManager, '_engine', engine)
    DatabaseManager.initialize_database()
    auth.clear_session()
    yield engine
    auth.clear_session()
    engine.dispose()


@pytest.fixture
def administrator(database):
    auth.bootstrap_admin(PASSWORD)
    assert isinstance(auth.verify_user_credentials('admin', PASSWORD), dict)
    return database


@pytest.fixture
def email_enabled(administrator, tmp_path, monkeypatch):
    from persistencia import security, mfa
    monkeypatch.delenv('NEXLIFY_SECRET_KEY', raising=False)
    monkeypatch.setattr(security, 'KEY_PATH', tmp_path / '.secrets' / 'secret.key')
    monkeypatch.setattr(config, 'MFA_ENABLED', True)
    auth.verify_user_credentials('admin', PASSWORD)
    sent = []
    monkeypatch.setattr(mfa, 'send_code', lambda address, code: sent.append((address, code)))
    return sent
