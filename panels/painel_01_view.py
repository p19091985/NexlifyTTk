# panels/painel_01_view.py
import tkinter as tk
from tkinter import ttk

class PainelLinguagensView(ttk.Frame):
    """
    A View (Interface Gráfica) para o painel de Gestão de Linguagens.
    Contém apenas a criação e layout dos widgets, sem lógica de negócio.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # --- Estrutura Principal ---
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)

        form_frame = ttk.LabelFrame(main_frame, text=" Cadastro de Linguagem ", padding=15)
        form_frame.pack(fill="x", pady=(0, 10))

        table_frame = ttk.LabelFrame(main_frame, text=" Linguagens Cadastradas ", padding=15)
        table_frame.pack(fill="both", expand=True)

        legacy_actions_frame = ttk.LabelFrame(main_frame, text=" Ações Atômicas ", padding=10)
        legacy_actions_frame.pack(fill="x", pady=(15, 0))

        # --- Criação dos Widgets ---
        self._create_form_widgets(form_frame)
        self._create_table_widgets(table_frame)
        self._create_legacy_action_buttons(legacy_actions_frame)

    def _create_form_widgets(self, parent):
        ttk.Label(parent, text="Nome:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.nome_entry = ttk.Entry(parent, textvariable=self.controller.nome_var, width=40)
        self.nome_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        ttk.Label(parent, text="Ano de Criação:").grid(row=0, column=3, sticky="w", padx=15, pady=5)
        self.ano_spinbox = ttk.Spinbox(parent, from_=1950, to=2025, textvariable=self.controller.ano_var, width=8)
        self.ano_spinbox.grid(row=0, column=4, sticky="w", padx=5, pady=5)

        ttk.Label(parent, text="Tipagem:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        tipo_frame = ttk.Frame(parent)
        tipo_frame.grid(row=1, column=1, columnspan=2, sticky="ew")

        self.tipo_combobox = ttk.Combobox(tipo_frame, textvariable=self.controller.tipo_var, state="readonly")
        self.tipo_combobox.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        self.add_tipo_button = ttk.Button(tipo_frame, text="➕", command=self.controller._open_tipos_modal,
                                          style="primary.Outline.TButton", width=3)
        self.add_tipo_button.pack(side="left", padx=(0, 5), pady=5)

        ttk.Label(parent, text="Categoria:").grid(row=1, column=3, sticky="w", padx=15, pady=5)
        self.categoria_entry = ttk.Entry(parent, textvariable=self.controller.categoria_var)
        self.categoria_entry.grid(row=1, column=4, sticky="ew", padx=5, pady=5)

        parent.columnconfigure(1, weight=1)
        parent.columnconfigure(4, weight=1)

        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=2, column=0, columnspan=5, pady=10, sticky="e")

        # Comandos dos botões são ligados aos métodos do Controller
        self.save_button = ttk.Button(btn_frame, text="Salvar", command=self.controller._save_item, style="success.TButton")
        self.save_button.pack(side="left", padx=5)
        self.delete_button = ttk.Button(btn_frame, text="Excluir", command=self.controller._delete_item, style="danger.TButton")
        self.delete_button.pack(side="left", padx=5)
        self.clear_button = ttk.Button(btn_frame, text="Limpar", command=self.controller._clear_form, style="secondary.TButton")
        self.clear_button.pack(side="left", padx=5)

    def _create_table_widgets(self, parent):
        inner_frame = ttk.Frame(parent)
        inner_frame.pack(fill="both", expand=True)
        columns = ('id', 'nome', 'tipo', 'ano_criacao', 'categoria')
        self.tree = ttk.Treeview(inner_frame, columns=columns, show='headings', selectmode='browse')

        headings = {'id': 'ID', 'nome': 'Linguagem', 'tipo': 'Tipagem', 'ano_criacao': 'Ano', 'categoria': 'Categoria'}
        for col, text in headings.items():
            self.tree.heading(col, text=text)

        column_configs = {'id': (50, 'center'), 'nome': (200, 'w'), 'tipo': (120, 'center'), 'ano_criacao': (80, 'center'), 'categoria': (200, 'w')}
        for col, (width, anchor) in column_configs.items():
            self.tree.column(col, width=width, anchor=anchor)

        scrollbar = ttk.Scrollbar(inner_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Evento da tabela é ligado a um método do Controller
        self.tree.bind('<<TreeviewSelect>>', self.controller._on_item_select)

    def _create_legacy_action_buttons(self, parent):
        reclassify_btn = ttk.Button(parent, text="Reclassificar C++ para 'Legado' (Exemplo Atômico)",
                                    command=self.controller._executar_reclassificacao, style="info.Outline.TButton")
        reclassify_btn.pack(side="left", padx=5, pady=5)