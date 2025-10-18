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
        Esta operação é atômica.
        """
        engine = GenericRepository.get_engine()
        with engine.connect() as connection:
            with connection.begin() as transaction:
                try:
                                                              
                    res_vegetal = connection.execute(
                        text("SELECT id, id_tipo FROM vegetais WHERE nome = :nome"),
                        {'nome': nome_vegetal}
                    ).first()   
                    if not res_vegetal:
                        return False, f"Vegetal '{nome_vegetal}' não encontrado."   
                    id_vegetal, id_tipo_antigo = res_vegetal

                                                              
                    res_novo_tipo = connection.execute(
                        text("SELECT id FROM tipos_vegetais WHERE nome = :nome"),
                        {'nome': novo_tipo_nome}
                    ).first()   
                    if not res_novo_tipo:
                        return False, f"Tipo '{novo_tipo_nome}' não encontrado."   
                    id_novo_tipo = res_novo_tipo[0]

                    if id_tipo_antigo == id_novo_tipo:
                        return False, "O vegetal já pertence a este tipo."   

                                                              
                    connection.execute(
                        text("UPDATE vegetais SET id_tipo = :id_tipo WHERE id = :id_vegetal"),
                        {'id_tipo': id_novo_tipo, 'id_vegetal': id_vegetal}
                    )   

                    acao_log = (f"O vegetal '{nome_vegetal}' (ID: {id_vegetal}) foi reclassificado "
                                f"para o tipo '{novo_tipo_nome}' (ID: {id_novo_tipo}).")

                                                                                    
                    connection.execute(
                        text("""
                             INSERT INTO log_alteracoes (timestamp, login_usuario, acao)
                             VALUES (:ts, :login, :acao)
                             """),
                        {'ts': datetime.now(), 'login': usuario, 'acao': acao_log}
                    )   

                    transaction.commit()
                    logging.info(f"Transação de reclassificação do vegetal '{nome_vegetal}' concluída com sucesso.")
                    return True, "Vegetal reclassificado e ação auditada com sucesso!"

                except exc.SQLAlchemyError as e:   
                    transaction.rollback()
                    logging.error(f"Falha na transação de reclassificação: {e}")
                    return False, f"Ocorreu um erro no banco de dados: {e}"

    @staticmethod
    def rename_especie_gato_e_logar(nome_antigo: str, nome_novo: str, usuario: str):
        """
        Renomeia uma espécie de gato e registra a ação na trilha de auditoria.
        Operação atômica.
        """
        engine = GenericRepository.get_engine()
        with engine.connect() as connection:
            with connection.begin() as transaction:
                try:
                                                              
                    res_check = connection.execute(
                        text("SELECT id FROM especie_gatos WHERE nome_especie = :nome"),
                        {'nome': nome_novo}
                    ).first()   
                    if res_check:   
                        return False, f"O nome '{nome_novo}' já está em uso."

                                                              
                    update_stmt = text("UPDATE especie_gatos SET nome_especie = :novo WHERE nome_especie = :antigo")
                    result = connection.execute(update_stmt, {'novo': nome_novo, 'antigo': nome_antigo})   

                    if result.rowcount == 0:
                        transaction.rollback()
                        return False, f"A espécie '{nome_antigo}' não foi encontrada para renomear."

                    acao_log = f"Espécie '{nome_antigo}' foi renomeada para '{nome_novo}'."   
                                                                                    
                    log_stmt = text(
                        "INSERT INTO log_alteracoes (timestamp, login_usuario, acao) VALUES (:ts, :login, :acao)")   
                    connection.execute(log_stmt, {'ts': datetime.now(), 'login': usuario, 'acao': acao_log})

                    transaction.commit()
                    logging.info(f"Transação de renomeação da espécie '{nome_antigo}' concluída com sucesso.")
                    return True, "Espécie renomeada e ação registrada no log com sucesso."   

                except exc.SQLAlchemyError as e:   
                    transaction.rollback()
                    logging.error(f"Falha na transação de renomeação: {e}")
                    return False, f"Ocorreu um erro no banco de dados: {e}"   