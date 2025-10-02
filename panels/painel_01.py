# painel_01.py
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from persistencia.base_panel import BasePanel
from persistencia.repository import GenericRepository
from persistencia.data_service import DataService


class PainelVisualizacaoDados(BasePanel):
    PANEL_NAME = "Gestão de Linguagens"
    PANEL_ICON = "⚙️"
    ALLOWED_ACCESS = [
        'Administrador Global', 'Diretor de Operações', 'Gerente de TI', 'Analista de Dados'
    ]

    def __init__(self, parent, app_controller, **kwargs):
        super().__init__(parent, app_controller, **kwargs)
        self.selected_item_id = None

    def create_widgets(self):
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
        self._carregar_tipos_linguagem()  # Carrega os tipos no ComboBox

    def _create_form_widgets(self, parent):
        ttk.Label(parent, text="Nome:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.nome_var = tk.StringVar()
        self.nome_entry = ttk.Entry(parent, textvariable=self.nome_var, width=40)
        self.nome_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # --- MODIFICAÇÃO AQUI ---
        ttk.Label(parent, text="Tipagem:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.tipo_var = tk.StringVar()
        self.tipo_combobox = ttk.Combobox(parent, textvariable=self.tipo_var, state="readonly")
        self.tipo_combobox.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(parent, text="Ano de Criação:").grid(row=0, column=2, sticky="w", padx=15, pady=5)
        self.ano_var = tk.IntVar()
        self.ano_spinbox = ttk.Spinbox(parent, from_=1950, to=2025, textvariable=self.ano_var, width=8)
        self.ano_spinbox.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        self.ano_var.set(2000)

        ttk.Label(parent, text="Categoria:").grid(row=1, column=2, sticky="w", padx=15, pady=5)
        self.categoria_var = tk.StringVar()
        self.categoria_entry = ttk.Entry(parent, textvariable=self.categoria_var)
        self.categoria_entry.grid(row=1, column=3, sticky="ew", padx=5, pady=5)

        parent.columnconfigure(1, weight=1)
        parent.columnconfigure(3, weight=1)

        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10, sticky="e")
        self.save_button = ttk.Button(btn_frame, text="Salvar", command=self._save_item, style="Accent.TButton")
        self.save_button.pack(side="left", padx=5)
        self.delete_button = ttk.Button(btn_frame, text="Excluir", command=self._delete_item)
        self.delete_button.pack(side="left", padx=5)
        self.clear_button = ttk.Button(btn_frame, text="Limpar Formulário", command=self._clear_form)
        self.clear_button.pack(side="left", padx=5)

    def _create_table_widgets(self, parent):
        style = ttk.Style()
        style.configure("Treeview", rowheight=25, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))
        style.map('Treeview', background=[('selected', '#0078D7')], foreground=[('selected', 'white')])
        inner_frame = ttk.Frame(parent)
        inner_frame.pack(fill="both", expand=True)
        columns = ('id', 'nome', 'tipo', 'ano_criacao', 'categoria')
        self.tree = ttk.Treeview(inner_frame, columns=columns, show='headings', selectmode='browse')
        self.tree.heading('id', text='ID');
        self.tree.heading('nome', text='Linguagem')
        self.tree.heading('tipo', text='Tipagem');
        self.tree.heading('ano_criacao', text='Ano')
        self.tree.heading('categoria', text='Categoria')
        self.tree.column('id', width=50, anchor='center');
        self.tree.column('nome', width=200, anchor='w')
        self.tree.column('tipo', width=120, anchor='center');
        self.tree.column('ano_criacao', width=80, anchor='center')
        self.tree.column('categoria', width=200, anchor='w')
        scrollbar = ttk.Scrollbar(inner_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self.tree.bind('<<TreeviewSelect>>', self._on_item_select)

    def _create_legacy_action_buttons(self, parent):
        reclassify_btn = ttk.Button(parent, text="Reclassificar C++ para 'Legado' (Exemplo Atômico)",
                                    command=self._executar_reclassificacao)
        reclassify_btn.pack(side="left", padx=5, pady=5)

    def _carregar_tipos_linguagem(self):
        """NOVO: Carrega os tipos da tabela e popula o ComboBox."""
        try:
            df_tipos = GenericRepository.read_table_to_dataframe("tipos_linguagem")
            if not df_tipos.empty:
                # Ordena alfabeticamente para uma melhor UX
                self.tipo_combobox['values'] = sorted(df_tipos['nome'].tolist())
        except Exception as e:
            messagebox.showerror("Erro de Carga", f"Não foi possível carregar os tipos de linguagem: {e}", parent=self)
            self.tipo_combobox['values'] = []

    def _save_item(self):
        nome = self.nome_var.get().strip()
        if not nome or not self.tipo_var.get():
            messagebox.showerror("Erro de Validação", "Os campos 'Nome' e 'Tipagem' são obrigatórios.", parent=self)
            return
        data = {'nome': nome, 'tipo': self.tipo_var.get(), 'ano_criacao': self.ano_var.get(),
                'categoria': self.categoria_var.get().strip()}
        try:
            if self.selected_item_id is None:
                df = pd.DataFrame([data]);
                GenericRepository.write_dataframe_to_table(df, "linguagens_programacao")
                messagebox.showinfo("Sucesso", "Linguagem cadastrada!", parent=self)
            else:
                GenericRepository.update_table("linguagens_programacao", data, {'id': self.selected_item_id})
                messagebox.showinfo("Sucesso", "Linguagem atualizada!", parent=self)
            self._clear_form();
            self._carregar_e_inserir_dados()
        except Exception as e:
            messagebox.showerror("Erro no Banco", f"Ocorreu um erro ao salvar: {e}", parent=self)

    def _delete_item(self):
        if self.selected_item_id is None:
            messagebox.showwarning("Atenção", "Selecione um item para excluir.", parent=self)
            return
        if messagebox.askyesno("Confirmar", "Deseja excluir esta linguagem?", icon='warning', parent=self):
            try:
                GenericRepository.delete_from_table("linguagens_programacao", {'id': self.selected_item_id})
                messagebox.showinfo("Sucesso", "Linguagem excluída!", parent=self)
                self._clear_form();
                self._carregar_e_inserir_dados()
            except Exception as e:
                messagebox.showerror("Erro no Banco", f"Ocorreu um erro ao excluir: {e}", parent=self)

    def _clear_form(self):
        self.selected_item_id = None;
        self.nome_var.set("");
        self.tipo_var.set("")
        self.ano_var.set(2000);
        self.categoria_var.set("")
        self.tree.selection_set('');
        self.nome_entry.focus()

    def _on_item_select(self, event=None):
        selected_items = self.tree.selection()
        if not selected_items: return
        item = self.tree.item(selected_items[0]);
        values = item['values']
        self.selected_item_id = values[0];
        self.nome_var.set(values[1])
        self.tipo_var.set(values[2]);
        self.ano_var.set(int(values[3]));
        self.categoria_var.set(values[4])

    def _carregar_e_inserir_dados(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        df_linguagens = GenericRepository.read_table_to_dataframe("linguagens_programacao")
        if not df_linguagens.empty:
            for _, row in df_linguagens.iterrows(): self.tree.insert("", "end", values=list(row))

    def _executar_reclassificacao(self):
        usuario_logado = self.app.get_current_user()['username']
        sucesso, mensagem = DataService.reclassificar_e_logar("C++", "Linguagens Legado", usuario_logado)
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem, parent=self);
            self._carregar_e_inserir_dados()
        else:
            messagebox.showerror("Falha na Transação", mensagem, parent=self)
