# modals/tipos_linguagem_model.py
import pandas as pd
from sqlalchemy import exc
# --- PONTO CHAVE: O Model importa a camada de persistência ---
from persistencia.repository import GenericRepository

class TiposLinguagemModel:
    """
    Modelo para gerenciar os dados de Tipos de Linguagem.
    Encapsula TODA a lógica de acesso ao banco de dados para esta funcionalidade.
    """

    def get_all_tipos(self):
        """
        Busca todos os tipos de linguagem usando o repositório.
        A View e o Controller não sabem como essa busca é feita, apenas pedem os dados.
        """
        try:
            # --- USO DA PERSISTÊNCIA ---
            return GenericRepository.read_table_to_dataframe("tipos_linguagem")
        except exc.SQLAlchemyError as e:
            # Propaga a exceção para ser tratada pelo controller
            raise ConnectionError(f"Não foi possível carregar a lista de tipos.\nDetalhe: {e}")

    def add_tipo(self, nome: str):
        """ Adiciona um novo tipo usando o repositório. """
        if not nome:
            raise ValueError("O campo 'Nome' é obrigatório.")
        try:
            df = pd.DataFrame([{'nome': nome}])
            # --- USO DA PERSISTÊNCIA ---
            GenericRepository.write_dataframe_to_table(df, "tipos_linguagem")
        except exc.IntegrityError:
            raise ValueError(f"O nome '{nome}' já existe.")
        except exc.SQLAlchemyError as e:
            raise ConnectionError(f"Ocorreu uma falha ao salvar os dados.\nDetalhe: {e}")

    def update_tipo(self, item_id: int, nome: str):
        """ Atualiza um tipo existente usando o repositório. """
        if not nome:
            raise ValueError("O campo 'Nome' é obrigatório.")
        try:
            # --- USO DA PERSISTÊNCIA ---
            GenericRepository.update_table("tipos_linguagem", {'nome': nome}, {'id': item_id})
        except exc.IntegrityError:
            raise ValueError(f"O nome '{nome}' já existe.")
        except exc.SQLAlchemyError as e:
            raise ConnectionError(f"Ocorreu uma falha ao atualizar os dados.\nDetalhe: {e}")

    def delete_tipo(self, item_id: int):
        """ Exclui um tipo de linguagem usando o repositório. """
        try:
            # --- USO DA PERSISTÊNCIA ---
            GenericRepository.delete_from_table("tipos_linguagem", {'id': item_id})
        except exc.IntegrityError:
            raise ConnectionError("Não foi possível excluir. Este tipo está em uso por uma ou mais linguagens.")
        except exc.SQLAlchemyError as e:
            raise ConnectionError(f"Ocorreu uma falha ao excluir os dados.\nDetalhe: {e}")