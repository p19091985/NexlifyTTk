# panels/painelGestaoLinguagens.py
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from .base_panel import BasePanel
from persistencia.repository import GenericRepository
from persistencia.data_service import DataService

class PainelGestaoLinguagens(BasePanel):
    """
    Painel para o gerenciamento completo (CRUD) de linguagens de programação.
    Demonstra como lidar com formulários, tabelas e chaves estrangeiras (tipos de linguagem).
    """
    PANEL_NAME = "Gestão de Linguagens"
    PANEL_ICON = "📚"
    ALLOWED_ACCESS = ['Administrador Global', 'Diretor de Operações', 'Gerente de TI', 'Analista de Dados']

    def __init__(self, parent, app_controller, **kwargs):
        self.selected_item_id = None
        self.nome_var = tk.StringVar()
        self.ano_var = tk.IntVar(value=2000)
        self.tipo_var = tk.StringVar()
        self.categoria_var = tk.StringVar()
        super().__init__(parent, app_controller, **kwargs)

    def create_widgets(self):
        """Constrói a interface gráfica do painel, dividida em seções."""
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)

        form_frame = ttk.LabelFrame(main_frame, text=" Cadastro de Linguagem ", padding=15)
        form_frame.pack(fill="x", pady=(0, 10))
        self._create_form_widgets(form_frame)

        table_frame = ttk.LabelFrame(main_frame, text=" Linguagens Cadastradas ", padding=15)
        table_frame.pack(fill="both", expand=True)
        self._create_table_widgets(table_frame)

        legacy_actions_frame = ttk.LabelFrame(main_frame, text=" Ações Atômicas ", padding=10)
        legacy_actions_frame.pack(fill="x", pady=(15, 0))
        self._create_legacy_action_buttons(legacy_actions_frame)

        self._carregar_e_inserir_dados()
        self._carregar_tipos_linguagem()

    def _create_form_widgets(self, parent):
        """Cria os campos de entrada e botões do formulário."""
        parent.columnconfigure(1, weight=1);
        parent.columnconfigure(4, weight=1)

        ttk.Label(parent, text="Nome:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.nome_entry = ttk.Entry(parent, textvariable=self.nome_var, width=40)
        self.nome_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        ttk.Label(parent, text="Ano de Criação:").grid(row=0, column=3, sticky="w", padx=15, pady=5)
        ttk.Spinbox(parent, from_=1950, to=2025, textvariable=self.ano_var, width=8).grid(row=0, column=4, sticky="w",
                                                                                          padx=5, pady=5)

        ttk.Label(parent, text="Tipagem:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        tipo_frame = ttk.Frame(parent)
        tipo_frame.grid(row=1, column=1, columnspan=2, sticky="ew")
        self.tipo_combobox = ttk.Combobox(tipo_frame, textvariable=self.tipo_var, state="readonly")
        self.tipo_combobox.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ttk.Button(tipo_frame, text="➕", command=self._open_tipos_modal, style="primary.Outline.TButton", width=3).pack(
            side="left", padx=(0, 5), pady=5)

        ttk.Label(parent, text="Categoria:").grid(row=1, column=3, sticky="w", padx=15, pady=5)
        ttk.Entry(parent, textvariable=self.categoria_var).grid(row=1, column=4, sticky="ew", padx=5, pady=5)

        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=2, column=0, columnspan=5, pady=10, sticky="e")
        ttk.Button(btn_frame, text="Salvar", command=self._save_item, style="success.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Excluir", command=self._delete_item, style="danger.TButton").pack(side="left",
                                                                                                      padx=5)
        ttk.Button(btn_frame, text="Limpar", command=self._clear_form, style="secondary.TButton").pack(side="left",
                                                                                                       padx=5)

    def _create_table_widgets(self, parent):
        """Cria a tabela (Treeview) para exibir as linguagens."""
        inner_frame = ttk.Frame(parent)
        inner_frame.pack(fill="both", expand=True)
        columns = ('id', 'nome', 'tipo', 'ano_criacao', 'categoria')
        self.tree = ttk.Treeview(inner_frame, columns=columns, show='headings', selectmode='browse')

        headings = {'id': 'ID', 'nome': 'Linguagem', 'tipo': 'Tipagem', 'ano_criacao': 'Ano', 'categoria': 'Categoria'}
        for col, text in headings.items(): self.tree.heading(col, text=text)

        col_widths = {'id': 50, 'nome': 200, 'tipo': 120, 'ano_criacao': 80, 'categoria': 200}
        for col, width in col_widths.items(): self.tree.column(col, width=width,
                                                               anchor='center' if col != 'nome' else 'w')

        scrollbar = ttk.Scrollbar(inner_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self.tree.bind('<<TreeviewSelect>>', self._on_item_select)

    def _create_legacy_action_buttons(self, parent):
        """Cria o botão que dispara a transação de exemplo."""
        ttk.Button(parent, text="Reclassificar C++ para 'Legado' (Exemplo Atômico)",
                   command=self._executar_reclassificacao, style="info.Outline.TButton").pack(side="left", padx=5,
                                                                                              pady=5)

    def _open_tipos_modal(self):
        """
        Delega a abertura da janela modal para a aplicação principal.
        Isso mantém o painel desacoplado da implementação do modal.
        """
        self.app._open_tipos_linguagem_modal()

    def _carregar_tipos_linguagem(self):
        """
        Busca os tipos de linguagem do banco e popula o Combobox.
        Este método serve como o CALLBACK para a janela modal.
        """
        try:
            df_tipos = GenericRepository.read_table_to_dataframe("tipos_linguagem")
            self.tipo_combobox['values'] = sorted(df_tipos['nome'].tolist()) if not df_tipos.empty else []
        except Exception as e:
            messagebox.showerror("Erro de Carga", f"Não foi possível recarregar os tipos de linguagem.\n{e}",
                                 parent=self)

    def _save_item(self):
        """Salva um novo item ou atualiza um existente no banco de dados."""
        nome = self.nome_var.get().strip()
        tipo_nome = self.tipo_var.get()
        if not nome or not tipo_nome:
            messagebox.showerror("Erro de Validação", "Os campos 'Nome' e 'Tipagem' são obrigatórios.", parent=self)
            return
        try:
            df_tipo = GenericRepository.read_table_to_dataframe("tipos_linguagem", where_conditions={'nome': tipo_nome})
            if df_tipo.empty:
                messagebox.showerror("Erro de Dados", f"O tipo '{tipo_nome}' não foi encontrado.", parent=self)
                return
            id_tipo = int(df_tipo.iloc[0]['id'])

            data = {'nome': nome, 'id_tipo': id_tipo, 'ano_criacao': self.ano_var.get(),
                    'categoria': self.categoria_var.get().strip()}

            if self.selected_item_id is None:
                GenericRepository.write_dataframe_to_table(pd.DataFrame([data]), "linguagens_programacao")
                messagebox.showinfo("Sucesso", "Linguagem cadastrada!", parent=self)
            else:
                GenericRepository.update_table("linguagens_programacao", data, {'id': self.selected_item_id})
                messagebox.showinfo("Sucesso", "Linguagem atualizada!", parent=self)

            self._clear_form()
            self._carregar_e_inserir_dados()
        except Exception as e:
            messagebox.showerror("Erro de Banco de Dados", f"Não foi possível salvar o registro.\n{e}", parent=self)

    def _delete_item(self):
        """Exclui o item selecionado da tabela."""
        if self.selected_item_id is None:
            messagebox.showwarning("Atenção", "Selecione um item para excluir.", parent=self)
            return
        if messagebox.askyesno("Confirmar Exclusão", "Deseja realmente excluir esta linguagem?", icon='warning',
                               parent=self):
            try:
                GenericRepository.delete_from_table("linguagens_programacao", {'id': self.selected_item_id})
                messagebox.showinfo("Sucesso", "Linguagem excluída!", parent=self)
                self._clear_form()
                self._carregar_e_inserir_dados()
            except Exception as e:
                messagebox.showerror("Erro de Banco de Dados", f"Não foi possível excluir o registro.\n{e}",
                                     parent=self)

    def _clear_form(self):
        """Limpa o formulário e a seleção da tabela."""
        self.selected_item_id = None
        self.nome_var.set("");
        self.tipo_var.set("");
        self.ano_var.set(2000);
        self.categoria_var.set("")
        if self.tree.selection(): self.tree.selection_remove(self.tree.selection()[0])
        self.nome_entry.focus()

    def _on_item_select(self, event=None):
        """Preenche o formulário quando um item é selecionado na tabela."""
        selected_items = self.tree.selection()
        if not selected_items: return
        item = self.tree.item(selected_items[0])
        values = item['values']
        self.selected_item_id = values[0]
        self.nome_var.set(values[1])
        self.tipo_var.set(values[2])
        self.ano_var.set(int(values[3]))
        self.categoria_var.set(values[4])

    def _carregar_e_inserir_dados(self):
        """Busca os dados do banco e os exibe na tabela (Treeview)."""
        try:
            for item in self.tree.get_children(): self.tree.delete(item)
            df_linguagens = GenericRepository.read_linguagens_com_tipo()
            if not df_linguagens.empty:
                for _, row in df_linguagens.iterrows():
                    self.tree.insert("", "end", values=list(row))
        except Exception as e:
            messagebox.showerror("Erro de Carga", f"Não foi possível carregar a lista de linguagens.\n{e}", parent=self)

    def _executar_reclassificacao(self):
        """Chama a camada de serviço para executar uma operação transacional."""
        usuario_logado = self.app.get_current_user()['username']
        sucesso, mensagem = DataService.reclassificar_e_logar("C++", "Linguagens Legado", usuario_logado)
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem, parent=self)
            self._carregar_e_inserir_dados()
        else:
            messagebox.showerror("Falha na Transação", mensagem, parent=self)
