# test_painel_catalogo_mvc_controller.py
import unittest
import tkinter as tk
from unittest.mock import patch, MagicMock

import mock_dependencies

mock_dependencies.setup_global_mocks()

from panels.painel_catalogo_mvc_controller import PainelCatalogoEspeciesMVC


@patch('panels.painel_catalogo_mvc_controller.CatalogoEspeciesView', mock_dependencies.MockViewBase)
@patch('panels.painel_catalogo_mvc_controller.DataService')
@patch('panels.painel_catalogo_mvc_controller.GenericRepository')
@patch('panels.painel_catalogo_mvc_controller.messagebox')
class TestPainelCatalogoEspeciesMVC(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.controller = PainelCatalogoEspeciesMVC(self.root, mock_dependencies.MockAppController())

    def tearDown(self):
        self.root.destroy()

    def test_inserir_item_sucesso(self, mock_messagebox, mock_repo, mock_service, mock_view):
        """Testa se a inserção chama o repositório."""
        self.controller.nome_var.set("Nova Especie")
        self.controller.inserir_item()
        mock_repo.write_dataframe_to_table.assert_called_once()
        mock_messagebox.showinfo.assert_called_with("Sucesso", "Nova espécie inserida com sucesso!",
                                                    parent=self.controller)

    def test_excluir_item_confirmado(self, mock_messagebox, mock_repo, mock_service, mock_view):
        """Testa a exclusão quando o usuário confirma."""
        self.controller.selected_item_id = 1
        mock_messagebox.askyesno.return_value = True  # Simula o "Sim" do usuário
        self.controller.excluir_item()
        mock_repo.delete_from_table.assert_called_once()
        mock_messagebox.showinfo.assert_called_with("Sucesso", "Espécie excluída com sucesso!", parent=self.controller)

    def test_executar_transacao_sucesso(self, mock_messagebox, mock_repo, mock_service, mock_view):
        """Testa se a transação chama o DataService."""
        self.controller.selected_item_id = 1
        self.controller.nome_var.set("Siamês")
        self.controller.novo_nome_var.set("Siamês Real")
        mock_service.rename_especie_gato_e_logar.return_value = (True, "Sucesso simulado")

        self.controller.executar_transacao()

        mock_service.rename_especie_gato_e_logar.assert_called_with("Siamês", "Siamês Real", "testuser")
        mock_messagebox.showinfo.assert_called_with("Transação Concluída", "Sucesso simulado", parent=self.controller)