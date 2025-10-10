import unittest
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError

import mock_dependencies
mock_dependencies.setup_global_mocks()

from persistencia.data_service import DataService
from persistencia.repository import GenericRepository

class TestDataService(unittest.TestCase):

    def setUp(self):
        self.engine = mock_dependencies.setup_test_database()
        self.db_patcher = patch('persistencia.data_service.DatabaseManager.get_engine', return_value=self.engine)
        self.db_patcher.start()

    def tearDown(self):
        self.db_patcher.stop()

    def test_reclassificar_e_logar_com_sucesso(self):
        sucesso, _ = DataService.reclassificar_e_logar("Python", "Linguagem de Alto Nível", "testuser")
        self.assertTrue(sucesso)

        df_lang = GenericRepository.read_table_to_dataframe("linguagens_programacao", where_conditions={'nome': 'Python'})
        self.assertEqual(df_lang.iloc[0]['categoria'], 'Linguagem de Alto Nível')

        df_log = GenericRepository.read_table_to_dataframe("log_alteracoes", where_conditions={'login_usuario': 'testuser'})
        self.assertTrue(any("Reclassificou 'Python'" in log for log in df_log['acao']))

    def test_reclassificar_e_logar_falha_se_linguagem_nao_existe(self):
        sucesso, mensagem = DataService.reclassificar_e_logar("Linguagem Inexistente", "Nova", "testuser")
        self.assertFalse(sucesso)
        self.assertIn("não encontrada para atualização", mensagem)

        df_log_after = GenericRepository.read_table_to_dataframe("log_alteracoes")
        self.assertTrue(df_log_after.empty)

    @patch('persistencia.data_service.GenericRepository.write_dataframe_to_table')
    def test_rename_especie_gato_e_logar_executa_rollback_se_log_falhar(self, mock_write_log):
        mock_write_log.side_effect = SQLAlchemyError("Simulação de falha no disco de log")

        sucesso, mensagem = DataService.rename_especie_gato_e_logar("Siamês", "Siamês Novo", "testuser")
        self.assertFalse(sucesso)
        self.assertIn("A operação foi revertida", mensagem)

        df_gato = GenericRepository.read_table_to_dataframe("especie_gatos", where_conditions={'nome_especie': 'Siamês'})
        self.assertEqual(len(df_gato), 1, "O nome do gato foi alterado, indicando que o rollback falhou.")