"""CRUD com identificadores permitidos, parâmetros e autorização no acesso a dados."""
import pandas as pd
from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.sql import Select
from sqlalchemy.exc import SQLAlchemyError
import config
from .database import DatabaseManager
from .passwords import valid_stored_hash
from .schema import metadata, usuarios, vegetais, tipos_vegetais, log_alteracoes, auth_state, ROLES
from .auth import authorize, utcnow, ADMIN, is_legacy_hash
from datetime import date, datetime
from decimal import Decimal
from numbers import Number


def _scalar(value):
    # SQLAlchemy expressions passed as values are SQL, not bound parameters.
    if value is not None and not isinstance(value, (str, bytes, Number, Decimal, date, datetime)):
        raise ValueError('Use somente valores escalares nos campos e filtros.')
    return value


def _query_tables(query):
    from sqlalchemy import Table, Column
    from sqlalchemy.sql import visitors, operators
    from sqlalchemy.sql.selectable import Alias, Subquery, CTE, Join, ScalarSelect, CompoundSelect
    from sqlalchemy.sql.elements import (Label, BindParameter, BinaryExpression, BooleanClauseList,
                                         UnaryExpression, Grouping, ClauseList, Null, True_, False_)
    from sqlalchemy.sql.functions import FunctionElement
    allowed = (Select, Table, Column, Alias, Subquery, CTE, Join, ScalarSelect, CompoundSelect,
               Label, BindParameter, BinaryExpression, BooleanClauseList, UnaryExpression,
               Grouping, ClauseList, Null, True_, False_)
    tables = set()
    secret = usuarios.c.senha_criptografada
    for node in visitors.iterate(query):
        if isinstance(node, FunctionElement):
            if node.name.lower() not in {'count', 'sum', 'min', 'max', 'avg', 'lower', 'upper', 'coalesce', 'length'} or getattr(node, 'packagenames', ()):
                raise ValueError('Função SQL não permitida.')
        elif not isinstance(node, allowed):
            raise ValueError('Expressão SQL não permitida; use colunas do schema e parâmetros.')
        if isinstance(node, Table):
            if node is not _table(node.name):
                raise ValueError('Use as tabelas originais do schema do template.')
            tables.add(node.name)
        if isinstance(node, Column) and secret in node.proxy_set:
            raise ValueError('Hashes de senha não são expostos pelo repositório.')
        if isinstance(node, Select):
            if any(secret in column.proxy_set for column in node.selected_columns):
                raise ValueError('Hashes de senha não são expostos pelo repositório.')
            if (node._for_update_arg is not None or node._hints or node._statement_hints
                    or node._prefixes or node._suffixes):
                raise ValueError('Modificadores SQL não são permitidos nesta API de leitura.')
        if isinstance(getattr(node, 'operator', None), operators.custom_op):
            raise ValueError('Operador SQL personalizado não permitido.')
    if not tables:
        raise ValueError('A consulta deve usar tabelas do schema.')
    return tables


def _table(name):
    if not isinstance(name, str) or name not in {'usuarios', 'vegetais', 'tipos_vegetais', 'especie_gatos', 'log_alteracoes'}:
        raise ValueError('Tabela não permitida.')
    return metadata.tables[name]


def _values(table, values):
    if not values:
        raise ValueError('Informe ao menos uma coluna.')
    normalized = {str(key).lower(): _scalar(value) for key, value in values.items()}
    if not set(normalized).issubset(table.columns.keys()):
        raise ValueError('Coluna não permitida.')
    if table is usuarios:
        if 'tipo_acesso' in normalized and normalized['tipo_acesso'] not in ROLES:
            raise ValueError('Perfil inválido.')
        hashed = normalized.get('senha_criptografada')
        if hashed is not None and (not isinstance(hashed, str) or not valid_stored_hash(hashed) or is_legacy_hash(hashed)):
            raise ValueError('Use hash_password para gerar uma senha válida.')
    return normalized


def _conditions(table, values):
    if not values:
        raise ValueError('Uma condição é obrigatória para alterar ou excluir registros.')
    normalized = {str(key).lower(): _scalar(value) for key, value in values.items()}
    if not set(normalized).issubset(table.columns.keys()) or 'senha_criptografada' in normalized:
        raise ValueError('Coluna de filtro não permitida.')
    return [table.c[key] == value for key, value in normalized.items()]


def _audit(connection, session, action):
    from .audit import record
    record(connection, session['username'], action)


def _protect_admin(connection, conditions, values=None, deleting=False):
    from .auth import lock_authentication_transaction, locked_users_query
    lock_authentication_transaction(connection)
    admins = connection.execute(locked_users_query().where(usuarios.c.tipo_acesso == ADMIN).order_by(usuarios.c.login_usuario)).mappings().all()
    rows = connection.execute(select(usuarios).where(*conditions).with_for_update()).mappings().all()
    if not deleting and values and 'login_usuario' in values:
        raise ValueError('O login não pode ser alterado.')
    loses_admin = deleting or (values and values.get('tipo_acesso', ADMIN) != ADMIN)
    if loses_admin:
        removed = sum(row['tipo_acesso'] == ADMIN for row in rows)
        count = len(admins)
        if removed and count <= removed:
            raise ValueError('Não é permitido remover o último administrador.')
    return rows


