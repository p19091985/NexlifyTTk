import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import config

from panels.base_panel import BasePanel
from persistencia.repository import GenericRepository
# from persistencia.data_service import DataService # REMOVIDO
from modals.tipos_vegetais_manager import TiposVegetaisManagerDialog


# Não precisamos mais importar a View, pois ela está nesta classe.


class PainelCadastroVegetais(BasePanel):
    """
    Controller e View unificados para a tela de cadastro de vegetais.
    Este painel herda de BasePanel e constrói seus próprios widgets.
    """
    PANEL_NAME = "Cadastro de Vegetais"
    PANEL_ICON = "🥕"
    ALLOWED_ACCESS = ['Administrador Global', 'Diretor de Operações', 'Gerente de TI', 'Analista de Dados']

    def __init__(self, parent, app_controller, **kwargs):
        # Variáveis de estado (da lógica do Controller)
        self.selected_item_id = None
        self.nome_var = tk.StringVar()
        self.tipo_var = tk.StringVar()

        # Widgets da View (serão criados em 'create_widgets')
        self.nome_entry = None
        self.tipo_combobox = None
        self.tree = None

        # Chama o __init__ do BasePanel, que por sua vez chama create_widgets()
        super().__init__(parent, app_controller, **kwargs)

    # --------------------------------------------------------------------
    # 1. CRIAÇÃO DE WIDGETS (Lógica que era da View)
    # --------------------------------------------------------------------

    def create_widgets(self):
        """
        Método principal que constrói a UI do painel.
        Substitui a necessidade de um arquivo de View separado.
        """
        if not config.DATABASE_ENABLED:
            ttk.Label(self, text="Funcionalidade indisponível: o banco de dados está desabilitado.",
                      font=("-size", 12, "-weight", "bold")).pack(pady=50)
            return

        # Estrutura principal (do __init__ da View)
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)

        form_frame = ttk.LabelFrame(main_frame, text=" 🥕 Cadastro de Vegetal ", padding=15)
        form_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 15))
        self._create_form_widgets(form_frame)  # Método da View, agora local

        table_frame = ttk.LabelFrame(main_frame, text=" 🍽️ Vegetais Cadastrados ", padding=15)
        table_frame.grid(row=1, column=0, sticky="nsew")
        self._create_table_widgets(table_frame)  # Método da View, agora local

        # Carrega os dados iniciais (da lógica do Controller)
        self._carregar_dados()
        self._carregar_tipos_vegetais()

    def _create_form_widgets(self, parent):
        """Cria o formulário de cadastro (copiado da View)"""
        parent.columnconfigure(1, weight=1)

        ttk.Label(parent, text="Nome do Vegetal:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        # Referência direta: self.nome_entry (não self.view.nome_entry)
        # Variável direta: self.nome_var (não self.controller.nome_var)
        self.nome_entry = ttk.Entry(parent, textvariable=self.nome_var)
        self.nome_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(parent, text="Tipo:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        tipo_frame = ttk.Frame(parent)
        tipo_frame.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        self.tipo_combobox = ttk.Combobox(tipo_frame, textvariable=self.tipo_var, state="readonly")
        self.tipo_combobox.pack(side="left", fill="x", expand=True)

        # Comando direto: self.open_tipos_modal (não self.controller.open_tipos_modal)
        ttk.Button(tipo_frame, text="Gerenciar Tipos...", command=self.open_tipos_modal, width=15).pack(
            side="left", padx=(5, 0))

        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=2, column=1, pady=(10, 0), sticky="e")

        # Comandos diretos: self.save_item, self.delete_item, self.clear_form
        ttk.Button(btn_frame, text="Salvar", command=self.save_item, style="Success.TButton").pack(
            side="left", padx=5)
        ttk.Button(btn_frame, text="Excluir", command=self.delete_item, style="Danger.TButton").pack(
            side="left", padx=5)
        ttk.Button(btn_frame, text="Limpar", command=self.clear_form, style="Secondary.TButton").pack(
            side="left")

    def _create_table_widgets(self, parent):
        """Cria a tabela de dados (copiado da View)"""
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)

        columns = ('id', 'nome', 'tipo')
        # Referência direta: self.tree
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

        # Evento direto: self.on_item_select
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)

    # --------------------------------------------------------------------
    # 2. LÓGICA DE EVENTOS (Métodos que eram do Controller)
    # --------------------------------------------------------------------

    def _carregar_dados(self):
        """Carrega a lista de vegetais já cadastrados na Treeview."""
        try:
            # Referência direta: self.tree
            for item in self.tree.get_children():
                self.tree.delete(item)

            df_vegetais = GenericRepository.read_vegetais_com_tipo()
            if not df_vegetais.empty:
                for _, row in df_vegetais.iterrows():
                    self.tree.insert("", "end", values=list(row))
        except Exception as e:
            messagebox.showerror("Erro de Carga", f"Não foi possível carregar a lista de vegetais.\n{e}", parent=self)

    def _carregar_tipos_vegetais(self):
        """Carrega ou recarrega os tipos de vegetais no Combobox."""
        try:
            df_tipos = GenericRepository.read_table_to_dataframe("tipos_vegetais")
            tipos_lista = sorted(df_tipos['nome'].tolist()) if not df_tipos.empty else []
            # Referência direta: self.tipo_combobox
            self.tipo_combobox['values'] = tipos_lista
        except Exception as e:
            messagebox.showerror("Erro de Carga", f"Não foi possível recarregar os tipos de vegetais.\n{e}",
                                 parent=self)

    def open_tipos_modal(self):
        """Abre a janela modal para gerenciar os tipos."""
        dialog = TiposVegetaisManagerDialog(self, on_close_callback=self._carregar_tipos_vegetais)
        dialog.wait_window()

    def save_item(self):
        """Salva um registro novo (CREATE) ou existente (UPDATE)."""
        nome = self.nome_var.get().strip()
        tipo_nome = self.tipo_var.get()
        if not nome or not tipo_nome:
            messagebox.showerror("Erro de Validação", "Os campos 'Nome' e 'Tipo' são obrigatórios.", parent=self)
            return

        try:
            df_tipo = GenericRepository.read_table_to_dataframe("tipos_vegetais", where_conditions={'nome': tipo_nome})
            if df_tipo.empty:
                messagebox.showerror("Erro de Dados", f"O tipo '{tipo_nome}' não foi encontrado.", parent=self)
                return

            id_tipo = int(df_tipo.iloc[0]['id'])
            data = {'nome': nome, 'id_tipo': id_tipo}

            if self.selected_item_id is None:
                GenericRepository.write_dataframe_to_table(pd.DataFrame([data]), "vegetais")
                messagebox.showinfo("Sucesso", "Vegetal cadastrado!", parent=self)
            else:
                GenericRepository.update_table("vegetais", data, {'id': self.selected_item_id})
                messagebox.showinfo("Sucesso", "Vegetal atualizado!", parent=self)

            self.clear_form()
            self._carregar_dados()
        except Exception as e:
            messagebox.showerror("Erro de Banco de Dados", f"Não foi possível salvar o registro.\n{e}", parent=self)

    def delete_item(self):
        """Exclui o registro selecionado."""
        if self.selected_item_id is None:
            messagebox.showwarning("Atenção", "Selecione um vegetal na tabela para excluir.", parent=self)
            return

        if messagebox.askyesno("Confirmar Exclusão", "Deseja realmente excluir este vegetal?", icon='warning',
                               parent=self):
            try:
                GenericRepository.delete_from_table("vegetais", {'id': self.selected_item_id})
                messagebox.showinfo("Sucesso", "Vegetal excluído!", parent=self)
                self.clear_form()
                self._carregar_dados()
            except Exception as e:
                messagebox.showerror("Erro de Banco de Dados", f"Não foi possível excluir o registro.\n{e}",
                                     parent=self)

    def clear_form(self):
        """Limpa o formulário e a seleção."""
        self.selected_item_id = None
        self.nome_var.set("")
        self.tipo_var.set("")
        # Referências diretas: self.tree e self.nome_entry
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])
        self.nome_entry.focus()

    def on_item_select(self, event=None):
        """Preenche o formulário quando um item é selecionado na tabela."""
        # Referência direta: self.tree
        selected_items = self.tree.selection()
        if not selected_items: return

        item = self.tree.item(selected_items[0])
        values = item['values']

        self.selected_item_id = values[0]
        self.nome_var.set(values[1])
        self.tipo_var.set(values[2])