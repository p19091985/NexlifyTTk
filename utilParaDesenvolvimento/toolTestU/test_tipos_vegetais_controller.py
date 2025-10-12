# utilParaDesenvolvimento/toolTestU/test_tipos_vegetais_controller.py
import unittest
import tkinter as tk
from unittest.mock import patch

import mock_dependencies

mock_dependencies.setup_global_mocks()

from modals.tipos_vegetais_controller import TiposVegetaisController
from persistencia.repository import GenericRepository


class TestTiposVegetaisController(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

        self.engine = mock_dependencies.setup_test_database()

        # Garante que o repositório dentro do Model use o engine de teste
        self.repo_patcher = patch('modals.tipos_vegetais_model.GenericRepository.get_engine', return_value=self.engine)
        self.repo_patcher.start()
        self.addCleanup(self.repo_patcher.stop)

        # Mock da View
        self.view_patcher = patch('modals.tipos_vegetais_controller.TiposVegetaisView',
                                  new_callable=mock_dependencies.MockTiposVegetaisView)
        self.mock_view_instance = self.view_patcher.start()
        self.addCleanup(self.view_patcher.stop)

        self.controller = TiposVegetaisController(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_save_item_cria_novo_registro(self):
        self.controller.view.get_form_data.return_value = {'nome': 'Leguminosas'}
        self.controller.selected_item_id = None

        self.controller.save_item()

        # Verifica se o dado foi inserido no banco
        df = GenericRepository.read_table_to_dataframe("tipos_vegetais", where_conditions={'NOME': 'Leguminosas'})
        self.assertEqual(len(df), 1)
        # Verifica se a UI foi notificada
        self.controller.view.show_info.assert_called_with("Sucesso", "Tipo cadastrado!")

    def test_delete_item_remove_registro_apos_confirmacao(self):
        # Garante que o item com ID 1 ('Raízes e Tubérculos') existe
        df_before = GenericRepository.read_table_to_dataframe("tipos_vegetais", where_conditions={'ID': 1})
        self.assertEqual(len(df_before), 1)

        self.controller.view.ask_yes_no.return_value = True  # Simula o "Sim" do usuário
        self.controller.selected_item_id = 1

        self.controller.delete_item()

        # Verifica se o item foi removido do banco
        df_after = GenericRepository.read_table_to_dataframe("tipos_vegetais", where_conditions={'ID': 1})
        self.assertTrue(df_after.empty)