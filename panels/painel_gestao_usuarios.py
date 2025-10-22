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
    Controller e View unificados para a gestão de usuários.
    Este painel herda de BasePanel e constrói seus próprios widgets.
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
        Método principal que constrói a UI do painel.
        Substitui a necessidade de um arquivo de View separado.
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

        form_frame = ttk.LabelFrame(top_container, text=" 📝 Dados do Usuário ", padding=15)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._create_form_widgets(form_frame)                              

        crud_buttons_frame = ttk.Frame(top_container, padding=(10,0))
        crud_buttons_frame.grid(row=0, column=1, sticky="nsew")
        self._create_crud_buttons(crud_buttons_frame)                              

        table_frame = ttk.LabelFrame(main_frame, text=" 👥 Usuários Cadastrados ", padding=15)
        table_frame.grid(row=1, column=0, sticky="nsew")
        self._create_table(table_frame)                              

                                                             
        self.carregar_dados()

    def _create_form_widgets(self, parent):
        """Cria os widgets dentro do LabelFrame do formulário (copiado da View)."""
        parent.columnconfigure(1, weight=1)

        ttk.Label(parent, text="Login:").grid(row=0, column=0, sticky="w", pady=3, padx=5)
                                             
                                                                         
        self.login_entry = ttk.Entry(parent, textvariable=self.login_var)
        self.login_entry.grid(row=0, column=1, sticky="ew", pady=3, padx=5)

        ttk.Label(parent, text="Nome Completo:").grid(row=1, column=0, sticky="w", pady=3, padx=5)
        self.nome_entry = ttk.Entry(parent, textvariable=self.nome_completo_var)
        self.nome_entry.grid(row=1, column=1, sticky="ew", pady=3, padx=5)

        ttk.Label(parent, text="Perfil de Acesso:").grid(row=2, column=0, sticky="w", pady=3, padx=5)
                                                      
        self.tipo_acesso_combo = ttk.Combobox(parent, textvariable=self.tipo_acesso_var,
                                              values=PERFIS_DE_ACESSO, state="readonly")
        self.tipo_acesso_combo.grid(row=2, column=1, sticky="ew", pady=3, padx=5)
        if PERFIS_DE_ACESSO:
             self.tipo_acesso_combo.current(0)

        ttk.Label(parent, text="Senha:").grid(row=3, column=0, sticky="w", pady=3, padx=5)
        self.senha_entry = ttk.Entry(parent, textvariable=self.senha_var, show="*")
        self.senha_entry.grid(row=3, column=1, sticky="ew", pady=3, padx=5)

    def _create_crud_buttons(self, parent):
        """Cria os botões de ação CRUD (copiado da View)."""
        parent.rowconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        parent.rowconfigure(2, weight=1)
        parent.columnconfigure(0, weight=1)

                                                                           
        save_btn = ttk.Button(parent, text="Salvar", command=self.salvar_usuario, style="Success.TButton")
        save_btn.grid(row=0, column=0, sticky="nsew", padx=2, pady=3, ipady=4)

        delete_btn = ttk.Button(parent, text="Excluir", command=self.excluir_usuario, style="Danger.TButton")
        delete_btn.grid(row=1, column=0, sticky="nsew", padx=2, pady=3, ipady=4)

        clear_btn = ttk.Button(parent, text="Limpar", command=self.limpar_form, style="Secondary.TButton")
        clear_btn.grid(row=2, column=0, sticky="nsew", padx=2, pady=3, ipady=4)

    def _create_table(self, parent):
        """Cria a Treeview para exibir os usuários (copiado da View)."""
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

                                            
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)

                                                                          
                                                           
                                                                          

    def carregar_dados(self):
        """(READ) Busca os usuários e instrui a View a exibi-los."""
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
            self.limpar_form()
        except Exception as e:
            messagebox.showerror("Erro de Leitura", f"Não foi possível carregar os usuários: {e}", parent=self)

    def on_item_select(self, event=None):
        """Atualiza o formulário quando um usuário é selecionado na Treeview."""
                                      
        selected_items = self.tree.selection()
        if not selected_items:
            self.limpar_form()
            return

        item_values = self.tree.item(selected_items[0], "values")

        self.selected_item_login = item_values[0]
        self.login_var.set(item_values[0])
        self.nome_completo_var.set(item_values[1])
        self.tipo_acesso_var.set(item_values[2])
        self.senha_var.set("")

                                                                  
        self.login_entry.config(state='disabled')
        self.senha_entry.focus()

    def limpar_form(self):
        """Limpa as variáveis de estado, o formulário e a seleção na Treeview."""
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

    def salvar_usuario(self):
        """(CREATE/UPDATE) Valida e salva/atualiza um usuário."""
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

            self.carregar_dados()

        except Exception as e:
            if "UNIQUE constraint failed" in str(e) or "Duplicate entry" in str(e) or "unique constraint" in str(e):
                 messagebox.showerror("Erro de Inserção", f"O login '{login}' já existe. Escolha outro.", parent=self)
            else:
                messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o usuário: {e}", parent=self)


    def excluir_usuario(self):
        """(DELETE) Exclui o usuário selecionado."""
        if not self.selected_item_login:
            messagebox.showwarning("Atenção", "Selecione um usuário da tabela para excluir.", parent=self)
            return

        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o usuário '{self.selected_item_login}'?\nEsta ação não pode ser desfeita.", icon='warning', parent=self):
            try:
                where_conditions = {'login_usuario': self.selected_item_login}
                GenericRepository.delete_from_table("usuarios", where_conditions)
                messagebox.showinfo("Sucesso", f"Usuário '{self.selected_item_login}' excluído com sucesso!", parent=self)
                self.carregar_dados()
            except Exception as e:
                messagebox.showerror("Erro de Exclusão", f"Não foi possível excluir o usuário: {e}", parent=self)