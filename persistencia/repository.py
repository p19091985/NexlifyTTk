# persistencia/repository.py
import logging
import pandas as pd
from sqlalchemy import text, exc
from .database import DatabaseManager


class GenericRepository:
    """
    Classe genérica para interagir com o banco de dados.
    Abstrai as operações CRUD e utiliza DataFrames do Pandas para manipulação de dados.
    Agora, suporta transações externas.
    """

    @classmethod
    def get_engine(cls):
        """Obtém a engine do SQLAlchemy de forma centralizada."""
        try:
            return DatabaseManager.get_engine()
        except (FileNotFoundError, KeyError, ConnectionError) as e:
            logging.error(f"Falha crítica ao obter a engine do banco de dados: {e}")
            return None

    @classmethod
    def read_table_to_dataframe(cls, table_name: str, columns: list = None, where_conditions: dict = None,
                                connection=None) -> pd.DataFrame:
        """
        Lê dados de uma tabela. Pode operar dentro de uma transação existente se uma 'connection' for passada.
        """
        query_str = f"SELECT {', '.join(columns) if columns else '*'} FROM {table_name}"
        params = {}
        if where_conditions:
            where_clauses = [f"{key} = :{key}" for key in where_conditions.keys()]
            query_str += " WHERE " + " AND ".join(where_clauses)
            params = where_conditions

        engine = cls.get_engine() if connection is None else None
        conn = connection if connection is not None else engine.connect()

        try:
            df = pd.read_sql(text(query_str), conn, params=params)
            logging.info(f"Leitura de {len(df)} registros da tabela '{table_name}' bem-sucedida.")
            return df
        except exc.SQLAlchemyError as e:
            logging.error(f"Erro ao ler a tabela '{table_name}': {e}")
            if connection: raise
            return pd.DataFrame()
        finally:
            if connection is None and conn:
                conn.close()

    @classmethod
    def write_dataframe_to_table(cls, df: pd.DataFrame, table_name: str, if_exists: str = 'append', connection=None):
        """
        Grava um DataFrame em uma tabela. Pode operar dentro de uma transação existente.
        """
        if df.empty:
            logging.warning(f"Operação de escrita na tabela '{table_name}' abortada (DataFrame vazio).")
            return False

        db_object = connection if connection is not None else cls.get_engine()

        if not db_object:
            logging.error("Engine/Conexão do banco de dados não disponível.")
            return False

        try:
            df.to_sql(table_name, db_object, if_exists=if_exists, index=False)
            logging.info(f"{len(df)} registros escritos com sucesso na tabela '{table_name}'.")
            return True
        except exc.SQLAlchemyError as e:
            logging.error(f"Erro ao escrever na tabela '{table_name}': {e}")
            if connection: raise
            return False

    @classmethod
    def delete_from_table(cls, table_name: str, where_conditions: dict, connection=None):
        """
        Deleta registros de uma tabela. Pode operar dentro de uma transação existente.
        """
        if not where_conditions:
            logging.error("A exclusão requer uma condição WHERE.")
            return -1

        where_clauses = [f"{key} = :{key}" for key in where_conditions.keys()]
        query = text(f"DELETE FROM {table_name} WHERE {' AND '.join(where_clauses)}")

        engine = cls.get_engine() if connection is None else None
        conn = connection if connection is not None else engine.connect()

        try:
            result = conn.execute(query, where_conditions)
            if connection is None: conn.commit()
            logging.info(f"{result.rowcount} registros deletados da tabela '{table_name}'.")
            return result.rowcount
        except exc.SQLAlchemyError as e:
            logging.error(f"Erro ao deletar da tabela '{table_name}': {e}")
            if connection: raise
            return -1
        finally:
            if connection is None and conn:
                conn.close()

    @classmethod
    def update_table(cls, table_name: str, update_values: dict, where_conditions: dict, connection=None):
        """
        Atualiza registros em uma tabela. Pode operar dentro de uma transação existente.
        """
        if not update_values or not where_conditions:
            logging.error("Update requer valores para atualizar e uma condição WHERE.")
            return -1

        set_clauses = [f"{key} = :{key}" for key in update_values.keys()]
        where_clauses = [f"{key} = :whr_{key}" for key in where_conditions.keys()]

        params = update_values.copy()
        params.update({f"whr_{key}": value for key, value in where_conditions.items()})

        # --- CORREÇÃO APLICADA AQUI ---
        # A query agora usa a cláusula WHERE com os parâmetros prefixados (ex: :whr_nome)
        query = text(f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)}")

        engine = cls.get_engine() if connection is None else None
        conn = connection if connection is not None else engine.connect()

        try:
            result = conn.execute(query, params)
            if connection is None: conn.commit()
            logging.info(f"{result.rowcount} registros atualizados na tabela '{table_name}'.")
            return result.rowcount
        except exc.SQLAlchemyError as e:
            logging.error(f"Erro ao atualizar a tabela '{table_name}': {e}")
            if connection: raise
            return -1
        finally:
            if connection is None and conn:
                conn.close()

