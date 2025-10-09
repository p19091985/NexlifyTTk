# panels/painel_catalogo_mvc_view.py
import tkinter as tk
from tkinter import ttk

class CatalogoEspeciesView(ttk.Frame):
    """
    A View para o painel de catálogo de espécies.
    Contém toda a criação e layout dos widgets.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        form_frame = ttk.LabelFrame(main_frame, text=" Formulário de Dados ", padding=15)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))

        crud_buttons_frame = ttk.LabelFrame(main_frame, text=" Operações CRUD ", padding=15)
        crud_buttons_frame.grid(row=0, column=1, sticky="nsew", pady=(0, 10))

        table_frame = ttk.LabelFrame(main_frame, text=" Tabela 'especie_gatos' ", padding=15)
        table_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

        trans_frame = ttk.LabelFrame(main_frame, text=" Operação Atômica ", padding=15)
        trans_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(10, 0))

        self._create_form(form_frame)
        self._create_crud_buttons(crud_buttons_frame)
        self._create_table(table_frame)
        self._create_transaction_widgets(trans_frame)

    def _create_form(self, parent):
        parent.columnconfigure(1, weight=1)
        ttk.Label(parent, text="Nome da Espécie:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(parent, textvariable=self.controller.nome_var).grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(parent, text="País de Origem:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(parent, textvariable=self.controller.pais_var).grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(parent, text="Temperamento:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(parent, textvariable=self.controller.temperamento_var).grid(row=2, column=1, sticky="ew", pady=2)

    def _create_crud_buttons(self, parent):
        parent.rowconfigure([0, 1], weight=1)
        parent.columnconfigure([0, 1], weight=1)

        ttk.Button(parent, text="CREATE (Inserir)", command=self.controller.inserir_item, style="success.TButton").grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        ttk.Button(parent, text="READ (Atualizar Lista)", command=self.controller.carregar_dados, style="info.TButton").grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        ttk.Button(parent, text="UPDATE (Salvar Edição)", command=self.controller.atualizar_item, style="warning.TButton").grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        ttk.Button(parent, text="DELETE (Excluir)", command=self.controller.excluir_item, style="danger.TButton").grid(row=1, column=1, sticky="nsew", padx=2, pady=2)
        ttk.Button(parent, text="Limpar Formulário", command=self.controller.limpar_form, style="secondary.Outline.TButton").grid(row=2, column=0, columnspan=2, sticky="ew", padx=2, pady=5)

    def _create_table(self, parent):
        # --- MODIFICAÇÃO: Colunas da view definidas em minúsculas ---
        columns = ('id', 'nome_especie', 'pais_origem', 'temperamento')
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', selectmode='browse')
        for col in columns: self.tree.heading(col, text=col.replace('_', ' ').title())
        self.tree.column('id', width=40, anchor='center')
        self.tree.column('nome_especie', width=150)
        self.tree.column('pais_origem', width=150)
        self.tree.column('temperamento', width=200)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.controller.on_item_select)

    def _create_transaction_widgets(self, parent):
        parent.columnconfigure(1, weight=1)
        ttk.Label(parent, text="Renomear espécie selecionada para:").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Entry(parent, textvariable=self.controller.novo_nome_var).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(parent, text="Executar Transação (Renomear e Logar)", command=self.controller.executar_transacao).grid(row=0, column=2, sticky="e", padx=5)