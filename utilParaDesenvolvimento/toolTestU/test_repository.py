# utilParaDesenvolvimento/toolTestU/test_repository.py
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
        self.addCleanup(self.db_patcher.stop)

    def test_read_table_retorna_colunas_em_minusculas(self):
        # Este teste valida a nova funcionalidade de padronização
        df = GenericRepository.read_table_to_dataframe("ESPECIE_GATOS")
        self.assertFalse(df.empty)
        self.assertTrue(all(col.islower() for col in df.columns))
        self.assertIn('nome_especie', df.columns)

    def test_ciclo_de_escrita_e_leitura(self):
        # CORRIGIDO: Testa o ciclo na nova tabela 'tipos_vegetais'
        df_to_write = pd.DataFrame([{'NOME': 'Novo Tipo de Vegetal'}])

        GenericRepository.write_dataframe_to_table(df_to_write, "tipos_vegetais")

        # A condição WHERE deve usar a coluna em maiúsculas
        df_read = GenericRepository.read_table_to_dataframe(
            "tipos_vegetais", where_conditions={'NOME': 'Novo Tipo de Vegetal'})

        self.assertEqual(len(df_read), 1)
        # A leitura do DataFrame deve ter a coluna em minúsculas
        self.assertEqual(df_read.iloc[0]['nome'], 'Novo Tipo de Vegetal')

    def test_update_table_atualiza_registro(self):
        # CORRIGIDO: Usa nomes de coluna em maiúsculas para as chaves
        GenericRepository.update_table(
            "ESPECIE_GATOS",
            update_values={'TEMPERAMENTO': 'Extremamente falante'},
            where_conditions={'ID': 1}
        )

        df = GenericRepository.read_table_to_dataframe("especie_gatos", where_conditions={'ID': 1})
        # A leitura do DataFrame tem a coluna em minúsculas
        self.assertEqual(df.iloc[0]['temperamento'], 'Extremamente falante')

    def test_delete_from_table_remove_registro(self):
        # CORRIGIDO: Usa nome da coluna em maiúsculas para a chave
        GenericRepository.delete_from_table("ESPECIE_GATOS", where_conditions={'ID': 2})

        df = GenericRepository.read_table_to_dataframe("especie_gatos", where_conditions={'ID': 2})
        self.assertTrue(df.empty)