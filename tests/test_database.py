import os
import pytest
from sqlalchemy import select, insert, func
from sqlalchemy.schema import CreateTable
from persistencia.database import DatabaseManager, build_url, create_database_engine, DRIVERS
from persistencia.schema import metadata, usuarios, especie_gatos, schema_versions
from persistencia.security import encrypt_message


def test_initialization_is_idempotent_and_has_no_default_accounts(database):
    with database.begin() as connection:
        connection.execute(insert(especie_gatos).values(nome_especie='Preservar'))
    DatabaseManager.initialize_database()
    with database.connect() as connection:
        assert connection.execute(select(especie_gatos.c.nome_especie)).scalar_one() == 'Preservar'
        assert connection.execute(select(func.count()).select_from(usuarios)).scalar_one() == 0
        assert connection.execute(select(schema_versions.c.version)).scalars().all() == [1, 2, 3]


@pytest.mark.parametrize('kind', tuple(DRIVERS))
def test_driver_and_schema_compilation(kind, monkeypatch):
    monkeypatch.setenv('NEXLIFY_TEST_PASSWORD', 'symbols @:/% secure')
    options = {'type': kind, 'host': 'localhost', 'dbname': 'template', 'user': 'template',
               'password_env': 'NEXLIFY_TEST_PASSWORD', 'path': ':memory:'}
    try:
        engine = create_database_engine(options)
    except RuntimeError as error:
        if 'Driver ausente' in str(error):
            pytest.skip('Driver opcional não instalado')
        raise
    try:
        if kind == 'firebird':
            # Offline compilation targets Firebird 4; a live connection normally
            # discovers this version during dialect initialization.
            engine.dialect.server_version_info = (4, 0)
            engine.dialect.supports_identity_columns = True
        for table in metadata.sorted_tables:
            assert 'CREATE TABLE' in str(CreateTable(table).compile(dialect=engine.dialect))
        if kind != 'sqlite':
            assert engine.url.password == 'symbols @:/% secure'
            assert 'symbols' not in str(engine.url)
    finally:
        engine.dispose()


def test_sqlite_paths_ignore_working_directory(tmp_path, monkeypatch):
    from utils.paths import PROJECT_ROOT
    monkeypatch.chdir(tmp_path)
    assert build_url({'type':'sqlite','path':'example.db'}).database == str(PROJECT_ROOT/'example.db')


def test_future_schema_is_rejected(database):
    from datetime import datetime
    with database.begin() as connection:
        connection.execute(insert(schema_versions).values(version=99, applied_at=datetime.now()))
    with pytest.raises(RuntimeError, match='mais nova'):
        DatabaseManager.initialize_database()


def test_explicit_test_configuration_does_not_use_production_env(monkeypatch):
    monkeypatch.setenv('NEXLIFY_DATABASE_URL', 'postgresql+missing://example.invalid/production')
    engine = create_database_engine({'type':'sqlite','path':':memory:'})
    assert engine.dialect.name == 'sqlite'
    engine.dispose()
