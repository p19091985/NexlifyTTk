# persistencia/security.py
import os
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken

# O caminho para o arquivo que armazenará a chave de criptografia
KEY_PATH = Path(__file__).parent.parent / "secret.key"

def generate_and_save_key():
    """Gera uma nova chave de criptografia e a salva no arquivo."""
    key = Fernet.generate_key()
    with open(KEY_PATH, "wb") as key_file:
        key_file.write(key)
    return key

def load_key():
    """Carrega a chave de criptografia do arquivo, ou a gera se não existir."""
    if not KEY_PATH.exists():
        return generate_and_save_key()
    with open(KEY_PATH, "rb") as key_file:
        return key_file.read()

def encrypt_message(message: str, key: bytes) -> str:
    """Criptografa uma string e retorna a versão codificada."""
    if not message:
        return ""
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode('utf-8'))
    return encrypted_message.decode('utf-8')

def decrypt_message(encrypted_message: str, key: bytes) -> str:
    """Descriptografa uma mensagem e retorna a string original."""
    if not encrypted_message:
        return ""
    f = Fernet(key)
    try:
        # Tenta descriptografar. Se falhar, pode ser que a string não esteja criptografada.
        decrypted_message = f.decrypt(encrypted_message.encode('utf-8'))
        return decrypted_message.decode('utf-8')
    except (InvalidToken, TypeError, AttributeError):
        # Se a descriptografia falhar, retorna a string original.
        # Isso permite que o sistema funcione com senhas em texto plano durante a transição.
        return encrypted_message
