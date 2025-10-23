import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from sqlalchemy import exc

from persistencia.repository import GenericRepository


class TiposVegetaisManagerDialog(tk.Toplevel):
    """
    Um diálogo modal unificado para gerenciar 'Tipos de Vegetais'.

    Esta classe combina a View (tk.Toplevel), o Controller (lógica de eventos)
    e o Model (acesso a dados) em um único arquivo para simplicidade.
    """

    def __init__(self, parent, on_close_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.on_close_callback = on_close_callback
        self.selected_item_id = None

        self.title("Gerenciar Tipos de Vegetais")
        self.geometry("600x450")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        self.nome_var = tk.StringVar()

        self._create_widgets()
        self._center_window()
        self._load_data()
        self.nome_entry.focus_set()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_widgets(self):
        """Cria a estrutura principal da UI."""
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)

        form_frame = ttk.LabelFrame(main_frame, text=" Cadastro de Tipo de Vegetal ", padding=15)
        form_frame.pack(side="left", fill="y", padx=(0, 10))
        self._create_form_widgets(form_frame)

        table_frame = ttk.LabelFrame(main_frame, text=" Tipos Cadastrados ", padding=15)
        table_frame.pack(side="right", fill="both", expand=True)
        self._create_table_widgets(table_frame)

    def _create_form_widgets(self, parent):
        """Cria o formulário de entrada e os botões de ação."""
        ttk.Label(parent, text="Nome do Tipo:").pack(anchor="w")
        self.nome_entry = ttk.Entry(parent, textvariable=self.nome_var, width=30)
        self.nome_entry.pack(anchor="w", pady=(5, 15))

        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill="x")

        self.save_button = ttk.Button(btn_frame, text="Salvar", style="Success.TButton",
                                      command=self._save_item)
        self.save_button.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.delete_button = ttk.Button(btn_frame, text="Excluir", style="Danger.TButton",
                                        command=self._delete_item)
        self.delete_button.pack(side="left", expand=True, fill="x")

        self.clear_button = ttk.Button(parent, text="Limpar Formulário", style="Secondary.TButton",
                                       command=self._clear_form)
        self.clear_button.pack(fill="x", pady=(10, 0))

    def _create_table_widgets(self, parent):
        """Cria a Treeview (tabela) para exibir os dados."""
        inner_frame = ttk.Frame(parent)
        inner_frame.pack(fill="both", expand=True)

        columns = ('id', 'nome')
        self.tree = ttk.Treeview(inner_frame, columns=columns, show='headings', selectmode='browse')
        self.tree.heading('id', text='ID')
        self.tree.heading('nome', text='Nome')
        self.tree.column('id', width=50, anchor='center')
        self.tree.column('nome', width=200)

        scrollbar = ttk.Scrollbar(inner_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.tree.bind('<<TreeviewSelect>>', self._on_item_select)

    def _load_data(self):
        """Busca os dados do modelo e atualiza a Treeview."""
        try:
            data = self._model_get_all_tipos()
            self.populate_treeview(data)
        except ConnectionError as e:
            self.show_error("Erro de Carga", str(e))

    def _save_item(self):
        """Salva um item (novo ou existente)."""
        nome = self.get_form_data()['nome']
        try:
            if self.selected_item_id is None:

                self._model_add_tipo(nome)
                self.show_info("Sucesso", "Tipo cadastrado!")
            else:

                self._model_update_tipo(self.selected_item_id, nome)
                self.show_info("Sucesso", "Tipo atualizado!")

            self._clear_form()
            self._load_data()
            if self.on_close_callback:
                self.on_close_callback()
        except (ValueError, ConnectionError) as e:
            self.show_error("Erro de Validação", str(e))

    def _delete_item(self):
        """Exclui o item selecionado."""
        if self.selected_item_id is None:
            self.show_warning("Atenção", "Selecione um item para excluir.")
            return

        confirm_msg = f"Deseja excluir o tipo ID {self.selected_item_id}?\nEsta ação não pode ser desfeita."
        if self.ask_yes_no("Confirmar Exclusão", confirm_msg):
            try:
                self._model_delete_tipo(self.selected_item_id)
                self._clear_form()
                self._load_data()
                if self.on_close_callback:
                    self.on_close_callback()
            except (ValueError, ConnectionError) as e:
                self.show_error("Erro de Banco de Dados", str(e))

    def _clear_form(self):
        """Limpa o formulário e a seleção."""
        self.selected_item_id = None
        self.clear_form_fields()

    def _on_item_select(self, event=None):
        """Chamado quando um item na Treeview é selecionado."""
        item_data = self.get_selected_item_data()
        if item_data:
            self.selected_item_id = item_data['id']
            self.set_form_data(item_data)
        else:
            self.selected_item_id = None

    def _on_close(self):
        """Chamado quando a janela é fechada pelo "X"."""
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()

    def _model_get_all_tipos(self):
        try:
            return GenericRepository.read_table_to_dataframe("tipos_vegetais")
        except exc.SQLAlchemyError as e:
            raise ConnectionError(f"Não foi possível carregar a lista de tipos de vegetais.\nDetalhe: {e}")

    def _model_add_tipo(self, nome: str):
        if not nome:
            raise ValueError("O campo 'Nome' é obrigatório.")
        try:
            df = pd.DataFrame([{'nome': nome}])
            GenericRepository.write_dataframe_to_table(df, "tipos_vegetais")
        except exc.IntegrityError:
            raise ValueError(f"O nome '{nome}' já existe.")
        except exc.SQLAlchemyError as e:
            raise ConnectionError(f"Ocorreu uma falha ao salvar os dados.\nDetalhe: {e}")

    def _model_update_tipo(self, item_id: int, nome: str):
        if not nome:
            raise ValueError("O campo 'Nome' é obrigatório.")
        try:
            GenericRepository.update_table("tipos_vegetais", {'nome': nome}, {'id': item_id})
        except exc.IntegrityError:
            raise ValueError(f"O nome '{nome}' já existe.")
        except exc.SQLAlchemyError as e:
            raise ConnectionError(f"Ocorreu uma falha ao atualizar os dados.\nDetalhe: {e}")

    def _model_delete_tipo(self, item_id: int):
        try:
            GenericRepository.delete_from_table("tipos_vegetais", {'id': item_id})
        except exc.IntegrityError:

            raise ValueError("Não foi possível excluir. Este tipo está em uso por um ou mais vegetais.")
        except exc.SQLAlchemyError as e:
            raise ConnectionError(f"Ocorreu uma falha ao excluir os dados.\nDetalhe: {e}")

    def populate_treeview(self, data):
        """Limpa e preenche a Treeview com dados de um DataFrame."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        if not data.empty:
            for _, row in data.iterrows():
                self.tree.insert("", "end", values=list(row))

    def get_form_data(self):
        """Retorna os dados do formulário."""
        return {'nome': self.nome_var.get().strip()}

    def set_form_data(self, data):
        """Preenche o formulário com dados."""
        self.nome_var.set(data.get('nome', ''))

    def clear_form_fields(self):
        """Limpa os campos de entrada e a seleção da tabela."""
        self.nome_var.set("")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])
        self.nome_entry.focus()

    def get_selected_item_data(self):
        """Retorna os dados do item selecionado na tabela."""
        selected_items = self.tree.selection()
        if not selected_items:
            return None
        item = self.tree.item(selected_items[0])
        return {'id': item['values'][0], 'nome': item['values'][1]}

    def show_error(self, title, message):
        messagebox.showerror(title, message, parent=self)

    def show_info(self, title, message):
        messagebox.showinfo(title, message, parent=self)

    def show_warning(self, title, message):
        messagebox.showwarning(title, message, parent=self)

    def ask_yes_no(self, title, message):
        """Mostra uma caixa de diálogo de confirmação."""
        return messagebox.askyesno(title, message, icon='warning', parent=self)

    def _center_window(self):
        """Centraliza esta janela modal sobre a janela pai."""
        self.update_idletasks()
        p_w, p_h = self.parent.winfo_width(), self.parent.winfo_height()
        p_x, p_y = self.parent.winfo_x(), self.parent.winfo_y()
        w, h = self.winfo_width(), self.winfo_height()
        x = p_x + (p_w // 2) - (w // 2)
        y = p_y + (p_h // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")