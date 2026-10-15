import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import config
from panels.base_panel import BasePanel
from persistencia.repository import GenericRepository
from persistencia.auth import prepare_user_password
from dialogs.mfa_dialog import ensure_recent_auth
from .painel_gestao_usuarios_view import GestaoUsuariosView

from persistencia.schema import ROLES

PERFIS_DE_ACESSO = list(ROLES)

class PainelGestaoUsuariosController(BasePanel):
    """Controller para a gestão de usuários."""
    PANEL_NAME = "Gestão de Usuários"
    PANEL_ICON = "👤"


    def __init__(self, parent, app_controller, **kwargs):
        self.selected_item_login = None

        self.login_var = tk.StringVar()
        self.nome_completo_var = tk.StringVar()
        self.tipo_acesso_var = tk.StringVar()
        self.senha_var = tk.StringVar()

        super().__init__(parent, app_controller, **kwargs)

    def create_widgets(self):
        """Cria a View e carrega os dados iniciais."""
        if not config.DATABASE_ENABLED:
            ttk.Label(self, text="Funcionalidade indisponível: o banco de dados está desabilitado.",
                       font=("-size", 12, "-weight", "bold")).pack(pady=50)
            return

        self.view = GestaoUsuariosView(self, controller=self, perfis_acesso=PERFIS_DE_ACESSO)
        self.view.pack(fill="both", expand=True)
        self.carregar_dados()

    def carregar_dados(self):
        """(READ) Busca os usuários e instrui a View a exibi-los."""
        try:

            for item in self.view.tree.get_children():
                self.view.tree.delete(item)

            df_users = GenericRepository.read_table_to_dataframe("usuarios")

            if 'senha_criptografada' in df_users.columns:
                df_users = df_users.drop(columns=['senha_criptografada'])

            if not df_users.empty:

                for _, row in df_users.iterrows():

                    self.view.tree.insert("", "end", values=(
                        row['login_usuario'],
                        row['nome_completo'],
                        row['tipo_acesso']
                    ))
            self.limpar_form()
        except Exception as e:
            messagebox.showerror("Erro de Leitura", f"Não foi possível carregar os usuários: {e}", parent=self)

    def on_item_select(self, event=None):
        """Atualiza o formulário quando um usuário é selecionado na Treeview."""
        selected_items = self.view.tree.selection()
        if not selected_items:
            self.limpar_form()
            return

        item_values = self.view.tree.item(selected_items[0], "values")

        self.selected_item_login = item_values[0]
        self.login_var.set(item_values[0])
        self.nome_completo_var.set(item_values[1])
        self.tipo_acesso_var.set(item_values[2])
        self.senha_var.set("")

        self.view.login_entry.config(state='disabled')
        self.view.senha_entry.focus()

    def limpar_form(self):
        """Limpa as variáveis de estado, o formulário e a seleção na Treeview."""
        self.selected_item_login = None
        self.login_var.set("")
        self.nome_completo_var.set("")
        self.tipo_acesso_var.set("")
        self.senha_var.set("")

        self.view.login_entry.config(state='normal')

        if self.view.tree.selection():
            self.view.tree.selection_remove(self.view.tree.selection()[0])

        self.view.login_entry.focus()

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
            if not ensure_recent_auth(self):
                return
            if self.selected_item_login:
                update_values = {
                    'nome_completo': nome,
                    'tipo_acesso': tipo_acesso
                }

                if nova_senha:
                    update_values.update(prepare_user_password(nova_senha))

                where_conditions = {'login_usuario': self.selected_item_login}
                GenericRepository.update_table("usuarios", update_values, where_conditions)
                messagebox.showinfo("Sucesso", f"Usuário '{login}' atualizado com sucesso!", parent=self)

            else:
                if not nova_senha:
                    messagebox.showwarning("Validação", "A Senha é obrigatória para novos usuários.", parent=self)
                    return

                password_values = prepare_user_password(nova_senha)
                df_data = pd.DataFrame([{
                    'login_usuario': login,
                    **password_values,
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
                if not ensure_recent_auth(self):
                    return
                where_conditions = {'login_usuario': self.selected_item_login}
                GenericRepository.delete_from_table("usuarios", where_conditions)
                messagebox.showinfo("Sucesso", f"Usuário '{self.selected_item_login}' excluído com sucesso!", parent=self)
                self.carregar_dados()
            except Exception as e:
                messagebox.showerror("Erro de Exclusão", f"Não foi possível excluir o usuário: {e}", parent=self)
