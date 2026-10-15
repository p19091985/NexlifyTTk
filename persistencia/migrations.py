"""Explicit additive revisions; rollback is a verified pre-migration snapshot."""
from datetime import datetime, timezone
from sqlalchemy import inspect, select, insert
from .schema import metadata, schema_versions

LATEST_VERSION = 3
REVISION_TABLES = {
    1: {'usuarios', 'tipos_vegetais', 'vegetais', 'especie_gatos', 'log_alteracoes', 'auth_state', 'schema_versions'},
    2: {'user_security', 'api_sessions', 'audit_outbox', 'external_identities'},
    3: {'email_mfa'},
}


def current_version(engine):
    if not inspect(engine).has_table('schema_versions'):
        return 0
    with engine.connect() as connection:
        versions = sorted(connection.execute(select(schema_versions.c.version)).scalars())
        revision = max(versions, default=0)
        if revision <= LATEST_VERSION and versions != list(range(1, revision + 1)):
            raise RuntimeError('Histórico de revisões incompleto. Restaure uma cópia validada.')
        return revision


def upgrade(engine):
    revision = current_version(engine)
    if revision > LATEST_VERSION:
        raise RuntimeError('Banco criado por uma versão mais nova do template.')
    inspector = inspect(engine)
    for table in metadata.sorted_tables:
        if inspector.has_table(table.name):
            actual = {column['name'].lower() for column in inspector.get_columns(table.name)}
            if not set(table.columns.keys()).issubset(actual):
                raise RuntimeError(f'Schema incompatível em {table.name}; restaure ou migre explicitamente.')
    for version in range(revision + 1, LATEST_VERSION + 1):
        with engine.begin() as connection:
            tables = [table for table in metadata.sorted_tables if table.name in REVISION_TABLES[version]]
            metadata.create_all(connection, tables=tables)
            connection.execute(insert(schema_versions).values(version=version,
                               applied_at=datetime.now(timezone.utc).replace(tzinfo=None)))
    # Detect incomplete/reverted schemas even if their revision marker survived.
    if not set(metadata.tables).issubset(inspect(engine).get_table_names()):
        raise RuntimeError('Schema incompleto para a revisão registrada. Restaure o backup.')
    return LATEST_VERSION
