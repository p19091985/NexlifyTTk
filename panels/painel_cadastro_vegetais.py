import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import config
from panels.base_panel import BasePanel
from persistencia.repository import GenericRepository
from modals.tipos_vegetais_manager import TiposVegetaisManagerDialog

class PainelCadastroVegetais(BasePanel):
    """
    Painel para cadastrar e gerenciar Vegetais e seus Tipos.
    Este painel combina a interface (View) e a lógica (Controller).
    Utiliza um diálogo modal (TiposVegetaisManagerDialog) para gerenciar
    a tabela auxiliar 'tipos_vegetais'.
    """
    PANEL_NAME = "Cadastro de Vegetais"
    PANEL_ICON = "🥕"
    ALLOWED_ACCESS = ['Administrador Global', 'Diretor de Operações', 'Gerente de TI', 'Analista de Dados']

    def __init__(self, parent, app_controller, **kwargs):
                                     
        self.selected_item_id = None                                               
        self.nome_var = tk.StringVar()                                        
        self.tipo_var = tk.StringVar()                                

                                        
        self.nome_entry = None                          
        self.tipo_combobox = None                  
        self.tree = None                    

                                                                 
        super().__init__(parent, app_controller, **kwargs)

                                               

    def create_widgets(self):
        """
        Método principal que organiza a criação da interface do painel.
        """
        if not config.DATABASE_ENABLED:
            ttk.Label(self, text="Funcionalidade indisponível: o banco de dados está desabilitado.",
                      font=("-size", 12, "-weight", "bold")).pack(pady=50)
            return

                                  
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)
                                                   
        main_frame.rowconfigure(1, weight=1)
                                 
        main_frame.columnconfigure(0, weight=1)

                                                                 
        self._build_form(main_frame)
        self._build_table(main_frame)

                                      
                                                           
        self._load_data_into_table()
        self._load_tipos_into_combobox()

    def _build_form(self, parent):
        """Cria o formulário de cadastro do vegetal."""
        form_frame = ttk.LabelFrame(parent, text=" 🥕 Cadastro de Vegetal ", padding=15)
                                                                       
        form_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 15))
                                                                      
        form_frame.columnconfigure(1, weight=1)

                               
        ttk.Label(form_frame, text="Nome do Vegetal:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.nome_entry = ttk.Entry(form_frame, textvariable=self.nome_var)
        self.nome_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

                                                 
        ttk.Label(form_frame, text="Tipo:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
                                                             
        tipo_frame = ttk.Frame(form_frame)
        tipo_frame.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        self.tipo_combobox = ttk.Combobox(tipo_frame, textvariable=self.tipo_var, state="readonly")
        self.tipo_combobox.pack(side="left", fill="x", expand=True)                    

                                                              
        ttk.Button(tipo_frame, text="Gerenciar Tipos...", command=self._on_manage_tipos_click, width=15).pack(
            side="left", padx=(5, 0))                             

                                                      
        btn_frame = ttk.Frame(form_frame)
                                                                 
        btn_frame.grid(row=2, column=1, pady=(10, 0), sticky="e")

                                                        
        ttk.Button(btn_frame, text="Salvar", command=self._on_save_button_click, style="Success.TButton").pack(
            side="left", padx=5)
        ttk.Button(btn_frame, text="Excluir", command=self._on_delete_button_click, style="Danger.TButton").pack(
            side="left", padx=5)
        ttk.Button(btn_frame, text="Limpar", command=self._on_clear_button_click, style="Secondary.TButton").pack(
            side="left")

    def _build_table(self, parent):
        """Cria a tabela (Treeview) para exibir os vegetais cadastrados."""
        table_frame = ttk.LabelFrame(parent, text=" 🍽️ Vegetais Cadastrados ", padding=15)
                                                                   
        table_frame.grid(row=1, column=0, sticky="nsew")
                                                                         
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

                           
        columns = ('id', 'nome', 'tipo')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', selectmode='browse')

                                                    
        self.tree.heading('id', text='ID')
        self.tree.heading('nome', text='Nome do Vegetal')
        self.tree.heading('tipo', text='Tipo')
        self.tree.column('id', width=50, anchor='center')
        self.tree.column('nome', width=200)
        self.tree.column('tipo', width=180)

                                 
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

                                              
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

                                                                
        self.tree.bind("<<TreeviewSelect>>", self._on_table_select)

                                       

    def _load_data_into_table(self):
        """ (READ) Busca os vegetais (com nome do tipo) e preenche a tabela. """
        try:
                            
            for item in self.tree.get_children():
                self.tree.delete(item)

                                                                                        
            df_vegetais = GenericRepository.read_vegetais_com_tipo()

                                               
            if not df_vegetais.empty:
                for _, row in df_vegetais.iterrows():
                    self.tree.insert("", "end", values=list(row))
        except Exception as e:
            messagebox.showerror("Erro de Carga", f"Não foi possível carregar a lista de vegetais.\n{e}", parent=self)

    def _load_tipos_into_combobox(self):
        """ (READ) Busca os tipos de vegetais e preenche o ComboBox. """
        try:
                                                             
            df_tipos = GenericRepository.read_table_to_dataframe("tipos_vegetais")
                                                             
            tipos_lista = sorted(df_tipos['nome'].tolist()) if not df_tipos.empty else []
                                                        
            self.tipo_combobox['values'] = tipos_lista
        except Exception as e:
            messagebox.showerror("Erro de Carga", f"Não foi possível recarregar os tipos de vegetais.\n{e}",
                                 parent=self)
                                                              
            self.tipo_combobox['values'] = []

    def _clear_form_fields(self):
        """ Limpa os campos do formulário e a seleção da tabela. """
        self.selected_item_id = None
        self.nome_var.set("")
        self.tipo_var.set("")                              

        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])
                               
        self.nome_entry.focus()

                                          

    def _on_manage_tipos_click(self):
        """ Chamado ao clicar no botão 'Gerenciar Tipos...'. Abre o diálogo modal. """
                                                                            
                                                                  
        dialog = TiposVegetaisManagerDialog(self, on_close_callback=self._load_tipos_into_combobox)
                                                                       
        dialog.wait_window()

    def _on_save_button_click(self):
        """ (CREATE/UPDATE) Chamado ao clicar no botão 'Salvar'. """
        nome = self.nome_var.get().strip()
        tipo_nome = self.tipo_var.get()                                              

                           
        if not nome or not tipo_nome:
            messagebox.showerror("Erro de Validação", "Os campos 'Nome' e 'Tipo' são obrigatórios.", parent=self)
            return

        try:
                                        
                                                                       
            df_tipo = GenericRepository.read_table_to_dataframe(
                "tipos_vegetais",
                where_conditions={'nome': tipo_nome}                               
            )
                                                                            
            if df_tipo.empty:
                messagebox.showerror("Erro de Dados", f"O tipo '{tipo_nome}' não foi encontrado.", parent=self)
                return

                                                              
            id_tipo = int(df_tipo.iloc[0]['id'])

                                      
            data = {'nome': nome, 'id_tipo': id_tipo}

                                                               
            if self.selected_item_id is None:
                                                                       
                GenericRepository.write_dataframe_to_table(pd.DataFrame([data]), "vegetais")
                messagebox.showinfo("Sucesso", "Vegetal cadastrado!", parent=self)
            else:
                                                                  
                GenericRepository.update_table(
                    "vegetais",
                    update_values=data,
                    where_conditions={'id': self.selected_item_id}
                )
                messagebox.showinfo("Sucesso", "Vegetal atualizado!", parent=self)

                              
            self._clear_form_fields()                     
            self._load_data_into_table()                     

        except Exception as e:
            messagebox.showerror("Erro de Banco de Dados", f"Não foi possível salvar o registro.\n{e}", parent=self)

    def _on_delete_button_click(self):
        """ (DELETE) Chamado ao clicar no botão 'Excluir'. """
        if self.selected_item_id is None:
            messagebox.showwarning("Atenção", "Selecione um vegetal na tabela para excluir.", parent=self)
            return

                     
        if messagebox.askyesno("Confirmar Exclusão", "Deseja realmente excluir este vegetal?", icon='warning',
                               parent=self):
            try:
                                             
                GenericRepository.delete_from_table(
                    "vegetais",
                    where_conditions={'id': self.selected_item_id}
                )
                messagebox.showinfo("Sucesso", "Vegetal excluído!", parent=self)

                                  
                self._clear_form_fields()
                self._load_data_into_table()
            except Exception as e:
                                                                           
                                                                            
                if "FOREIGN KEY constraint failed" in str(e) or "violates foreign key constraint" in str(e):
                     messagebox.showerror("Erro de Integridade",
                                          "Não foi possível excluir este vegetal pois ele está referenciado em outro lugar.",
                                          parent=self)
                else:
                    messagebox.showerror("Erro de Banco de Dados", f"Não foi possível excluir o registro.\n{e}",
                                         parent=self)

    def _on_clear_button_click(self):
        """ Chamado ao clicar no botão 'Limpar'. """
        self._clear_form_fields()

    def _on_table_select(self, event=None):
        """ Chamado quando um item é selecionado na tabela. Preenche o formulário. """
        selected_items = self.tree.selection()
        if not selected_items:
            return

        item = self.tree.item(selected_items[0])
        values = item['values']                                                          

                                          
        self.selected_item_id = values[0]
        self.nome_var.set(values[1])
                                                                           
        self.tipo_var.set(values[2])