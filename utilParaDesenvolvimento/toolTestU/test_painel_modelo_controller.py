# test_painel_modelo_controller.py (Versão Final Corrigida)
import unittest
import tkinter as tk
from unittest.mock import patch
import sys
import os

# Configura o ambiente de teste
sys.path.insert(0, os.path.dirname(__file__))
import mock_dependencies

mock_dependencies.setup_global_mocks()

from panels.painel_modelo_controller import PainelModelo


class TestPainelModelo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()

    def setUp(self):
        self.messagebox_mock = mock_dependencies.MockMessageBox()
        messagebox_patcher = patch('panels.painel_modelo_controller.messagebox', self.messagebox_mock)
        self.addCleanup(messagebox_patcher.stop)
        messagebox_patcher.start()

        view_patcher = patch('panels.painel_modelo_controller.ModeloView',
                             new_callable=mock_dependencies.MockModeloView)
        self.addCleanup(view_patcher.stop)
        view_patcher.start()

        self.controller = PainelModelo(self.root, mock_dependencies.MockAppController())

    def test_on_botao_click(self):
        """Testa se o evento do botão gera a mensagem correta no log do mock."""
        self.controller._on_botao_click()

        # Verificação
        self.assertEqual(len(self.messagebox_mock.log), 1)
        self.assertIn("INFO: Interação Funcionou!", self.messagebox_mock.log[0])
        self.assertIn("Olá, Usuário de Teste!", self.messagebox_mock.log[0])

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()