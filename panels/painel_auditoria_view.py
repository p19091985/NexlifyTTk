# panels/painel_auditoria_view.py
import tkinter as tk
from tkinter import ttk


class AuditoriaView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)

        action_frame = ttk.LabelFrame(main_frame, text=" Executar Transação Atômica ", padding=15)
        action_frame.pack(fill="x", pady=(0, 10))
        self._create_action_widgets(action_frame)

        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill="both", expand=True)

        linguagens_frame = ttk.LabelFrame(paned_window, text=" Tabela 'linguagens_programacao' ", padding=10)
        paned_window.add(linguagens_frame, weight=2)
        self._create_linguagens_table(linguagens_frame)

        log_frame = ttk.LabelFrame(paned_window, text=" Tabela 'log_alteracoes' (Trilha de Auditoria) ", padding=10)
        paned_window.add(log_frame, weight=3)
        self._create_log_table(log_frame)

    def _create_action_widgets(self, parent):
        parent.columnconfigure(1, weight=1)
        ttk.Label(parent, text="Linguagem a Reclassificar:").grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.linguagem_combo = ttk.Combobox(parent, textvariable=self.controller.linguagem_selecionada_var,
                                            state="readonly")
        self.linguagem_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.linguagem_combo.bind("<<ComboboxSelected>>", lambda e: self.exec_button.config(state="normal"))

        ttk.Label(parent, text="Nova Categoria:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(parent, textvariable=self.controller.nova_categoria_var).grid(row=1, column=1, sticky="ew", padx=5,
                                                                                pady=5)

        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=0, column=2, rowspan=2, sticky="ns", padx=(20, 0))

        self.exec_button = ttk.Button(btn_frame, text="Executar\nTransação",
                                      command=self.controller._executar_transacao, style="Success.TButton",
                                      state="disabled")
        self.exec_button.pack(fill="both", expand=True)

        ttk.Button(btn_frame, text="🔄 Atualizar Dados", command=self.controller._carregar_dados_iniciais,
                   style="Info.TButton").pack(fill="x", pady=(5, 0))

    def _create_linguagens_table(self, parent):
        columns = ('id', 'nome', 'categoria')
        self.linguagens_tree = ttk.Treeview(parent, columns=columns, show='headings', selectmode='browse')
        self.linguagens_tree.heading('id', text='ID')
        self.linguagens_tree.heading('nome', text='Linguagem')
        self.linguagens_tree.heading('categoria', text='Categoria Atual')
        self.linguagens_tree.column('id', width=50, anchor='center')
        self.linguagens_tree.column('nome', width=150)
        self.linguagens_tree.column('categoria', width=200)
        self.linguagens_tree.pack(fill="both", expand=True)

    def _create_log_table(self, parent):
        columns = ('id', 'timestamp', 'login_usuario', 'acao')
        self.log_tree = ttk.Treeview(parent, columns=columns, show='headings', selectmode='browse')
        self.log_tree.heading('id', text='ID')
        self.log_tree.heading('timestamp', text='Data e Hora')
        self.log_tree.heading('login_usuario', text='Usuário')
        self.log_tree.heading('acao', text='Ação Realizada')
        self.log_tree.column('id', width=50, anchor='center')
        self.log_tree.column('timestamp', width=160)
        self.log_tree.column('login_usuario', width=100)
        self.log_tree.column('acao', width=350)
        self.log_tree.pack(fill="both", expand=True)