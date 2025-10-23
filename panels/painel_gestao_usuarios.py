import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import config
from panels.base_panel import BasePanel
from persistencia.repository import GenericRepository
from persistencia.auth import hash_password                                         

                                                            
PERFIS_DE_ACESSO = [
    'Administrador Global',
    'Diretor de Operações',
    'Gerente de TI',
    'Supervisor de Produção',
    'Operador de Linha',
    'Analista de Dados',
    'Auditor Externo'
]

class PainelGestaoUsuariosController(BasePanel):
    """
    Painel para gerenciar (CRUD) os usuários do sistema na tabela 'usuarios'.
    Este painel combina a interface (View) e a lógica (Controller).
    Realiza o hashing de senhas antes de salvar.
    """
    PANEL_NAME = "Gestão de Usuários"
    PANEL_ICON = "👤"
                                                                   
    ALLOWED_ACCESS = ['Administrador Global', 'Gerente de TI']

    def __init__(self, parent, app_controller, **kwargs):
                                     
        self.selected_item_login = None                                                  
        self.login_var = tk.StringVar()
        self.nome_completo_var = tk.StringVar()
        self.tipo_acesso_var = tk.StringVar()
        self.senha_var = tk.StringVar()                                          

                                        
        self.tree = None
        self.login_entry = None
        self.nome_entry = None
        self.tipo_acesso_combo = None
        self.senha_entry = None

                                                                 
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

                                                          
        top_container = ttk.Frame(main_frame)
        top_container.grid(row=0, column=0, sticky="nsew", pady=(0, 15))
        top_container.columnconfigure(0, weight=1)                               
        top_container.columnconfigure(1, minsize=180)                                       

                                                                  
        self._build_form(top_container)
        self._build_crud_buttons(top_container)

                                             
        self._build_table(main_frame)

                                      
        self._load_data_into_table()

    def _build_form(self, parent):
        """Cria os campos de entrada (formulário) para os dados do usuário."""
        form_frame = ttk.LabelFrame(parent, text=" 📝 Dados do Usuário ", padding=15)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))                            
        form_frame.columnconfigure(1, weight=1)                               

                     
        ttk.Label(form_frame, text="Login:").grid(row=0, column=0, sticky="w", pady=3, padx=5)
        self.login_entry = ttk.Entry(form_frame, textvariable=self.login_var)
        self.login_entry.grid(row=0, column=1, sticky="ew", pady=3, padx=5)

                             
        ttk.Label(form_frame, text="Nome Completo:").grid(row=1, column=0, sticky="w", pady=3, padx=5)
        self.nome_entry = ttk.Entry(form_frame, textvariable=self.nome_completo_var)
        self.nome_entry.grid(row=1, column=1, sticky="ew", pady=3, padx=5)

                                           
        ttk.Label(form_frame, text="Perfil de Acesso:").grid(row=2, column=0, sticky="w", pady=3, padx=5)
        self.tipo_acesso_combo = ttk.Combobox(form_frame, textvariable=self.tipo_acesso_var,
                                              values=PERFIS_DE_ACESSO, state="readonly")
        self.tipo_acesso_combo.grid(row=2, column=1, sticky="ew", pady=3, padx=5)
                                                                                        
        if PERFIS_DE_ACESSO:
             self.tipo_acesso_combo.current(0)

                                            
        ttk.Label(form_frame, text="Senha:").grid(row=3, column=0, sticky="w", pady=3, padx=5)
                                             
        self.senha_entry = ttk.Entry(form_frame, textvariable=self.senha_var, show="*")
        self.senha_entry.grid(row=3, column=1, sticky="ew", pady=3, padx=5)

    def _build_crud_buttons(self, parent):
        """Cria os botões de ação (Salvar, Excluir, Limpar)."""
        crud_buttons_frame = ttk.Frame(parent, padding=(10,0))                              
        crud_buttons_frame.grid(row=0, column=1, sticky="nsew")                            
                                                                                    
        crud_buttons_frame.rowconfigure(0, weight=1)
        crud_buttons_frame.rowconfigure(1, weight=1)
        crud_buttons_frame.rowconfigure(2, weight=1)
        crud_buttons_frame.columnconfigure(0, weight=1)                      

                                                        
        save_btn = ttk.Button(crud_buttons_frame, text="Salvar", command=self._on_save_button_click, style="Success.TButton")
                                                                             
        save_btn.grid(row=0, column=0, sticky="nsew", padx=2, pady=3, ipady=4)

        delete_btn = ttk.Button(crud_buttons_frame, text="Excluir", command=self._on_delete_button_click, style="Danger.TButton")
        delete_btn.grid(row=1, column=0, sticky="nsew", padx=2, pady=3, ipady=4)

        clear_btn = ttk.Button(crud_buttons_frame, text="Limpar", command=self._on_clear_button_click, style="Secondary.TButton")
        clear_btn.grid(row=2, column=0, sticky="nsew", padx=2, pady=3, ipady=4)

    def _build_table(self, parent):
        """Cria a tabela (Treeview) para exibir os usuários."""
        table_frame = ttk.LabelFrame(parent, text=" 👥 Usuários Cadastrados ", padding=15)
        table_frame.grid(row=1, column=0, sticky="nsew")                        
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

                                                            
        columns = ('login_usuario', 'nome_completo', 'tipo_acesso')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', selectmode='browse')

                                        
        self.tree.heading('login_usuario', text='Login')
        self.tree.heading('nome_completo', text='Nome Completo')
        self.tree.heading('tipo_acesso', text='Perfil de Acesso')
        self.tree.column('login_usuario', width=120, anchor='w')                             
        self.tree.column('nome_completo', width=250, anchor='w')
        self.tree.column('tipo_acesso', width=150, anchor='w')

                                 
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

                           
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

                                     
        self.tree.bind("<<TreeviewSelect>>", self._on_table_select)

                                       

    def _load_data_into_table(self):
        """ (READ) Busca os usuários no banco e preenche a tabela. """
        try:
                            
            for item in self.tree.get_children():
                self.tree.delete(item)

                            
            df_users = GenericRepository.read_table_to_dataframe("usuarios")

                                                                                
            if 'senha_criptografada' in df_users.columns:
                df_users = df_users.drop(columns=['senha_criptografada'])

                               
            if not df_users.empty:
                for _, row in df_users.iterrows():
                                                                                        
                    self.tree.insert("", "end", values=(
                        row['login_usuario'],
                        row['nome_completo'],
                        row['tipo_acesso']
                    ))
                                              
            self._clear_form_fields()
        except Exception as e:
            messagebox.showerror("Erro de Leitura", f"Não foi possível carregar os usuários: {e}", parent=self)

    def _clear_form_fields(self):
        """ Limpa os campos do formulário e a seleção da tabela. """
        self.selected_item_login = None
        self.login_var.set("")
        self.nome_completo_var.set("")
        self.tipo_acesso_var.set("")
        self.senha_var.set("")                         

                                                                               
        if self.login_entry:
            self.login_entry.config(state='normal')

                                         
        if self.tree and self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])

                                
        if self.login_entry:
            self.login_entry.focus()

                                          

    def _on_table_select(self, event=None):
        """ Chamado quando um usuário é selecionado na tabela. Preenche o formulário. """
        selected_items = self.tree.selection()
        if not selected_items:
                                                           
            self._clear_form_fields()
            return

        item_values = self.tree.item(selected_items[0], "values")

                                                                
        self.selected_item_login = item_values[0]

                                          
        self.login_var.set(item_values[0])
        self.nome_completo_var.set(item_values[1])
        self.tipo_acesso_var.set(item_values[2])
        self.senha_var.set("")                                                      

                                                                            
        self.login_entry.config(state='disabled')
                                                                
        self.senha_entry.focus()

    def _on_clear_button_click(self):
        """ Chamado ao clicar no botão 'Limpar'. """
        self._clear_form_fields()

    def _on_save_button_click(self):
        """ (CREATE/UPDATE) Chamado ao clicar no botão 'Salvar'. """
        login = self.login_var.get().strip()
        nome = self.nome_completo_var.get().strip()
        tipo_acesso = self.tipo_acesso_var.get()
        nova_senha = self.senha_var.get()                                  

                           
        if not login or not nome or not tipo_acesso:
            messagebox.showwarning("Validação", "Login, Nome Completo e Perfil de Acesso são obrigatórios.", parent=self)
            return

        try:
                                                    
            if self.selected_item_login:
                                                   
                update_values = {
                    'nome_completo': nome,
                    'tipo_acesso': tipo_acesso
                }
                                                                  
                if nova_senha:
                                               
                    hashed_pw = hash_password(nova_senha)
                    update_values['senha_criptografada'] = hashed_pw

                                                                 
                where_conditions = {'login_usuario': self.selected_item_login}
                                     
                GenericRepository.update_table("usuarios", update_values, where_conditions)
                messagebox.showinfo("Sucesso", f"Usuário '{login}' atualizado com sucesso!", parent=self)

                                                
            else:
                                                         
                if not nova_senha:
                    messagebox.showwarning("Validação", "A Senha é obrigatória para novos usuários.", parent=self)
                    return

                                      
                hashed_pw = hash_password(nova_senha)
                                                
                df_data = pd.DataFrame([{
                    'login_usuario': login,
                    'senha_criptografada': hashed_pw,
                    'nome_completo': nome,
                    'tipo_acesso': tipo_acesso
                }])
                                     
                GenericRepository.write_dataframe_to_table(df_data, "usuarios")
                messagebox.showinfo("Sucesso", f"Usuário '{login}' criado com sucesso!", parent=self)

                                                        
            self._load_data_into_table()                     

        except Exception as e:
                                                                                    
            if "UNIQUE constraint failed" in str(e) or "Duplicate entry" in str(e) or "unique constraint" in str(e):
                 messagebox.showerror("Erro de Inserção", f"O login '{login}' já existe. Escolha outro.", parent=self)
            else:
                                                 
                messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o usuário: {e}", parent=self)

    def _on_delete_button_click(self):
        """ (DELETE) Chamado ao clicar no botão 'Excluir'. """
        if not self.selected_item_login:
            messagebox.showwarning("Atenção", "Selecione um usuário da tabela para excluir.", parent=self)
            return

                     
        if messagebox.askyesno("Confirmar Exclusão",
                               f"Tem certeza que deseja excluir o usuário '{self.selected_item_login}'?\nEsta ação não pode ser desfeita.",
                               icon='warning', parent=self):
            try:
                                        
                where_conditions = {'login_usuario': self.selected_item_login}
                                     
                GenericRepository.delete_from_table("usuarios", where_conditions)
                messagebox.showinfo("Sucesso", f"Usuário '{self.selected_item_login}' excluído com sucesso!", parent=self)
                                    
                self._load_data_into_table()
            except Exception as e:
                messagebox.showerror("Erro de Exclusão", f"Não foi possível excluir o usuário: {e}", parent=self)