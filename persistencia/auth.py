# persistencia/auth.py
import logging
import bcrypt
from sqlalchemy import text
from .database import DatabaseManager


def verify_user_credentials(username, password):
    """
    Verifica as credenciais do usuário de forma segura, comparando o hash da senha.
    Agora é imune à capitalização das colunas retornadas pelo banco e diferencia falhas de conexão.
    """
    logger = logging.getLogger("login_attempts")

    try:
        engine = DatabaseManager.get_engine()
        if not engine:
            logger.error("Falha na autenticação: engine do banco de dados não disponível.")
            # Retorna o novo sinalizador de erro de conexão
            return "connection_error"

        with engine.connect() as connection:
            query = text("""
                         SELECT LOGIN_USUARIO, SENHA_CRIPTOGRAFADA, NOME_COMPLETO, TIPO_ACESSO
                         FROM USUARIOS
                         WHERE LOGIN_USUARIO = :user
                         """)
            result = connection.execute(query, {"user": username}).fetchone()

            if result:
                user_data = {key.lower(): value for key, value in result._mapping.items()}
                hashed_password_from_db = user_data['senha_criptografada'].encode('utf-8')
                password_from_user = password.encode('utf-8')

                if bcrypt.checkpw(password_from_user, hashed_password_from_db):
                    logger.info(f"Login bem-sucedido para: {username}")
                    return {
                        "username": user_data['login_usuario'],
                        "name": user_data['nome_completo'],
                        "access_level": user_data['tipo_acesso']
                    }
                else:
                    logger.warning(f"Senha inválida para o usuário: {username}")
                    return None
            else:
                logger.warning(f"Usuário não encontrado: {username}")
                return None

    # --- MODIFICAÇÃO: Captura o ConnectionError especificamente ---
    except ConnectionError as e:
        logger.critical(f"Falha de conexão durante a autenticação: {e}")
        return "connection_error"

    except Exception as e:
        logger.error(f"Erro inesperado durante a verificação de credenciais para '{username}': {e}")
        return None


def hash_password(plain_text_password):
    """Gera um hash seguro de uma senha em texto plano."""
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(plain_text_password.encode('utf-8'), salt)
    return hashed_bytes.decode('utf-8')


def check_password_hash(plain_password, hashed_password):
    """
    Verifica se uma senha em texto plano corresponde a um hash bcrypt.
    """
    try:
        # bcrypt.checkpw espera bytes, então codificamos as strings
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except (ValueError, TypeError):
        # Retorna False se o hash for malformado ou ocorrer outro erro
        return False