# test_painel_auditoria_controller.py (Versão Final Corrigida)
import unittest
import tkinter as tk
from unittest.mock import patch
import sys
import os

# Configura o ambiente de teste
sys.path.insert(0, os.path.dirname(__file__))
import mock_dependencies

mock_dependencies.setup_global_mocks()

from panels.painel_auditoria_controller import PainelAuditoria
from persistencia.repository import GenericRepository


class TestPainelAuditoria(unittest.TestCase):

    def setUp(self):
        """Prepara um ambiente limpo com DB em memória e mocks corretos para cada teste."""
        self.root = tk.Tk()
        self.root.withdraw()

        # Cria um banco de dados em memória limpo para este teste
        self.engine = mock_dependencies.setup_test_database()

        # Limpa o log do messagebox mockado entre os testes
        self.messagebox_mock = mock_dependencies.MockMessageBox()
        messagebox_patcher = patch('panels.painel_auditoria_controller.messagebox', self.messagebox_mock)
        self.addCleanup(messagebox_patcher.stop)
        messagebox_patcher.start()

        # Garante que a aplicação use o DB em memória e a View Mockada
        db_patcher = patch('persistencia.database.DatabaseManager.get_engine', return_value=self.engine)
        view_patcher = patch('panels.painel_auditoria_controller.AuditoriaView',
                             new_callable=mock_dependencies.MockAuditoriaView)

        self.addCleanup(db_patcher.stop)
        self.addCleanup(view_patcher.stop)

        db_patcher.start()
        MockView = view_patcher.start()

        # Instancia o controller com as dependências mockadas
        self.controller = PainelAuditoria(self.root, mock_dependencies.MockAppController())
        self.view = self.controller.view

    def tearDown(self):
        self.root.destroy()

    def test_carregar_dados_iniciais(self):
        """Testa se as linguagens e logs do DB em memória são carregados na view."""
        self.controller._carregar_dados_iniciais()

        # Verificação: O schema SQL tem 5 linguagens. A view deve ter tentado inserir 5.
        self.assertEqual(self.view.linguagens_tree.insert.call_count, 5,
                         "Deveria ter inserido 5 linguagens na treeview.")

        # Verificação: O combobox de linguagens deve ter sido populado.
        self.assertIn('Python', self.view.linguagem_combo['values'])

        # Verificação: O schema SQL não tem logs iniciais. A treeview de log não deve inserir nada.
        self.assertEqual(self.view.log_tree.insert.call_count, 0)

    def test_executar_transacao_sucesso(self):
        """Testa a transação e verifica o resultado no banco de dados e no log."""
        self.controller.linguagem_selecionada_var.set("Python")
        self.controller.nova_categoria_var.set("Linguagem Divina")

        # Ação: Executa a transação através do controller
        self.controller._executar_transacao()

        # Verificação 1: Checa se a categoria foi atualizada no banco de dados
        df_lang = GenericRepository.read_table_to_dataframe(
            "linguagens_programacao", where_conditions={'nome': 'Python'}
        )
        self.assertEqual(df_lang.iloc[0]['categoria'], "Linguagem Divina")

        # Verificação 2: Checa se a ação foi registrada corretamente na tabela de log
        df_log = GenericRepository.read_table_to_dataframe("log_alteracoes")
        self.assertEqual(len(df_log), 1)
        last_log_action = df_log.iloc[-1]['acao']
        self.assertIn("Reclassificou 'Python' para 'Linguagem Divina'", last_log_action)