import unittest
from unittest.mock import patch
import pandas as pd

import mock_dependencies

mock_dependencies.setup_global_mocks()

from persistencia.repository import GenericRepository


class TestGenericRepository(unittest.TestCase):

    def setUp(self):
        self.engine = mock_dependencies.setup_test_database()
        self.db_patcher = patch('persistencia.repository.DatabaseManager.get_engine', return_value=self.engine)
        self.db_patcher.start()

    def tearDown(self):
        self.db_patcher.stop()

    def test_read_table_retorna_colunas_em_minusculas(self):
        df = GenericRepository.read_table_to_dataframe("ESPECIE_GATOS")
        self.assertFalse(df.empty)
        self.assertTrue(all(col.islower() for col in df.columns))
        self.assertIn('nome_especie', df.columns)

    def test_ciclo_de_escrita_e_leitura(self):
        df_to_write = pd.DataFrame(
            [{'nome': 'Nova Linguagem', 'id_tipo': 1, 'ano_criacao': 2025, 'categoria': 'Teste'}])

        success = GenericRepository.write_dataframe_to_table(df_to_write, "linguagens_programacao")
        self.assertTrue(success)

        df_read = GenericRepository.read_table_to_dataframe(
            "linguagens_programacao", where_conditions={'nome': 'Nova Linguagem'})

        self.assertEqual(len(df_read), 1)
        self.assertEqual(df_read.iloc[0]['ano_criacao'], 2025)

    def test_update_table_atualiza_registro(self):
        rows_affected = GenericRepository.update_table(
            "especie_gatos",
            update_values={'temperamento': 'Extremamente falante'},
            where_conditions={'id': 1}
        )
        self.assertEqual(rows_affected, 1)

        df = GenericRepository.read_table_to_dataframe("especie_gatos", where_conditions={'id': 1})
        self.assertEqual(df.iloc[0]['temperamento'], 'Extremamente falante')

    def test_delete_from_table_remove_registro(self):
        rows_affected = GenericRepository.delete_from_table("especie_gatos", where_conditions={'id': 2})
        self.assertEqual(rows_affected, 1)

        df = GenericRepository.read_table_to_dataframe("especie_gatos", where_conditions={'id': 2})
        self.assertTrue(df.empty)

    def test_delete_from_table_lanca_erro_sem_clausula_where(self):
        with self.assertRaises(ValueError):
            GenericRepository.delete_from_table("qualquer_tabela", where_conditions={})