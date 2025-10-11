# panels/painel_especies_controller.py
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from panels.base_panel import BasePanel
from persistencia.repository import GenericRepository
from persistencia.data_service import DataService
from .painel_especies_view import GatosView

class PainelGestaoEspecies(BasePanel):
    PANEL_NAME = "Gestão de Espécies"
    PANEL_ICON = "🐾"
    ALLOWED_ACCESS = []

    def __init__(self, parent, app_controller, **kwargs):
        self.selected_item_id = None
        self.nome_var = tk.StringVar()
        self.pais_var = tk.StringVar()
        self.temperamento_var = tk.StringVar()
        super().__init__(parent, app_controller, **kwargs)

    def create_widgets(self):
        self.view = GatosView(self, controller=self)
        self.view.pack(fill="both", expand=True)
        self.carregar_dados_iniciais()

    def carregar_dados_iniciais(self):
        try:
            for item in self.view.tree.get_children():
                self.view.tree.delete(item)
            df_gatos = GenericRepository.read_table_to_dataframe("especie_gatos")
            if not df_gatos.empty:
                for _, row in df_gatos.iterrows():
                    self.view.tree.insert("", "end", values=list(row))
        except Exception as e:
            messagebox.showerror("Erro de Carga", f"Não foi possível carregar os dados: {e}", parent=self)

    def salvar_item(self):
        nome = self.nome_var.get().strip()
        if not nome:
            messagebox.showwarning("Validação", "O nome da espécie é obrigatório.", parent=self)
            return
        data = {'nome_especie': nome, 'pais_origem': self.pais_var.get().strip(), 'temperamento': self.temperamento_var.get().strip()}
        try:
            if self.selected_item_id is None:
                df = pd.DataFrame([data])
                GenericRepository.write_dataframe_to_table(df, "especie_gatos")
                messagebox.showinfo("Sucesso", "Nova espécie cadastrada!", parent=self)
            else:
                GenericRepository.update_table("especie_gatos", data, {'id': self.selected_item_id})
                messagebox.showinfo("Sucesso", "Espécie atualizada!", parent=self)
            self.limpar_formulario()
            self.carregar_dados_iniciais()
        except Exception as e:
            messagebox.showerror("Erro no Banco", f"Ocorreu um erro ao salvar: {e}", parent=self)

    def excluir_item(self):
        if self.selected_item_id is None:
            messagebox.showwarning("Atenção", "Selecione um item para excluir.", parent=self)
            return
        if messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir esta espécie?", icon='warning', parent=self):
            try:
                GenericRepository.delete_from_table("especie_gatos", {'id': self.selected_item_id})
                messagebox.showinfo("Sucesso", "Espécie excluída!", parent=self)
                self.limpar_formulario()
                self.carregar_dados_iniciais()
            except Exception as e:
                messagebox.showerror("Erro no Banco", f"Ocorreu um erro ao excluir: {e}", parent=self)

    def limpar_formulario(self):
        self.selected_item_id = None
        self.nome_var.set("")
        self.pais_var.set("")
        self.temperamento_var.set("")
        if self.view.tree.selection():
            self.view.tree.selection_remove(self.view.tree.selection()[0])
        self.view.nome_entry.focus()

    def on_item_select(self, event=None):
        selected_items = self.view.tree.selection()
        if not selected_items: return
        item = self.view.tree.item(selected_items[0])
        values = item['values']
        self.selected_item_id = values[0]
        self.nome_var.set(values[1])
        self.pais_var.set(values[2])
        self.temperamento_var.set(values[3])

    def executar_acao_atomica(self):
        usuario_logado = self.app.get_current_user()['username']
        sucesso, mensagem = DataService.rename_especie_gato_e_logar(nome_antigo="Siamês", nome_novo="Siamês Gato Tailandês", usuario=usuario_logado)
        if sucesso:
            messagebox.showinfo("Transação Concluída", mensagem, parent=self)
            self.carregar_dados_iniciais()
        else:
            messagebox.showerror("Falha na Transação", mensagem, parent=self)