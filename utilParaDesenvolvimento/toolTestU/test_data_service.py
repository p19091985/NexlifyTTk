# test_data_service.py (Reescrito para o DB em Memória)
import unittest
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError

# Configura o ambiente de teste
import mock_dependencies
mock_dependencies.setup_global_mocks()

from persistencia.data_service import DataService
from persistencia.repository import GenericRepository

# --- REESCRITO: Testa as transações contra um banco de dados real em memória ---
class TestDataService(unittest.TestCase):

    def setUp(self):
        """Prepara o banco de dados em memória para cada teste."""
        self.engine = mock_dependencies.setup_test_database()
        self.db_manager_patch = patch('persistencia.data_service.DatabaseManager.get_engine', return_value=self.engine)
        self.db_manager_patch.start()

    def tearDown(self):
        self.db_manager_patch.stop()

    def test_reclassificar_e_logar_success(self):
        """Verifica a transação de reclassificação com sucesso."""
        # Ação
        sucesso, _ = DataService.reclassificar_e_logar("Python", "Linguagem de Alto Nível", "testuser")
        self.assertTrue(sucesso)

        # Verificação 1: A linguagem foi atualizada
        df_lang = GenericRepository.read_table_to_dataframe("linguagens_programacao", where_conditions={'nome': 'Python'})
        self.assertEqual(df_lang.iloc[0]['categoria'], 'Linguagem de Alto Nível')

        # Verificação 2: O log foi criado
        df_log = GenericRepository.read_table_to_dataframe("log_alteracoes", where_conditions={'login_usuario': 'testuser'})
        self.assertTrue(any("Reclassificou 'Python'" in log for log in df_log['acao']))

    def test_reclassificar_e_logar_rollback_on_update_fail(self):
        """Verifica o rollback se a atualização falhar (linguagem não encontrada)."""
        # Ação
        sucesso, mensagem = DataService.reclassificar_e_logar("Linguagem Inexistente", "Nova", "testuser")
        self.assertFalse(sucesso)
        self.assertIn("não encontrada para atualização", mensagem)

        # Verificação: Nenhum log deve ter sido criado
        df_log_after = GenericRepository.read_table_to_dataframe("log_alteracoes")
        self.assertTrue(df_log_after.empty)

    @patch('persistencia.data_service.GenericRepository.write_dataframe_to_table')
    def test_rename_especie_gato_e_logar_rollback_on_log_fail(self, mock_write_log):
        """Verifica o rollback se a escrita do log falhar."""
        # Preparação: Força a falha apenas na escrita do log
        mock_write_log.side_effect = SQLAlchemyError("Simulação de falha no disco de log")

        # Ação
        sucesso, mensagem = DataService.rename_especie_gato_e_logar("Siamês", "Siamês Novo", "testuser")
        self.assertFalse(sucesso)
        self.assertIn("A operação foi revertida", mensagem)

        # Verificação: O nome do gato NÃO deve ter sido alterado no banco (rollback funcionou)
        df_gato = GenericRepository.read_table_to_dataframe("especie_gatos", where_conditions={'nome_especie': 'Siamês'})
        self.assertEqual(len(df_gato), 1, "O nome do gato foi alterado, o rollback falhou.")