import pytest
import config
from persistencia.database import create_database_engine


def test_production_rejects_postgres_without_verified_tls(monkeypatch):
    monkeypatch.setattr(config, 'ENVIRONMENT', 'production')
    with pytest.raises(ValueError, match='verify-full'):
        create_database_engine({'type':'postgresql','host':'localhost','dbname':'test','user':'test','sslmode':'disable'})


def test_production_rejects_oracle_plain_tcp(monkeypatch):
    monkeypatch.setattr(config, 'ENVIRONMENT', 'production')
    with pytest.raises(ValueError, match='TCPS'):
        create_database_engine({'type':'oracle','host':'localhost','dbname':'test','user':'test','oracle_protocol':'tcp'})
