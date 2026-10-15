"""Allowlisted operation packages with a verifiable SHA-256 manifest."""
import argparse
import configparser
import hashlib
import io
import json
from pathlib import Path
import zipfile
from utils.paths import PROJECT_ROOT
from utils.secure_files import reject_link_path, private_directory

ROOT_FILES = ('app.py', 'run.py', 'config.py', 'settings_manager.py', 'theme.py',
              'iniciar.bat', 'inciciar.bat', 'iniciar.sh', 'iniciar.ps1',
              'requirements.txt', 'requirements-core.txt', 'requirements-core.lock',
              'requirements-server.txt', 'requirements-server.lock', 'README.md')
MODULES = ('dialogs', 'modals', 'panels', 'persistencia', 'utils')
INSTALLER = ('install.py', 'setup.bat', 'setup.sh', 'config_banco_gui.py', 'diagnostics_gui.py')
MAINTENANCE = ('backup.py', 'harden.py', 'rotate_key.py', 'provision.py', 'db_permissions.py', 'config_email.py')
DEV_MODULES = {'monitor_processo.py', 'launch_devtools.py', 'resetar_banco_de_dados.py', 'limpa_logs.py',
               'gerador_credenciais_gui.py', 'config_gui.py', 'painel_testes_visuais_view.py'}


def build(destination, mode='client', api_url='', root=PROJECT_ROOT):
    root = Path(root)
    destination = reject_link_path(destination)
    if mode not in {'local', 'client', 'server'}:
        raise ValueError('Modo inválido.')
    if mode == 'client':
        from urllib.parse import urlsplit
        parsed = urlsplit(api_url)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError('Pacote cliente requer --api-url HTTPS sem credenciais.')
    files = {name: (root / name).read_bytes() for name in ROOT_FILES}
    for module in MODULES:
        for path in (root / module).rglob('*.py'):
            if path.name not in DEV_MODULES and '__pycache__' not in path.parts:
                reject_link_path(path)
                files[path.relative_to(root).as_posix()] = path.read_bytes()
    for name in INSTALLER + (() if mode == 'client' else MAINTENANCE):
        files['instalacao/' + name] = (root / 'instalacao' / name).read_bytes()
    for path in (root / 'requirements').glob('*.lock'):
        files[path.relative_to(root).as_posix()] = path.read_bytes()
    for name in ('__init__.py', 'transport.py', 'client.py', 'email_delivery.py', 'email_settings.py', 'email_providers.py', 'email_oauth.py'):
        files['services/' + name] = (root / 'services' / name).read_bytes()
    if mode == 'server':
        files['servidor.py'] = (root / 'servidor.py').read_bytes()
        for path in (root / 'services').glob('*.py'):
            files[path.relative_to(root).as_posix()] = path.read_bytes()
    for name in ('README.md', 'GUIA_USUARIO.md', 'DESENVOLVIMENTO.md', 'EVOLUCOES.md',
                 'SEGURANCA.md', 'SEGURANCA_OPERACAO.md', 'BANCOS.md', 'MULTIPLATAFORMA.md', 'EMAIL.md', 'ACESSOS.md'):
        if (root / 'docs' / name).is_file():
            files['docs/' + name] = (root / 'docs' / name).read_bytes()
    # Generated defaults only: never reuse developer settings or database files.
    parser = configparser.ConfigParser(interpolation=None)
    parser['Settings'] = {'environment': 'production', 'database_enabled': 'True', 'use_login': 'True',
        'mfa_enabled': 'False', 'logging_enabled': 'True', 'initialize_database_on_startup': 'False', 'api_mode': mode, 'api_url': api_url}
    stream = io.StringIO()
    parser.write(stream)
    files['config_settings.ini'] = stream.getvalue().encode('utf-8')
    if mode != 'client':
        files['banco.ini'] = b'[database]\ntype = sqlite\npath = NexlifyTTk.db\n'
    files['.runtime/installation.json'] = b'{"id": "core"}\n'
    manifest = {name: hashlib.sha256(content).hexdigest() for name, content in sorted(files.items())}
    files['SHA256SUMS.json'] = json.dumps(manifest, indent=2).encode('utf-8')
    private_directory(destination.parent)
    with zipfile.ZipFile(destination, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(files.items()):
            archive.writestr(name, content)
    return {'files': len(files), 'sha256': hashlib.sha256(destination.read_bytes()).hexdigest()}


def verify(archive_path):
    with zipfile.ZipFile(archive_path) as archive:
        manifest = json.loads(archive.read('SHA256SUMS.json'))
        if set(archive.namelist()) != set(manifest) | {'SHA256SUMS.json'}:
            raise ValueError('Manifesto não cobre todos os arquivos.')
        if any(hashlib.sha256(archive.read(name)).hexdigest() != checksum for name, checksum in manifest.items()):
            raise ValueError('Integridade do pacote inválida.')
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('destination', type=Path)
    parser.add_argument('--mode', choices=['client', 'server', 'local'], default='client')
    parser.add_argument('--api-url', default='')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    print(verify(args.destination) if args.verify else json.dumps(build(args.destination, args.mode, args.api_url)))
