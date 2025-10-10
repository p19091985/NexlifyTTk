# test_tipos_linguagem_controller.py (Versão Final Corrigida)
import unittest
import tkinter as tk
from unittest.mock import patch
import sys
import os

# Configura o ambiente de teste
sys.path.insert(0, os.path.dirname(__file__))
import mock_dependencies

mock_dependencies.setup_global_mocks()

from modals.tipos_linguagem_controller import TiposLinguagemController
from persistencia.repository import GenericRepository


class TestTiposLinguagemController(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

        self.engine = mock_dependencies.setup_test_database()

        db_patcher = patch('persistencia.database.DatabaseManager.get_engine', return_value=self.engine)
        view_patcher = patch('modals.tipos_linguagem_controller.TiposLinguagemView',
                             new_callable=mock_dependencies.MockTiposLinguagemView)

        self.addCleanup(db_patcher.stop)
        self.addCleanup(view_patcher.stop)

        db_patcher.start()
        view_patcher.start()

        self.controller = TiposLinguagemController(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_save_item_novo(self):
        """Testa o salvamento de um novo item e verifica no banco."""
        self.controller.view.get_form_data.return_value = {'nome': 'Lógica'}
        self.controller.selected_item_id = None

        # Ação
        self.controller.save_item()

        # Verificação no DB em memória
        df = GenericRepository.read_table_to_dataframe("tipos_linguagem", where_conditions={'nome': 'Lógica'})
        self.assertEqual(len(df), 1)
        self.controller.view.show_info.assert_called_with("Sucesso", "Tipo cadastrado!")

    def test_delete_item_confirmado(self):
        """Testa a exclusão de um item e verifica no banco."""
        df_before = GenericRepository.read_table_to_dataframe("tipos_linguagem", where_conditions={'id': 1})
        self.assertEqual(len(df_before), 1)

        self.controller.view.ask_yes_no.return_value = True
        self.controller.selected_item_id = 1

        # Ação
        self.controller.delete_item()

        # Verificação no DB em memória
        df_after = GenericRepository.read_table_to_dataframe("tipos_linguagem", where_conditions={'id': 1})
        self.assertTrue(df_after.empty)