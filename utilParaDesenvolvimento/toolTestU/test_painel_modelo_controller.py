import unittest
import tkinter as tk
from unittest.mock import patch

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

                                                                                   
        view_patcher = patch('panels.painel_modelo_controller.ModeloView', autospec=True)
        self.addCleanup(view_patcher.stop)
        self.mock_view_class = view_patcher.start()

        self.controller = PainelModelo(self.root, mock_dependencies.MockAppController())

    def test_on_botao_click_exibe_mensagem_correta(self):
        self.controller._on_botao_click()

        self.assertEqual(len(self.messagebox_mock.log), 1)
        self.assertIn("INFO: Interação Funcionou!", self.messagebox_mock.log[0])
        self.assertIn("Olá, Usuário de Teste!", self.messagebox_mock.log[0])

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()