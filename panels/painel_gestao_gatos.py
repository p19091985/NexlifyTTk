import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import config
from panels.base_panel import BasePanel
from persistencia.repository import GenericRepository

class PainelGestaoGatos(BasePanel):
    """
    Painel para gerenciar (criar, ler, atualizar, deletar)
    as espécies de gatos na tabela 'especie_gatos'.
    Este painel combina a interface (View) e a lógica (Controller).
    """
    PANEL_NAME = "Gestão de Espécies (Gatos)"
    PANEL_ICON = "🐈"
                                                             

    def __init__(self, parent, app_controller, **kwargs):
                                     
        self.selected_item_id = None                                            
        self.nome_var = tk.StringVar()                                        
        self.pais_var = tk.StringVar()                                        
        self.temperamento_var = tk.StringVar()                                                

                                        
                                                                                        
        self.tree = None                      
        self.nome_entry = None                            

                                                                             
        super().__init__(parent, app_controller, **kwargs)

                                               

    def create_widgets(self):
        """
        Método principal que organiza a criação da interface do painel.
        Chama métodos auxiliares para construir cada parte da UI.
        """
                                                                   
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

                                                                                      
        self._build_form(top_container)
        self._build_crud_buttons(top_container)

                                             
                                                                 
        self._build_table(main_frame)

                                      
                                                                     
        self._load_data_into_table()

    def _build_form(self, parent):
        """Cria os campos de entrada (formulário) para os dados do gato."""
        form_frame = ttk.LabelFrame(parent, text=" 📝 Formulário de Dados ", padding=15)
                                                                          
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
                                                                            
        form_frame.columnconfigure(1, weight=1)

                                                                           
        ttk.Label(form_frame, text="Nome da Espécie:").grid(row=0, column=0, sticky="w", pady=2)
        self.nome_entry = ttk.Entry(form_frame, textvariable=self.nome_var)
        self.nome_entry.grid(row=0, column=1, sticky="ew", pady=2)                                 

        ttk.Label(form_frame, text="País de Origem:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(form_frame, textvariable=self.pais_var).grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(form_frame, text="Temperamento:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(form_frame, textvariable=self.temperamento_var).grid(row=2, column=1, sticky="ew", pady=2)

    def _build_crud_buttons(self, parent):
        """Cria os botões de ação (Inserir, Atualizar, Excluir, Limpar)."""
        crud_buttons_frame = ttk.LabelFrame(parent, text=" ⚙️ Operações CRUD ", padding=15)
                                                                       
        crud_buttons_frame.grid(row=0, column=1, sticky="nsew")
                                                                                   
        crud_buttons_frame.rowconfigure([0, 1], weight=1)
        crud_buttons_frame.columnconfigure([0, 1], weight=1)

                                                                                   
        ttk.Button(crud_buttons_frame, text="Inserir (CREATE)", command=self._on_insert_button_click, style="Success.TButton").grid(
            row=0, column=0, sticky="nsew", padx=2, pady=2)                                     
        ttk.Button(crud_buttons_frame, text="Atualizar Lista (READ)", command=self._load_data_into_table,
                   style="Info.TButton").grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        ttk.Button(crud_buttons_frame, text="Salvar Edição (UPDATE)", command=self._on_update_button_click,
                   style="Warning.TButton").grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        ttk.Button(crud_buttons_frame, text="Excluir (DELETE)", command=self._on_delete_button_click, style="Danger.TButton").grid(
            row=1, column=1, sticky="nsew", padx=2, pady=2)
        ttk.Button(crud_buttons_frame, text="Limpar Formulário", command=self._on_clear_button_click,
                   style="Secondary.TButton").grid(row=2, column=0, columnspan=2, sticky="ew", padx=2, pady=5)                  

    def _build_table(self, parent):
        """Cria a tabela (Treeview) para exibir os dados dos gatos."""
        table_frame = ttk.LabelFrame(parent, text=" 🐱 Tabela 'especie_gatos' ", padding=15)
                                                                  
        table_frame.grid(row=1, column=0, sticky="nsew")
                                                                         
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

                                     
        columns = ('id', 'nome_especie', 'pais_origem', 'temperamento')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', selectmode='browse')

                                                       
        for col in columns:
                                                                        
            self.tree.heading(col, text=col.replace('_', ' ').title())
                                           
        self.tree.column('id', width=40, anchor='center')
        self.tree.column('nome_especie', width=150)
        self.tree.column('pais_origem', width=150)
        self.tree.column('temperamento', width=200)

                                          
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)                           

                                                         
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")                               

                                   
                                                                          
        self.tree.bind("<<TreeviewSelect>>", self._on_table_select)

                                       

    def _load_data_into_table(self):
        """ (READ) Busca os dados no banco e preenche a tabela. """
        try:
                                                          
            for item in self.tree.get_children():
                self.tree.delete(item)

                                                          
            df = GenericRepository.read_table_to_dataframe("especie_gatos")

                                                                           
            if not df.empty:
                for _, row in df.iterrows():                                     
                                                                       
                    self.tree.insert("", "end", values=list(row))

                                                       
            self._clear_form_fields()
        except Exception as e:
                                                             
            messagebox.showerror("Erro de Leitura", f"Não foi possível ler os dados: {e}", parent=self)

    def _get_data_from_form(self) -> dict:
        """ Pega os valores atuais dos campos de entrada do formulário. """
        return {
            'nome_especie': self.nome_var.get().strip(),                                 
            'pais_origem': self.pais_var.get().strip(),
            'temperamento': self.temperamento_var.get().strip()
        }

    def _clear_form_fields(self):
        """ Limpa os campos do formulário e a seleção da tabela. """
        self.selected_item_id = None                          
        self.nome_var.set("")                                                
        self.pais_var.set("")
        self.temperamento_var.set("")

                                                      
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])

                                                                      
        if self.nome_entry:
            self.nome_entry.focus()

                                                             

    def _on_table_select(self, event=None):
        """ Chamado quando um item é selecionado na tabela. Preenche o formulário. """
        selected_items = self.tree.selection()                           
        if not selected_items:
                                                                         
            return

                                              
        item = self.tree.item(selected_items[0], "values")

                                         
        self.selected_item_id = item[0]

                                                                     
        self.nome_var.set(item[1])
        self.pais_var.set(item[2])
        self.temperamento_var.set(item[3])

    def _on_clear_button_click(self):
        """ Chamado ao clicar no botão 'Limpar Formulário'. """
        self._clear_form_fields()

    def _on_insert_button_click(self):
        """ (CREATE) Chamado ao clicar no botão 'Inserir'. Valida e salva um novo item. """
        data = self._get_data_from_form()                              

                                   
        if not data['nome_especie']:
            messagebox.showwarning("Validação", "O campo 'Nome da Espécie' é obrigatório.", parent=self)
            return                                              

                                     
        try:
                                                                              
            GenericRepository.write_dataframe_to_table(pd.DataFrame([data]), "especie_gatos")
            messagebox.showinfo("Sucesso", "Nova espécie inserida com sucesso!", parent=self)
                                                         
            self._load_data_into_table()
        except Exception as e:
                                              
                                                                                
            messagebox.showerror("Erro de Inserção", f"Não foi possível inserir o registro: {e}", parent=self)

    def _on_update_button_click(self):
        """ (UPDATE) Chamado ao clicar no botão 'Salvar Edição'. Valida e atualiza o item selecionado. """
                                                       
        if self.selected_item_id is None:
            messagebox.showwarning("Atenção", "Selecione um item da tabela para atualizar.", parent=self)
            return

        data = self._get_data_from_form()                                     

                                                                         
        if not data['nome_especie']:
             messagebox.showwarning("Validação", "O campo 'Nome da Espécie' não pode ficar vazio.", parent=self)
             return

                                     
        try:
                                                                         
                                                              
            GenericRepository.update_table(
                table_name="especie_gatos",
                update_values=data,
                where_conditions={'id': self.selected_item_id}
            )
            messagebox.showinfo("Sucesso", "Espécie atualizada com sucesso!", parent=self)
                                                         
            self._load_data_into_table()
        except Exception as e:
                                                 
            messagebox.showerror("Erro de Atualização", f"Não foi possível atualizar o registro: {e}", parent=self)

    def _on_delete_button_click(self):
        """ (DELETE) Chamado ao clicar no botão 'Excluir'. Confirma e remove o item selecionado. """
                                             
        if self.selected_item_id is None:
            messagebox.showwarning("Atenção", "Selecione um item da tabela para excluir.", parent=self)
            return

                             
                                                      
        if not messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir a espécie selecionada?",
                                   icon='warning', parent=self):
            return                                          

                                     
        try:
                                                                        
                                                              
            GenericRepository.delete_from_table(
                table_name="especie_gatos",
                where_conditions={'id': self.selected_item_id}
            )
            messagebox.showinfo("Sucesso", "Espécie excluída com sucesso!", parent=self)
                                                                
            self._load_data_into_table()
        except Exception as e:
                                                                                   
            messagebox.showerror("Erro de Exclusão", f"Não foi possível excluir o registro: {e}", parent=self)