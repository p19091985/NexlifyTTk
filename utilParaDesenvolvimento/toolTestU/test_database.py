import unittest
from unittest.mock import patch, mock_open
from pathlib import Path

from persistencia.database import DatabaseManager


class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        DatabaseManager._engine = None

    @patch('persistencia.database.config.DATABASE_ENABLED', False)
    def test_get_engine_retorna_none_se_banco_desabilitado(self):
        engine = DatabaseManager.get_engine()
        self.assertIsNone(engine)

    def test_parse_active_config_identifica_config_do_arquivo_real(self):
        project_root = Path(__file__).parent.parent.parent.resolve()
        ini_path = project_root / "banco.ini"

        with patch('persistencia.database.CONFIG_PATH', ini_path):
            config = DatabaseManager._parse_active_config()
            self.assertIsNotNone(config)
            self.assertEqual(config.get('type'), 'sqlite')
            self.assertEqual(config.get('path'), 'NexlifyTTk.db')

    @patch('persistencia.database.decrypt_message', return_value='senha_decifrada')
    @patch('persistencia.database.create_engine')
    def test_get_engine_cria_engine_para_config_ativa(self, mock_create_engine, mock_decrypt):
        mock_create_engine.return_value.connect.return_value.__enter__.return_value = None

        project_root = Path(__file__).parent.parent.parent.resolve()
        ini_path = project_root / "banco.ini"

        with patch('persistencia.database.CONFIG_PATH', ini_path):

            active_config = DatabaseManager._parse_active_config()
            active_type = active_config.get('type')

            DatabaseManager.get_engine()

            if active_type == 'sqlite':
                db_path = project_root / active_config.get('path')
                expected_url = f"sqlite:///{db_path}"
                mock_create_engine.assert_called_with(expected_url, echo=False, connect_args={'timeout': 15})

            elif active_type == 'postgresql':
                expected_url = "postgresql+psycopg2://gato:senha_decifrada@localhost:5432/NexlifyTTk"
                mock_create_engine.assert_called_with(expected_url, echo=False)

            elif active_type == 'sqlserver':
                expected_url = "mssql+pymssql://gato:senha_decifrada@10.77.77.189:1433/NexlifyTTk"
                mock_create_engine.assert_called_with(expected_url, echo=False)

            elif active_type == 'mysql':
                expected_url = "mysql+pymysql://gato:senha_decifrada@localhost:3306/NexlifyTTk"
                mock_create_engine.assert_called_with(expected_url, echo=False)

            else:
                self.skipTest(
                    f"O tipo de banco ativo '{active_type}' não possui um teste de URL específico implementado.")