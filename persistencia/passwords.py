"""Argon2id for new passwords; bcrypt verification only during migration."""
import hashlib
import hmac
import re
from pathlib import Path

import bcrypt
import httpx
from argon2 import PasswordHasher, Type, extract_parameters
from argon2.exceptions import Argon2Error
import config

HASHER = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4, type=Type.ID)
COMMON = {
    'password123456789', 'password123456789!', 'admin1234567890!',
    '123456789012345', '1234567890123456', 'qwertyuiop123456',
    'p@ssword123456789!', 'senha12345678901', 'administrador123',
}


def compromised(password):
    if password.casefold() in COMMON:
        return True
    if config.PASSWORD_BLOCKLIST_PATH:
        digest = hashlib.sha256(password.encode('utf-8')).hexdigest()
        with Path(config.PASSWORD_BLOCKLIST_PATH).open(encoding='ascii') as stream:
            if any(hmac.compare_digest(line.strip().lower(), digest) for line in stream if line.strip()):
                return True
    if config.PASSWORD_BREACH_MODE == 'hibp':
        # SHA-1 is the lookup protocol, never the stored password hash.
        digest = hashlib.sha1(password.encode('utf-8'), usedforsecurity=False).hexdigest().upper()
        try:
            response = httpx.get('https://api.pwnedpasswords.com/range/' + digest[:5],
                                 headers={'Add-Padding': 'true'}, timeout=10, follow_redirects=False)
            response.raise_for_status()
            for line in response.text.splitlines():
                suffix, count = line.split(':', 1)
                if hmac.compare_digest(suffix, digest[5:]) and int(count) > 0:
                    return True
        except (httpx.HTTPError, ValueError):
            raise ValueError('Verificação de senhas comprometidas indisponível. Tente novamente.') from None
    return False


def valid_stored_hash(value):
    if not isinstance(value, str):
        return False
    if value.startswith('$argon2id$'):
        try:
            parameters = extract_parameters(value)
            return (parameters.type == Type.ID and parameters.version == 19
                    and 19456 <= parameters.memory_cost <= 131072
                    and 2 <= parameters.time_cost <= 6 and 1 <= parameters.parallelism <= 8
                    and parameters.salt_len >= 16 and parameters.hash_len >= 32)
        except (Argon2Error, ValueError):
            return False
    return bool(re.fullmatch(r'\$2[aby]\$12\$[./A-Za-z0-9]{53}', value))


def verify(password, hashed):
    try:
        if not isinstance(password, str) or len(password.encode('utf-8')) > 1024 or not valid_stored_hash(hashed):
            return False
        if hashed.startswith('$argon2id$'):
            return HASHER.verify(hashed, password)
        return len(password.encode('utf-8')) <= 72 and bcrypt.checkpw(password.encode('utf-8'), hashed.encode('ascii'))
    except (Argon2Error, ValueError, TypeError, UnicodeError, AttributeError):
        return False


def needs_upgrade(hashed):
    return not hashed.startswith('$argon2id$') or HASHER.check_needs_rehash(hashed)
