# test_data_service.py
import unittest
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError

import mock_dependencies

mock_dependencies.setup_global_mocks()

from persistencia.data_service import DataService


class TestDataService(unittest.TestCase):

    @patch('persistencia.data_service.GenericRepository')
    def test_reclassificar_e_logar_success(self, mock_repo):
        """Verifica a transação de reclassificação com sucesso."""
        mock_repo.update_table.return_value = 1  # Simula 1 linha atualizada

        sucesso, _ = DataService.reclassificar_e_logar("Python", "Nova", "testuser")

        self.assertTrue(sucesso)
        mock_repo.update_table.assert_called_once()
        mock_repo.write_dataframe_to_table.assert_called_once()

    @patch('persistencia.data_service.GenericRepository')
    def test_reclassificar_e_logar_rollback_on_update_fail(self, mock_repo):
        """Verifica o rollback se a atualização falhar (0 linhas afetadas)."""
        mock_repo.update_table.return_value = 0  # Simula falha na atualização

        sucesso, mensagem = DataService.reclassificar_e_logar("Inexistente", "Nova", "testuser")

        self.assertFalse(sucesso)
        self.assertIn("não encontrada para atualização", mensagem)
        mock_repo.write_dataframe_to_table.assert_not_called()  # O log não deve ser escrito

    @patch('persistencia.data_service.GenericRepository')
    def test_rename_especie_gato_e_logar_rollback_on_log_fail(self, mock_repo):
        """Verifica o rollback se a escrita do log falhar."""
        mock_repo.update_table.return_value = 1
        mock_repo.write_dataframe_to_table.side_effect = SQLAlchemyError("Falha no Log")

        sucesso, mensagem = DataService.rename_especie_gato_e_logar("Antigo", "Novo", "testuser")

        self.assertFalse(sucesso)
        self.assertIn("A operação foi revertida", mensagem)