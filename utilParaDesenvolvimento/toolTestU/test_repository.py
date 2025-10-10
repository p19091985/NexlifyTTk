# test_repository.py (Reescrito para o DB em Memória)
import unittest
from unittest.mock import patch
import pandas as pd

# Configura o ambiente de teste
import mock_dependencies

mock_dependencies.setup_global_mocks()

from persistencia.repository import GenericRepository


# --- REESCRITO: Testa o repositório contra um banco de dados real em memória ---
class TestGenericRepository(unittest.TestCase):

    def setUp(self):
        """Prepara o banco de dados em memória para cada teste."""
        self.engine = mock_dependencies.setup_test_database()
        self.db_manager_patch = patch('persistencia.repository.DatabaseManager.get_engine', return_value=self.engine)
        self.db_manager_patch.start()

    def tearDown(self):
        self.db_manager_patch.stop()

    def test_read_table_to_dataframe_returns_lowercase_columns(self):
        """Verifica se a leitura da tabela retorna colunas em minúsculas."""
        # Ação: Lê a tabela 'ESPECIE_GATOS' que foi pré-populada no DB em memória
        df = GenericRepository.read_table_to_dataframe("ESPECIE_GATOS")

        # Verificação
        self.assertFalse(df.empty)
        # O schema tem colunas maiúsculas, o método deve retornar minúsculas
        self.assertTrue(all(col.islower() for col in df.columns))
        self.assertIn('nome_especie', df.columns)

    def test_write_and_read_cycle(self):
        """Verifica um ciclo completo de escrita e leitura."""
        # Preparação: Cria um DataFrame de teste
        df_to_write = pd.DataFrame(
            [{'nome': 'Nova Linguagem', 'id_tipo': 1, 'ano_criacao': 2025, 'categoria': 'Teste'}])

        # Ação 1: Escreve no banco
        success = GenericRepository.write_dataframe_to_table(df_to_write, "linguagens_programacao")
        self.assertTrue(success)

        # Ação 2: Lê o dado de volta
        df_read = GenericRepository.read_table_to_dataframe(
            "linguagens_programacao", where_conditions={'nome': 'Nova Linguagem'}
        )

        # Verificação
        self.assertEqual(len(df_read), 1)
        self.assertEqual(df_read.iloc[0]['ano_criacao'], 2025)

    def test_update_table(self):
        """Verifica se a atualização de um registro funciona."""
        # Ação: Atualiza o temperamento do Siamês (ID 1)
        rows_affected = GenericRepository.update_table(
            "especie_gatos",
            update_values={'temperamento': 'Muito barulhento'},
            where_conditions={'id': 1}
        )
        self.assertEqual(rows_affected, 1)

        # Verificação: Lê o registro e confere a alteração
        df = GenericRepository.read_table_to_dataframe("especie_gatos", where_conditions={'id': 1})
        self.assertEqual(df.iloc[0]['temperamento'], 'Muito barulhento')

    def test_delete_from_table(self):
        """Verifica se a deleção de um registro funciona."""
        # Ação: Deleta o gato Persa (ID 2)
        rows_affected = GenericRepository.delete_from_table("especie_gatos", where_conditions={'id': 2})
        self.assertEqual(rows_affected, 1)

        # Verificação: Tenta ler o registro deletado
        df = GenericRepository.read_table_to_dataframe("especie_gatos", where_conditions={'id': 2})
        self.assertTrue(df.empty)

    def test_delete_from_table_requires_where(self):
        """Verifica se a exclusão sem WHERE lança ValueError (teste inalterado)."""
        with self.assertRaises(ValueError):
            GenericRepository.delete_from_table("ANY_TABLE", where_conditions={})