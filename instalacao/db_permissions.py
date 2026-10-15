"""Generate runtime GRANTs for review by the database administrator; no DDL or passwords."""
import argparse
import re
from persistencia.schema import metadata
from persistencia.database import DRIVERS


def identifier(value):
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,62}', value):
        raise ValueError('Use identificadores ASCII simples, de até 63 caracteres.')
    return value


def grants(database, user, schema='public', host='localhost'):
    user, schema = identifier(user), identifier(schema)
    if database not in DRIVERS or database == 'sqlite':
        raise ValueError('SQLite usa permissões do sistema; selecione um servidor externo.')
    if not re.fullmatch(r'[A-Za-z0-9_.:%-]+', host):
        raise ValueError('Host inválido.')
    quote = (lambda name: f'`{identifier(name)}`') if database in {'mysql', 'mariadb'} else (
        (lambda name: f'[{identifier(name)}]') if database == 'sqlserver' else lambda name: '"' + identifier(name) + '"')
    target = f"'{user}'@'{host}'" if database in {'mysql', 'mariadb'} else quote(user)
    lines = ['-- Apply only to an existing dedicated runtime account. Revoke prior broad grants separately.']
    if database == 'postgresql':
        lines += [f'GRANT USAGE ON SCHEMA {quote(schema)} TO {target};',
                  f'GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA {quote(schema)} TO {target};']
    for name in sorted(metadata.tables):
        permissions = 'SELECT' if name in {'schema_versions', 'external_identities'} else (
            'SELECT, INSERT' if name == 'log_alteracoes' else 'SELECT, INSERT, UPDATE' if name == 'audit_outbox' else 'SELECT, INSERT, UPDATE, DELETE')
        # Oracle/Firebird fold unquoted identifiers to uppercase in SQLAlchemy DDL.
        table_name = name.upper() if database in {'oracle', 'firebird'} else name
        table = quote(table_name) if database == 'firebird' else quote(schema) + '.' + quote(table_name)
        if database == 'sqlserver':
            table = 'OBJECT::' + table
        lines.append(f'GRANT {permissions} ON {table} TO {target};')
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Gerar privilégios mínimos; não executa SQL no servidor.')
    parser.add_argument('--database', choices=tuple(DRIVERS), required=True)
    parser.add_argument('--user', required=True)
    parser.add_argument('--schema', default='public', help='Schema ou nome do banco, conforme dialeto; preserve a caixa em Oracle.')
    parser.add_argument('--host', default='localhost', help='Host permitido para a conta MySQL/MariaDB')
    args = parser.parse_args()
    print(grants(args.database, args.user, args.schema, args.host))
