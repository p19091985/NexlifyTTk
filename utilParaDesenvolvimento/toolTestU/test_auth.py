# test_auth.py
import unittest
from unittest.mock import patch
import bcrypt

# Configura o ambiente de mock ANTES de importar o código da aplicação
import mock_dependencies
mock_dependencies.setup_global_mocks()

from persistencia.auth import verify_user_credentials, hash_password

class TestAuth(unittest.TestCase):

    def setUp(self):
        # Reseta o estado do mock antes de cada teste
        mock_dependencies.MockDatabaseManager.set_engine_state('default')

    @patch('persistencia.auth.bcrypt.checkpw', return_value=True)
    def test_verify_user_credentials_success(self, mock_checkpw):
        """Verifica a autenticação com sucesso."""
        result = verify_user_credentials('testuser', 'senha123')
        self.assertIsInstance(result, dict)
        self.assertEqual(result['username'], 'testuser')
        mock_checkpw.assert_called_once()

    @patch('persistencia.auth.bcrypt.checkpw', return_value=False)
    def test_verify_user_credentials_invalid_password(self, mock_checkpw):
        """Verifica a autenticação com senha inválida."""
        result = verify_user_credentials('testuser', 'senha_errada')
        self.assertIsNone(result)

    def test_verify_user_credentials_connection_error(self):
        """Verifica o retorno correto em caso de falha de conexão."""
        mock_dependencies.MockDatabaseManager.set_engine_state('fail_connect')
        result = verify_user_credentials('testuser', 'senha123')
        self.assertEqual(result, "connection_error")

    def test_hash_password(self):
        """Verifica se a função de hash cria um hash compatível com bcrypt."""
        password = "new_secure_password"
        hashed = hash_password(password)
        self.assertTrue(bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8')))