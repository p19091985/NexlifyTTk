import unittest
import tkinter as tk
from unittest.mock import patch

import mock_dependencies

mock_dependencies.setup_global_mocks()

from panels.painel_catalogo_mvc_controller import PainelCatalogoEspeciesMVC
from persistencia.repository import GenericRepository


class TestPainelCatalogoEspeciesMVC(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.engine = mock_dependencies.setup_test_database()

        messagebox_patcher = patch('panels.painel_catalogo_mvc_controller.messagebox',
                                   new_callable=mock_dependencies.MockMessageBox)
        db_patcher = patch('persistencia.database.DatabaseManager.get_engine', return_value=self.engine)
        view_patcher = patch('panels.painel_catalogo_mvc_controller.CatalogoEspeciesView',
                             new_callable=mock_dependencies.MockCatalogoEspeciesView)

        self.addCleanup(messagebox_patcher.stop)
        self.addCleanup(db_patcher.stop)
        self.addCleanup(view_patcher.stop)

        messagebox_patcher.start()
        db_patcher.start()
        view_patcher.start()

        self.controller = PainelCatalogoEspeciesMVC(self.root, mock_dependencies.MockAppController())

    def tearDown(self):
        self.root.destroy()

    def test_inserir_item_com_sucesso(self):
        self.controller.nome_var.set("Gato Sphynx")
        self.controller.pais_var.set("Canadá")

        self.controller.inserir_item()

        df = GenericRepository.read_table_to_dataframe("especie_gatos",
                                                       where_conditions={'nome_especie': 'Gato Sphynx'})
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['pais_origem'], 'Canadá')

    def test_excluir_item_apos_confirmacao(self):
        self.controller.selected_item_id = 2
        self.controller.view.ask_yes_no.return_value = True

        self.controller.excluir_item()

        df = GenericRepository.read_table_to_dataframe("especie_gatos", where_conditions={'id': 2})
        self.assertTrue(df.empty)

    def test_executar_transacao_renomeia_e_audita_com_sucesso(self):
        self.controller.selected_item_id = 1
        self.controller.nome_var.set("Siamês")
        self.controller.novo_nome_var.set("Siamês Tailandês")

        self.controller.executar_transacao()

        df_antigo = GenericRepository.read_table_to_dataframe("especie_gatos",
                                                              where_conditions={'nome_especie': 'Siamês'})
        self.assertTrue(df_antigo.empty)

        df_novo = GenericRepository.read_table_to_dataframe("especie_gatos",
                                                            where_conditions={'nome_especie': 'Siamês Tailandês'})
        self.assertEqual(len(df_novo), 1)

        df_log = GenericRepository.read_table_to_dataframe("log_alteracoes")
        self.assertIn("Renomeou a espécie de gato de 'Siamês' para 'Siamês Tailandês'", df_log['acao'].to_list())