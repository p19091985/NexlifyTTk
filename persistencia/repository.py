# persistencia/repository.py
import logging
import pandas as pd
from sqlalchemy import text, exc
from .database import DatabaseManager


class GenericRepository:
    """
    Classe genérica para interagir com o banco de dados.
    Abstrai as operações CRUD e utiliza DataFrames do Pandas para manipulação de dados.
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
        engine = cls.get_engine() if connection is None else None
        conn = connection if connection is not None else (engine.connect() if engine else None)
        if not conn:
            logging.warning(f"Operação de leitura em '{table_name}' abortada (banco desativado).")
            return pd.DataFrame()
        query_str = f"SELECT {', '.join(columns) if columns else '*'} FROM {table_name}"
        params = {}
        if where_conditions:
            where_clauses = [f"{key} = :{key}" for key in where_conditions.keys()]
            query_str += " WHERE " + " AND ".join(where_clauses)
            params = where_conditions
        try:
            df = pd.read_sql(text(query_str), conn, params=params)
            logging.info(f"Leitura de {len(df)} registros da tabela '{table_name}' bem-sucedida.")
            return df
        except exc.SQLAlchemyError as e:
            logging.error(f"Erro ao ler a tabela '{table_name}': {e}")
            raise
        finally:
            if connection is None and conn:
                conn.close()

    # --- NOVO MÉTODO ESPECIALIZADO ---
    @classmethod
    def read_linguagens_com_tipo(cls) -> pd.DataFrame:
        """
        Retorna um DataFrame de linguagens de programação
        já com o nome do tipo (fazendo um JOIN).
        """
        engine = cls.get_engine()
        if not engine:
            return pd.DataFrame()

        query = text("""
                     SELECT lp.id,
                            lp.nome,
                            tl.nome AS tipo,
                            lp.ano_criacao,
                            lp.categoria
                     FROM linguagens_programacao lp
                              LEFT JOIN
                          tipos_linguagem tl ON lp.id_tipo = tl.id
                     ORDER BY lp.id
                     """)

        try:
            with engine.connect() as conn:
                df = pd.read_sql(query, conn)
                logging.info(f"Leitura com JOIN de {len(df)} registros de linguagens bem-sucedida.")
                return df
        except exc.SQLAlchemyError as e:
            logging.error(f"Erro ao ler linguagens com JOIN: {e}")
            raise

    @classmethod
    def write_dataframe_to_table(cls, df: pd.DataFrame, table_name: str, if_exists: str = 'append', connection=None):
        db_object = connection if connection is not None else cls.get_engine()
        if not db_object:
            logging.warning(f"Operação de escrita em '{table_name}' abortada (banco desativado).")
            return False
        if df.empty:
            logging.warning(f"Operação de escrita na tabela '{table_name}' abortada (DataFrame vazio).")
            return False
        try:
            df.to_sql(table_name, db_object, if_exists=if_exists, index=False)
            logging.info(f"{len(df)} registros escritos com sucesso na tabela '{table_name}'.")
            return True
        except exc.SQLAlchemyError as e:
            logging.error(f"Erro ao escrever na tabela '{table_name}': {e}")
            raise

    @classmethod
    def delete_from_table(cls, table_name: str, where_conditions: dict, connection=None):
        engine = cls.get_engine() if connection is None else None
        conn = connection if connection is not None else (engine.connect() if engine else None)
        if not conn:
            logging.warning(f"Operação de exclusão em '{table_name}' abortada (banco desativado).")
            return -1
        if not where_conditions:
            raise ValueError("A exclusão requer uma condição WHERE.")
        where_clauses = [f"{key} = :{key}" for key in where_conditions.keys()]
        query = text(f"DELETE FROM {table_name} WHERE {' AND '.join(where_clauses)}")
        try:
            result = conn.execute(query, where_conditions)
            if connection is None: conn.commit()
            logging.info(f"{result.rowcount} registros deletados da tabela '{table_name}'.")
            return result.rowcount
        except exc.SQLAlchemyError as e:
            logging.error(f"Erro ao deletar da tabela '{table_name}': {e}")
            raise
        finally:
            if connection is None and conn:
                conn.close()

    @classmethod
    def update_table(cls, table_name: str, update_values: dict, where_conditions: dict, connection=None):
        engine = cls.get_engine() if connection is None else None
        conn = connection if connection is not None else (engine.connect() if engine else None)
        if not conn:
            logging.warning(f"Operação de atualização em '{table_name}' abortada (banco desativado).")
            return -1
        if not update_values or not where_conditions:
            raise ValueError("Update requer valores para atualizar e uma condição WHERE.")
        set_clauses = [f"{key} = :{key}" for key in update_values.keys()]
        where_clauses = [f"{key} = :whr_{key}" for key in where_conditions.keys()]
        params = update_values.copy()
        params.update({f"whr_{key}": value for key, value in where_conditions.items()})
        query = text(f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)}")
        try:
            result = conn.execute(query, params)
            if connection is None: conn.commit()
            logging.info(f"{result.rowcount} registros atualizados na tabela '{table_name}'.")
            return result.rowcount
        except exc.SQLAlchemyError as e:
            logging.error(f"Erro ao atualizar a tabela '{table_name}': {e}")
            raise
        finally:
            if connection is None and conn:
                conn.close()