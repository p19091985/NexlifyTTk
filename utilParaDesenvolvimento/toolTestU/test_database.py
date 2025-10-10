# test_database.py (Versão Final Corrigida)
import unittest
from unittest.mock import patch, mock_open
# --- CORREÇÃO: Não importa mais o mock_dependencies globalmente ---

# Importa a classe real a ser testada
from persistencia.database import DatabaseManager


class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        DatabaseManager._engine = None

    @patch('persistencia.database.config.DATABASE_ENABLED', False)
    def test_get_engine_database_disabled(self):
        """Verifica o retorno None quando o banco está desativado."""
        engine = DatabaseManager.get_engine()
        self.assertIsNone(engine)

    def test_parse_active_config_sqlite(self):
        """Verifica se o parser lê corretamente uma configuração SQLite ativa."""
        ini_content = "[SQLITE]\ntype = sqlite\npath = db/sistema.db"
        with patch('builtins.open', mock_open(read_data=ini_content)):
            with patch('pathlib.Path.is_file', return_value=True):
                config = DatabaseManager._parse_active_config()
                self.assertEqual(config['type'], 'sqlite')
                self.assertEqual(config['path'], 'db/sistema.db')

    @patch('persistencia.database.decrypt_message', return_value='decoded_pass')
    @patch('persistencia.database.create_engine')
    def test_get_engine_creates_postgresql_url(self, mock_create_engine, mock_decrypt):
        """Verifica se a URL de conexão para PostgreSQL é montada corretamente."""
        # A engine real não será criada, pois o create_engine está mockado
        mock_create_engine.return_value.connect.return_value.__enter__.return_value = None

        ini_content = "type = postgresql\nhost = localhost\nport = 5432\ndbname = testdb\nuser = testuser\npassword = encrypted"
        with patch('builtins.open', mock_open(read_data=ini_content)):
            with patch('pathlib.Path.is_file', return_value=True):
                DatabaseManager.get_engine()
                expected_url = "postgresql+psycopg2://testuser:decoded_pass@localhost:5432/testdb"
                # A asserção agora funciona, pois o teste está isolado
                mock_create_engine.assert_called_with(expected_url, echo=False)