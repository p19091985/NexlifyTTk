                                    
import tkinter as tk
from tkinter import ttk

class GestaoGatosView(ttk.Frame):
    """A View consolidada para a gestão de espécies de gatos."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)

        top_container = ttk.Frame(main_frame)
        top_container.grid(row=0, column=0, sticky="nsew", pady=(0, 15))
        top_container.columnconfigure(0, weight=1)
        top_container.columnconfigure(1, weight=1)

        form_frame = ttk.LabelFrame(top_container, text=" 📝 Formulário de Dados ", padding=15)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._create_form_widgets(form_frame)

        crud_buttons_frame = ttk.LabelFrame(top_container, text=" ⚙️ Operações CRUD ", padding=15)
        crud_buttons_frame.grid(row=0, column=1, sticky="nsew")
        self._create_crud_buttons(crud_buttons_frame)

        table_frame = ttk.LabelFrame(main_frame, text=" 🐱 Tabela 'especie_gatos' ", padding=15)
        table_frame.grid(row=1, column=0, sticky="nsew")
        self._create_table(table_frame)

        trans_frame = ttk.LabelFrame(main_frame, text=" 🛡️ Operação Atômica (Transação) ", padding=15)
        trans_frame.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        self._create_transaction_widgets(trans_frame)

    def _create_form_widgets(self, parent):
        parent.columnconfigure(1, weight=1)
        ttk.Label(parent, text="Nome da Espécie:").grid(row=0, column=0, sticky="w", pady=2)
        self.nome_entry = ttk.Entry(parent, textvariable=self.controller.nome_var)
        self.nome_entry.grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(parent, text="País de Origem:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(parent, textvariable=self.controller.pais_var).grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(parent, text="Temperamento:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(parent, textvariable=self.controller.temperamento_var).grid(row=2, column=1, sticky="ew", pady=2)

    def _create_crud_buttons(self, parent):
        parent.rowconfigure([0, 1], weight=1)
        parent.columnconfigure([0, 1], weight=1)

        ttk.Button(parent, text="Inserir (CREATE)", command=self.controller.inserir_item, style="Success.TButton").grid(
            row=0, column=0, sticky="nsew", padx=2, pady=2)
        ttk.Button(parent, text="Atualizar Lista (READ)", command=self.controller.carregar_dados,
                   style="Info.TButton").grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        ttk.Button(parent, text="Salvar Edição (UPDATE)", command=self.controller.atualizar_item,
                   style="Warning.TButton").grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        ttk.Button(parent, text="Excluir (DELETE)", command=self.controller.excluir_item, style="Danger.TButton").grid(
            row=1, column=1, sticky="nsew", padx=2, pady=2)
        ttk.Button(parent, text="Limpar Formulário", command=self.controller.limpar_form,
                   style="Secondary.TButton").grid(row=2, column=0, columnspan=2, sticky="ew", padx=2, pady=5)

    def _create_table(self, parent):
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)

        columns = ('id', 'nome_especie', 'pais_origem', 'temperamento')
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', selectmode='browse')
        for col in columns: self.tree.heading(col, text=col.replace('_', ' ').title())
        self.tree.column('id', width=40, anchor='center')
        self.tree.column('nome_especie', width=150)
        self.tree.column('pais_origem', width=150)
        self.tree.column('temperamento', width=200)

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self.controller.on_item_select)

    def _create_transaction_widgets(self, parent):
        parent.columnconfigure(1, weight=1)
        ttk.Label(parent, text="Renomear espécie selecionada para:").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Entry(parent, textvariable=self.controller.novo_nome_var).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(parent, text="Executar Transação (Renomear e Auditar)",
                   command=self.controller.executar_transacao_rename).grid(row=0, column=2, sticky="e", padx=5)