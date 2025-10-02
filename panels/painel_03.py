# painel_03.py
import tkinter as tk
from tkinter import ttk
import pandas as pd
import io
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from persistencia.base_panel import BasePanel
import config

class PainelDashboard(BasePanel):
    PANEL_NAME = "Dashboard de Alunos"
    PANEL_ICON = "📈"
    ALLOWED_ACCESS = [
        'Administrador Global', 'Diretor de Operações',
        'Supervisor de Produção', 'Analista de Dados'
    ]

    def create_widgets(self):
        self._carregar_dados()

        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(filter_frame, text="Selecione um aluno:", font=config.FONTS["default"]).pack(side="left", padx=(0, 10))

        self.student_var = tk.StringVar()
        student_combobox = ttk.Combobox(filter_frame, textvariable=self.student_var, state="readonly", width=30)
        student_combobox['values'] = list(self.dados['Aluno'].unique())
        student_combobox.pack(side="left")
        student_combobox.bind("<<ComboboxSelected>>", self._atualizar_dashboard)

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        table_frame = ttk.LabelFrame(content_frame, text=" Boletim Detalhado ", padding=10)
        table_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self._criar_tabela(table_frame)

        chart_frame = ttk.LabelFrame(content_frame, text=" Desempenho por Disciplina ", padding=10)
        chart_frame.pack(side="right", fill="both", expand=True)
        self._criar_grafico(chart_frame)

        if student_combobox['values']:
            self.student_var.set(student_combobox['values'][0])
            self._atualizar_dashboard()

    def _get_synthetic_dataset_string(self):
        # Adicionado mais dados para um exemplo mais rico
        return """Aluno,Série,Turma,Disciplina,N1,F1,N2,F2,N3,F3,N4,F4
Ana Silva,3,A,PORTUGUÊS,8,1,7,1,9,0,8,1
Ana Silva,3,A,MATEMÁTICA,5,2,4,2,6,3,5,2
Ana Silva,3,A,HISTÓRIA,9,0,9,0,8,1,10,0
Ana Silva,3,A,BIOLOGIA,7,1,8,0,7,1,8,0
Bruno Costa,3,A,PORTUGUÊS,6,1,7,2,5,1,6,1
Bruno Costa,3,A,MATEMÁTICA,7,0,8,1,7,0,8,0
Bruno Costa,3,A,HISTÓRIA,5,2,6,3,4,2,5,3
Bruno Costa,3,A,BIOLOGIA,9,0,8,0,9,0,10,0
"""

    def _carregar_dados(self):
        csv_string = self._get_synthetic_dataset_string()
        self.dados = pd.read_csv(io.StringIO(csv_string))
        notas_cols, faltas_cols = ['N1', 'N2', 'N3', 'N4'], ['F1', 'F2', 'F3', 'F4']
        self.dados['Média'] = self.dados[notas_cols].mean(axis=1).round(1)
        total_faltas = self.dados[faltas_cols].sum(axis=1)
        self.dados['% Freq Total'] = (100 - (total_faltas * 5)).astype(str) + '%'
        self.dados['Situação'] = self.dados.apply(
            lambda r: "Aprovado" if r['Média'] >= 6 and (100 - (self.dados.loc[r.name, faltas_cols].sum() * 5)) >= 75 else "Reprovado",
            axis=1
        )

    def _criar_tabela(self, parent):
        self.tree = ttk.Treeview(parent, style="Treeview")
        cols = ('Disciplina', 'N1', 'F1', 'N2', 'F2', 'N3', 'F3', 'N4', 'F4', 'Média', '% Freq Total', 'Situação')
        self.tree['columns'] = cols
        self.tree.column("#0", width=0, stretch=tk.NO)
        for col in cols:
            self.tree.column(col, anchor="center", width=80)
            self.tree.heading(col, text=col, anchor="center")
        self.tree.column("Disciplina", anchor="w", width=120)
        self.tree.tag_configure('aprovado', foreground='green')
        self.tree.tag_configure('reprovado', foreground='red')
        self.tree.pack(fill="both", expand=True)

    def _criar_grafico(self, parent):
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _atualizar_dashboard(self, event=None):
        aluno = self.student_var.get()
        dados_aluno = self.dados[self.dados['Aluno'] == aluno].copy()

        self.tree.delete(*self.tree.get_children())
        cols_para_mostrar = ['Disciplina', 'N1', 'F1', 'N2', 'F2', 'N3', 'F3', 'N4', 'F4', 'Média', '% Freq Total', 'Situação']
        for _, row in dados_aluno.iterrows():
            self.tree.insert("", "end", values=list(row[cols_para_mostrar]), tags=(row['Situação'].lower(),))

        self.ax.clear()
        cores = ['#28a745' if sit == 'Aprovado' else '#dc3545' for sit in dados_aluno['Situação']]
        self.ax.barh(dados_aluno['Disciplina'], dados_aluno['Média'], color=cores)
        self.ax.set_title(f"Média Final - {aluno}")
        self.ax.set_xlabel("Média")
        self.ax.set_xlim(0, 10)
        self.ax.grid(axis='x', linestyle='--', alpha=0.7)
        self.fig.tight_layout()
        self.canvas.draw()