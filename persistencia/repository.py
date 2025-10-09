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
    def _build_where_clause(cls, conditions: dict):
        """
        Constrói a cláusula WHERE e o dicionário de parâmetros de forma segura,
        suportando operadores no nome da chave (ex: 'coluna LIKE').
        """
        if not conditions:
            return "", {}

        where_clauses = []
        params = {}
        i = 0
        for key_with_operator, value in conditions.items():
            parts = key_with_operator.split()

            column_name = parts[0].upper()

            param_name = f"param_{i}"
            i += 1

            if len(parts) > 1:
                operator = " ".join(parts[1:])
                where_clauses.append(f"{column_name} {operator} :{param_name}")
            else:
                where_clauses.append(f"{column_name} = :{param_name}")

            params[param_name] = value

        return " WHERE " + " AND ".join(where_clauses), params


    @classmethod
    def read_table_to_dataframe(cls, table_name: str, columns: list = None, where_conditions: dict = None,
                                connection=None) -> pd.DataFrame:
        engine = cls.get_engine() if connection is None else None
        conn = connection if connection is not None else (engine.connect() if engine else None)
        if not conn:
            logging.warning(f"Operação de leitura em '{table_name}' abortada (banco desativado).")
            return pd.DataFrame()

        # MODIFICAÇÃO: Nomes de tabela e colunas na query sempre em maiúsculas
        query_cols = ', '.join([col.upper() for col in columns]) if columns else '*'
        query_str = f"SELECT {query_cols} FROM {table_name.upper()}"

        where_clause, params = cls._build_where_clause(where_conditions)
        query_str += where_clause

        try:
            df = pd.read_sql(text(query_str), conn, params=params)

            # --- PONTO CHAVE DA IMUNIDADE: Padroniza colunas para minúsculas após a leitura ---
            if not df.empty:
                df.columns = [col.lower() for col in df.columns]

            logging.info(f"Leitura de {len(df)} registros da tabela '{table_name.upper()}' bem-sucedida.")
            return df
        except exc.SQLAlchemyError as e:
            logging.error(f"Erro ao ler a tabela '{table_name.upper()}': {e}")
            raise
        finally:
            if connection is None and conn:
                conn.close()

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
                     SELECT
                         lp.ID,
                         lp.NOME,
                         tl.NOME AS TIPO,
                         lp.ANO_CRIACAO,
                         lp.CATEGORIA
                     FROM
                         LINGUAGENS_PROGRAMACAO lp
                     LEFT JOIN
                         TIPOS_LINGUAGEM tl ON lp.ID_TIPO = tl.ID
                     ORDER BY lp.ID
                     """)

        try:
            with engine.connect() as conn:
                df = pd.read_sql(query, conn)

                # --- PONTO CHAVE DA IMUNIDADE: Padroniza colunas para minúsculas após a leitura ---
                if not df.empty:
                    df.columns = [col.lower() for col in df.columns]

                logging.info(f"Leitura com JOIN de {len(df)} registros de linguagens bem-sucedida.")
                return df
        except exc.SQLAlchemyError as e:
            logging.error(f"Erro ao ler linguagens com JOIN: {e}")
            raise

    @classmethod
    def write_dataframe_to_table(cls, df: pd.DataFrame, table_name: str, if_exists: str = 'append', connection=None):
        db_object = connection if connection is not None else cls.get_engine()
        if not db_object:
            logging.warning(f"Operação de escrita em '{table_name.upper()}' abortada (banco desativado).")
            return False

        if df.empty:
            logging.warning(f"Operação de escrita na tabela '{table_name.upper()}' abortada (DataFrame vazio).")
            return False

        # Garante que os nomes das colunas do DataFrame estão em maiúsculas para corresponder ao schema
        df.columns = [col.upper() for col in df.columns]

        conn = None
        is_external_connection = connection is not None
        try:
            conn = connection if is_external_connection else db_object.connect()
            target_table = table_name.upper()

            if not is_external_connection:
                with conn.begin():
                    df.to_sql(target_table, conn, if_exists=if_exists, index=False)
            else:
                df.to_sql(target_table, conn, if_exists=if_exists, index=False)

            logging.info(f"{len(df)} registros escritos com sucesso na tabela '{target_table}'.")
            return True
        except exc.SQLAlchemyError as e:
            logging.error(f"Erro ao escrever na tabela '{table_name.upper()}': {e}")
            raise
        finally:
            if not is_external_connection and conn:
                conn.close()

    @classmethod
    def delete_from_table(cls, table_name: str, where_conditions: dict, connection=None):
        engine = cls.get_engine() if connection is None else None
        conn = connection if connection is not None else (engine.connect() if engine else None)
        if not conn:
            logging.warning(f"Operação de exclusão em '{table_name.upper()}' abortada (banco desativado).")
            return -1

        if not where_conditions:
            raise ValueError("A exclusão requer uma condição WHERE.")

        where_clause, params = cls._build_where_clause(where_conditions)
        query = text(f"DELETE FROM {table_name.upper()}{where_clause}")

        try:
            if connection is None:
                with conn.begin():
                    result = conn.execute(query, params)
            else:
                result = conn.execute(query, params)

            logging.info(f"{result.rowcount} registros deletados da tabela '{table_name.upper()}'.")
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
        if not conn:
            logging.warning(f"Operação de atualização em '{table_name.upper()}' abortada (banco desativado).")
            return -1

        if not update_values or not where_conditions:
            raise ValueError("Update requer valores para atualizar e uma condição WHERE.")

        # MODIFICAÇÃO: Garante que colunas na cláusula SET estejam em maiúsculas
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

            logging.info(f"{result.rowcount} registros atualizados na tabela '{table_name.upper()}'.")
            return result.rowcount
        except exc.SQLAlchemyError as e:
            logging.error(f"Erro ao atualizar a tabela '{table_name.upper()}': {e}")
            raise
        finally:
            if connection is None and conn:
                conn.close()