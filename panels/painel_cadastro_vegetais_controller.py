import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import config

from panels.base_panel import BasePanel   
from persistencia.repository import GenericRepository   
from modals.tipos_vegetais_controller import TiposVegetaisController   
from .painel_cadastro_vegetais_view import CadastroVegetaisView   


class PainelCadastroVegetais(BasePanel):   
    """Controller para a tela de cadastro de vegetais."""
    PANEL_NAME = "Cadastro de Vegetais"   
    PANEL_ICON = "🥕"   
    ALLOWED_ACCESS = ['Administrador Global', 'Diretor de Operações', 'Gerente de TI', 'Analista de Dados']   

    def __init__(self, parent, app_controller, **kwargs):
        self.selected_item_id = None
        self.nome_var = tk.StringVar()
        self.tipo_var = tk.StringVar()
        super().__init__(parent, app_controller, **kwargs)

    def create_widgets(self):
        if not config.DATABASE_ENABLED:   
            ttk.Label(self, text="Funcionalidade indisponível: o banco de dados está desabilitado.",
                      font=("-size", 12, "-weight", "bold")).pack(pady=50)   
            return

        self.view = CadastroVegetaisView(self, controller=self)   
        self.view.pack(fill="both", expand=True)   
        self._carregar_dados()   
        self._carregar_tipos_vegetais()   

    def _carregar_dados(self):
        """Carrega a lista de vegetais já cadastrados na Treeview."""
        try:
            for item in self.view.tree.get_children():
                self.view.tree.delete(item)   

                                                                             
            df_vegetais = GenericRepository.read_vegetais_com_tipo()   
            if not df_vegetais.empty:   
                for _, row in df_vegetais.iterrows():   
                    self.view.tree.insert("", "end", values=list(row))   
        except Exception as e:
            messagebox.showerror("Erro de Carga", f"Não foi possível carregar a lista de vegetais.\n{e}", parent=self)   

    def _carregar_tipos_vegetais(self):
        """Carrega ou recarrega os tipos de vegetais no Combobox."""
        try:
                                                                     
            df_tipos = GenericRepository.read_table_to_dataframe("tipos_vegetais")   

            tipos_lista = sorted(df_tipos['nome'].tolist()) if not df_tipos.empty else []   
            self.view.tipo_combobox['values'] = tipos_lista   
        except Exception as e:
            messagebox.showerror("Erro de Carga", f"Não foi possível recarregar os tipos de vegetais.\n{e}",
                                 parent=self)   

    def open_tipos_modal(self):
        """
        Abre a janela modal para gerenciar os tipos.
        A função _carregar_tipos_vegetais é passada como callback para ser executada
        quando o modal for fechado, garantindo que o combobox seja atualizado.
        """
        modal = TiposVegetaisController(self, on_close_callback=self._carregar_tipos_vegetais)   
        modal.show()   

    def save_item(self):
        """Salva um registro novo (CREATE) ou existente (UPDATE)."""
        nome = self.nome_var.get().strip()
        tipo_nome = self.tipo_var.get()
        if not nome or not tipo_nome:   
            messagebox.showerror("Erro de Validação", "Os campos 'Nome' e 'Tipo' são obrigatórios.", parent=self)
            return   

        try:
                                                                    
            df_tipo = GenericRepository.read_table_to_dataframe("tipos_vegetais", where_conditions={'nome': tipo_nome})   
            if df_tipo.empty:   
                messagebox.showerror("Erro de Dados", f"O tipo '{tipo_nome}' não foi encontrado.", parent=self)   
                return

                                                  
            id_tipo = int(df_tipo.iloc[0]['id'])   

                                                           
            data = {'nome': nome, 'id_tipo': id_tipo}   

            if self.selected_item_id is None:   
                GenericRepository.write_dataframe_to_table(pd.DataFrame([data]), "vegetais")   
                messagebox.showinfo("Sucesso", "Vegetal cadastrado!", parent=self)   
            else:   
                                                                      
                GenericRepository.update_table("vegetais", data, {'id': self.selected_item_id})   
                messagebox.showinfo("Sucesso", "Vegetal atualizado!", parent=self)   

            self.clear_form()   
            self._carregar_dados()   
        except Exception as e:
            messagebox.showerror("Erro de Banco de Dados", f"Não foi possível salvar o registro.\n{e}", parent=self)   

    def delete_item(self):
        """Exclui o registro selecionado."""
        if self.selected_item_id is None:   
            messagebox.showwarning("Atenção", "Selecione um vegetal na tabela para excluir.", parent=self)   
            return

        if messagebox.askyesno("Confirmar Exclusão", "Deseja realmente excluir este vegetal?", icon='warning',
                               parent=self):   
            try:
                                                                      
                GenericRepository.delete_from_table("vegetais", {'id': self.selected_item_id})   
                messagebox.showinfo("Sucesso", "Vegetal excluído!", parent=self)   
                self.clear_form()   
                self._carregar_dados()   
            except Exception as e:
                messagebox.showerror("Erro de Banco de Dados", f"Não foi possível excluir o registro.\n{e}",
                                     parent=self)   

    def clear_form(self):
        """Limpa o formulário e a seleção."""
        self.selected_item_id = None   
        self.nome_var.set("")   
        self.tipo_var.set("")   
        if self.view.tree.selection():
            self.view.tree.selection_remove(self.view.tree.selection()[0])   
        self.view.nome_entry.focus()   

    def on_item_select(self, event=None):
        """Preenche o formulário quando um item é selecionado na tabela."""
        selected_items = self.view.tree.selection()   
        if not selected_items: return   

        item = self.view.tree.item(selected_items[0])   
        values = item['values']   
                                                              
        self.selected_item_id = values[0]        
        self.nome_var.set(values[1])          
        self.tipo_var.set(values[2])          