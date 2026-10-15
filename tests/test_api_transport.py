"""Real HTTPS process verifies the desktop-to-server boundary on both OSes."""
from datetime import datetime, timedelta, timezone
import ipaddress
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import httpx
import pandas as pd
import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
import config
from persistencia import auth
from persistencia.repository import GenericRepository
from services import client
from services.transport import tls_context

PASSWORD = 'Teste seguro do template 2026!'


def test_real_https_desktop_crud_and_certificate_validation(administrator, tmp_path, monkeypatch):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'localhost')])
    now = datetime.now(timezone.utc)
    certificate = (x509.CertificateBuilder().subject_name(subject).issuer_name(subject).public_key(key.public_key())
        .serial_number(x509.random_serial_number()).not_valid_before(now-timedelta(minutes=1))
        .not_valid_after(now+timedelta(hours=1))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName('localhost'), x509.IPAddress(ipaddress.ip_address('127.0.0.1'))]), critical=False)
        .sign(key, hashes.SHA256()))
    cert_file, key_file = tmp_path/'cert.pem', tmp_path/'key.pem'
    cert_file.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
    key_file.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    env = dict(os.environ, NEXLIFY_API_MODE='server', NEXLIFY_ENV='development',
        NEXLIFY_DATABASE_URL=administrator.url.render_as_string(hide_password=False), NEXLIFY_LOG_DIR=str(tmp_path/'logs'))
    env.pop('NEXLIFY_AUDIT_URL', None)
    root = Path(__file__).resolve().parents[1]
    process = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'services.api:app', '--host', '127.0.0.1',
        '--port', str(port), '--ssl-certfile', str(cert_file), '--ssl-keyfile', str(key_file), '--no-access-log'],
        cwd=root, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    url = f'https://127.0.0.1:{port}'
    try:
        with httpx.Client(verify=tls_context(str(cert_file)), trust_env=False, timeout=1) as transport:
            deadline = time.monotonic() + 20
            while True:
                if process.poll() is not None:
                    pytest.fail('Servidor HTTPS encerrou durante a inicialização.')
                try:
                    if transport.get(url + '/health').status_code == 200:
                        break
                except httpx.HTTPError:
                    if time.monotonic() >= deadline:
                        raise
                    time.sleep(0.1)
        monkeypatch.setattr(config, 'API_MODE', 'client')
        monkeypatch.setattr(config, 'API_URL', url)
        monkeypatch.setattr(config, 'API_CA', '')
        assert client.login('admin', PASSWORD) == 'connection_error'
        monkeypatch.setattr(config, 'API_CA', str(cert_file))
        assert auth.verify_user_credentials('admin', PASSWORD)['username'] == 'admin'
        GenericRepository.write_dataframe_to_table(pd.DataFrame([{'nome': 'HTTPS real'}]), 'tipos_vegetais')
        frame = GenericRepository.read_table_to_dataframe('tipos_vegetais')
        assert frame['nome'].tolist() == ['HTTPS real']
        GenericRepository.update_table('tipos_vegetais', {'nome': 'Updated HTTPS'}, {'nome': 'HTTPS real'})
        assert GenericRepository.read_table_to_dataframe('tipos_vegetais')['nome'].tolist() == ['Updated HTTPS']
        GenericRepository.delete_from_table('tipos_vegetais', {'nome': 'Updated HTTPS'})
        assert GenericRepository.read_table_to_dataframe('tipos_vegetais').empty
        assert GenericRepository.read_vegetais_com_tipo().empty
        client.logout()
        with pytest.raises(PermissionError):
            GenericRepository.read_table_to_dataframe('tipos_vegetais')
    finally:
        client._token = None
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
