                                                        
import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError

import mock_dependencies

mock_dependencies.setup_global_mocks()

from persistencia.data_service import DataService
from persistencia.repository import GenericRepository


class TestDataService(unittest.TestCase):

    def setUp(self):
        self.engine = mock_dependencies.setup_test_database()
        self.db_patcher = patch('persistencia.repository.GenericRepository.get_engine', return_value=self.engine)
        self.db_patcher.start()
        self.addCleanup(self.db_patcher.stop)

    def tearDown(self):
        pass

    def test_reclassificar_vegetal_e_logar_com_sucesso(self):
        sucesso, _ = DataService.reclassificar_vegetal_e_logar("Cenoura", "Legumes", "testuser")
        self.assertTrue(sucesso)

        df_veg = GenericRepository.read_vegetais_com_tipo()
        cenoura_record = df_veg[df_veg['nome'] == 'Cenoura']
        self.assertEqual(cenoura_record.iloc[0]['tipo'], 'Legumes')

        df_log = GenericRepository.read_table_to_dataframe("log_alteracoes",
                                                           where_conditions={'LOGIN_USUARIO': 'testuser'})
        self.assertTrue(any("reclassificado" in log for log in df_log['acao']))

    def test_reclassificar_vegetal_e_logar_falha_se_vegetal_nao_existe(self):
        sucesso, mensagem = DataService.reclassificar_vegetal_e_logar("Vegetal Inexistente", "Frutos", "testuser")
        self.assertFalse(sucesso)
        self.assertIn("'Vegetal Inexistente' não encontrado", mensagem)

        df_log_after = GenericRepository.read_table_to_dataframe("log_alteracoes")
        self.assertTrue(df_log_after.empty)

    @patch('sqlalchemy.engine.base.Connection.execute')
    def test_rename_especie_gato_e_logar_executa_rollback_se_log_falhar(self, mock_execute):
                                                                                            
                                                                                  
        mock_execute.side_effect = [
            MagicMock(first=lambda: None),                                     
            MagicMock(rowcount=1),                                    
            SQLAlchemyError("Simulação de falha no disco de log")                          
        ]

        sucesso, mensagem = DataService.rename_especie_gato_e_logar("Siamês", "Siamês Novo", "testuser")

        self.assertFalse(sucesso)
        self.assertIn("Ocorreu um erro no banco de dados", mensagem)