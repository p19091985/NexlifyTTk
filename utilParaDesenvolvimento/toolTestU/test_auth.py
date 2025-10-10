# test_auth.py (Reescrito para o DB em Memória)
import unittest
from unittest.mock import patch
import bcrypt

# Configura o ambiente de teste
import mock_dependencies
mock_dependencies.setup_global_mocks()

from persistencia.auth import verify_user_credentials, hash_password
from persistencia.database import DatabaseManager

# --- REESCRITO: Agora testa a autenticação contra o DB em memória ---
class TestAuth(unittest.TestCase):

    def setUp(self):
        """Prepara o banco de dados em memória para cada teste."""
        # Garante que o DatabaseManager use a engine de teste
        self.engine = mock_dependencies.setup_test_database()
        self.db_manager_patch = patch('persistencia.database.DatabaseManager.get_engine', return_value=self.engine)
        self.db_manager_patch.start()

    def tearDown(self):
        self.db_manager_patch.stop()

    def test_verify_user_credentials_success(self):
        """Verifica a autenticação com sucesso usando a senha correta do schema."""
        # A senha para o usuário 'admin' no arquivo de schema é 'admin'
        result = verify_user_credentials('admin', 'admin')
        self.assertIsInstance(result, dict)
        self.assertEqual(result['username'], 'admin')
        self.assertEqual(result['access_level'], 'Administrador Global')

    def test_verify_user_credentials_invalid_password(self):
        """Verifica a autenticação com senha inválida."""
        result = verify_user_credentials('admin', 'senha_errada')
        self.assertIsNone(result)

    def test_verify_user_credentials_user_not_found(self):
        """Verifica a autenticação com um usuário que não existe."""
        result = verify_user_credentials('usuario_fantasma', 'qualquer_senha')
        self.assertIsNone(result)

    @patch('persistencia.auth.DatabaseManager.get_engine')
    def test_verify_user_credentials_connection_error(self, mock_get_engine):
        """Verifica o retorno correto em caso de falha de conexão."""
        # Força o get_engine a simular um erro de conexão
        mock_get_engine.side_effect = ConnectionError("Erro de conexão simulado")
        result = verify_user_credentials('admin', 'admin')
        self.assertEqual(result, "connection_error")

    def test_hash_password(self):
        """Verifica se a função de hash cria um hash compatível com bcrypt (teste inalterado)."""
        password = "new_secure_password"
        hashed = hash_password(password)
        self.assertTrue(bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8')))