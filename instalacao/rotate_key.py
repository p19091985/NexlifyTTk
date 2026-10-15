"""Crash-safe local key rotation. Old keys remain available for backup recovery."""
import configparser
import io
import json
import os
from cryptography.fernet import Fernet
from sqlalchemy import select, update
from persistencia import security, audit
from persistencia.database import DatabaseManager, CONFIG_PATH
from persistencia.schema import user_security
from utils.secure_files import atomic_write_private, private_directory


def rotate(config_path=CONFIG_PATH):
    if os.environ.get('NEXLIFY_SECRET_KEY'):
        raise ValueError('Chave externa: rotacione no cofre e migre os tokens em janela de manutenção.')
    engine = DatabaseManager.get_engine()  # Open old database credentials first.
    old_keys = security.load_keys(create=True)
    if len(old_keys) >= 10:
        raise ValueError('Limite do chaveiro atingido. Arquive as chaves de recuperação antes de continuar.')
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(config_path, encoding='utf-8')
    plaintext_config = []
    for section in parser.sections():
        for key, value in parser[section].items():
            if value.startswith(('ENC:', 'gAAAA')):
                plaintext_config.append((section, key, security.decrypt_message(value)))
    with engine.connect() as connection:
        rows = connection.execute(select(user_security)).mappings().all()
    plaintext_rows = [(row['login_usuario'], {key: security.decrypt_message(row[key]) for key in
                       ('mfa_secret', 'pending_secret') if row[key]}) for row in rows]
    new = Fernet.generate_key()
    private_directory(security.KEY_PATH.parent)
    # Publish decrypt compatibility first; a crash cannot strand old ciphertext.
    atomic_write_private(security.KEY_PATH.with_name('keyring.json'),
                         json.dumps([key.decode('ascii') for key in [new, *old_keys]]))
    with engine.begin() as connection:
        for username, values in plaintext_rows:
            if values:
                connection.execute(update(user_security).where(user_security.c.login_usuario == username).values(
                    **{key: security.encrypt_message(value, new) for key, value in values.items()}))
        audit.record(connection, None, 'Chave local de criptografia rotacionada; cópias antigas exigem proteção.')
    for section, key, value in plaintext_config:
        parser[section][key] = security.encrypt_message(value, new)
    if config_path.exists():
        stream = io.StringIO()
        parser.write(stream)
        atomic_write_private(config_path, stream.getvalue())
    from services.email_settings import rotate_encryption
    email_fields = rotate_encryption()
    atomic_write_private(security.KEY_PATH, new.decode('ascii'))
    return {'rotated': True, 'encrypted_fields': email_fields + len(plaintext_config) + sum(len(values) for _, values in plaintext_rows),
            'recovery_keys': len(old_keys)}


if __name__ == '__main__':
    print(json.dumps(rotate()))
