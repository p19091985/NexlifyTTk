"""Offline installation operations; never distributed with a desktop client."""
import argparse
import getpass
import json
from pathlib import Path
from sqlalchemy import insert, select
from persistencia.database import DatabaseManager, create_database_engine
from persistencia import auth, audit
from persistencia.schema import external_identities, usuarios
from persistencia.migrations import current_version


def main():
    parser = argparse.ArgumentParser(description='Provisionamento com conta de instalação separada do runtime.')
    parser.add_argument('operation', choices=['migrate', 'bootstrap-admin', 'bind-sso'])
    parser.add_argument('--backup-evidence', type=Path, help='Manifesto JSON do backup externo restaurado e validado')
    parser.add_argument('--login')
    parser.add_argument('--issuer')
    parser.add_argument('--subject')
    args = parser.parse_args()
    if args.operation == 'migrate':
        engine = create_database_engine(provisioning=True)
        try:
            if engine.dialect.name != 'sqlite' and current_version(engine):
                if not args.backup_evidence:
                    raise ValueError('Migração externa requer --backup-evidence de restauração homologada.')
                evidence = json.loads(args.backup_evidence.read_text(encoding='utf-8'))
                if evidence.get('restore_verified') is not True or not evidence.get('backup_id') or not evidence.get('verified_at'):
                    raise ValueError('Evidência deve incluir backup_id, verified_at e restore_verified=true.')
            DatabaseManager.initialize_database(engine, provisioned=True)
        finally:
            engine.dispose()
        print('Migração concluída. Use a conta limitada no runtime e desative initialize_database_on_startup.')
    elif args.operation == 'bootstrap-admin':
        password = getpass.getpass('Senha inicial (mínimo 15 caracteres): ')
        confirmation = getpass.getpass('Confirme a senha: ')
        error = auth.password_validation_error(password, confirmation)
        if error:
            raise ValueError(error)
        auth.bootstrap_admin(password)
        print('Administrador criado. MFA por e-mail é opcional e vem desabilitado na instalação.')
    else:
        from services.transport import validate_service_url
        validate_service_url(args.issuer or '')
        if not args.login or not args.subject or len(args.subject) > 255 or len(args.issuer) > 255:
            raise ValueError('Informe --login, --issuer e --subject válidos.')
        with DatabaseManager.get_engine().begin() as connection:
            if not connection.execute(select(usuarios.c.login_usuario).where(usuarios.c.login_usuario == args.login)).first():
                raise ValueError('Conta local não encontrada; crie-a antes de vincular SSO.')
            connection.execute(insert(external_identities).values(issuer=args.issuer, subject=args.subject, login_usuario=args.login))
            audit.record(connection, args.login, 'Identidade SSO vinculada pelo operador de instalação.')
        print('Identidade vinculada; o perfil continua sendo controlado localmente.')


if __name__ == '__main__':
    main()
