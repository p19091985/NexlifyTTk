                                          
import tkinter as tk
from tkinter import ttk

class VegetaisAuditoriaView(ttk.Frame):
    """
    A View consolidada para a gestão de Vegetais e visualização da Auditoria.
    """

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

        form_frame = ttk.LabelFrame(top_container, text=" 🥕 Formulário de Vegetal ", padding=15)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._create_form_widgets(form_frame)

        crud_buttons_frame = ttk.LabelFrame(top_container, text=" ⚙️ Operações CRUD ", padding=15)
        crud_buttons_frame.grid(row=0, column=1, sticky="nsew")
        self._create_crud_buttons(crud_buttons_frame)

        bottom_pane = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        bottom_pane.grid(row=1, column=0, sticky="nsew")

        table_frame = ttk.LabelFrame(bottom_pane, text=" 🍽️ Tabela 'VEGETAIS' ", padding=15)
        bottom_pane.add(table_frame, weight=3)
        self._create_table_vegetais(table_frame)

        log_frame = ttk.LabelFrame(bottom_pane, text=" 🛡️ Tabela 'LOG_ALTERACOES' ", padding=15)
        bottom_pane.add(log_frame, weight=2)
        self._create_table_log(log_frame)

        trans_frame = ttk.LabelFrame(main_frame, text=" 🔄 Operação Atômica (Transação) ", padding=15)
        trans_frame.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        self._create_transaction_widgets(trans_frame)

    def _create_form_widgets(self, parent):
        parent.columnconfigure(1, weight=1)

        ttk.Label(parent, text="Nome do Vegetal:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.nome_entry = ttk.Entry(parent, textvariable=self.controller.nome_var)
        self.nome_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(parent, text="Tipo:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        tipo_frame = ttk.Frame(parent)
        tipo_frame.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.tipo_combobox = ttk.Combobox(tipo_frame, textvariable=self.controller.tipo_var, state="readonly")
        self.tipo_combobox.pack(side="left", fill="x", expand=True)
                                                 
        ttk.Button(tipo_frame, text="Gerenciar Tipos...", command=self.controller.open_tipos_modal, width=15).pack(
            side="left", padx=(5, 0))

    def _create_crud_buttons(self, parent):
        parent.columnconfigure((0, 1), weight=1)
        parent.rowconfigure((0, 1), weight=1)

        ttk.Button(parent, text="Salvar (Create/Update)", command=self.controller.save_item,
                   style="Success.TButton").grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        ttk.Button(parent, text="Excluir (Delete)", command=self.controller.delete_item, style="Danger.TButton").grid(
            row=0, column=1, sticky="nsew", padx=2, pady=2)
        ttk.Button(parent, text="Limpar Formulário", command=self.controller.clear_form,
                   style="Secondary.TButton").grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        ttk.Button(parent, text="Atualizar Tabelas", command=self.controller.carregar_dados, style="Info.TButton").grid(
            row=1, column=1, sticky="nsew", padx=2, pady=2)

    def _create_table_vegetais(self, parent):
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        columns = ('id', 'nome', 'tipo')
        self.tree_vegetais = ttk.Treeview(parent, columns=columns, show='headings', selectmode='browse')

        self.tree_vegetais.heading('id', text='ID')
        self.tree_vegetais.heading('nome', text='Nome do Vegetal')
        self.tree_vegetais.heading('tipo', text='Tipo')

        self.tree_vegetais.column('id', width=50, anchor='center')
        self.tree_vegetais.column('nome', width=150)
        self.tree_vegetais.column('tipo', width=150)

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree_vegetais.yview)
        self.tree_vegetais.configure(yscrollcommand=scrollbar.set)

        self.tree_vegetais.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree_vegetais.bind("<<TreeviewSelect>>", self.controller.on_vegetal_select)

    def _create_table_log(self, parent):
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        columns = ('id', 'timestamp', 'login_usuario', 'acao')
        self.tree_log = ttk.Treeview(parent, columns=columns, show='headings', selectmode='browse')
        self.tree_log.heading('id', text='ID')
        self.tree_log.heading('timestamp', text='Data/Hora')
        self.tree_log.heading('login_usuario', text='Usuário')
        self.tree_log.heading('acao', text='Ação Realizada')

        self.tree_log.column('id', width=40, anchor='center')
        self.tree_log.column('timestamp', width=140)
        self.tree_log.column('login_usuario', width=100)
        self.tree_log.column('acao', width=300)

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree_log.yview)
        self.tree_log.configure(yscrollcommand=scrollbar.set)

        self.tree_log.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _create_transaction_widgets(self, parent):
        parent.columnconfigure(1, weight=1)
        ttk.Label(parent, text="Reclassificar vegetal selecionado para o tipo:").grid(row=0, column=0, sticky="w",
                                                                                      padx=5)

        self.trans_tipo_combo = ttk.Combobox(parent, textvariable=self.controller.novo_tipo_trans_var, state="readonly")
        self.trans_tipo_combo.grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Button(parent, text="Executar Transação e Auditar",
                   command=self.controller.executar_transacao_reclassify).grid(row=0, column=2, sticky="e", padx=5)