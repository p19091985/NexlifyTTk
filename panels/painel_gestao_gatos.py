import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import config
from panels.base_panel import BasePanel
                                                      
from persistencia.repository import GenericRepository
                                                              


class PainelGestaoGatos(BasePanel):
    """
    Controller e View unificados para as operações CRUD da tabela especie_gatos.
    A funcionalidade de transação/auditoria foi removida.
    """
    PANEL_NAME = "Gestão de Espécies (Gatos)"
    PANEL_ICON = "🐈"
    ALLOWED_ACCESS = []

    def __init__(self, parent, app_controller, **kwargs):
        self.selected_item_id = None
        self.nome_var = tk.StringVar()
        self.pais_var = tk.StringVar()
        self.temperamento_var = tk.StringVar()
                                                        

        self.tree = None
        self.nome_entry = None
        super().__init__(parent, app_controller, **kwargs)

    def create_widgets(self):
        if not config.DATABASE_ENABLED:
            ttk.Label(self, text="Funcionalidade indisponível: o banco de dados está desabilitado.",
                      font=("-size", 12, "-weight", "bold")).pack(pady=50)
            return

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

                                                                                  
                                                                                                        
                                                                                    
                                                       

        self.carregar_dados()

    def _create_form_widgets(self, parent):
        """Cria o formulário de dados"""
        parent.columnconfigure(1, weight=1)
        ttk.Label(parent, text="Nome da Espécie:").grid(row=0, column=0, sticky="w", pady=2)
        self.nome_entry = ttk.Entry(parent, textvariable=self.nome_var)
        self.nome_entry.grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Label(parent, text="País de Origem:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(parent, textvariable=self.pais_var).grid(row=1, column=1, sticky="ew", pady=2)
        ttk.Label(parent, text="Temperamento:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(parent, textvariable=self.temperamento_var).grid(row=2, column=1, sticky="ew", pady=2)

    def _create_crud_buttons(self, parent):
        """Cria os botões de ação"""
        parent.rowconfigure([0, 1], weight=1)
        parent.columnconfigure([0, 1], weight=1)
        ttk.Button(parent, text="Inserir (CREATE)", command=self.inserir_item, style="Success.TButton").grid(
            row=0, column=0, sticky="nsew", padx=2, pady=2)
        ttk.Button(parent, text="Atualizar Lista (READ)", command=self.carregar_dados,
                   style="Info.TButton").grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        ttk.Button(parent, text="Salvar Edição (UPDATE)", command=self.atualizar_item,
                   style="Warning.TButton").grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        ttk.Button(parent, text="Excluir (DELETE)", command=self.excluir_item, style="Danger.TButton").grid(
            row=1, column=1, sticky="nsew", padx=2, pady=2)
        ttk.Button(parent, text="Limpar Formulário", command=self.limpar_form,
                   style="Secondary.TButton").grid(row=2, column=0, columnspan=2, sticky="ew", padx=2, pady=5)

    def _create_table(self, parent):
        """Cria a tabela de dados"""
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
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)

                                                  
                                                    
             

    def carregar_dados(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            df = GenericRepository.read_table_to_dataframe("especie_gatos")
            if not df.empty:
                for _, row in df.iterrows():
                    self.tree.insert("", "end", values=list(row))
            self.limpar_form()
        except Exception as e:
            messagebox.showerror("Erro de Leitura", f"Não foi possível ler os dados: {e}", parent=self)

    def on_item_select(self, event=None):
        selected_items = self.tree.selection()
        if not selected_items: return
        item = self.tree.item(selected_items[0], "values")
        self.selected_item_id = item[0]
        self.nome_var.set(item[1])
        self.pais_var.set(item[2])
        self.temperamento_var.set(item[3])

    def limpar_form(self):
        self.selected_item_id = None
        self.nome_var.set("")
        self.pais_var.set("")
        self.temperamento_var.set("")
                                               
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])
        if self.nome_entry:
            self.nome_entry.focus()

    def inserir_item(self):
        nome = self.nome_var.get().strip()
        if not nome:
            messagebox.showwarning("Validação", "O campo 'Nome da Espécie' é obrigatório.", parent=self)
            return
        data = {'nome_especie': nome, 'pais_origem': self.pais_var.get().strip(),
                'temperamento': self.temperamento_var.get().strip()}
        try:
            GenericRepository.write_dataframe_to_table(pd.DataFrame([data]), "especie_gatos")
            messagebox.showinfo("Sucesso", "Nova espécie inserida com sucesso!", parent=self)
            self.carregar_dados()
        except Exception as e:
            messagebox.showerror("Erro de Inserção", f"Não foi possível inserir o registro: {e}", parent=self)

    def atualizar_item(self):
        if self.selected_item_id is None:
            messagebox.showwarning("Atenção", "Selecione um item da tabela para atualizar.", parent=self)
            return
        update_values = {'nome_especie': self.nome_var.get().strip(), 'pais_origem': self.pais_var.get().strip(),
                         'temperamento': self.temperamento_var.get().strip()}
        try:
            GenericRepository.update_table("especie_gatos", update_values=update_values,
                                           where_conditions={'id': self.selected_item_id})
            messagebox.showinfo("Sucesso", "Espécie atualizada com sucesso!", parent=self)
            self.carregar_dados()
        except Exception as e:
            messagebox.showerror("Erro de Atualização", f"Não foi possível atualizar o registro: {e}", parent=self)

    def excluir_item(self):
        if self.selected_item_id is None:
            messagebox.showwarning("Atenção", "Selecione um item da tabela para excluir.", parent=self)
            return
        if not messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir a espécie selecionada?",
                                   icon='warning', parent=self):
            return
        try:
            GenericRepository.delete_from_table("especie_gatos", where_conditions={'id': self.selected_item_id})
            messagebox.showinfo("Sucesso", "Espécie excluída com sucesso!", parent=self)
            self.carregar_dados()
        except Exception as e:
            messagebox.showerror("Erro de Exclusão", f"Não foi possível excluir o registro: {e}", parent=self)

                                                
                                          
             