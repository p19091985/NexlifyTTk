                                         
import tkinter as tk
from tkinter import ttk


class CadastroVegetaisView(ttk.Frame):
    """
    A View para o painel de cadastro de vegetais.
    Contém a criação e o layout de todos os widgets da interface.
    """

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)

                                                        
        form_frame = ttk.LabelFrame(main_frame, text=" 🥕 Cadastro de Vegetal ", padding=15)
        form_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 15))
        self._create_form_widgets(form_frame)

                                    
        table_frame = ttk.LabelFrame(main_frame, text=" 🍽️ Vegetais Cadastrados ", padding=15)
        table_frame.grid(row=1, column=0, sticky="nsew")
        self._create_table_widgets(table_frame)

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

                                     
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=2, column=1, pady=(10, 0), sticky="e")

        ttk.Button(btn_frame, text="Salvar", command=self.controller.save_item, style="Success.TButton").pack(
            side="left", padx=5)
        ttk.Button(btn_frame, text="Excluir", command=self.controller.delete_item, style="Danger.TButton").pack(
            side="left", padx=5)
        ttk.Button(btn_frame, text="Limpar", command=self.controller.clear_form, style="Secondary.TButton").pack(
            side="left")

    def _create_table_widgets(self, parent):
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)

        columns = ('id', 'nome', 'tipo')
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', selectmode='browse')

        self.tree.heading('id', text='ID')
        self.tree.heading('nome', text='Nome do Vegetal')
        self.tree.heading('tipo', text='Tipo')

        self.tree.column('id', width=50, anchor='center')
        self.tree.column('nome', width=200)
        self.tree.column('tipo', width=180)

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self.controller.on_item_select)