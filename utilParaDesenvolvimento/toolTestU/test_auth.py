import unittest
from unittest.mock import patch
import bcrypt

import mock_dependencies
mock_dependencies.setup_global_mocks()

from persistencia.auth import verify_user_credentials, hash_password

class TestAuth(unittest.TestCase):

    def setUp(self):
        self.engine = mock_dependencies.setup_test_database()
        self.db_manager_patcher = patch('persistencia.auth.DatabaseManager.get_engine', return_value=self.engine)
        self.db_manager_patcher.start()

    def tearDown(self):
        self.db_manager_patcher.stop()

    def test_verify_credentials_com_sucesso(self):
        result = verify_user_credentials('admin', 'admin')
        self.assertIsInstance(result, dict)
        self.assertEqual(result['username'], 'admin')
        self.assertEqual(result['access_level'], 'Administrador Global')

    def test_verify_credentials_com_senha_invalida(self):
        result = verify_user_credentials('admin', 'senha_errada')
        self.assertIsNone(result)

    def test_verify_credentials_com_usuario_inexistente(self):
        result = verify_user_credentials('usuario_fantasma', 'qualquer_senha')
        self.assertIsNone(result)

    @patch('persistencia.auth.DatabaseManager.get_engine')
    def test_verify_credentials_quando_ha_erro_de_conexao(self, mock_get_engine):
        mock_get_engine.side_effect = ConnectionError("Erro de conexão simulado")
        result = verify_user_credentials('admin', 'admin')
        self.assertEqual(result, "connection_error")

    def test_hash_password_gera_hash_valido(self):
        password = "new_secure_password"
        hashed = hash_password(password)
        self.assertTrue(bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8')))