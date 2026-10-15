"""Ensaio real opcional: somente banco dedicado explicitamente via variável de teste."""
import os
from uuid import uuid4
import pytest
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Identity, select, insert, update, delete

pytestmark = pytest.mark.integration


def test_external_roundtrip():
    url = os.environ.get('NEXLIFY_TEST_DATABASE_URL')
    if not url:
        pytest.skip('Defina NEXLIFY_TEST_DATABASE_URL para um banco dedicado de homologação.')
    engine = create_engine(url, hide_parameters=True, pool_pre_ping=True)
    metadata = MetaData()
    table = Table('nexlify_test_' + uuid4().hex[:10], metadata,
                  Column('id', Integer, Identity(), primary_key=True), Column('value', String(80)))
    created = False
    try:
        metadata.create_all(engine)
        created = True
        with engine.begin() as connection:
            connection.execute(insert(table).values(value='antes'))
        with engine.connect() as connection:
            transaction = connection.begin()
            connection.execute(update(table).values(value='rollback'))
            transaction.rollback()
            assert connection.execute(select(table.c.value)).scalar_one() == 'antes'
        with engine.begin() as connection:
            connection.execute(update(table).values(value='depois'))
            assert connection.execute(select(table.c.value)).scalar_one() == 'depois'
            connection.execute(delete(table))
    finally:
        if created:
            metadata.drop_all(engine)
        engine.dispose()
