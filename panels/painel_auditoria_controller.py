# panels/painel_auditoria_controller.py
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from .base_panel import BasePanel
from persistencia.repository import GenericRepository
from persistencia.data_service import DataService
from .painel_auditoria_view import AuditoriaView  # Importa a nova View

class PainelAuditoria(BasePanel):
    PANEL_NAME = "Auditoria de Alterações"
    PANEL_ICON = "🛡️"
    ALLOWED_ACCESS = ['Administrador Global', 'Gerente de TI']

    def __init__(self, parent, app_controller, **kwargs):
        self.linguagem_selecionada_var = tk.StringVar()
        self.nova_categoria_var = tk.StringVar()
        super().__init__(parent, app_controller, **kwargs)

    def create_widgets(self):
        # O Controller cria a View
        self.view = AuditoriaView(self, controller=self)
        self.view.pack(fill="both", expand=True)
        self._carregar_dados_iniciais()

    def _carregar_dados_iniciais(self):
        self._carregar_linguagens()
        self._carregar_log()

    def _carregar_linguagens(self):
        try:
            for item in self.view.linguagens_tree.get_children(): self.view.linguagens_tree.delete(item)
            df = GenericRepository.read_table_to_dataframe("linguagens_programacao", columns=['id', 'nome', 'categoria'])
            if not df.empty:
                for _, row in df.iterrows(): self.view.linguagens_tree.insert("", "end", values=list(row))
                self.view.linguagem_combo['values'] = sorted(df['nome'].tolist())
        except Exception as e:
            messagebox.showerror("Erro de Carga", f"Não foi possível carregar as linguagens.\n{e}", parent=self)

    def _carregar_log(self):
        try:
            for item in self.view.log_tree.get_children(): self.view.log_tree.delete(item)
            df = GenericRepository.read_table_to_dataframe("log_alteracoes")
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df_sorted = df.sort_values(by='timestamp', ascending=False)
                for _, row in df_sorted.iterrows():
                    row['timestamp'] = row['timestamp'].strftime('%d/%m/%Y %H:%M:%S')
                    self.view.log_tree.insert("", "end", values=list(row))
        except Exception as e:
            messagebox.showerror("Erro de Carga", f"Não foi possível carregar o log.\n{e}", parent=self)

    def _executar_transacao(self):
        linguagem = self.linguagem_selecionada_var.get()
        categoria = self.nova_categoria_var.get().strip()
        if not linguagem or not categoria:
            messagebox.showwarning("Dados Incompletos", "Selecione uma linguagem e informe a nova categoria.", parent=self)
            return

        usuario_logado = self.app.get_current_user()['username']

        if not messagebox.askyesno("Confirmar Transação", f"Deseja reclassificar '{linguagem}' para '{categoria}'?\n\nEsta ação será auditada.", icon='warning', parent=self):
            return

        sucesso, mensagem = DataService.reclassificar_e_logar(linguagem, categoria, usuario_logado)

        if sucesso:
            messagebox.showinfo("Sucesso", mensagem, parent=self)
            self._limpar_campos_acao()
            self._carregar_dados_iniciais()
        else:
            messagebox.showerror("Falha na Transação", mensagem, parent=self)

    def _limpar_campos_acao(self):
        self.nova_categoria_var.set("")
        self.linguagem_selecionada_var.set("")
        self.view.exec_button.config(state="disabled")