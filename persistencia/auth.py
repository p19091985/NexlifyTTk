# persistencia/auth.py
import logging
import bcrypt  # Importa a biblioteca de hashing
from sqlalchemy import text
from .database import DatabaseManager


def verify_user_credentials(username, password):
    """
    Verifica as credenciais do usuário de forma segura, comparando o hash da senha.
    """
    logger = logging.getLogger("login_attempts")
    engine = DatabaseManager.get_engine()

    if not engine:
        logger.error("Falha na autenticação: engine do banco de dados não disponível.")
        return None

    try:
        with engine.connect() as connection:
            query = text("""
                         SELECT LoginUsuario, SenhaCriptografada, NomeCompleto, TipoAcesso
                         FROM Usuarios
                         WHERE LoginUsuario = :user
                         """)
            result = connection.execute(query, {"user": username}).fetchone()

            if result:
                # ALTERAÇÃO 1: Acessando o hash armazenado pelo nome da coluna
                hashed_password_from_db = result.SenhaCriptografada.encode('utf-8')
                password_from_user = password.encode('utf-8')

                # ALTERAÇÃO 2: Usando bcrypt para comparar a senha de forma segura
                if bcrypt.checkpw(password_from_user, hashed_password_from_db):
                    logger.info(f"Login bem-sucedido para: {username}")

                    # ALTERAÇÃO 3: Retornando dados pelo nome e SEM a senha
                    return {
                        "username": result.LoginUsuario,
                        "name": result.NomeCompleto,
                        "access_level": result.TipoAcesso
                    }
                else:
                    logger.warning(f"Senha inválida para o usuário: {username}")
                    return None
            else:
                logger.warning(f"Usuário não encontrado: {username}")
                return None

    except Exception as e:
        logger.error(f"Erro durante a verificação de credenciais para '{username}': {e}")
        return None


# --- Função de exemplo para criar um hash de senha ---
# Você usaria isso ao registrar um novo usuário
def hash_password(plain_text_password):
    """Gera um hash seguro de uma senha em texto plano."""
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(plain_text_password.encode('utf-8'), salt)
    return hashed_bytes.decode('utf-8')

# Exemplo de como usar:
# nova_senha_hash = hash_password("senha123")
# print(nova_senha_hash) -> $2b$12$.... (isso é o que você salvaria no banco)