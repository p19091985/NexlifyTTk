"""Autorização real por perfil, independente da visibilidade dos menus."""
from types import SimpleNamespace

import pytest
from sqlalchemy import update

import config
from panels import ALL_PANELS
from persistencia import auth
from persistencia.access_policy import can_access_page, PageAccessDenied
from persistencia.schema import usuarios, auth_state
from utils.installation_profile import write_installation_profile_marker

PASSWORD = 'Teste seguro do template 2026!'


def test_page_matrix_and_repository_authorization(access_user, tmp_path):
    write_installation_profile_marker(tmp_path, 'dev')
    for spec in ALL_PANELS:
        if spec['name'] in access_user['pages']:
            result = auth.authorize_page(spec['name'], project_root=tmp_path)
            assert result['access_level'] == access_user['user']['access_level']
        else:
            with pytest.raises(PageAccessDenied):
                auth.authorize_page(spec['name'], project_root=tmp_path)
    role = access_user['user']['access_level']
    expected_reads = {'especie_gatos'}
    if 'Vegetais e Auditoria' in access_user['pages']:
        expected_reads |= {'vegetais', 'tipos_vegetais', 'log_alteracoes'}
    if role == 'Administrador Global':
        expected_reads.add('usuarios')
    expected_writes = expected_reads - {'log_alteracoes'} if role != 'Auditor Externo' else set()
    for table in ('usuarios', 'vegetais', 'tipos_vegetais', 'especie_gatos', 'log_alteracoes'):
        for write, expected in ((False, expected_reads), (True, expected_writes)):
            if table in expected:
                assert auth.authorize(table, write=write)
            else:
                with pytest.raises(PermissionError):
                    auth.authorize(table, write=write)


@pytest.mark.parametrize('role', [None, '', 'admin', 'Perfil desconhecido'])
def test_unknown_roles_fail_closed(role):
    for spec in ALL_PANELS:
        assert not can_access_page(role, spec['name'], profile_id='dev', environment='development')


def test_unregistered_pages_and_direct_controller_construction(administrator, tmp_path):
    from panels.base_panel import BasePanel
    class UnregisteredPanel(BasePanel):
        PANEL_NAME = 'Painel novo sem regra'
        def create_widgets(self):
            pytest.fail('Não pode construir widgets sem autorização.')
    with pytest.raises(PageAccessDenied):
        UnregisteredPanel(None, SimpleNamespace(project_root=tmp_path))
    for page in (None, [], '', 'Página inexistente'):
        with pytest.raises(PageAccessDenied):
            auth.authorize_page(page, project_root=tmp_path)


def test_dev_pages_require_admin_development_installation_and_local_mode(access_user, tmp_path, monkeypatch):
    pages = ('Painel Modelo', 'dev.tests', 'dev.tools', 'dev.processes', 'dev.reset_preferences')
    role = access_user['user']['access_level']
    for page in pages:
        for profile, environment, mode in (('core', 'development', 'local'), ('dev', 'production', 'local'),
                                           ('dev', 'development', 'client')):
            assert not can_access_page(role, page, profile_id=profile, environment=environment, api_mode=mode)
        assert can_access_page(role, page, profile_id='dev', environment='development') == (role == auth.ADMIN)
    write_installation_profile_marker(tmp_path, 'core')
    with pytest.raises(PageAccessDenied):
        auth.authorize_page('dev.tools', project_root=tmp_path)


@pytest.mark.parametrize('change', ['logout', 'role', 'password_required'])
def test_session_is_rechecked_before_page_access(administrator, tmp_path, change):
    auth.authorize_page('Gestão de Usuários', project_root=tmp_path)
    if change == 'logout':
        auth.clear_session()
    else:
        with administrator.begin() as connection:
            if change == 'role':
                connection.execute(update(usuarios).values(tipo_acesso='Auditor Externo'))
            else:
                connection.execute(update(auth_state).values(must_change=1))
    with pytest.raises(PermissionError):
        auth.authorize_page('Gestão de Usuários', project_root=tmp_path)


def test_api_uses_authenticated_role_and_blocks_direct_data_access(access_user, monkeypatch):
    from fastapi.testclient import TestClient
    from services.api import app, _limits
    from services import sessions
    monkeypatch.setattr(config, 'API_MODE', 'server')
    token = sessions.issue()
    _limits.clear()
    with TestClient(app, base_url='https://testserver') as client:
        def call(method, params, authenticated=True):
            return client.post('/rpc', json={'method': method, 'params': params},
                headers={'Authorization': 'Bearer ' + token} if authenticated else {})
        assert call('pages/authorize', {'page': 'Guia de Configuração'}, False).status_code == 403
        for spec in ALL_PANELS:
            if spec['name'] == 'Painel Modelo':
                continue  # A instalação do servidor tem sua própria restrição DEV.
            expected = 200 if spec['name'] in access_user['pages'] else 403
            assert call('pages/authorize', {'page': spec['name']}).status_code == expected
        assert call('pages/authorize', {'page': 'Gestão de Usuários', 'access_level': auth.ADMIN}).status_code == 400
        assert call('pages/authorize', {'page': 'Página inexistente'}).status_code == 403
        assert call('read', {'table': 'vegetais'}).status_code == (
            200 if 'Vegetais e Auditoria' in access_user['pages'] else 403)
        assert call('read', {'table': 'usuarios'}).status_code == (
            200 if access_user['user']['access_level'] == auth.ADMIN else 403)
        assert call('insert', {'table': 'especie_gatos', 'rows': [{'nome_especie': 'Teste'}]}).status_code == (
            403 if access_user['user']['access_level'] == 'Auditor Externo' else 200)
        with access_user['engine'].begin() as connection:
            connection.execute(update(auth_state).where(auth_state.c.login_usuario == 'profile_test').values(must_change=1))
        assert call('pages/authorize', {'page': 'Guia de Configuração'}).status_code == 403


def test_client_page_check_requires_server_confirmation(monkeypatch, tmp_path):
    from services import client
    calls = []
    monkeypatch.setattr(config, 'API_MODE', 'client')
    def request(method, path, params):
        calls.append((method, path, params))
        return {'username': 'remote', 'access_level': 'Operador de Linha'}
    monkeypatch.setattr(client, 'request', request)
    assert auth.authorize_page('Guia de Configuração', project_root=tmp_path)['username'] == 'remote'
    with pytest.raises(PageAccessDenied):
        auth.authorize_page('Gestão de Usuários', project_root=tmp_path)
    assert calls == [('POST', '/pages/authorize', {'page': page}) for page in ('Guia de Configuração', 'Gestão de Usuários')]
    def unavailable(*args, **kwargs):
        raise ConnectionError('Servidor indisponível')
    monkeypatch.setattr(client, 'request', unavailable)
    with pytest.raises(ConnectionError):
        auth.authorize_page('Guia de Configuração', project_root=tmp_path)


def test_page_access_requires_mfa_setup_when_enforced(email_enabled, monkeypatch, tmp_path):
    monkeypatch.setattr(config, 'ENVIRONMENT', 'production')
    with pytest.raises(PermissionError, match='MFA'):
        auth.authorize_page('Guia de Configuração', project_root=tmp_path)
