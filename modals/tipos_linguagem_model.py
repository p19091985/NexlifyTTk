# modals/tipos_linguagem_model.py
import pandas as pd
from sqlalchemy import exc
from persistencia.repository import GenericRepository

class TiposLinguagemModel:
    def get_all_tipos(self):
        try:
            return GenericRepository.read_table_to_dataframe("tipos_linguagem")
        except exc.SQLAlchemyError as e:
            raise ConnectionError(f"Não foi possível carregar a lista de tipos.\nDetalhe: {e}")

    def add_tipo(self, nome: str):
        if not nome:
            raise ValueError("O campo 'Nome' é obrigatório.")
        try:
            df = pd.DataFrame([{'NOME': nome}])
            GenericRepository.write_dataframe_to_table(df, "tipos_linguagem")
        except exc.IntegrityError:
            raise ValueError(f"O nome '{nome}' já existe.")
        except exc.SQLAlchemyError as e:
            raise ConnectionError(f"Ocorreu uma falha ao salvar os dados.\nDetalhe: {e}")

    def update_tipo(self, item_id: int, nome: str):
        if not nome:
            raise ValueError("O campo 'Nome' é obrigatório.")
        try:
            GenericRepository.update_table("tipos_linguagem", {'NOME': nome}, {'ID': item_id})
        except exc.IntegrityError:
            raise ValueError(f"O nome '{nome}' já existe.")
        except exc.SQLAlchemyError as e:
            raise ConnectionError(f"Ocorreu uma falha ao atualizar os dados.\nDetalhe: {e}")

    def delete_tipo(self, item_id: int):
        try:
            GenericRepository.delete_from_table("tipos_linguagem", {'ID': item_id})
        except exc.IntegrityError:
            raise ConnectionError("Não foi possível excluir. Este tipo está em uso por uma ou mais linguagens.")
        except exc.SQLAlchemyError as e:
            raise ConnectionError(f"Ocorreu uma falha ao excluir os dados.\nDetalhe: {e}")