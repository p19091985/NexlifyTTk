import unittest
from unittest.mock import patch, mock_open
from pathlib import Path

import mock_dependencies
mock_dependencies.setup_global_mocks()

from persistencia.database import DatabaseManager

class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        DatabaseManager._engine = None

    @patch('persistencia.database.config.DATABASE_ENABLED', False)
    def test_get_engine_retorna_none_se_banco_desabilitado(self):
        engine = DatabaseManager.get_engine()
        self.assertIsNone(engine)

    @patch("builtins.open", new_callable=mock_open, read_data="[sqlite]\ntype=sqlite\npath=NexlifyTTk.db")
    def test_parse_active_config_identifica_config_do_arquivo_mockado(self, mock_file):
        config = DatabaseManager._parse_active_config()
        self.assertIsNotNone(config)
        self.assertEqual(config.get('type'), 'sqlite')
        self.assertEqual(config.get('path'), 'NexlifyTTk.db')

    @patch('persistencia.database.decrypt_message', return_value='senha_decifrada')
    @patch('persistencia.database.create_engine')
    @patch('persistencia.database.DatabaseManager._parse_active_config')
    def test_get_engine_cria_engine_para_postgresql(self, mock_parse_config, mock_create_engine, mock_decrypt):
        mock_parse_config.return_value = {
            'type': 'postgresql', 'user': 'gato', 'password': 'mock_password',
            'host': 'localhost', 'port': '5432', 'dbname': 'NexlifyTTk'
        }
        mock_create_engine.return_value.connect.return_value.__enter__.return_value = None

        DatabaseManager.get_engine()

                                                                                          
                                                          
        expected_url = "postgresql+psycopg2://senha_decifrada:senha_decifrada@localhost:5432/NexlifyTTk"
        mock_create_engine.assert_called_with(expected_url, echo=False)