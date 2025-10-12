# panels/painel_vegetais_auditoria_controller.py
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import logging
from .base_panel import BasePanel
from persistencia.repository import GenericRepository
from persistencia.data_service import DataService
from modals.tipos_vegetais_controller import TiposVegetaisController
from .painel_vegetais_auditoria_view import VegetaisAuditoriaView


class PainelVegetaisAuditoria(BasePanel):
    """Controller consolidado para a gestão de Vegetais e visualização de Auditoria."""
    PANEL_NAME = "Vegetais e Auditoria"
    PANEL_ICON = "🌿"
    ALLOWED_ACCESS = ['Administrador Global', 'Diretor de Operações', 'Gerente de TI', 'Analista de Dados']

    def __init__(self, parent, app_controller, **kwargs):
        self.selected_item_id = None
        self.nome_var = tk.StringVar()
        self.tipo_var = tk.StringVar()
        self.novo_tipo_trans_var = tk.StringVar()
        super().__init__(parent, app_controller, **kwargs)

    def create_widgets(self):
        self.view = VegetaisAuditoriaView(self, controller=self)
        self.view.pack(fill="both", expand=True)
        self.carregar_dados()

    def carregar_dados(self):
        """(READ) Carrega/recarrega todos os dados necessários para a tela."""
        self._carregar_vegetais()
        self._carregar_tipos_vegetais()
        self._carregar_log()
        self.clear_form()

    def _carregar_vegetais(self):
        try:
            for item in self.view.tree_vegetais.get_children():
                self.view.tree_vegetais.delete(item)
            df_vegetais = GenericRepository.read_vegetais_com_tipo()
            if not df_vegetais.empty:
                for _, row in df_vegetais.iterrows():
                    self.view.tree_vegetais.insert("", "end", values=list(row))
        except Exception as e:
            messagebox.showerror("Erro de Carga", f"Não foi possível carregar a lista de vegetais.\n{e}", parent=self)

    def _carregar_tipos_vegetais(self):
        try:
            df_tipos = GenericRepository.read_table_to_dataframe("tipos_vegetais")
            # CORRIGIDO: Acessa a coluna 'nome' em minúsculas, conforme padronizado pelo repositório.
            tipos_lista = sorted(df_tipos['nome'].tolist()) if not df_tipos.empty else []
            self.view.tipo_combobox['values'] = tipos_lista
            self.view.trans_tipo_combo['values'] = tipos_lista
        except Exception as e:
            messagebox.showerror("Erro de Carga", f"Não foi possível recarregar os tipos de vegetais.\n{e}",
                                 parent=self)

    def _carregar_log(self):
        try:
            for item in self.view.tree_log.get_children(): self.view.tree_log.delete(item)
            df = GenericRepository.read_table_to_dataframe("log_alteracoes")
            if not df.empty:
                # CORRIGIDO: Acessa a coluna 'timestamp' em minúsculas.
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df_sorted = df.sort_values(by='timestamp', ascending=False)
                for _, row in df_sorted.iterrows():
                    row['timestamp'] = row['timestamp'].strftime('%d/%m/%Y %H:%M:%S')
                    self.view.tree_log.insert("", "end", values=list(row))
        except Exception as e:
            logging.getLogger("main_app").error(f"Falha ao carregar log de auditoria: {e}", exc_info=True)
            messagebox.showerror("Erro de Carga", f"Não foi possível carregar o log de auditoria.\nDetalhe: {e}",
                                 parent=self)

    def open_tipos_modal(self):
        """Abre a janela de gestão de tipos e define o recarregamento como callback."""
        modal = TiposVegetaisController(self, on_close_callback=self._carregar_tipos_vegetais)
        modal.show()

    def save_item(self):
        """(CREATE/UPDATE) Salva um registro novo ou existente."""
        nome = self.nome_var.get().strip()
        tipo_nome = self.tipo_var.get()
        if not nome or not tipo_nome:
            messagebox.showerror("Erro de Validação", "Os campos 'Nome' e 'Tipo' são obrigatórios.", parent=self)
            return
        try:
            # Para a condição WHERE, usamos a chave MAIÚSCULA que corresponde ao schema do banco.
            df_tipo = GenericRepository.read_table_to_dataframe("tipos_vegetais", where_conditions={'NOME': tipo_nome})
            if df_tipo.empty:
                messagebox.showerror("Erro de Dados", f"O tipo '{tipo_nome}' não foi encontrado.", parent=self)
                return

            # CORRIGIDO: Ao ler o resultado (df_tipo), acessamos a coluna 'id' em minúsculas.
            id_tipo = int(df_tipo.iloc[0]['id'])

            # Para a escrita, usamos chaves MAIÚSCULAS para corresponder ao schema do banco.
            data = {'NOME': nome, 'ID_TIPO': id_tipo}

            if self.selected_item_id is None:
                GenericRepository.write_dataframe_to_table(pd.DataFrame([data]), "vegetais")
                messagebox.showinfo("Sucesso", "Vegetal cadastrado!", parent=self)
            else:
                GenericRepository.update_table("vegetais", data, {'ID': self.selected_item_id})
                messagebox.showinfo("Sucesso", "Vegetal atualizado!", parent=self)
            self.carregar_dados()
        except Exception as e:
            messagebox.showerror("Erro de Banco de Dados", f"Não foi possível salvar o registro.\n{e}", parent=self)

    def delete_item(self):
        """(DELETE) Exclui o registro selecionado."""
        if self.selected_item_id is None:
            messagebox.showwarning("Atenção", "Selecione um vegetal na tabela para excluir.", parent=self)
            return
        if messagebox.askyesno("Confirmar Exclusão", "Deseja realmente excluir este vegetal?", icon='warning',
                               parent=self):
            try:
                # Para a condição WHERE, usamos a chave MAIÚSCULA que corresponde ao schema.
                GenericRepository.delete_from_table("vegetais", {'ID': self.selected_item_id})
                messagebox.showinfo("Sucesso", "Vegetal excluído!", parent=self)
                self.carregar_dados()
            except Exception as e:
                messagebox.showerror("Erro de Banco de Dados", f"Não foi possível excluir o registro.\n{e}",
                                     parent=self)

    def clear_form(self):
        """Limpa as variáveis de estado e a seleção na Treeview."""
        self.selected_item_id = None
        self.nome_var.set("")
        self.tipo_var.set("")
        self.novo_tipo_trans_var.set("")
        if self.view.tree_vegetais.selection():
            self.view.tree_vegetais.selection_remove(self.view.tree_vegetais.selection()[0])
        self.view.nome_entry.focus()

    def on_vegetal_select(self, event=None):
        """Preenche o formulário quando um vegetal é selecionado na tabela."""
        selected_items = self.view.tree_vegetais.selection()
        if not selected_items: return
        item = self.view.tree_vegetais.item(selected_items[0])
        values = item['values']
        self.selected_item_id = values[0]
        self.nome_var.set(values[1])
        self.tipo_var.set(values[2])

    def executar_transacao_reclassify(self):
        """Chama o DataService para reclassificar um vegetal de forma atômica e auditada."""
        if self.selected_item_id is None:
            messagebox.showwarning("Atenção", "Selecione um vegetal na tabela para reclassificar.", parent=self)
            return

        vegetal_nome = self.nome_var.get()
        novo_tipo = self.novo_tipo_trans_var.get()

        if not novo_tipo:
            messagebox.showwarning("Validação", "Selecione o novo tipo para a transação.", parent=self)
            return

        usuario_logado = self.app.get_current_user()['username']
        msg = f"Deseja reclassificar '{vegetal_nome}' para o tipo '{novo_tipo}'?\n\nEsta ação será registrada na trilha de auditoria."
        if not messagebox.askyesno("Confirmar Transação", msg, icon='warning', parent=self):
            return

        sucesso, mensagem = DataService.reclassificar_vegetal_e_logar(vegetal_nome, novo_tipo, usuario_logado)

        if sucesso:
            messagebox.showinfo("Sucesso", mensagem, parent=self)
            self.carregar_dados()
        else:
            messagebox.showerror("Falha na Transação", mensagem, parent=self)