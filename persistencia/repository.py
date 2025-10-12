# persistencia/repository.py
import pandas as pd
from sqlalchemy import text, exc
import logging

# Importa o DatabaseManager para ser a única fonte de conexão
from .database import DatabaseManager

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class GenericRepository:
    """
    Uma classe genérica para interagir com o banco de dados usando SQLAlchemy e Pandas.
    Fornece métodos básicos de CRUD (Create, Read, Update, Delete).
    """

    @staticmethod
    def get_engine():
        """
        Retorna a instância do motor diretamente do DatabaseManager.
        Isso garante que toda a aplicação use a mesma e única conexão.
        """
        return DatabaseManager.get_engine()

    @staticmethod
    def execute_query_to_dataframe(query: str, params: dict = None):
        """
        Executa uma query SQL e retorna o resultado como um DataFrame Pandas,
        com todas as colunas convertidas para minúsculas para padronização.
        """
        engine = GenericRepository.get_engine()
        try:
            with engine.connect() as connection:
                df = pd.read_sql_query(text(query), connection, params=params)

                # Converte todas as colunas para minúsculas, tornando o código indiferente ao schema do BD.
                df.columns = [col.lower() for col in df.columns]

                return df
        except exc.SQLAlchemyError as e:
            logging.error(f"Erro ao executar a query: {query}\nErro: {e}")
            raise

    @staticmethod
    def read_table_to_dataframe(table_name: str, columns: list = None, where_conditions: dict = None):
        """Lê dados de uma tabela e retorna como DataFrame, com filtros opcionais."""
        cols = ", ".join(columns) if columns else "*"
        query = f"SELECT {cols} FROM {table_name.upper()}"
        if where_conditions:
            conditions = " AND ".join([f"{key} = :{key.lower()}" for key in where_conditions.keys()])
            query += f" WHERE {conditions}"

            params_lower = {k.lower(): v for k, v in where_conditions.items()}
            return GenericRepository.execute_query_to_dataframe(query, params=params_lower)

        return GenericRepository.execute_query_to_dataframe(query, params=where_conditions)

    @staticmethod
    def read_vegetais_com_tipo():
        """
        Busca todos os vegetais e faz o JOIN com a tabela de tipos para obter o nome do tipo.
        Específico para o Painel de Vegetais.
        """
        query = """
                SELECT v.ID, v.NOME, tv.NOME as TIPO
                FROM VEGETAIS v
                         LEFT JOIN TIPOS_VEGETAIS tv ON v.ID_TIPO = tv.ID
                ORDER BY v.NOME;
                """
        return GenericRepository.execute_query_to_dataframe(query)

    @staticmethod
    def write_dataframe_to_table(df: pd.DataFrame, table_name: str):
        """Escreve um DataFrame inteiro em uma tabela do banco de dados."""
        engine = GenericRepository.get_engine()
        try:
            df.to_sql(table_name.upper(), con=engine, if_exists='append', index=False)
            logging.info(f"{len(df)} registros inseridos com sucesso na tabela '{table_name.upper()}'.")
        except exc.SQLAlchemyError as e:
            logging.error(f"Erro ao escrever na tabela '{table_name.upper()}': {e}")
            raise

    @staticmethod
    def update_table(table_name: str, update_values: dict, where_conditions: dict):
        """Atualiza registros em uma tabela com base em condições."""
        engine = GenericRepository.get_engine()
        set_clause = ", ".join([f"{key} = :{key.lower()}_val" for key in update_values.keys()])
        where_clause = " AND ".join([f"{key} = :wh_{key.lower()}" for key in where_conditions.keys()])

        params = {}
        for key, value in update_values.items():
            params[f'{key.lower()}_val'] = value
        for key, value in where_conditions.items():
            params[f'wh_{key.lower()}'] = value

        query = f"UPDATE {table_name.upper()} SET {set_clause} WHERE {where_clause}"

        try:
            with engine.connect() as connection:
                with connection.begin() as transaction:
                    connection.execute(text(query), params)
                    # CORREÇÃO: A linha transaction.commit() foi removida daqui.
                    # O bloco 'with' já gerencia o commit e rollback automaticamente.
            logging.info(f"Tabela '{table_name.upper()}' atualizada com sucesso.")
        except exc.SQLAlchemyError as e:
            logging.error(f"Erro ao atualizar a tabela '{table_name.upper()}': {e}")
            raise

    @staticmethod
    def delete_from_table(table_name: str, where_conditions: dict):
        """Deleta registros de uma tabela com base em condições."""
        engine = GenericRepository.get_engine()
        where_clause = " AND ".join([f"{key} = :{key.lower()}" for key in where_conditions.keys()])
        params = {k.lower(): v for k, v in where_conditions.items()}
        query = f"DELETE FROM {table_name.upper()} WHERE {where_clause}"
        try:
            with engine.connect() as connection:
                with connection.begin() as transaction:
                    connection.execute(text(query), params)
                    # CORREÇÃO: A linha transaction.commit() foi removida daqui.
                    # O bloco 'with' já gerencia o commit e rollback automaticamente.
            logging.info(f"Registros da tabela '{table_name.upper()}' deletados com sucesso.")
        except exc.SQLAlchemyError as e:
            logging.error(f"Erro ao deletar da tabela '{table_name.upper()}': {e}")
            raise