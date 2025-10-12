                                     
from .tipos_vegetais_model import TiposVegetaisModel
from .tipos_vegetais_view import TiposVegetaisView

class TiposVegetaisController:
    def __init__(self, parent, on_close_callback=None):
        self.model = TiposVegetaisModel()
        self.view = TiposVegetaisView(parent)
        self.view.set_controller(self)
        self.on_close_callback = on_close_callback
        self.selected_item_id = None
        self.load_data()

    def show(self):
        self.view.wait_window()

    def load_data(self):
        try:
            data = self.model.get_all_tipos()
            self.view.populate_treeview(data)
        except ConnectionError as e:
            self.view.show_error("Erro de Carga", str(e))

    def save_item(self):
        form_data = self.view.get_form_data()
        nome = form_data['nome']
        try:
            if self.selected_item_id is None:
                self.model.add_tipo(nome)
                self.view.show_info("Sucesso", "Tipo cadastrado!")
            else:
                self.model.update_tipo(self.selected_item_id, nome)
                self.view.show_info("Sucesso", "Tipo atualizado!")
            self.clear_form()
            self.load_data()
            if self.on_close_callback:
                self.on_close_callback()
        except (ValueError, ConnectionError) as e:
            self.view.show_error("Erro de Validação", str(e))

    def delete_item(self):
        if self.selected_item_id is None:
            self.view.show_warning("Atenção", "Selecione um item para excluir.")
            return
        confirm_msg = f"Deseja excluir o tipo ID {self.selected_item_id}?\nEsta ação não pode ser desfeita."
        if self.view.ask_yes_no("Confirmar Exclusão", confirm_msg):
            try:
                self.model.delete_tipo(self.selected_item_id)
                self.clear_form()
                self.load_data()
                if self.on_close_callback:
                    self.on_close_callback()
            except ConnectionError as e:
                self.view.show_error("Erro de Banco de Dados", str(e))

    def clear_form(self):
        self.selected_item_id = None
        self.view.clear_form_fields()

    def on_item_select(self, event=None):
        item_data = self.view.get_selected_item_data()
        if item_data:
            self.selected_item_id = item_data['id']
            self.view.set_form_data(item_data)
        else:
            self.selected_item_id = None