# modals/tipos_linguagem_controller.py
from .tipos_linguagem_model import TiposLinguagemModel
from .tipos_linguagem_view import TiposLinguagemView

class TiposLinguagemController:
    """
    Controller para a janela de gerenciamento de Tipos de Linguagem.
    Conecta a View (GUI) com o Model (lógica de dados).
    """

    def __init__(self, parent, on_close_callback=None):
        # 1. Instancia o Model e a View
        self.model = TiposLinguagemModel()
        self.view = TiposLinguagemView(parent)
        # 2. Conecta a View a este Controller
        self.view.set_controller(self)
        self.on_close_callback = on_close_callback
        self.selected_item_id = None
        # 3. Pede ao Model para carregar os dados iniciais e os envia para a View
        self.load_data()

    def show(self):
        """ Exibe a janela e aguarda seu fechamento. """
        self.view.wait_window()

    def load_data(self):
        """ Pede os dados ao Model e manda a View exibi-los. """
        try:
            # --- Comunicação Controller -> Model ---
            data = self.model.get_all_tipos()
            # --- Comunicação Controller -> View ---
            self.view.populate_treeview(data)
        except ConnectionError as e:
            self.view.show_error("Erro de Carga", str(e))

    def save_item(self):
        """
        Chamado quando o botão 'Salvar' (na View) é clicado.
        """
        # 1. Pega os dados do formulário da View
        form_data = self.view.get_form_data()
        nome = form_data['nome']

        try:
            # 2. Pede ao Model para salvar ou atualizar os dados
            if self.selected_item_id is None:
                self.model.add_tipo(nome)
                self.view.show_info("Sucesso", "Tipo cadastrado!")
            else:
                self.model.update_tipo(self.selected_item_id, nome)
                self.view.show_info("Sucesso", "Tipo atualizado!")

            # 3. Atualiza a tela após a operação
            self.clear_form()
            self.load_data()
            if self.on_close_callback:
                self.on_close_callback()

        except (ValueError, ConnectionError) as e:
            # 4. Se o Model retornar um erro, exibe-o na View
            self.view.show_error("Erro de Validação", str(e))

    def delete_item(self):
        """ Chamado quando o botão 'Excluir' (na View) é clicado. """
        if self.selected_item_id is None:
            self.view.show_warning("Atenção", "Selecione um item para excluir.")
            return

        confirm_msg = f"Deseja excluir o tipo ID {self.selected_item_id}?\nEsta ação não pode ser desfeita."
        if self.view.ask_yes_no("Confirmar Exclusão", confirm_msg):
            try:
                # --- Comunicação Controller -> Model ---
                self.model.delete_tipo(self.selected_item_id)
                self.clear_form()
                self.load_data()
                if self.on_close_callback:
                    self.on_close_callback()
            except ConnectionError as e:
                # --- Comunicação Controller -> View ---
                self.view.show_error("Erro de Banco de Dados", str(e))

    def clear_form(self):
        """ Chamado pelo botão 'Limpar', limpa os dados na View. """
        self.selected_item_id = None
        self.view.clear_form_fields()

    def on_item_select(self, event=None):
        """ Chamado quando um item na tabela (na View) é selecionado. """
        item_data = self.view.get_selected_item_data()
        if item_data:
            self.selected_item_id = item_data['id']
            self.view.set_form_data(item_data)
        else:
            self.selected_item_id = None