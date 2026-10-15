"""Segredos locais; falhas de descriptografia nunca retornam texto original."""
import os
import json
from cryptography.fernet import Fernet, InvalidToken, MultiFernet
from utils.paths import PROJECT_ROOT
from utils.secure_files import reject_link_path, private_directory, restrict_permissions
KEY_PATH = PROJECT_ROOT / '.secrets' / 'secret.key'
def generate_and_save_key():
    reject_link_path(KEY_PATH)
    private_directory(KEY_PATH.parent)
    key = Fernet.generate_key()
    fd = os.open(KEY_PATH, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        restrict_permissions(KEY_PATH)
        stream.write(key)
        stream.flush()
        os.fsync(stream.fileno())
    return key
def _load_single_key(create=False):
    value = os.environ.get('NEXLIFY_SECRET_KEY')
    if value:
        key = value.encode('ascii')
    else:
        reject_link_path(KEY_PATH)
        if KEY_PATH.is_file():
            private_directory(KEY_PATH.parent)
            restrict_permissions(KEY_PATH)
            key = KEY_PATH.read_bytes()
        elif create:
            try:
                return generate_and_save_key()
            except FileExistsError:
                reject_link_path(KEY_PATH)
                key = KEY_PATH.read_bytes()
        else:
            raise ValueError('Chave de criptografia ausente. Restaure a chave correta antes de abrir as credenciais.')
    Fernet(key)
    return key
def load_keys(create=False):
    if os.environ.get('NEXLIFY_SECRET_KEY'):
        return [_load_single_key(create)]
    keyring = reject_link_path(KEY_PATH.with_name('keyring.json'))
    if keyring.exists():
        restrict_permissions(keyring)
        values = json.loads(keyring.read_text(encoding='utf-8'))
        if not isinstance(values, list) or not 1 <= len(values) <= 10:
            raise ValueError('Chaveiro inválido.')
        keys = [value.encode('ascii') for value in values]
        for key in keys:
            Fernet(key)
        return keys
    return [_load_single_key(create)]


def load_key(create=False):
    return load_keys(create)[0]


def encrypt_message(message, key=None):
    if not message:
        return ''
    return 'ENC:' + Fernet(key or load_key(create=True)).encrypt(message.encode('utf-8')).decode('ascii')


def decrypt_message(encrypted_message, key=None):
    if not encrypted_message:
        return ''
    try:
        token = encrypted_message.removeprefix('ENC:')
        cipher = Fernet(key) if key else MultiFernet([Fernet(item) for item in load_keys()])
        return cipher.decrypt(token.encode('ascii')).decode('utf-8')
    except (InvalidToken, ValueError, UnicodeError, TypeError) as error:
        raise ValueError('Credencial criptografada inválida ou chave incorreta.') from error
