# utilParaDesenvolvimento/toolTestU/mock_dependencies.py
import sys
import tkinter as tk
from unittest.mock import MagicMock, create_autospec
from pathlib import Path
from sqlalchemy import create_engine, text

# CORRIGIDO: Importa as classes de View corretas e atuais do projeto.
from panels.painel_vegetais_auditoria_view import VegetaisAuditoriaView
from modals.tipos_vegetais_view import TiposVegetaisView
from panels.painel_gestao_gatos_view import GestaoGatosView
from panels.painel_modelo_view import ModeloView


# --- MOCKS DE INFRAESTRUTURA ---

class MockLogger(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.info = MagicMock()
        self.warning = MagicMock()
        self.error = MagicMock()
        self.critical = MagicMock()


class MockConfig:
    DATABASE_ENABLED = True
    INITIALIZE_DATABASE_ON_STARTUP = True
    USE_LOGIN = True
    REDIRECT_CONSOLE_TO_LOG = False
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(message)s'


# --- MOCKS DE INTERFACE GRÁFICA (GUI) ---

class MockMessageBox:
    def __init__(self):
        self.log = []

    def showinfo(self, title, message, **kwargs):
        self.log.append(f"INFO: {title} - {message}")

    def showwarning(self, title, message, **kwargs):
        self.log.append(f"WARNING: {title} - {message}")

    def showerror(self, title, message, **kwargs):
        self.log.append(f"ERROR: {title} - {message}")

    def askyesno(self, title, message, **kwargs):
        self.log.append(f"ASKYESNO: {title} - {message}")
        return True


# CORRIGIDO: Mocks de View atualizados para os nomes corretos e mais claros.
MockVegetaisAuditoriaView = create_autospec(VegetaisAuditoriaView, instance=True)
MockTiposVegetaisView = create_autospec(TiposVegetaisView, instance=True)
MockGestaoGatosView = create_autospec(GestaoGatosView, instance=True)
MockModeloView = create_autospec(ModeloView, instance=True)


class MockAppController:
    def get_current_user(self):
        return {'username': 'testuser', 'name': 'Usuário de Teste', 'access_level': 'Administrador Global'}


# --- LÓGICA DO BANCO DE DADOS EM MEMÓRIA ---

def setup_test_database():
    engine = create_engine("sqlite:///:memory:")
    try:
        # Aponta para o diretório correto do projeto para encontrar o schema
        project_root = Path(__file__).parent.parent.parent.resolve()
        schema_path = project_root / "persistencia/sql_schema_SQLLite.sql"

        with engine.connect() as connection:
            schema_sql = schema_path.read_text(encoding='utf-8')
            for command in schema_sql.split(';'):
                if command.strip():
                    connection.execute(text(command))
            connection.commit()
    except Exception as e:
        print(f"ERRO CRÍTICO AO CONFIGURAR BANCO DE DADOS DE TESTE: {e}")
        raise
    return engine


# --- FUNÇÃO DE SETUP GLOBAL ---

def setup_global_mocks():
    sys.modules['config'] = MockConfig()

    if 'logging' not in sys.modules:
        sys.modules['logging'] = MagicMock()
    sys.modules['logging'].getLogger.return_value = MockLogger("mock_logger")

    mock_db_manager = MagicMock()
    # Garante que todas as chamadas para get_engine() usem o mesmo banco em memória
    mock_db_manager.get_engine.return_value = setup_test_database()

    # Aplica o patch em todos os lugares onde DatabaseManager pode ser importado
    sys.modules['persistencia.database'] = MagicMock(DatabaseManager=mock_db_manager)
    sys.modules['persistencia.repository'] = MagicMock(DatabaseManager=mock_db_manager)
    sys.modules['persistencia.data_service'] = MagicMock(DatabaseManager=mock_db_manager)
    sys.modules['persistencia.auth'] = MagicMock(DatabaseManager=mock_db_manager)