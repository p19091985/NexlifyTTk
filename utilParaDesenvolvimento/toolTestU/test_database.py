# test_database.py (Corrigido)
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from pathlib import Path
import logging
from sqlalchemy.exc import OperationalError

# Importa o mock_dependencies.py
sys.path.insert(0, os.path.dirname(__file__))
import mock_dependencies

# Antes de importar o DatabaseManager real, corrige o mock no sys.modules
# Adiciona os métodos que estavam faltando no mock_dependencies.MockDatabaseManager
mock_dependencies.MockDatabaseManager.initialize_database = MagicMock(name='initialize_database')
mock_dependencies.MockDatabaseManager._parse_active_config = MagicMock(name='_parse_active_config')
mock_dependencies.MockDatabaseManager._parse_active_config.return_value = {'type': 'sqlite', 'path': 'test.db'}

# Agora importa a classe real que usa o mock injetado
from persistencia.database import DatabaseManager


class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        # Garante o estado inicial do mock
        mock_dependencies.MockDatabaseManager.set_engine_state('none')
        self.db_logger = logging.getLogger("persistencia.database")

    @patch('persistencia.database.config')
    def test_get_engine_database_disabled(self, mock_config):
        """Verifica o retorno None quando o banco está desativado."""
        mock_config.DATABASE_ENABLED = False
        engine = DatabaseManager.get_engine()
        self.assertIsNone(engine)  # Agora deve passar

    @patch('persistencia.database.logging')
    def test_get_engine_first_call_success(self, mock_logging):
        """Verifica a criação da engine na primeira chamada (SQLite)."""
        # O mock_dependencies.MockDatabaseManager._parse_active_config já está mockado
        with patch('persistencia.database.create_engine', return_value=mock_dependencies.MockEngine()):
            engine = DatabaseManager.get_engine()
            self.assertIsNotNone(engine)

    @patch('persistencia.database.logging')
    def test_initialize_database_engine_none(self, mock_logging):
        """Verifica o erro quando a engine não está disponível na inicialização."""
        # DatabaseManager.get_engine vai retornar None (configuração default do setUp)
        DatabaseManager.initialize_database()
        # O mock implementado no mock_dependencies.py é que deve ser rastreado
        mock_logging.error.assert_called_with("Não foi possível inicializar o banco: engine não disponível.")


if __name__ == '__main__':
    unittest.main()