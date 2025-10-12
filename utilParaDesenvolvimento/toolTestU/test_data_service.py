# utilParaDesenvolvimento/toolTestU/test_data_service.py
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
        # Garante que o DataService use o engine de teste
        self.db_patcher = patch('persistencia.data_service.GenericRepository.get_engine', return_value=self.engine)
        self.db_patcher.start()
        self.addCleanup(self.db_patcher.stop)

    def tearDown(self):
        pass  # O cleanup já é gerenciado pelo addCleanup

    def test_reclassificar_vegetal_e_logar_com_sucesso(self):
        # CORRIGIDO: Testa o novo método com dados de vegetais
        sucesso, _ = DataService.reclassificar_vegetal_e_logar("Cenoura", "Legumes", "testuser")
        self.assertTrue(sucesso)

        # Verifica se o vegetal foi atualizado corretamente
        df_veg = GenericRepository.read_vegetais_com_tipo()
        cenoura_record = df_veg[df_veg['nome'] == 'Cenoura']
        self.assertEqual(cenoura_record.iloc[0]['tipo'], 'Legumes')

        # Verifica se a auditoria foi registrada
        df_log = GenericRepository.read_table_to_dataframe("log_alteracoes",
                                                           where_conditions={'LOGIN_USUARIO': 'testuser'})
        self.assertTrue(any("Reclassificou 'Cenoura'" in log for log in df_log['acao']))

    def test_reclassificar_vegetal_e_logar_falha_se_vegetal_nao_existe(self):
        # CORRIGIDO: Testa o cenário de falha com vegetais
        sucesso, mensagem = DataService.reclassificar_vegetal_e_logar("Vegetal Inexistente", "Frutos", "testuser")
        self.assertFalse(sucesso)
        self.assertIn("'Vegetal Inexistente' não encontrado", mensagem)

        # Garante que nada foi logado
        df_log_after = GenericRepository.read_table_to_dataframe("log_alteracoes")
        self.assertTrue(df_log_after.empty)

    @patch('sqlalchemy.engine.base.Connection.execute')
    def test_rename_especie_gato_e_logar_executa_rollback_se_log_falhar(self, mock_execute):
        # Configura o mock para falhar na segunda chamada (o INSERT no log)
        mock_execute.side_effect = [
            MagicMock(rowcount=1),  # Simula sucesso no UPDATE
            SQLAlchemyError("Simulação de falha no disco de log")  # Simula falha no INSERT
        ]

        sucesso, mensagem = DataService.rename_especie_gato_e_logar("Siamês", "Siamês Novo", "testuser")

        self.assertFalse(sucesso)
        self.assertIn("Ocorreu um erro no banco de dados", mensagem)