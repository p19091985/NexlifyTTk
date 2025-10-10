# test_painel_catalogo_mvc_controller.py (Versão Final Corrigida)
import unittest
import tkinter as tk
from unittest.mock import patch
import sys
import os

# Configura o ambiente de teste
sys.path.insert(0, os.path.dirname(__file__))
import mock_dependencies

mock_dependencies.setup_global_mocks()

from panels.painel_catalogo_mvc_controller import PainelCatalogoEspeciesMVC
from persistencia.repository import GenericRepository


class TestPainelCatalogoEspeciesMVC(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.engine = mock_dependencies.setup_test_database()

        self.messagebox_mock = mock_dependencies.MockMessageBox()
        messagebox_patcher = patch('panels.painel_catalogo_mvc_controller.messagebox', self.messagebox_mock)
        self.addCleanup(messagebox_patcher.stop)
        messagebox_patcher.start()

        db_patcher = patch('persistencia.database.DatabaseManager.get_engine', return_value=self.engine)
        view_patcher = patch('panels.painel_catalogo_mvc_controller.CatalogoEspeciesView',
                             new_callable=mock_dependencies.MockCatalogoEspeciesView)

        self.addCleanup(db_patcher.stop)
        self.addCleanup(view_patcher.stop)

        db_patcher.start()
        view_patcher.start()

        self.controller = PainelCatalogoEspeciesMVC(self.root, mock_dependencies.MockAppController())

    def tearDown(self):
        self.root.destroy()

    def test_inserir_item_sucesso(self):
        """Testa a inserção de um item e verifica no banco."""
        self.controller.nome_var.set("Gato Sphynx")
        self.controller.pais_var.set("Canadá")

        # Ação
        self.controller.inserir_item()

        # Verificação no DB em memória
        df = GenericRepository.read_table_to_dataframe("especie_gatos",
                                                       where_conditions={'nome_especie': 'Gato Sphynx'})
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['pais_origem'], 'Canadá')

    def test_excluir_item_confirmado(self):
        """Testa a exclusão de um item e verifica no banco."""
        self.controller.selected_item_id = 2  # Excluir o 'Persa' do DB de teste

        # Ação
        self.controller.excluir_item()

        # Verificação no DB em memória
        df = GenericRepository.read_table_to_dataframe("especie_gatos", where_conditions={'id': 2})
        self.assertTrue(df.empty)

    def test_executar_transacao_sucesso(self):
        """Testa a transação de renomear e verifica a atualização e o log no banco."""
        self.controller.selected_item_id = 1  # Renomear 'Siamês'
        self.controller.nome_var.set("Siamês")
        self.controller.novo_nome_var.set("Siamês Tailandês")

        # Ação
        self.controller.executar_transacao()

        # Verificação no DB em memória
        df_antigo = GenericRepository.read_table_to_dataframe("especie_gatos",
                                                              where_conditions={'nome_especie': 'Siamês'})
        self.assertTrue(df_antigo.empty)

        df_novo = GenericRepository.read_table_to_dataframe("especie_gatos",
                                                            where_conditions={'nome_especie': 'Siamês Tailandês'})
        self.assertEqual(len(df_novo), 1)

        df_log = GenericRepository.read_table_to_dataframe("log_alteracoes")
        self.assertIn("Renomeou a espécie de gato de 'Siamês' para 'Siamês Tailandês'", df_log['acao'].to_list())