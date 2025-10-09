# test_repository.py
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

# Mock apenas da camada de banco, para testar o repositório REAL
import mock_dependencies

mock_dependencies.setup_global_mocks()

from persistencia.repository import GenericRepository


class TestGenericRepository(unittest.TestCase):

    @patch('persistencia.repository.DatabaseManager')
    @patch('persistencia.repository.pd.read_sql')
    def test_read_table_to_dataframe_success(self, mock_read_sql, mock_db_manager):
        """Verifica se a leitura da tabela retorna colunas em minúsculas."""
        mock_db_manager.get_engine.return_value = mock_dependencies.MockEngine()
        mock_read_sql.return_value = mock_dependencies.MOCK_DF_GATOS.copy()

        df = GenericRepository.read_table_to_dataframe("ESPECIE_GATOS")

        self.assertFalse(df.empty)
        self.assertTrue(all(col.islower() for col in df.columns))
        mock_read_sql.assert_called()

    @patch('persistencia.repository.DatabaseManager')
    @patch('persistencia.repository.pd.DataFrame.to_sql')
    def test_write_dataframe_to_table_uppercase_columns(self, mock_to_sql, mock_db_manager):
        """Verifica se as colunas do DF são convertidas para maiúsculas antes de escrever."""
        mock_db_manager.get_engine.return_value = mock_dependencies.MockEngine()
        df_lowercase = pd.DataFrame([{'nome': ['Test'], 'id': [1]}])

        GenericRepository.write_dataframe_to_table(df_lowercase, "TEST_TABLE")

        # Acessa os argumentos com que a função mock foi chamada
        args, kwargs = mock_to_sql.call_args
        called_df = kwargs['con'].execute.call_args[0][0]  # Pega o dataframe que foi passado para a engine
        self.assertTrue(all(col.isupper() for col in called_df.columns))

    @patch('persistencia.repository.DatabaseManager')
    def test_delete_from_table_success(self, mock_db_manager):
        """Verifica se a deleção funciona com WHERE."""
        mock_engine = mock_dependencies.MockEngine()
        mock_db_manager.get_engine.return_value = mock_engine

        rows = GenericRepository.delete_from_table("ANY_TABLE", where_conditions={'id': 1})
        self.assertEqual(rows, 1)
        # Verifica se o 'execute' da engine mockada foi chamado
        mock_engine.connect().execute.assert_called()

    def test_delete_from_table_requires_where(self):
        """Verifica se a exclusão sem WHERE lança ValueError."""
        with self.assertRaises(ValueError):
            GenericRepository.delete_from_table("ANY_TABLE", where_conditions={})