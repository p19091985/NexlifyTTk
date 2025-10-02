# services/data_service.py
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

        1. Atualiza a categoria da linguagem.
        2. Grava um registro de auditoria em uma tabela de log.

        Se qualquer passo falhar, a transação inteira é revertida (rollback).

        Returns:
            tuple[bool, str]: (Sucesso, Mensagem)
        """
        engine = GenericRepository.get_engine()
        if not engine:
            return False, "Não foi possível conectar ao banco de dados."

        with engine.connect() as connection:
            with connection.begin() as transaction:
                try:
                    update_values = {'categoria': nova_categoria}
                    where_conditions = {'nome': nome_linguagem}

                    rows_updated = GenericRepository.update_table(
                        'linguagens_programacao',
                        update_values=update_values,
                        where_conditions=where_conditions,
                        connection=connection
                    )

                    if rows_updated == 0:
                        transaction.rollback()
                        return False, f"Linguagem '{nome_linguagem}' não encontrada para atualização."

                    log_data = {
                        'timestamp': [datetime.now()],
                        'usuario': [usuario],
                        'acao': [f"Reclassificou '{nome_linguagem}' para '{nova_categoria}'"]
                    }
                    df_log = pd.DataFrame(log_data)

                    GenericRepository.write_dataframe_to_table(
                        df_log,
                        'log_alteracoes',
                        connection=connection
                    )

                    logging.info("Transação de reclassificação e log bem-sucedida.")
                    return True, f"Linguagem '{nome_linguagem}' reclassificada com sucesso!"

                except Exception as e:
                    logging.error(f"Erro na transação. Rollback executado. Detalhe: {e}")
                    return False, f"Ocorreu um erro. A operação foi revertida. Detalhe: {e}"