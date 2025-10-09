# test_painel_modelo_controller.py (Corrigido)
import unittest
import tkinter as tk
from unittest.mock import patch
import sys
import os

# Importa o mock_dependencies.py
sys.path.insert(0, os.path.dirname(__file__))
import mock_dependencies
from panels.painel_modelo_controller import PainelModelo


class TestPainelModelo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk();
        cls.root.withdraw()

    def setUp(self):
        with patch('panels.painel_modelo_controller.ModeloView', mock_dependencies.MockViewBase):
            self.controller = PainelModelo(self.root, mock_dependencies.MockAppController())
            self.controller.create_widgets()

        self.messagebox_patcher = patch('panels.painel_modelo_controller.messagebox')
        self.messagebox_mock = self.messagebox_patcher.start()

    def tearDown(self):
        self.messagebox_patcher.stop()

    def test_on_botao_click(self):
        """Testa se o evento do botão exibe a mensagem correta."""
        self.controller._on_botao_click()
        expected_message = (
            "Olá, Usuário de Teste!\n\n"
            "O painel modelo no padrão MVC está funcionando corretamente."
        )
        self.messagebox_mock.showinfo.assert_called_with(
            "Interação Funcionou!",
            expected_message,
            parent=self.controller
        )

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()


if __name__ == '__main__':
    unittest.main()