import sys
import tkinter as tk
from tkinter import ttk
from unittest.mock import MagicMock, create_autospec
from pathlib import Path
from sqlalchemy import create_engine, text

# Importa as classes reais para criar mocks com a mesma "assinatura" (métodos e atributos),
# o que torna os testes mais seguros contra futuras alterações no código original.
from panels.painel_auditoria_view import AuditoriaView
from modals.tipos_linguagem_view import TiposLinguagemView
from panels.painel_catalogo_mvc_view import CatalogoEspeciesView
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


# Mocks de View específicos e auto-especificados via create_autospec
# Isso garante que o mock se comportará exatamente como a classe real,
# lançando um erro se um método inexistente for chamado.
MockAuditoriaView = create_autospec(AuditoriaView, instance=True)
MockTiposLinguagemView = create_autospec(TiposLinguagemView, instance=True)
MockCatalogoEspeciesView = create_autospec(CatalogoEspeciesView, instance=True)
MockModeloView = create_autospec(ModeloView, instance=True)


class MockAppController:
    def get_current_user(self):
        return {'username': 'testuser', 'name': 'Usuário de Teste', 'access_level': 'Administrador Global'}


# --- LÓGICA DO BANCO DE DADOS EM MEMÓRIA ---

def setup_test_database():
    engine = create_engine("sqlite:///:memory:")
    try:
        current_dir = Path(__file__).parent.parent
        project_root = current_dir.parent
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
    mock_db_manager.get_engine.return_value = setup_test_database()

    if 'persistencia.database' not in sys.modules:
        sys.modules['persistencia.database'] = MagicMock()
    sys.modules['persistencia.database'].DatabaseManager = mock_db_manager