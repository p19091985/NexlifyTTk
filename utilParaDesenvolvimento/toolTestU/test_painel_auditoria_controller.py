# test_painel_auditoria_controller.py (Corrigido)
import unittest
import tkinter as tk
from unittest.mock import patch
import sys
import os

# Importa o mock_dependencies.py
sys.path.insert(0, os.path.dirname(__file__))
import mock_dependencies
from panels.painel_auditoria_controller import PainelAuditoria


class TestPainelAuditoria(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk();
        cls.root.withdraw()

    def setUp(self):
        with patch('panels.painel_auditoria_controller.AuditoriaView', mock_dependencies.MockViewBase):
            self.controller = PainelAuditoria(self.root, mock_dependencies.MockAppController())
            self.controller.create_widgets()

        #  Patching dos métodos de classe
        self.read_lang_patcher = patch('panels.painel_auditoria_controller.GenericRepository.read_table_to_dataframe')
        self.read_log_patcher = patch('panels.painel_auditoria_controller.GenericRepository.read_table_to_dataframe')
        self.service_patcher = patch('panels.painel_auditoria_controller.DataService.reclassificar_e_logar')
        self.messagebox_patcher = patch('panels.painel_auditoria_controller.messagebox')

        self.read_lang_mock = self.read_lang_patcher.start()
        self.read_log_mock = self.read_log_patcher.start()
        self.service_mock = self.service_patcher.start()
        self.messagebox_mock = self.messagebox_patcher.start()

        # Simula o retorno de dados para as cargas
        self.read_lang_mock.side_effect = [
            mock_dependencies.MOCK_DF_LINGUAGENS.copy(),  # 1ª chamada: linguagens
            mock_dependencies.MOCK_DF_LOG.copy()  # 2ª chamada: log
        ]
        self.service_mock.return_value = (True, "Reclassificação OK")
        self.messagebox_mock.askyesno.return_value = True

    def tearDown(self):
        self.read_lang_patcher.stop();
        self.read_log_patcher.stop()
        self.service_patcher.stop();
        self.messagebox_patcher.stop()

    def test_carregar_linguagens_e_log(self):
        """Testa se as linguagens e o log são carregados."""
        self.controller._carregar_dados_iniciais()
        # Não é assert_called_with pois o método é chamado duas vezes pelo side_effect
        self.assertEqual(self.read_lang_mock.call_count, 2)
        self.assertIn('Python', self.controller.view.linguagem_combo['values'])

    def test_executar_transacao_sucesso(self):
        """Testa a transação de reclassificar e logar com sucesso."""
        self.controller.linguagem_selecionada_var.set("Python")
        self.controller.nova_categoria_var.set("Compilada e Interpretada")
        self.controller._executar_transacao()
        self.service_mock.assert_called_with("Python", "Compilada e Interpretada", 'testuser')

    def test_executar_transacao_falha_dados_incompletos(self):
        """Testa a transação com dados incompletos (sem linguagem)."""
        self.controller.linguagem_selecionada_var.set("")
        self.controller.nova_categoria_var.set("Nova")
        self.controller._executar_transacao()
        self.messagebox_mock.showwarning.assert_called()
        self.assertFalse(self.service_mock.called)

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()


if __name__ == '__main__':
    unittest.main()