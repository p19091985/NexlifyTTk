# mock_dependencies.py (Versão Corrigida e Unificada)
import pandas as pd
from unittest.mock import MagicMock
from sqlalchemy.exc import SQLAlchemyError
import logging
import sys
import tkinter as tk
from tkinter import ttk

# Importa as funções reais que precisamos para criar dados de mock realistas
import persistencia.auth as auth_utils

# -
# MOCKS DE SAÍDA E CONFIGURAÇÃO
# -
class MockLogger(MagicMock):
    """Mock completo para o logger, para evitar falhas de atributos."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.info = MagicMock()
        self.warning = MagicMock()
        self.error = MagicMock()
        self.critical = MagicMock()

class MockConfig:
    """Mock do módulo de configuração."""
    DATABASE_ENABLED = True
    INITIALIZE_DATABASE_ON_STARTUP = True
    USE_LOGIN = True
    REDIRECT_CONSOLE_TO_LOG = False
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# -
# DADOS SIMULADOS (MOCK DATA)
# -
# Usa a função de hash real para criar dados de teste realistas.
HASH_SENHA_123 = auth_utils.hash_password('senha123')

MOCK_USUARIOS_DB = pd.DataFrame({
    'LOGIN_USUARIO': ['testuser'],
    'SENHA_CRIPTOGRAFADA': [HASH_SENHA_123],
    'NOME_COMPLETO': ['Usuário de Teste'],
    'TIPO_ACESSO': ['Administrador Global']
})
MOCK_DF_GATOS = pd.DataFrame([
    {'ID': 1, 'NOME_ESPECIE': 'Siamês', 'PAIS_ORIGEM': 'Tailândia', 'TEMPERAMENTO': 'Vocal'},
    {'ID': 2, 'NOME_ESPECIE': 'Persa', 'PAIS_ORIGEM': 'Irã', 'TEMPERAMENTO': 'Calmo'}
])
MOCK_DF_LINGUAGENS = pd.DataFrame([
    {'ID': 101, 'NOME': 'Python', 'CATEGORIA': 'Interpretada'},
    {'ID': 102, 'NOME': 'Java', 'CATEGORIA': 'Compilada'}
])
MOCK_DF_LOG = pd.DataFrame([
    {'ID': 1, 'TIMESTAMP': pd.Timestamp.now(), 'LOGIN_USUARIO': 'admin', 'ACAO': 'Teste'}
])

# -
# MOCKS DA CAMADA DE BANCO DE DADOS
# -
class MockEngine:
    """Simula a Engine do SQLAlchemy, incluindo o retorno de resultados."""
    def __init__(self, fail_connect=False):
        self.fail_connect = fail_connect
        self.url = MagicMock(); self.url.drivername = 'sqlite'

    def connect(self):
        if self.fail_connect: raise SQLAlchemyError("Erro simulado de conexão.")
        conn = MagicMock()
        conn.begin.return_value.__enter__.return_value = conn # Simula 'with ... .begin()'
        conn.execute.return_value.rowcount = 1 # Simula sucesso em updates/deletes

        # Simula o retorno de fetchone() para o login
        result_proxy = MagicMock()
        result_proxy.fetchone.return_value = MagicMock()
        result_proxy.fetchone.return_value._mapping = MOCK_USUARIOS_DB.iloc[0].to_dict()
        conn.execute.return_value = result_proxy
        return conn

class MockDatabaseManager:
    """Mock completo do DatabaseManager."""
    _engine = None
    _fail_connect = False

    @classmethod
    def get_engine(cls):
        return MockEngine(fail_connect=cls._fail_connect)

    @classmethod
    def set_engine_state(cls, state='default'):
        cls._fail_connect = (state == 'fail_connect')

    #  Adiciona os métodos que estavam faltando para evitar erros de atributo
    initialize_database = MagicMock()
    _parse_active_config = MagicMock(return_value={'type': 'sqlite'})

# -
# MOCKS DE GUI E APLICAÇÃO
# -
class MockAppController:
    """Simulação do App Controller."""
    def get_current_user(self):
        return {'username': 'testuser', 'name': 'Usuário de Teste', 'access_level': 'Administrador Global'}

class MockViewBase(MagicMock):
    """Base unificada para Mocks de View."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mock de widgets comuns
        self.tree = MagicMock(spec=ttk.Treeview)
        self.linguagens_tree = MagicMock(spec=ttk.Treeview)
        self.log_tree = MagicMock(spec=ttk.Treeview)
        self.linguagem_combo = MagicMock()
        self.meter = MagicMock()

        # Configurações de retorno padrão para os mocks
        self.tree.get_children.return_value = ['I001']
        self.tree.selection.return_value = ['I001']
        self.tree.item.return_value = {'values': MOCK_DF_GATOS.iloc[0].tolist()}
        self.get_selected_item_data.return_value = {'id': 1, 'nome': 'Funcional'}
        self.ask_yes_no.return_value = True

# -
# FUNÇÃO PARA ATIVAR OS MOCKS GLOBAIS
# -
def setup_global_mocks():
    """Injeta os mocks no sys.modules. Deve ser chamado antes dos imports dos testes."""
    sys.modules['config'] = MockConfig()
    sys.modules['logging'] = MagicMock()
    sys.modules['logging'].getLogger.return_value = MockLogger("mock_logger")

    # Módulos da aplicação a serem substituídos por mocks
    if 'persistencia.database' not in sys.modules: sys.modules['persistencia.database'] = MagicMock()
    sys.modules['persistencia.database'].DatabaseManager = MockDatabaseManager