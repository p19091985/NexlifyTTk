"""Pinned Gitleaks binary and checksums; scan all refs without printing secrets."""
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import shutil
import tarfile
import httpx
import zipfile
from utils.paths import PROJECT_ROOT
from utils.secure_files import private_directory, atomic_write_private, restrict_permissions, reject_link_path

VERSION = '8.30.1'
CHECKSUMS_SHA256 = '061476c21adaf5441516f96f185c1a4706a83cd6329b9b38762271b3d4a52fae'


def download(url):
    if not url.startswith(f'https://github.com/gitleaks/gitleaks/releases/download/v{VERSION}/'):
        raise ValueError('Origem de download não autorizada.')
    with httpx.stream('GET', url, timeout=30, follow_redirects=True, trust_env=False) as response:
        response.raise_for_status()
        data = bytearray()
        for chunk in response.iter_bytes():
            data.extend(chunk)
            if len(data) > 25 * 1024 * 1024:
                raise ValueError('Download excede o limite.')
        return bytes(data)


def scanner(root=PROJECT_ROOT):
    import platform
    if platform.machine().lower() not in {'amd64', 'x86_64'}:
        raise ValueError('Scanner automático requer x64; instale Gitleaks auditado para sua arquitetura.')
    platform_name = 'windows' if os.name == 'nt' else 'linux'
    suffix = 'zip' if os.name == 'nt' else 'tar.gz'
    artifact = f'gitleaks_{VERSION}_{platform_name}_x64.{suffix}'
    directory = private_directory(Path(root) / '.runtime' / 'security-tools')
    base = f'https://github.com/gitleaks/gitleaks/releases/download/v{VERSION}/'
    checksums = download(base + f'gitleaks_{VERSION}_checksums.txt')
    if hashlib.sha256(checksums).hexdigest() != CHECKSUMS_SHA256:
        raise ValueError('Checksum da distribuição Gitleaks divergiu.')
    expected = dict((line.split()[1], line.split()[0]) for line in checksums.decode().splitlines())[artifact]
    package = download(base + artifact)
    if hashlib.sha256(package).hexdigest() != expected:
        raise ValueError('Binário Gitleaks divergiu do checksum fixado.')
    binary_name = 'gitleaks.exe' if os.name == 'nt' else 'gitleaks'
    if os.name == 'nt':
        with zipfile.ZipFile(io.BytesIO(package)) as archive:
            executable = archive.read(binary_name)
    else:
        with tarfile.open(fileobj=io.BytesIO(package), mode='r:gz') as archive:
            with archive.extractfile(binary_name) as stream:
                executable = stream.read()
    target = reject_link_path(directory / binary_name)
    target.write_bytes(executable)
    restrict_permissions(target)
    if os.name != 'nt':
        target.chmod(0o700)
    return target


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Examinar todos os refs e arquivos atuais com Gitleaks.')
    parser.add_argument('--history-only', action='store_true')
    args = parser.parse_args()
    binary = scanner()
    report = PROJECT_ROOT / '.runtime' / 'secrets-history.json'
    command = [str(binary), 'git', str(PROJECT_ROOT), '--log-opts=--all --full-history', '--redact=100',
               '--no-banner', '--log-level=error', '--report-format=json', '--report-path', str(report),
               '--config', str(PROJECT_ROOT / '.gitleaks.toml')]
    result = subprocess.run(command, capture_output=True)
    if result.returncode not in {0, 1}:
        raise RuntimeError('Scanner falhou. Verifique Git, rede e configuração; saída suprimida para proteger segredos.')
    findings = json.loads(report.read_text(encoding='utf-8'))
    atomic_write_private(report, json.dumps(findings, indent=2))
    print(f'Histórico: {len(findings)} achado(s); relatório com valores ocultados em .runtime/secrets-history.json.')
    if not args.history_only:
        import tempfile
        git = shutil.which('git')
        if not git or Path(git).resolve().is_relative_to(PROJECT_ROOT.resolve()):
            raise ValueError('Use uma instalação confiável de Git fora do projeto.')
        with tempfile.TemporaryDirectory(prefix='nexlify-scan-') as temporary:
            files = subprocess.run([git, 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
                cwd=PROJECT_ROOT, check=True, capture_output=True).stdout.decode('utf-8').split('\0')
            for name in set(files) - {''}:
                source = PROJECT_ROOT / name
                if source.is_file() and not source.is_symlink():
                    destination = Path(temporary) / name
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, destination)
            working_report = PROJECT_ROOT / '.runtime' / 'secrets-working.json'
            current = subprocess.run([str(binary), 'dir', temporary, '--redact=100', '--no-banner', '--log-level=error',
                '--config', str(PROJECT_ROOT / '.gitleaks.toml'), '--report-format=json', '--report-path', str(working_report)], capture_output=True)
            if current.returncode not in {0, 1}:
                raise RuntimeError('Scanner da árvore atual falhou.')
            print(f'Árvore atual: {len(json.loads(working_report.read_text(encoding="utf-8")))} achado(s).')
            if current.returncode:
                return 1
    return int(bool(findings))


if __name__ == '__main__':
    raise SystemExit(main())