class GenericRepository:
    @staticmethod
    def get_engine():
        return DatabaseManager.get_engine()

    @staticmethod
    def execute_query_to_dataframe(query, params=None):
        if config.API_MODE == 'client':
            raise ValueError('Consultas locais não estão disponíveis no cliente da API.')
        if not isinstance(query, Select):
            raise ValueError('Use uma expressão SQLAlchemy select; SQL textual não é aceito aqui.')
        tables = _query_tables(query)
        for name in tables:
            _table(name)
            authorize(name)
        try:
            with GenericRepository.get_engine().connect() as connection:
                return pd.read_sql_query(query, connection, params=params)
        except SQLAlchemyError:
            raise ValueError('Não foi possível consultar os dados. Verifique a conexão e o schema.') from None

    @staticmethod
    def read_table_to_dataframe(table_name, columns=None, where_conditions=None):
        if config.API_MODE == 'client':
            from services.client import request, dataframe
            return dataframe(request('POST', '/read', {'table': table_name, 'columns': columns, 'where': where_conditions}))
        table = _table(table_name)
        if not config.DATABASE_ENABLED:
            return pd.DataFrame()
        authorize(table_name)
        names = columns or [c.name for c in table.columns if c.name != 'senha_criptografada']
        if not set(names).issubset(table.columns.keys()) or 'senha_criptografada' in names:
            raise ValueError('Coluna não permitida para leitura.')
        query = select(*(table.c[name] for name in names))
        if where_conditions:
            query = query.where(*_conditions(table, where_conditions))
        return GenericRepository.execute_query_to_dataframe(query)

    @staticmethod
    def write_dataframe_to_table(df, table_name):
        if config.API_MODE == 'client':
            from services.client import request
            import json
            return request('POST', '/insert', {'table': table_name, 'rows': json.loads(df.to_json(orient='records'))})
        table = _table(table_name)
        session = authorize(table_name, write=True)
        rows = [_values(table, row) for row in df.to_dict(orient='records')]
        if not rows:
            return
        try:
            with GenericRepository.get_engine().begin() as connection:
                session = authorize(table_name, write=True, connection=connection)
                connection.execute(insert(table), rows)
                if table is usuarios:
                    for row in rows:
                        connection.execute(insert(auth_state).values(login_usuario=row['login_usuario'], must_change=1, failed_attempts=0))
                _audit(connection, session, f'Inserção de {len(rows)} registro(s) em {table_name}.')
        except SQLAlchemyError:
            raise ValueError('Não foi possível inserir: verifique duplicidade e campos obrigatórios.') from None

    @staticmethod
    def update_table(table_name, update_values, where_conditions):
        if config.API_MODE == 'client':
            from services.client import request
            return request('POST', '/update', {'table': table_name, 'values': update_values, 'where': where_conditions})
        table = _table(table_name)
        session = authorize(table_name, write=True)
        values = _values(table, update_values)
        conditions = _conditions(table, where_conditions)
        try:
            with GenericRepository.get_engine().begin() as connection:
                session = authorize(table_name, write=True, connection=connection)
                rows = _protect_admin(connection, conditions, values) if table is usuarios else []
                connection.execute(update(table).where(*conditions).values(**values))
                if table is usuarios and 'senha_criptografada' in values:
                    from .auth import _state
                    for row in rows:
                        _state(connection, row['login_usuario'])
                        connection.execute(update(auth_state).where(auth_state.c.login_usuario == row['login_usuario']).values(must_change=1, failed_attempts=0, locked_until=None))
                _audit(connection, session, f'Atualização em {table_name}.')
        except SQLAlchemyError:
            raise ValueError('Não foi possível atualizar: verifique os campos e relacionamentos.') from None

    @staticmethod
    def delete_from_table(table_name, where_conditions):
        if config.API_MODE == 'client':
            from services.client import request
            return request('POST', '/delete', {'table': table_name, 'where': where_conditions})
        table = _table(table_name)
        session = authorize(table_name, write=True)
        conditions = _conditions(table, where_conditions)
        try:
            with GenericRepository.get_engine().begin() as connection:
                session = authorize(table_name, write=True, connection=connection)
                if table is usuarios:
                    rows = _protect_admin(connection, conditions, deleting=True)
                    if any(row['login_usuario'] == session['username'] for row in rows):
                        raise ValueError('Não é permitido excluir a própria conta.')
                connection.execute(delete(table).where(*conditions))
                _audit(connection, session, f'Exclusão em {table_name}.')
        except SQLAlchemyError:
            raise ValueError('Não foi possível excluir: existem registros vinculados.') from None

    @staticmethod
    def read_vegetais_com_tipo():
        if config.API_MODE == 'client':
            from services.client import request, dataframe
            return dataframe(request('GET', '/read_vegetais'))
        query = select(vegetais.c.id, vegetais.c.nome, tipos_vegetais.c.nome.label('tipo')).select_from(
            vegetais.outerjoin(tipos_vegetais)).order_by(vegetais.c.nome)
        return GenericRepository.execute_query_to_dataframe(query)
