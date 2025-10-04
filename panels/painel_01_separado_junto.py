# panels/painel_01_separado_junto.py
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from .base_panel import BasePanel
from persistencia.repository import GenericRepository
from persistencia.data_service import DataService


# --- CLASSE DA VIEW (INTERFACE) ---
# Nenhuma alteração necessária aqui
class PainelLinguagensView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)
        form_frame = ttk.LabelFrame(main_frame, text=" Cadastro de Linguagem ", padding=15)
        form_frame.pack(fill="x", pady=(0, 10))
        table_frame = ttk.LabelFrame(main_frame, text=" Linguagens Cadastradas ", padding=15)
        table_frame.pack(fill="both", expand=True)
        legacy_actions_frame = ttk.LabelFrame(main_frame, text=" Ações Atômicas ", padding=10)
        legacy_actions_frame.pack(fill="x", pady=(15, 0))
        self._create_form_widgets(form_frame)
        self._create_table_widgets(table_frame)
        self._create_legacy_action_buttons(legacy_actions_frame)

    def _create_form_widgets(self, parent):
        ttk.Label(parent, text="Nome:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.nome_entry = ttk.Entry(parent, textvariable=self.controller.nome_var, width=40)
        self.nome_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        ttk.Label(parent, text="Ano de Criação:").grid(row=0, column=3, sticky="w", padx=15, pady=5)
        self.ano_spinbox = ttk.Spinbox(parent, from_=1950, to=2025, textvariable=self.controller.ano_var, width=8)
        self.ano_spinbox.grid(row=0, column=4, sticky="w", padx=5, pady=5)
        ttk.Label(parent, text="Tipagem:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        tipo_frame = ttk.Frame(parent)
        tipo_frame.grid(row=1, column=1, columnspan=2, sticky="ew")
        self.tipo_combobox = ttk.Combobox(tipo_frame, textvariable=self.controller.tipo_var, state="readonly")
        self.tipo_combobox.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.add_tipo_button = ttk.Button(tipo_frame, text="➕", command=self.controller._open_tipos_modal,
                                          style="primary.Outline.TButton", width=3)
        self.add_tipo_button.pack(side="left", padx=(0, 5), pady=5)
        ttk.Label(parent, text="Categoria:").grid(row=1, column=3, sticky="w", padx=15, pady=5)
        self.categoria_entry = ttk.Entry(parent, textvariable=self.controller.categoria_var)
        self.categoria_entry.grid(row=1, column=4, sticky="ew", padx=5, pady=5)
        parent.columnconfigure(1, weight=1);
        parent.columnconfigure(4, weight=1)
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=2, column=0, columnspan=5, pady=10, sticky="e")
        self.save_button = ttk.Button(btn_frame, text="Salvar", command=self.controller._save_item,
                                      style="success.TButton")
        self.save_button.pack(side="left", padx=5)
        self.delete_button = ttk.Button(btn_frame, text="Excluir", command=self.controller._delete_item,
                                        style="danger.TButton")
        self.delete_button.pack(side="left", padx=5)
        self.clear_button = ttk.Button(btn_frame, text="Limpar", command=self.controller._clear_form,
                                       style="secondary.TButton")
        self.clear_button.pack(side="left", padx=5)

    def _create_table_widgets(self, parent):
        inner_frame = ttk.Frame(parent);
        inner_frame.pack(fill="both", expand=True)
        columns = ('id', 'nome', 'tipo', 'ano_criacao', 'categoria')
        self.tree = ttk.Treeview(inner_frame, columns=columns, show='headings', selectmode='browse')
        headings = {'id': 'ID', 'nome': 'Linguagem', 'tipo': 'Tipagem', 'ano_criacao': 'Ano', 'categoria': 'Categoria'}
        for col, text in headings.items(): self.tree.heading(col, text=text)
        column_configs = {'id': (50, 'center'), 'nome': (200, 'w'), 'tipo': (120, 'center'),
                          'ano_criacao': (80, 'center'), 'categoria': (200, 'w')}
        for col, (width, anchor) in column_configs.items(): self.tree.column(col, width=width, anchor=anchor)
        scrollbar = ttk.Scrollbar(inner_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True);
        scrollbar.pack(side='right', fill='y')
        self.tree.bind('<<TreeviewSelect>>', self.controller._on_item_select)

    def _create_legacy_action_buttons(self, parent):
        reclassify_btn = ttk.Button(parent, text="Reclassificar C++ para 'Legado' (Exemplo Atômico)",
                                    command=self.controller._executar_reclassificacao, style="info.Outline.TButton")
        reclassify_btn.pack(side="left", padx=5, pady=5)


# --- CLASSE DO CONTROLADOR (LÓGICA) ---
class PainelVisualizacaoDadosSeparadoJunto(BasePanel):
    PANEL_NAME = "Gestão - Separado 1 Arquivo"
    PANEL_ICON = "📑"  # Ícone alterado para diferenciar
    ALLOWED_ACCESS = ['Administrador Global', 'Diretor de Operações', 'Gerente de TI', 'Analista de Dados']

    def __init__(self, parent, app_controller, **kwargs):
        self.selected_item_id = None
        self.nome_var = tk.StringVar()
        self.ano_var = tk.IntVar(value=2000)
        self.tipo_var = tk.StringVar()
        self.categoria_var = tk.StringVar()
        super().__init__(parent, app_controller, **kwargs)

    def create_widgets(self):
        self.view = PainelLinguagensView(self, controller=self)
        self.view.pack(fill="both", expand=True)
        self._carregar_e_inserir_dados()
        self._carregar_tipos_linguagem()

    def _open_tipos_modal(self):
        self.app._open_tipos_linguagem_modal()

    def _carregar_tipos_linguagem(self):
        try:
            valor_selecionado = self.tipo_var.get()
            df_tipos = GenericRepository.read_table_to_dataframe("tipos_linguagem")
            novos_valores = sorted(df_tipos['nome'].tolist()) if not df_tipos.empty else []
            self.view.tipo_combobox['values'] = novos_valores
            if valor_selecionado in novos_valores:
                self.tipo_var.set(valor_selecionado)
            elif self.tipo_var.get() not in novos_valores:
                self.tipo_var.set('')
        except Exception as e:
            messagebox.showerror("Erro de Carga", f"Não foi possível recarregar os tipos de linguagem.\nDetalhe: {e}",
                                 parent=self)
            self.view.tipo_combobox['values'] = []

    # --- MÉTODO MODIFICADO ---
    def _save_item(self):
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
            messagebox.showerror("Erro de Banco de Dados", f"Não foi possível salvar o registro.\nDetalhe: {e}",
                                 parent=self)

    def _delete_item(self):
        if self.selected_item_id is None:
            messagebox.showwarning("Atenção", "Selecione um item para excluir.", parent=self)
            return
        if messagebox.askyesno("Confirmar", "Deseja excluir esta linguagem?", icon='warning', parent=self):
            try:
                GenericRepository.delete_from_table("linguagens_programacao", {'id': self.selected_item_id})
                messagebox.showinfo("Sucesso", "Linguagem excluída!", parent=self)
                self._clear_form()
                self._carregar_e_inserir_dados()
            except Exception as e:
                messagebox.showerror("Erro de Banco de Dados", f"Não foi possível excluir o registro.\nDetalhe: {e}",
                                     parent=self)

    def _clear_form(self):
        self.selected_item_id = None
        self.nome_var.set("");
        self.tipo_var.set("");
        self.ano_var.set(2000);
        self.categoria_var.set("")
        if self.view.tree.selection(): self.view.tree.selection_remove(self.view.tree.selection()[0])
        self.view.nome_entry.focus()

    def _on_item_select(self, event=None):
        selected_items = self.view.tree.selection()
        if not selected_items: return
        item = self.view.tree.item(selected_items[0])
        values = item['values']
        self.selected_item_id = values[0];
        self.nome_var.set(values[1]);
        self.tipo_var.set(values[2])
        self.ano_var.set(int(values[3]));
        self.categoria_var.set(values[4])

    # --- MÉTODO MODIFICADO ---
    def _carregar_e_inserir_dados(self):
        try:
            for item in self.view.tree.get_children(): self.view.tree.delete(item)
            df_linguagens = GenericRepository.read_linguagens_com_tipo()  # <-- USA O NOVO MÉTODO
            if not df_linguagens.empty:
                for _, row in df_linguagens.iterrows(): self.view.tree.insert("", "end", values=list(row))
        except Exception as e:
            messagebox.showerror("Erro de Carga", f"Não foi possível carregar a lista de linguagens.\nDetalhe: {e}",
                                 parent=self)

    def _executar_reclassificacao(self):
        usuario_logado = self.app.get_current_user()['username']
        sucesso, mensagem = DataService.reclassificar_e_logar("C++", "Linguagens Legado", usuario_logado)
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem, parent=self)
            self._carregar_e_inserir_dados()
        else:
            messagebox.showerror("Falha na Transação", mensagem, parent=self)