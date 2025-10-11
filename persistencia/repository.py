# persistencia/repository.py
import logging
import pandas as pd
from sqlalchemy import text, exc
from .database import DatabaseManager


class GenericRepository:
    @classmethod
    def get_engine(cls):
        try:
            return DatabaseManager.get_engine()
        except Exception as e:
            logging.error(f"Falha crítica ao obter a engine do banco de dados: {e}")
            return None

    @classmethod
    def _build_where_clause(cls, conditions: dict):
        if not conditions:
            return "", {}
        where_clauses = []
        params = {}
        for i, (key, value) in enumerate(conditions.items()):
            parts = key.split()
            column_name = parts[0].upper()
            param_name = f"param_{i}"
            operator = " ".join(parts[1:]) if len(parts) > 1 else "="
            where_clauses.append(f"{column_name} {operator} :{param_name}")
            params[param_name] = value
        return " WHERE " + " AND ".join(where_clauses), params

    @classmethod
    def read_table_to_dataframe(cls, table_name: str, columns: list = None, where_conditions: dict = None,
                                connection=None) -> pd.DataFrame:
        engine = cls.get_engine() if connection is None else None
        conn = connection if connection is not None else (engine.connect() if engine else None)
        if not conn:
            return pd.DataFrame()

        query_cols = ', '.join([col.upper() for col in columns]) if columns else '*'
        query_str = f"SELECT {query_cols} FROM {table_name.upper()}"
        where_clause, params = cls._build_where_clause(where_conditions)
        query_str += where_clause

        try:
            df = pd.read_sql(text(query_str), conn, params=params)
            if not df.empty:
                df.columns = [col.lower() for col in df.columns]
            return df
        except exc.SQLAlchemyError as e:
            logging.error(f"Erro ao ler a tabela '{table_name.upper()}': {e}")
            raise
        finally:
            if connection is None and conn:
                conn.close()

    @classmethod
    def read_linguagens_com_tipo(cls) -> pd.DataFrame:
        engine = cls.get_engine()
        if not engine: return pd.DataFrame()
        query = text(
            "SELECT lp.ID, lp.NOME, tl.NOME AS TIPO, lp.ANO_CRIACAO, lp.CATEGORIA FROM LINGUAGENS_PROGRAMACAO lp LEFT JOIN TIPOS_LINGUAGEM tl ON lp.ID_TIPO = tl.ID ORDER BY lp.ID")
        try:
            with engine.connect() as conn:
                df = pd.read_sql(query, conn)
                if not df.empty:
                    df.columns = [col.lower() for col in df.columns]
                return df
        except exc.SQLAlchemyError as e:
            logging.error(f"Erro ao ler linguagens com JOIN: {e}")
            raise

    @classmethod
    def write_dataframe_to_table(cls, df: pd.DataFrame, table_name: str, if_exists: str = 'append', connection=None):
        db_object = connection if connection is not None else cls.get_engine()
        if not db_object or df.empty: return False

        df.columns = [col.upper() for col in df.columns]
        conn = connection if connection is not None else db_object.connect()
        try:
            target_table = table_name.upper()
            if connection is None:
                with conn.begin():
                    df.to_sql(target_table, conn, if_exists=if_exists, index=False)
            else:
                df.to_sql(target_table, conn, if_exists=if_exists, index=False)
            return True
        except exc.SQLAlchemyError as e:
            logging.error(f"Erro ao escrever na tabela '{table_name.upper()}': {e}")
            raise
        finally:
            if connection is None and conn:
                conn.close()

    @classmethod
    def delete_from_table(cls, table_name: str, where_conditions: dict, connection=None):
        engine = cls.get_engine() if connection is None else None
        conn = connection if connection is not None else (engine.connect() if engine else None)
        if not conn: return -1
        if not where_conditions: raise ValueError("A exclusão requer uma condição WHERE.")
        where_clause, params = cls._build_where_clause(where_conditions)
        query = text(f"DELETE FROM {table_name.upper()}{where_clause}")
        try:
            result = conn.execute(query, params) if connection is not None else conn.execute(query, params,
                                                                                             autocommit=True)
            if connection is None: conn.commit()
            return result.rowcount
        except exc.SQLAlchemyError as e:
            logging.error(f"Erro ao deletar da tabela '{table_name.upper()}': {e}")
            raise
        finally:
            if connection is None and conn:
                conn.close()

    @classmethod
    def update_table(cls, table_name: str, update_values: dict, where_conditions: dict, connection=None):
        engine = cls.get_engine() if connection is None else None
        conn = connection if connection is not None else (engine.connect() if engine else None)
        if not conn: return -1
        if not update_values or not where_conditions: raise ValueError("Update requer valores e condição.")

        set_clauses = [f"{key.upper()} = :{key}" for key in update_values.keys()]
        where_clause, where_params = cls._build_where_clause(where_conditions)
        params = {**update_values, **where_params}
        query = text(f"UPDATE {table_name.upper()} SET {', '.join(set_clauses)}{where_clause}")

        try:
            if connection is None:
                with conn.begin():
                    result = conn.execute(query, params)
            else:
                result = conn.execute(query, params)
            return result.rowcount
        except exc.SQLAlchemyError as e:
            logging.error(f"Erro ao atualizar a tabela '{table_name.upper()}': {e}")
            raise
        finally:
            if connection is None and conn:
                conn.close()