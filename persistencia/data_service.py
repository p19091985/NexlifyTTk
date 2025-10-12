# persistencia/data_service.py
from datetime import datetime
from sqlalchemy import text, exc
from .repository import GenericRepository
import logging


class DataService:
    """
    Classe de serviço para executar operações de negócio complexas e transações atômicas.
    Garante a integridade dos dados em operações que envolvem múltiplas tabelas.
    """

    @staticmethod
    def reclassificar_vegetal_e_logar(nome_vegetal: str, novo_tipo_nome: str, usuario: str):
        """
        Reclassifica um vegetal para um novo tipo e registra a ação na trilha de auditoria.
        Esta operação é atômica: ou ambas as tabelas (vegetais, log_alteracoes) são
        atualizadas, ou nenhuma delas é.
        """
        engine = GenericRepository.get_engine()
        with engine.connect() as connection:
            with connection.begin() as transaction:
                try:
                    # 1. Obter o ID do vegetal e o ID do seu tipo antigo
                    res_vegetal = connection.execute(
                        text("SELECT ID, ID_TIPO FROM VEGETAIS WHERE NOME = :nome"),
                        {'nome': nome_vegetal}
                    ).first()
                    if not res_vegetal:
                        return False, f"Vegetal '{nome_vegetal}' não encontrado."
                    id_vegetal, id_tipo_antigo = res_vegetal

                    # 2. Obter o ID do novo tipo
                    res_novo_tipo = connection.execute(
                        text("SELECT ID FROM TIPOS_VEGETAIS WHERE NOME = :nome"),
                        {'nome': novo_tipo_nome}
                    ).first()
                    if not res_novo_tipo:
                        return False, f"Tipo '{novo_tipo_nome}' não encontrado."
                    id_novo_tipo = res_novo_tipo[0]

                    if id_tipo_antigo == id_novo_tipo:
                        return False, "O vegetal já pertence a este tipo."

                    # 3. Atualizar a tabela de vegetais
                    connection.execute(
                        text("UPDATE VEGETAIS SET ID_TIPO = :id_tipo WHERE ID = :id_vegetal"),
                        {'id_tipo': id_novo_tipo, 'id_vegetal': id_vegetal}
                    )

                    # 4. Criar a mensagem de log
                    acao_log = (f"O vegetal '{nome_vegetal}' (ID: {id_vegetal}) foi reclassificado "
                                f"para o tipo '{novo_tipo_nome}' (ID: {id_novo_tipo}).")

                    # 5. Inserir o registro de log
                    connection.execute(
                        text("""
                             INSERT INTO LOG_ALTERACOES (TIMESTAMP, LOGIN_USUARIO, ACAO)
                             VALUES (:ts, :login, :acao)
                             """),
                        {'ts': datetime.now(), 'login': usuario, 'acao': acao_log}
                    )

                    # 6. Se tudo deu certo, comita a transação
                    transaction.commit()
                    logging.info(f"Transação de reclassificação do vegetal '{nome_vegetal}' concluída com sucesso.")
                    return True, "Vegetal reclassificado e ação auditada com sucesso!"

                except exc.SQLAlchemyError as e:
                    # 7. Se algo deu errado, desfaz tudo (rollback)
                    transaction.rollback()
                    logging.error(f"Falha na transação de reclassificação: {e}")
                    return False, f"Ocorreu um erro no banco de dados: {e}"

    @staticmethod
    def rename_especie_gato_e_logar(nome_antigo: str, nome_novo: str, usuario: str):
        """
        Renomeia uma espécie de gato e registra a ação na trilha de auditoria.
        Operação atômica para garantir consistência.
        """
        engine = GenericRepository.get_engine()
        with engine.connect() as connection:
            with connection.begin() as transaction:
                try:
                    # 1. Verificar se o novo nome já existe
                    res_check = connection.execute(
                        text("SELECT ID FROM ESPECIE_GATOS WHERE NOME_ESPECIE = :nome"),
                        {'nome': nome_novo}
                    ).first()
                    if res_check:
                        return False, f"O nome '{nome_novo}' já está em uso."

                    # 2. Atualizar o nome na tabela de espécies
                    update_stmt = text("UPDATE ESPECIE_GATOS SET NOME_ESPECIE = :novo WHERE NOME_ESPECIE = :antigo")
                    result = connection.execute(update_stmt, {'novo': nome_novo, 'antigo': nome_antigo})

                    if result.rowcount == 0:
                        transaction.rollback()
                        return False, f"A espécie '{nome_antigo}' não foi encontrada para renomear."

                    # 3. Criar e inserir o registro de log
                    acao_log = f"Espécie '{nome_antigo}' foi renomeada para '{nome_novo}'."
                    log_stmt = text(
                        "INSERT INTO LOG_ALTERACOES (TIMESTAMP, LOGIN_USUARIO, ACAO) VALUES (:ts, :login, :acao)")
                    connection.execute(log_stmt, {'ts': datetime.now(), 'login': usuario, 'acao': acao_log})

                    transaction.commit()
                    logging.info(f"Transação de renomeação da espécie '{nome_antigo}' concluída com sucesso.")
                    return True, "Espécie renomeada e ação registrada no log com sucesso."

                except exc.SQLAlchemyError as e:
                    transaction.rollback()
                    logging.error(f"Falha na transação de renomeação: {e}")
                    return False, f"Ocorreu um erro no banco de dados: {e}"