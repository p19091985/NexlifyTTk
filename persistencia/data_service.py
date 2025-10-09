# persistencia/data_service.py
import logging
import pandas as pd
from datetime import datetime
from persistencia.repository import GenericRepository
from persistencia.database import DatabaseManager


class DataService:
    """
    Camada de serviço para encapsular a lógica de negócio e as transações.
    """

    @staticmethod
    def reclassificar_e_logar(nome_linguagem: str, nova_categoria: str, usuario: str):
        """
        Exemplo de uma operação de negócio que envolve múltiplos passos e
        deve ser executada em uma única transação atômica.
        """
        engine = GenericRepository.get_engine()
        if not engine:
            return False, "Não foi possível conectar ao banco de dados."

        try:
            with engine.connect() as connection:
                with connection.begin() as transaction:  # Inicia a transação
                    # Passo 1: Atualizar a linguagem
                    update_values = {'CATEGORIA': nova_categoria}
                    where_conditions = {'NOME': nome_linguagem}
                    rows_updated = GenericRepository.update_table('LINGUAGENS_PROGRAMACAO', update_values=update_values,
                                                                  where_conditions=where_conditions,
                                                                  connection=connection)

                    if rows_updated == 0:
                        transaction.rollback()
                        raise ValueError(f"Linguagem '{nome_linguagem}' não encontrada para atualização.")

                    # Passo 2: Criar o log
                    log_data = {'TIMESTAMP': [datetime.now()], 'LOGIN_USUARIO': [usuario],
                                'ACAO': [f"Reclassificou '{nome_linguagem}' para '{nova_categoria}'"]}
                    df_log = pd.DataFrame(log_data)
                    GenericRepository.write_dataframe_to_table(df_log, 'LOG_ALTERACOES', connection=connection)

            logging.info("Transação de reclassificação e log bem-sucedida.")
            return True, f"Linguagem '{nome_linguagem}' reclassificada com sucesso!"

        except Exception as e:
            logging.error(f"Erro na transação de reclassificação. Rollback executado. Detalhe: {e}")
            return False, f"Ocorreu um erro. A operação foi revertida. Detalhe: {e}"

    @staticmethod
    def rename_especie_gato_e_logar(nome_antigo: str, nome_novo: str, usuario: str):
        """
        Transação atómica para renomear uma espécie de gato e registar a alteração no log.
        """
        engine = GenericRepository.get_engine()
        if not engine:
            return False, "Não foi possível conectar ao banco de dados."

        try:
            with engine.connect() as connection:
                with connection.begin() as transaction:  # Inicia a transação
                    # Passo 1: Renomear a espécie
                    update_values = {'NOME_ESPECIE': nome_novo}
                    where_conditions = {'NOME_ESPECIE': nome_antigo}
                    rows_updated = GenericRepository.update_table('ESPECIE_GATOS', update_values=update_values,
                                                                  where_conditions=where_conditions,
                                                                  connection=connection)

                    if rows_updated == 0:
                        raise ValueError(f"Espécie '{nome_antigo}' não encontrada para renomear.")

                    # Passo 2: Registar a alteração no log
                    log_data = {'TIMESTAMP': [datetime.now()], 'LOGIN_USUARIO': [usuario],
                                'ACAO': [f"Renomeou a espécie de gato de '{nome_antigo}' para '{nome_novo}'"]}
                    df_log = pd.DataFrame(log_data)
                    GenericRepository.write_dataframe_to_table(df_log, 'LOG_ALTERACOES', connection=connection)

            logging.info(f"Transação de renomeação da espécie '{nome_antigo}' bem-sucedida.")
            return True, "Espécie renomeada e alteração auditada com sucesso!"

        except Exception as e:
            logging.error(f"Erro na transação de renomeação. Rollback executado. Detalhe: {e}")
            return False, f"Ocorreu um erro. A operação foi revertida. Detalhe: {e}"