# panels/painel_01_controller.py
import tkinter as tk
from tkinter import messagebox
import pandas as pd
from .base_panel import BasePanel
from persistencia.repository import GenericRepository
from persistencia.data_service import DataService
from .painel_01_view import PainelLinguagensView


class PainelVisualizacaoDados(BasePanel):
    PANEL_NAME = "Gestão - Arquivos Separados"
    PANEL_ICON = "📑"
    ALLOWED_ACCESS = ['Administrador Global', 'Diretor de Operações', 'Gerente de TI', 'Analista de Dados']

    def __init__(self, parent, app_controller, **kwargs):
        self.selected_item_id = None
        self.nome_var = tk.StringVar()
        self.ano_var = tk.IntVar(value=2000)
        self.tipo_var = tk.StringVar()
        self.categoria_var = tk.StringVar()
        super().__init__(parent, app_controller, **kwargs)

    def create_widgets(self):
        self.view = PainelLinguagensView(self, controller=self)
        self.view.pack(fill="both", expand=True)
        self._carregar_e_inserir_dados()
        self._carregar_tipos_linguagem()

    def _open_tipos_modal(self):
        self.app._open_tipos_linguagem_modal()

    def _carregar_tipos_linguagem(self):
        try:
            valor_selecionado = self.tipo_var.get()
            df_tipos = GenericRepository.read_table_to_dataframe("tipos_linguagem")
            novos_valores = sorted(df_tipos['nome'].tolist()) if not df_tipos.empty else []
            self.view.tipo_combobox['values'] = novos_valores
            if valor_selecionado in novos_valores:
                self.tipo_var.set(valor_selecionado)
            elif self.tipo_var.get() not in novos_valores:
                self.tipo_var.set('')
        except Exception as e:
            messagebox.showerror("Erro de Carga", f"Não foi possível recarregar os tipos de linguagem.\nDetalhe: {e}",
                                 parent=self)
            self.view.tipo_combobox['values'] = []

    # --- MÉTODO MODIFICADO ---
    def _save_item(self):
        """Lógica para salvar um item, agora com busca do ID do tipo."""
        nome = self.nome_var.get().strip()
        tipo_nome = self.tipo_var.get()
        if not nome or not tipo_nome:
            messagebox.showerror("Erro de Validação", "Os campos 'Nome' e 'Tipagem' são obrigatórios.", parent=self)
            return

        try:
            # Busca o ID correspondente ao nome do tipo
            df_tipo = GenericRepository.read_table_to_dataframe("tipos_linguagem", where_conditions={'nome': tipo_nome})
            if df_tipo.empty:
                messagebox.showerror("Erro de Dados", f"O tipo '{tipo_nome}' não foi encontrado.", parent=self)
                return
            id_tipo = int(df_tipo.iloc[0]['id'])

            # Usa o id_tipo para salvar
            data = {'nome': nome, 'id_tipo': id_tipo, 'ano_criacao': self.ano_var.get(),
                    'categoria': self.categoria_var.get().strip()}

            if self.selected_item_id is None:
                df_to_write = pd.DataFrame([data])
                GenericRepository.write_dataframe_to_table(df_to_write, "linguagens_programacao")
                messagebox.showinfo("Sucesso", "Linguagem cadastrada!", parent=self)
            else:
                GenericRepository.update_table("linguagens_programacao", data, {'id': self.selected_item_id})
                messagebox.showinfo("Sucesso", "Linguagem atualizada!", parent=self)

            self._clear_form()
            self._carregar_e_inserir_dados()
        except Exception as e:
            messagebox.showerror("Erro de Banco de Dados", f"Não foi possível salvar o registro.\nDetalhe: {e}",
                                 parent=self)

    def _delete_item(self):
        if self.selected_item_id is None:
            messagebox.showwarning("Atenção", "Selecione um item para excluir.", parent=self)
            return
        if messagebox.askyesno("Confirmar", "Deseja excluir esta linguagem?", icon='warning', parent=self):
            try:
                GenericRepository.delete_from_table("linguagens_programacao", {'id': self.selected_item_id})
                messagebox.showinfo("Sucesso", "Linguagem excluída!", parent=self)
                self._clear_form()
                self._carregar_e_inserir_dados()
            except Exception as e:
                messagebox.showerror("Erro de Banco de Dados", f"Não foi possível excluir o registro.\nDetalhe: {e}",
                                     parent=self)

    def _clear_form(self):
        self.selected_item_id = None
        self.nome_var.set("");
        self.tipo_var.set("");
        self.ano_var.set(2000);
        self.categoria_var.set("")
        if self.view.tree.selection():
            self.view.tree.selection_remove(self.view.tree.selection()[0])
        self.view.nome_entry.focus()

    def _on_item_select(self, event=None):
        selected_items = self.view.tree.selection()
        if not selected_items: return
        item = self.view.tree.item(selected_items[0])
        values = item['values']
        self.selected_item_id = values[0];
        self.nome_var.set(values[1]);
        self.tipo_var.set(values[2])
        self.ano_var.set(int(values[3]));
        self.categoria_var.set(values[4])

    # --- MÉTODO MODIFICADO ---
    def _carregar_e_inserir_dados(self):
        """Busca os dados usando o novo método com JOIN."""
        try:
            for item in self.view.tree.get_children():
                self.view.tree.delete(item)

            # Usa o novo método que já traz o nome do tipo
            df_linguagens = GenericRepository.read_linguagens_com_tipo()
            if not df_linguagens.empty:
                for _, row in df_linguagens.iterrows():
                    self.view.tree.insert("", "end", values=list(row))
        except Exception as e:
            messagebox.showerror("Erro de Carga", f"Não foi possível carregar a lista de linguagens.\nDetalhe: {e}",
                                 parent=self)

    def _executar_reclassificacao(self):
        usuario_logado = self.app.get_current_user()['username']
        sucesso, mensagem = DataService.reclassificar_e_logar("C++", "Linguagens Legado", usuario_logado)
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem, parent=self)
            self._carregar_e_inserir_dados()
        else:
            messagebox.showerror("Falha na Transação", mensagem, parent=self)