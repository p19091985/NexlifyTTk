import unittest
import tkinter as tk
from unittest.mock import patch

from persistencia.database import DatabaseManager
import mock_dependencies

mock_dependencies.setup_global_mocks()

from modals.tipos_linguagem_controller import TiposLinguagemController
from persistencia.repository import GenericRepository


class TestTiposLinguagemController(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

        DatabaseManager._engine = None

        self.engine = mock_dependencies.setup_test_database()

        self.db_patcher = patch('persistencia.repository.DatabaseManager.get_engine', return_value=self.engine)
        self.addCleanup(self.db_patcher.stop)
        self.db_patcher.start()

        self.view_patcher = patch('modals.tipos_linguagem_controller.TiposLinguagemView')
        mock_view_class = self.view_patcher.start()
        self.addCleanup(self.view_patcher.stop)

        mock_view_instance = mock_dependencies.MockTiposLinguagemView
        mock_view_class.return_value = mock_view_instance

        self.controller = TiposLinguagemController(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_save_item_cria_novo_registro(self):
        self.controller.view.get_form_data.return_value = {'nome': 'Lógica'}
        self.controller.selected_item_id = None

        self.controller.save_item()

        df = GenericRepository.read_table_to_dataframe("tipos_linguagem", where_conditions={'NOME': 'Lógica'})
        self.assertEqual(len(df), 1)
        self.controller.view.show_info.assert_called_with("Sucesso", "Tipo cadastrado!")

    def test_delete_item_remove_registro_apos_confirmacao(self):
        df_before = GenericRepository.read_table_to_dataframe("tipos_linguagem", where_conditions={'ID': 1})
        self.assertEqual(len(df_before), 1)

        self.controller.view.ask_yes_no.return_value = True
        self.controller.selected_item_id = 1

        self.controller.delete_item()

        df_after = GenericRepository.read_table_to_dataframe("tipos_linguagem", where_conditions={'ID': 1})
        self.assertTrue(df_after.empty)