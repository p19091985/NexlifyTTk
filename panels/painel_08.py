# panels/painel_08.py
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from .base_panel import BasePanel
from persistencia.repository import GenericRepository
from persistencia.data_service import DataService

class PainelCrudCompleto(BasePanel):
    PANEL_NAME = "Demonstração CRUD & Transações"
    PANEL_ICON = "📦"
    ALLOWED_ACCESS = []

    def __init__(self, parent, app_controller, **kwargs):
        self.selected_item_id = None
        self.nome_var = tk.StringVar()
        self.pais_var = tk.StringVar()
        self.temperamento_var = tk.StringVar()
        self.novo_nome_var = tk.StringVar()
        super().__init__(parent, app_controller, **kwargs)

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # --- Frames Principais ---
        form_frame = ttk.LabelFrame(main_frame, text=" Formulário de Dados ", padding=15)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0,10))
        crud_buttons_frame = ttk.LabelFrame(main_frame, text=" Operações CRUD (GenericRepository) ", padding=15)
        crud_buttons_frame.grid(row=0, column=1, sticky="nsew", pady=(0,10))
        table_frame = ttk.LabelFrame(main_frame, text=" Tabela 'especie_gatos' ", padding=15)
        table_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        trans_frame = ttk.LabelFrame(main_frame, text=" Operação Atómica (DataService) ", padding=15)
        trans_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(10,0))

        # --- Widgets ---
        self._create_form(form_frame)
        self._create_crud_buttons(crud_buttons_frame)
        self._create_table(table_frame)
        self._create_transaction_widgets(trans_frame)

        self._carregar_dados()

    def _create_form(self, parent):
        parent.columnconfigure(1, weight=1)
        ttk.Label(parent, text="Nome da Espécie:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(parent, textvariable=self.nome_var).grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Label(parent, text="País de Origem:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(parent, textvariable=self.pais_var).grid(row=1, column=1, sticky="ew", pady=2)
        ttk.Label(parent, text="Temperamento:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(parent, textvariable=self.temperamento_var).grid(row=2, column=1, sticky="ew", pady=2)

    def _create_crud_buttons(self, parent):
        parent.rowconfigure(0, weight=1); parent.rowconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1); parent.columnconfigure(1, weight=1)
        ttk.Button(parent, text="CREATE (Inserir)", command=self._inserir_item, style="success.TButton").grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        ttk.Button(parent, text="READ (Atualizar Lista)", command=self._carregar_dados, style="info.TButton").grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        ttk.Button(parent, text="UPDATE (Salvar Edição)", command=self._atualizar_item, style="warning.TButton").grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        ttk.Button(parent, text="DELETE (Excluir)", command=self._excluir_item, style="danger.TButton").grid(row=1, column=1, sticky="nsew", padx=2, pady=2)
        ttk.Button(parent, text="Limpar Formulário", command=self._limpar_form, style="secondary.Outline.TButton").grid(row=2, column=0, columnspan=2, sticky="ew", padx=2, pady=5)

    def _create_table(self, parent):
        columns = ('id', 'nome_especie', 'pais_origem', 'temperamento')
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', selectmode='browse')
        for col in columns: self.tree.heading(col, text=col.replace('_', ' ').title())
        self.tree.column('id', width=40, anchor='center'); self.tree.column('nome_especie', width=150)
        self.tree.column('pais_origem', width=150); self.tree.column('temperamento', width=200)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_item_select)

    def _create_transaction_widgets(self, parent):
        parent.columnconfigure(1, weight=1)
        ttk.Label(parent, text="Renomear espécie selecionada para:").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Entry(parent, textvariable=self.novo_nome_var).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(parent, text="Executar Transação (Renomear e Logar)", command=self._executar_transacao).grid(row=0, column=2, sticky="e", padx=5)

    def _carregar_dados(self):
        try:
            for item in self.tree.get_children(): self.tree.delete(item)
            df = GenericRepository.read_table_to_dataframe("especie_gatos")
            for _, row in df.iterrows(): self.tree.insert("", "end", values=list(row))
            self._limpar_form()
        except Exception as e: messagebox.showerror("Erro de Leitura", f"Não foi possível ler os dados: {e}", parent=self)

    def _on_item_select(self, event=None):
        selected_items = self.tree.selection()
        if not selected_items: return
        item = self.tree.item(selected_items[0], "values")
        self.selected_item_id = item[0]
        self.nome_var.set(item[1]); self.pais_var.set(item[2]); self.temperamento_var.set(item[3])

    def _limpar_form(self):
        self.selected_item_id = None
        self.nome_var.set(""); self.pais_var.set(""); self.temperamento_var.set(""); self.novo_nome_var.set("")
        if self.tree.selection(): self.tree.selection_remove(self.tree.selection()[0])

    def _inserir_item(self):
        nome = self.nome_var.get().strip()
        if not nome: messagebox.showwarning("Validação", "O campo 'Nome da Espécie' é obrigatório.", parent=self); return
        data = {'nome_especie': nome, 'pais_origem': self.pais_var.get().strip(), 'temperamento': self.temperamento_var.get().strip()}
        try:
            GenericRepository.write_dataframe_to_table(pd.DataFrame([data]), "especie_gatos")
            messagebox.showinfo("Sucesso", "Nova espécie inserida com sucesso!", parent=self)
            self._carregar_dados()
        except Exception as e: messagebox.showerror("Erro de Inserção", f"Não foi possível inserir o registo: {e}", parent=self)

    def _atualizar_item(self):
        if self.selected_item_id is None: messagebox.showwarning("Atenção", "Selecione um item da tabela para atualizar.", parent=self); return
        nome = self.nome_var.get().strip()
        if not nome: messagebox.showwarning("Validação", "O campo 'Nome da Espécie' é obrigatório.", parent=self); return
        update_values = {'nome_especie': nome, 'pais_origem': self.pais_var.get().strip(), 'temperamento': self.temperamento_var.get().strip()}
        try:
            GenericRepository.update_table("especie_gatos", update_values=update_values, where_conditions={'id': self.selected_item_id})
            messagebox.showinfo("Sucesso", "Espécie atualizada com sucesso!", parent=self)
            self._carregar_dados()
        except Exception as e: messagebox.showerror("Erro de Atualização", f"Não foi possível atualizar o registo: {e}", parent=self)

    def _excluir_item(self):
        if self.selected_item_id is None: messagebox.showwarning("Atenção", "Selecione um item da tabela para excluir.", parent=self); return
        if not messagebox.askyesno("Confirmar Exclusão", "Tem a certeza que deseja excluir a espécie selecionada?", icon='warning', parent=self): return
        try:
            GenericRepository.delete_from_table("especie_gatos", where_conditions={'id': self.selected_item_id})
            messagebox.showinfo("Sucesso", "Espécie excluída com sucesso!", parent=self)
            self._carregar_dados()
        except Exception as e: messagebox.showerror("Erro de Exclusão", f"Não foi possível excluir o registo: {e}", parent=self)

    def _executar_transacao(self):
        if self.selected_item_id is None: messagebox.showwarning("Atenção", "Selecione um item da tabela para renomear.", parent=self); return
        nome_antigo = self.nome_var.get()
        nome_novo = self.novo_nome_var.get().strip()
        if not nome_novo: messagebox.showwarning("Validação", "Informe o novo nome para a espécie.", parent=self); return
        usuario = self.app.get_current_user()['username']
        sucesso, mensagem = DataService.rename_especie_gato_e_logar(nome_antigo, nome_novo, usuario)
        if sucesso:
            messagebox.showinfo("Transação Concluída", mensagem, parent=self)
            self._carregar_dados()
            # Também seria ideal recarregar o painel de auditoria, se estivesse visível
        else:
            messagebox.showerror("Falha na Transação", mensagem, parent=self)