# mock_dependencies.py (Versão Final com Mocks Específicos)
import pandas as pd
from unittest.mock import MagicMock, create_autospec
from sqlalchemy import create_engine, text
import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import persistencia.auth as auth_utils
# Importa as classes reais da View para criar mocks mais precisos
from panels.painel_auditoria_view import AuditoriaView
from modals.tipos_linguagem_view import TiposLinguagemView
from panels.painel_catalogo_mvc_view import CatalogoEspeciesView
from panels.painel_modelo_view import ModeloView

# --- MOCKS DE INFRAESTRUTURA ---
class MockLogger(MagicMock):
    # ... (código inalterado) ...
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.info, self.warning, self.error, self.critical = MagicMock(), MagicMock(), MagicMock(), MagicMock()

class MockConfig: # ... (código inalterado) ...
    DATABASE_ENABLED, INITIALIZE_DATABASE_ON_STARTUP, USE_LOGIN = True, True, True
    REDIRECT_CONSOLE_TO_LOG, LOG_LEVEL, LOG_FORMAT = False, 'INFO', '%(message)s'

# --- MOCKS DE GUI ---
class MockMessageBox:
    def __init__(self): self.log = []
    def showinfo(self, title, message, **kwargs): self.log.append(f"INFO: {title} - {message}")
    def showwarning(self, title, message, **kwargs): self.log.append(f"WARNING: {title} - {message}")
    def showerror(self, title, message, **kwargs): self.log.append(f"ERROR: {title} - {message}")
    def askyesno(self, title, message, **kwargs):
        self.log.append(f"ASKYESNO: {title} - {message}"); return True

# --- NOVO: Mocks de View específicos e auto-especificados ---
# create_autospec garante que o mock tenha exatamente os mesmos métodos e atributos da classe real.
MockAuditoriaView = create_autospec(AuditoriaView, instance=True)
MockTiposLinguagemView = create_autospec(TiposLinguagemView, instance=True)
MockCatalogoEspeciesView = create_autospec(CatalogoEspeciesView, instance=True)
MockModeloView = create_autospec(ModeloView, instance=True)

class MockAppController: # ... (código inalterado) ...
    def get_current_user(self): return {'username': 'testuser', 'name': 'Usuário de Teste', 'access_level': 'Administrador Global'}

# --- LÓGICA DO BANCO DE DADOS EM MEMÓRIA ---
def setup_test_database():
    engine = create_engine("sqlite:///:memory:")
    project_root = Path(__file__).parent.parent.parent
    schema_path = project_root / "persistencia/sql_schema_SQLLite.sql"
    with engine.connect() as connection:
        schema_sql = schema_path.read_text(encoding='utf-8')
        for command in schema_sql.split(';'):
            if command.strip(): connection.execute(text(command))
        connection.commit()
    return engine

# --- FUNÇÃO PRINCIPAL DE MOCKING ---
def setup_global_mocks():
    sys.modules['config'] = MockConfig()
    sys.modules['logging'] = MagicMock()
    sys.modules['logging'].getLogger.return_value = MockLogger("mock_logger")
    mock_db_manager = MagicMock()
    mock_db_manager.get_engine.return_value = setup_test_database()
    if 'persistencia.database' not in sys.modules:
        sys.modules['persistencia.database'] = MagicMock()
    sys.modules['persistencia.database'].DatabaseManager = mock_db_manager