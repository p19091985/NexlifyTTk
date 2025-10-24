import pandas as pd
from sqlalchemy import exc
from persistencia.repository import GenericRepository

class TiposVegetaisModel:
    def get_all_tipos(self):
        try:
                                              
            return GenericRepository.read_table_to_dataframe("tipos_vegetais")
        except exc.SQLAlchemyError as e:   
                                                                             
            raise ConnectionError(f"Não foi possível carregar a lista de tipos de vegetais.\nDetalhe: {e}")   

    def add_tipo(self, nome: str):
        if not nome:
            raise ValueError("O campo 'Nome' é obrigatório.")   
        try:
                                                 
            df = pd.DataFrame([{'nome': nome}])   
            GenericRepository.write_dataframe_to_table(df, "tipos_vegetais")   
        except exc.IntegrityError:   
                                                                       
            raise ValueError(f"O nome '{nome}' já existe.")   
        except exc.SQLAlchemyError as e:   
                                                                
            raise ConnectionError(f"Ocorreu uma falha ao salvar os dados.\nDetalhe: {e}")   

    def update_tipo(self, item_id: int, nome: str):
        if not nome:   
            raise ValueError("O campo 'Nome' é obrigatório.")   
        try:
                                                         
            GenericRepository.update_table("tipos_vegetais", {'nome': nome}, {'id': item_id})   
        except exc.IntegrityError:   
                                                                       
            raise ValueError(f"O nome '{nome}' já existe.")   
        except exc.SQLAlchemyError as e:   
                                                                
            raise ConnectionError(f"Ocorreu uma falha ao atualizar os dados.\nDetalhe: {e}")   

    def delete_tipo(self, item_id: int):
        try:
                                               
            GenericRepository.delete_from_table("tipos_vegetais", {'id': item_id})   
        except exc.IntegrityError:

            raise ValueError("Não foi possível excluir. Este tipo está em uso por um ou mais vegetais.")   
        except exc.SQLAlchemyError as e:   
                                                                
            raise ConnectionError(f"Ocorreu uma falha ao excluir os dados.\nDetalhe: {e}")   