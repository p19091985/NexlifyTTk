import tkinter as tk
from tkinter import ttk

class GestaoUsuariosView(ttk.Frame):
    """A View para a gestão de usuários."""

    def __init__(self, parent, controller, perfis_acesso):
        super().__init__(parent)
        self.controller = controller
        self.perfis_acesso = perfis_acesso                           

        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)
        main_frame.rowconfigure(1, weight=1)                        
        main_frame.columnconfigure(0, weight=1)                        

                                                               
        top_container = ttk.Frame(main_frame)
        top_container.grid(row=0, column=0, sticky="nsew", pady=(0, 15))
        top_container.columnconfigure(0, weight=1)                       
        top_container.columnconfigure(1, minsize=180)                                       

        form_frame = ttk.LabelFrame(top_container, text=" 📝 Dados do Usuário ", padding=15)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._create_form_widgets(form_frame)

        crud_buttons_frame = ttk.Frame(top_container, padding=(10,0))                            
        crud_buttons_frame.grid(row=0, column=1, sticky="nsew")
        self._create_crud_buttons(crud_buttons_frame)

                                             
        table_frame = ttk.LabelFrame(main_frame, text=" 👥 Usuários Cadastrados ", padding=15)
        table_frame.grid(row=1, column=0, sticky="nsew")
        self._create_table(table_frame)

    def _create_form_widgets(self, parent):
        """Cria os widgets dentro do LabelFrame do formulário."""
        parent.columnconfigure(1, weight=1)                            

               
        ttk.Label(parent, text="Login:").grid(row=0, column=0, sticky="w", pady=3, padx=5)
        self.login_entry = ttk.Entry(parent, textvariable=self.controller.login_var)
        self.login_entry.grid(row=0, column=1, sticky="ew", pady=3, padx=5)
                            
                                                                                              

                       
        ttk.Label(parent, text="Nome Completo:").grid(row=1, column=0, sticky="w", pady=3, padx=5)
        self.nome_entry = ttk.Entry(parent, textvariable=self.controller.nome_completo_var)
        self.nome_entry.grid(row=1, column=1, sticky="ew", pady=3, padx=5)

                                     
        ttk.Label(parent, text="Perfil de Acesso:").grid(row=2, column=0, sticky="w", pady=3, padx=5)
        self.tipo_acesso_combo = ttk.Combobox(parent, textvariable=self.controller.tipo_acesso_var,
                                              values=self.perfis_acesso, state="readonly")
        self.tipo_acesso_combo.grid(row=2, column=1, sticky="ew", pady=3, padx=5)
        if self.perfis_acesso:                                          
             self.tipo_acesso_combo.current(0)


               
        ttk.Label(parent, text="Senha:").grid(row=3, column=0, sticky="w", pady=3, padx=5)
        self.senha_entry = ttk.Entry(parent, textvariable=self.controller.senha_var, show="*")
        self.senha_entry.grid(row=3, column=1, sticky="ew", pady=3, padx=5)
                            
                                                                          

    def _create_crud_buttons(self, parent):
        """Cria os botões de ação CRUD."""
                                                            
        parent.rowconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        parent.rowconfigure(2, weight=1)
        parent.columnconfigure(0, weight=1)                                   

                                      
        save_btn = ttk.Button(parent, text="Salvar", command=self.controller.salvar_usuario, style="Success.TButton")
        save_btn.grid(row=0, column=0, sticky="nsew", padx=2, pady=3, ipady=4)

                                
        delete_btn = ttk.Button(parent, text="Excluir", command=self.controller.excluir_usuario, style="Danger.TButton")
        delete_btn.grid(row=1, column=0, sticky="nsew", padx=2, pady=3, ipady=4)

                                 
        clear_btn = ttk.Button(parent, text="Limpar", command=self.controller.limpar_form, style="Secondary.TButton")
        clear_btn.grid(row=2, column=0, sticky="nsew", padx=2, pady=3, ipady=4)

    def _create_table(self, parent):
        """Cria a Treeview para exibir os usuários."""
        parent.rowconfigure(0, weight=1)                          
        parent.columnconfigure(0, weight=1)                          

                                                              
        columns = ('login_usuario', 'nome_completo', 'tipo_acesso')
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', selectmode='browse')

                              
        self.tree.heading('login_usuario', text='Login')
        self.tree.heading('nome_completo', text='Nome Completo')
        self.tree.heading('tipo_acesso', text='Perfil de Acesso')

                                                       
        self.tree.column('login_usuario', width=120, anchor='w')
        self.tree.column('nome_completo', width=250, anchor='w')
        self.tree.column('tipo_acesso', width=150, anchor='w')

                                     
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

                                           
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

                                                            
        self.tree.bind("<<TreeviewSelect>>", self.controller.on_item_select)