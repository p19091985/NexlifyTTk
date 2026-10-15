import config
from .audit import record
from sqlalchemy import text, exc
from .repository import GenericRepository
import logging
from .auth import authorize

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
        if config.API_MODE == 'client':
            from services.client import request
            return request('POST', '/reclassificar', {'nome': nome_vegetal, 'tipo': novo_tipo_nome})
        session = authorize('vegetais', write=True)
        usuario = session['username']
        engine = GenericRepository.get_engine()
        with engine.connect() as connection:
            with connection.begin() as transaction:
                session = authorize('vegetais', write=True, connection=connection)
                usuario = session['username']
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

                    record(connection, usuario, acao_log)

                    transaction.commit()
                    logging.info('Transação de reclassificação concluída: %r.', nome_vegetal)
                    return True, "Vegetal reclassificado e ação auditada com sucesso!"

                except exc.SQLAlchemyError as e:
                    transaction.rollback()
                    logging.error("Falha na transação de reclassificação.")
                    return False, "Ocorreu um erro no banco de dados; nenhuma alteração foi aplicada."

    @staticmethod
    def rename_especie_gato_e_logar(nome_antigo: str, nome_novo: str, usuario: str):
        """
        Renomeia uma espécie de gato e registra a ação na trilha de auditoria.
        Operação atômica.
        """
        if config.API_MODE == 'client':
            from services.client import request
            return request('POST', '/renomear', {'antigo': nome_antigo, 'novo': nome_novo})
        session = authorize('especie_gatos', write=True)
        usuario = session['username']
        engine = GenericRepository.get_engine()
        with engine.connect() as connection:
            with connection.begin() as transaction:
                session = authorize('especie_gatos', write=True, connection=connection)
                usuario = session['username']
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

                    record(connection, usuario, acao_log)

                    transaction.commit()
                    logging.info('Transação de renomeação concluída: %r.', nome_antigo)
                    return True, "Espécie renomeada e ação registrada no log com sucesso."

                except exc.SQLAlchemyError as e:
                    transaction.rollback()
                    logging.error("Falha na transação de renomeação.")
                    return False, "Ocorreu um erro no banco de dados; nenhuma alteração foi aplicada."
