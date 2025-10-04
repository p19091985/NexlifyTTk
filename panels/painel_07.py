# panels/painel_07.py
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from .base_panel import BasePanel
from persistencia.repository import GenericRepository
from persistencia.data_service import DataService


class PainelTransacoes(BasePanel):
    PANEL_NAME = "Auditoria e Transações"
    PANEL_ICON = "⛓️"
    ALLOWED_ACCESS = ['Administrador Global', 'Gerente de TI']

    def __init__(self, parent, app_controller, **kwargs):
        self.linguagem_selecionada_var = tk.StringVar()
        self.nova_categoria_var = tk.StringVar()
        super().__init__(parent, app_controller, **kwargs)

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)
        action_frame = ttk.LabelFrame(main_frame, text=" Executar Transação Atómica ", padding=15)
        action_frame.pack(fill="x", pady=(0, 10))
        self._create_action_widgets(action_frame)
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill="both", expand=True)
        linguagens_frame = ttk.LabelFrame(paned_window, text=" Tabela 'linguagens_programacao' ", padding=10)
        paned_window.add(linguagens_frame, weight=2)
        self._create_linguagens_table(linguagens_frame)
        log_frame = ttk.LabelFrame(paned_window, text=" Tabela 'log_alteracoes' ", padding=10)
        paned_window.add(log_frame, weight=3)
        self._create_log_table(log_frame)
        self._carregar_dados_iniciais()

    def _create_action_widgets(self, parent):
        parent.columnconfigure(1, weight=1)
        ttk.Label(parent, text="Linguagem a Reclassificar:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.linguagem_combo = ttk.Combobox(parent, textvariable=self.linguagem_selecionada_var, state="readonly")
        self.linguagem_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.linguagem_combo.bind("<<ComboboxSelected>>", lambda e: self.exec_button.config(state="normal"))
        ttk.Label(parent, text="Nova Categoria:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.categoria_entry = ttk.Entry(parent, textvariable=self.nova_categoria_var)
        self.categoria_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=0, column=2, rowspan=2, sticky="e", padx=(20, 0))
        self.exec_button = ttk.Button(btn_frame, text="Executar Transação", command=self._executar_transacao,
                                      style="success.TButton", state="disabled")
        self.exec_button.pack(fill="x", ipady=5)
        refresh_button = ttk.Button(btn_frame, text="🔄 Atualizar Dados", command=self._carregar_dados_iniciais,
                                    style="info.Outline.TButton")
        refresh_button.pack(fill="x", pady=(5, 0))

    def _create_linguagens_table(self, parent):
        columns = ('id', 'nome', 'categoria')
        self.linguagens_tree = ttk.Treeview(parent, columns=columns, show='headings', selectmode='browse')
        self.linguagens_tree.heading('id', text='ID');
        self.linguagens_tree.heading('nome', text='Linguagem');
        self.linguagens_tree.heading('categoria', text='Categoria Atual')
        self.linguagens_tree.column('id', width=50, anchor='center');
        self.linguagens_tree.column('nome', width=150);
        self.linguagens_tree.column('categoria', width=200)
        self.linguagens_tree.pack(fill="both", expand=True)

    def _create_log_table(self, parent):
        # --- MODIFICAÇÃO: 'usuario' -> 'login_usuario' ---
        columns = ('id', 'timestamp', 'login_usuario', 'acao')
        self.log_tree = ttk.Treeview(parent, columns=columns, show='headings', selectmode='browse')

        self.log_tree.heading('id', text='ID')
        self.log_tree.heading('timestamp', text='Data e Hora')
        self.log_tree.heading('login_usuario', text='Usuário')  # <-- Alterado aqui
        self.log_tree.heading('acao', text='Ação Realizada')

        self.log_tree.column('id', width=50, anchor='center')
        self.log_tree.column('timestamp', width=160)
        self.log_tree.column('login_usuario', width=100)  # <-- E aqui
        self.log_tree.column('acao', width=350)

        self.log_tree.pack(fill="both", expand=True)

    def _carregar_dados_iniciais(self):
        self._carregar_linguagens()
        self._carregar_log()

    def _carregar_linguagens(self):
        try:
            for item in self.linguagens_tree.get_children(): self.linguagens_tree.delete(item)
            df = GenericRepository.read_table_to_dataframe("linguagens_programacao",
                                                           columns=['id', 'nome', 'categoria'])
            if not df.empty:
                for _, row in df.iterrows(): self.linguagens_tree.insert("", "end", values=list(row))
                self.linguagem_combo['values'] = sorted(df['nome'].tolist())
            else:
                self.linguagem_combo['values'] = []
        except Exception as e:
            messagebox.showerror("Erro de Carga", f"Não foi possível carregar as linguagens.\nDetalhe: {e}",
                                 parent=self)

    def _carregar_log(self):
        try:
            for item in self.log_tree.get_children(): self.log_tree.delete(item)
            # A leitura genérica já vai trazer a coluna com o nome novo
            df = GenericRepository.read_table_to_dataframe("log_alteracoes")
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df_sorted = df.sort_values(by='timestamp', ascending=False)
                for _, row in df_sorted.iterrows():
                    row['timestamp'] = row['timestamp'].strftime('%d/%m/%Y %H:%M:%S')
                    self.log_tree.insert("", "end", values=list(row))
        except Exception as e:
            if "no such table: log_alteracoes" not in str(e).lower():
                messagebox.showerror("Erro de Carga", f"Não foi possível carregar o log de alterações.\nDetalhe: {e}",
                                     parent=self)

    def _executar_transacao(self):
        linguagem = self.linguagem_selecionada_var.get()
        categoria = self.nova_categoria_var.get().strip()
        if not linguagem or not categoria:
            messagebox.showwarning("Dados Incompletos",
                                   "Por favor, selecione uma linguagem e informe a nova categoria.", parent=self)
            return
        usuario_logado = self.app.get_current_user()['username']
        if not messagebox.askyesno("Confirmar Transação",
                                   f"Tem a certeza que deseja reclassificar '{linguagem}' para a categoria '{categoria}'?\n\nEsta ação será auditada.",
                                   icon='warning', parent=self):
            return
        sucesso, mensagem = DataService.reclassificar_e_logar(linguagem, categoria, usuario_logado)
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem, parent=self)
            self.nova_categoria_var.set("");
            self.linguagem_selecionada_var.set("");
            self.exec_button.config(state="disabled")
            self._carregar_dados_iniciais()
        else:
            messagebox.showerror("Falha na Transação", mensagem, parent=self)