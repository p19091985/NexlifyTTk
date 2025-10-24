import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import config
from panels.base_panel import BasePanel   
from persistencia.repository import GenericRepository   
from persistencia.data_service import DataService   
from .painel_gestao_gatos_view import GestaoGatosView

class PainelGestaoGatos(BasePanel):   
    """Controller consolidado para todas as operações da tabela especie_gatos."""
    PANEL_NAME = "Gestão de Espécies (Gatos)"   
    PANEL_ICON = "🐈"   
    ALLOWED_ACCESS = []   

    def __init__(self, parent, app_controller, **kwargs):
        self.selected_item_id = None
        self.nome_var = tk.StringVar()
        self.pais_var = tk.StringVar()
        self.temperamento_var = tk.StringVar()
        self.novo_nome_var = tk.StringVar()   
        super().__init__(parent, app_controller, **kwargs)

    def create_widgets(self):
        if not config.DATABASE_ENABLED:   
            ttk.Label(self, text="Funcionalidade indisponível: o banco de dados está desabilitado.",
                       font=("-size", 12, "-weight", "bold")).pack(pady=50)   
            return

        self.view = GestaoGatosView(self, controller=self)   
        self.view.pack(fill="both", expand=True)   
        self.carregar_dados()   

    def carregar_dados(self):
        """(READ) Busca os dados e instrui a View a exibi-los."""
        try:
            for item in self.view.tree.get_children():   
                self.view.tree.delete(item)   
                                             
            df = GenericRepository.read_table_to_dataframe("especie_gatos")   
            if not df.empty:   
                                                                                        
                for _, row in df.iterrows():   
                    self.view.tree.insert("", "end", values=list(row))   
            self.limpar_form()   
        except Exception as e:
            messagebox.showerror("Erro de Leitura", f"Não foi possível ler os dados: {e}", parent=self)   

    def on_item_select(self, event=None):
        """Atualiza o estado do Controller quando um item é selecionado na View."""
        selected_items = self.view.tree.selection()   
        if not selected_items: return   
        item = self.view.tree.item(selected_items[0], "values")

        self.selected_item_id = item[0]        
        self.nome_var.set(item[1])                  
        self.pais_var.set(item[2])                 
        self.temperamento_var.set(item[3])                  

    def limpar_form(self):
        """Limpa as variáveis de estado e a seleção na Treeview."""
        self.selected_item_id = None
        self.nome_var.set("")   
        self.pais_var.set("")   
        self.temperamento_var.set("")   
        self.novo_nome_var.set("")   
        if self.view.tree.selection():   
            self.view.tree.selection_remove(self.view.tree.selection()[0])   
        self.view.nome_entry.focus()   

    def inserir_item(self):
        """(CREATE) Valida os dados e insere um novo registro."""
        nome = self.nome_var.get().strip()
        if not nome:
            messagebox.showwarning("Validação", "O campo 'Nome da Espécie' é obrigatório.", parent=self)   
            return

        data = {'nome_especie': nome, 'pais_origem': self.pais_var.get().strip(),
                'temperamento': self.temperamento_var.get().strip()}
        try:
                                             
            GenericRepository.write_dataframe_to_table(pd.DataFrame([data]), "especie_gatos")
            messagebox.showinfo("Sucesso", "Nova espécie inserida com sucesso!", parent=self)
            self.carregar_dados()   
        except Exception as e:
            messagebox.showerror("Erro de Inserção", f"Não foi possível inserir o registro: {e}", parent=self)   

    def atualizar_item(self):
        """(UPDATE) Valida os dados e atualiza um registro existente."""
        if self.selected_item_id is None:
            messagebox.showwarning("Atenção", "Selecione um item da tabela para atualizar.", parent=self)   
            return

        update_values = {'nome_especie': self.nome_var.get().strip(), 'pais_origem': self.pais_var.get().strip(),
                         'temperamento': self.temperamento_var.get().strip()}   
        try:
                                                          
            GenericRepository.update_table("especie_gatos", update_values=update_values,
                                           where_conditions={'id': self.selected_item_id})   
            messagebox.showinfo("Sucesso", "Espécie atualizada com sucesso!", parent=self)   
            self.carregar_dados()   
        except Exception as e:
            messagebox.showerror("Erro de Atualização", f"Não foi possível atualizar o registro: {e}", parent=self)   

    def excluir_item(self):
        """(DELETE) Exclui o registro selecionado."""
        if self.selected_item_id is None:   
            messagebox.showwarning("Atenção", "Selecione um item da tabela para excluir.", parent=self)   
            return
        if not messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir a espécie selecionada?",
                                   icon='warning', parent=self):   
            return   
        try:
                                                          
            GenericRepository.delete_from_table("especie_gatos", where_conditions={'id': self.selected_item_id})   
            messagebox.showinfo("Sucesso", "Espécie excluída com sucesso!", parent=self)   
            self.carregar_dados()   
        except Exception as e:
            messagebox.showerror("Erro de Exclusão", f"Não foi possível excluir o registro: {e}", parent=self)   

    def executar_transacao_rename(self):
        """Chama a camada de serviço para a operação atômica de renomear e auditar."""
        if self.selected_item_id is None:   
            messagebox.showwarning("Atenção", "Selecione um item da tabela para renomear.", parent=self)   
            return
        nome_antigo = self.nome_var.get()
        nome_novo = self.novo_nome_var.get().strip()
        if not nome_novo:
            messagebox.showwarning("Validação", "Informe o novo nome para a espécie.", parent=self)   
            return
        usuario = self.app.get_current_user()['username']   
                                                                        
        sucesso, mensagem = DataService.rename_especie_gato_e_logar(nome_antigo, nome_novo, usuario)   
        if sucesso:   
            messagebox.showinfo("Transação Concluída", mensagem, parent=self)   
            self.carregar_dados()   
        else:   
            messagebox.showerror("Falha na Transação", mensagem, parent=self)   