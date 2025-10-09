# test_tipos_linguagem_controller.py
import unittest
import tkinter as tk
from unittest.mock import patch, MagicMock

import mock_dependencies

mock_dependencies.setup_global_mocks()

from modals.tipos_linguagem_controller import TiposLagemController


# Mock do Model específico para este teste
class MockTiposLinguagemModel:
    def __init__(self): self.data = [
        {'id': 1, 'nome': 'Funcional'}]; self.add_tipo = MagicMock(); self.delete_tipo = MagicMock()

    def get_all_tipos(self): return self.data


@patch('modals.tipos_linguagem_controller.TiposLinguagemView', mock_dependencies.MockViewBase)
@patch('modals.tipos_linguagem_controller.TiposLinguagemModel', MockTiposLinguagemModel)
class TestTiposLinguagemController(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk();
        self.root.withdraw()
        self.controller = TiposLagemController(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_save_item_novo(self):
        """Testa o salvamento de um novo item."""
        self.controller.selected_item_id = None
        self.controller.view.get_form_data.return_value = {'nome': 'Lógica'}
        self.controller.save_item()
        self.controller.model.add_tipo.assert_called_with('Lógica')
        self.controller.view.show_info.assert_called_with("Sucesso", "Tipo cadastrado!")

    def test_delete_item_confirmado(self):
        """Testa a exclusão de um item com confirmação."""
        self.controller.selected_item_id = 1
        self.controller.view.ask_yes_no.return_value = True
        self.controller.delete_item()
        self.controller.model.delete_tipo.assert_called_with(1)