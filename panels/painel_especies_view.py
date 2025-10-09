# panels/painel_especies_view.py
import tkinter as tk
from tkinter import ttk

class GatosView(ttk.Frame):
    """
    A View (Apresentação) para o painel de gestão de espécies.
    Contém apenas a criação e o layout dos widgets.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)

        form_frame = ttk.LabelFrame(main_frame, text=" 📝 Cadastro de Espécie de Gato ", padding=15)
        form_frame.pack(fill="x", pady=(0, 10))

        table_frame = ttk.LabelFrame(main_frame, text=" 🐱 Espécies Cadastradas ", padding=15)
        table_frame.pack(fill="both", expand=True)

        actions_frame = ttk.LabelFrame(main_frame, text=" ⚙️ Ações Atômicas (Exemplo) ", padding=10)
        actions_frame.pack(fill="x", pady=(15, 0))

        self._create_form_widgets(form_frame)
        self._create_table_widgets(table_frame)
        self._create_action_buttons(actions_frame)

    def _create_form_widgets(self, parent):
        ttk.Label(parent, text="Nome da Espécie:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.nome_entry = ttk.Entry(parent, textvariable=self.controller.nome_var, width=30)
        self.nome_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(parent, text="País de Origem:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.pais_entry = ttk.Entry(parent, textvariable=self.controller.pais_var, width=30)
        self.pais_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(parent, text="Temperamento:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.temperamento_entry = ttk.Entry(parent, textvariable=self.controller.temperamento_var)
        self.temperamento_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        parent.columnconfigure(1, weight=1)

        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="e")
        ttk.Button(btn_frame, text="Salvar", command=self.controller.salvar_item, style="success.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Excluir", command=self.controller.excluir_item, style="danger.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Limpar", command=self.controller.limpar_formulario, style="secondary.TButton").pack(side="left", padx=5)

    def _create_table_widgets(self, parent):
        inner_frame = ttk.Frame(parent)
        inner_frame.pack(fill="both", expand=True)
        # --- MODIFICAÇÃO: Colunas da view definidas em minúsculas ---
        columns = ('id', 'nome_especie', 'pais_origem', 'temperamento')
        self.tree = ttk.Treeview(inner_frame, columns=columns, show='headings', selectmode='browse')

        self.tree.heading('id', text='ID')
        self.tree.heading('nome_especie', text='Nome da Espécie')
        self.tree.heading('pais_origem', text='País de Origem')
        self.tree.heading('temperamento', text='Temperamento')

        self.tree.column('id', width=50, anchor='center')
        self.tree.column('nome_especie', width=150)
        self.tree.column('pais_origem', width=120)
        self.tree.column('temperamento', width=250)

        scrollbar = ttk.Scrollbar(inner_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self.tree.bind('<<TreeviewSelect>>', self.controller.on_item_select)

    def _create_action_buttons(self, parent):
        ttk.Button(parent, text="Renomear 'Siamês' para 'Siamês Gato Tailandês'",
                   command=self.controller.executar_acao_atomica, style="info.Outline.TButton").pack(side="left", padx=5, pady=5)