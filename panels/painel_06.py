# painel_01.py (CORRIGIDO)
import tkinter as tk
from tkinter import ttk
from persistencia.base_panel import BasePanel
import config  # <--- IMPORTAÇÃO ADICIONADA

class PainelVisualizacaoDados(BasePanel):
    PANEL_NAME = "Visualização de Dados"
    PANEL_ICON = "📊"
    ALLOWED_ACCESS = [
        'Administrador Global',
        'Diretor de Operações',
        'Gerente de TI',
        'Analista de Dados'
    ]

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        # --- LINHA CORRIGIDA ---
        # Usando a fonte do config para garantir consistência e evitar o TypeError
        title_font = config.FONTS["section_title"]
        title_label = ttk.Label(main_frame, text="Widget Treeview com Estilo", font=title_font)
        title_label.pack(pady=(0, 20))

        # --- Treeview ---
        style = ttk.Style()
        style.configure("Treeview", rowheight=25, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))
        style.map('Treeview', background=[('selected', '#0078D7')], foreground=[('selected', 'white')])

        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(tree_frame, selectmode='browse')
        self.tree.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree['columns'] = ('Linguagem', 'Tipo', 'Ano de Criação')

        self.tree.column("#0", width=200, minwidth=150)
        self.tree.column("Linguagem", anchor=tk.W, width=150)
        self.tree.column("Tipo", anchor=tk.CENTER, width=120)
        self.tree.column("Ano de Criação", anchor=tk.E, width=100)

        self.tree.heading("#0", text="Categoria", anchor=tk.W)
        self.tree.heading("Linguagem", text="Linguagem", anchor=tk.W)
        self.tree.heading("Tipo", text="Tipagem", anchor=tk.CENTER)
        self.tree.heading("Ano de Criação", text="Ano", anchor=tk.E)

        self.tree.tag_configure('oddrow', background='#f0f0f0')
        self.tree.tag_configure('evenrow', background='white')

        self._inserir_dados()

    def _inserir_dados(self):
        dados = {
            "Linguagens Compiladas": [("C++", "Estática", 1985), ("Java", "Estática", 1995), ("Rust", "Estática", 2010), ("Go", "Estática", 2009), ("C#", "Estática", 2000)],
            "Linguagens Interpretadas": [("Python", "Dinâmica", 1991), ("JavaScript", "Dinâmica", 1995), ("Ruby", "Dinâmica", 1995), ("PHP", "Dinâmica", 1995)]
        }
        count = 0
        for categoria, linguagens in dados.items():
            parent = self.tree.insert("", "end", text=categoria, open=True)
            for lang_data in linguagens:
                tag = 'evenrow' if count % 2 == 0 else 'oddrow'
                self.tree.insert(parent, "end", text=lang_data[0], values=lang_data, tags=(tag,))
                count += 1