import unittest
import tkinter as tk
from unittest.mock import patch

import mock_dependencies

mock_dependencies.setup_global_mocks()

from panels.painel_auditoria_controller import PainelAuditoria
from persistencia.repository import GenericRepository


class TestPainelAuditoriaController(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.engine = mock_dependencies.setup_test_database()

        messagebox_patcher = patch('panels.painel_auditoria_controller.messagebox',
                                   new_callable=mock_dependencies.MockMessageBox)
        db_patcher = patch('persistencia.database.DatabaseManager.get_engine', return_value=self.engine)
        view_patcher = patch('panels.painel_auditoria_controller.AuditoriaView',
                             new_callable=mock_dependencies.MockAuditoriaView)

        self.addCleanup(messagebox_patcher.stop)
        self.addCleanup(db_patcher.stop)
        self.addCleanup(view_patcher.stop)

        messagebox_patcher.start()
        db_patcher.start()
        view_patcher.start()

        self.controller = PainelAuditoria(self.root, mock_dependencies.MockAppController())
        self.view = self.controller.view

    def tearDown(self):
        self.root.destroy()

    def test_carregar_dados_iniciais_popula_view(self):
        self.controller._carregar_dados_iniciais()

        self.assertEqual(self.view.linguagens_tree.insert.call_count, 5)
        self.assertIn('Python', self.view.linguagem_combo['values'])
        self.assertEqual(self.view.log_tree.insert.call_count, 0)

    def test_executar_transacao_com_sucesso_atualiza_banco_e_log(self):
        self.controller.linguagem_selecionada_var.set("Python")
        self.controller.nova_categoria_var.set("Linguagem Divina")

        # Simular a confirmação do usuário na caixa de diálogo
        self.controller.app.messagebox.askyesno = lambda title, message, **kwargs: True

        self.controller._executar_transacao()

        df_lang = GenericRepository.read_table_to_dataframe("linguagens_programacao",
                                                            where_conditions={'nome': 'Python'})
        self.assertEqual(df_lang.iloc[0]['categoria'], "Linguagem Divina")

        df_log = GenericRepository.read_table_to_dataframe("log_alteracoes")
        self.assertEqual(len(df_log), 1)
        self.assertIn("Reclassificou 'Python' para 'Linguagem Divina'", df_log.iloc[-1]['acao'])