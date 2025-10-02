# panels/painel_02.py
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from persistencia.base_panel import BasePanel
from persistencia.repository import GenericRepository


class PainelTiposLinguagem(BasePanel):
    PANEL_NAME = "Tipos de Linguagem"
    PANEL_ICON = "🏷️"
    ALLOWED_ACCESS = ['Administrador Global', 'Gerente de TI']

    def __init__(self, parent, app_controller, **kwargs):
        super().__init__(parent, app_controller, **kwargs)
        self.selected_item_id = None

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)

        # --- Frame do Formulário (Esquerda) ---
        form_frame = ttk.LabelFrame(main_frame, text=" Cadastro de Tipo ", padding=15)
        form_frame.pack(side="left", fill="y", padx=(0, 10))
        self._create_form_widgets(form_frame)

        # --- Frame da Tabela (Direita) ---
        table_frame = ttk.LabelFrame(main_frame, text=" Tipos Cadastrados ", padding=15)
        table_frame.pack(side="right", fill="both", expand=True)
        self._create_table_widgets(table_frame)

        self._carregar_dados()

    def _create_form_widgets(self, parent):
        ttk.Label(parent, text="Nome do Tipo:").pack(anchor="w")
        self.nome_var = tk.StringVar()
        self.nome_entry = ttk.Entry(parent, textvariable=self.nome_var, width=30)
        self.nome_entry.pack(anchor="w", pady=(5, 15))
        self.nome_entry.focus()

        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill="x")

        self.save_button = ttk.Button(btn_frame, text="Salvar", command=self._save_item, style="Accent.TButton")
        self.save_button.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.delete_button = ttk.Button(btn_frame, text="Excluir", command=self._delete_item)
        self.delete_button.pack(side="left", expand=True, fill="x")

        ttk.Button(parent, text="Limpar Formulário", command=self._clear_form).pack(fill="x", pady=(10, 0))

    def _create_table_widgets(self, parent):
        inner_frame = ttk.Frame(parent)
        inner_frame.pack(fill="both", expand=True)

        columns = ('id', 'nome')
        self.tree = ttk.Treeview(inner_frame, columns=columns, show='headings', selectmode='browse')
        self.tree.heading('id', text='ID')
        self.tree.heading('nome', text='Nome')
        self.tree.column('id', width=50, anchor='center')
        self.tree.column('nome', width=200)

        scrollbar = ttk.Scrollbar(inner_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.tree.bind('<<TreeviewSelect>>', self._on_item_select)

    def _save_item(self):
        nome = self.nome_var.get().strip()
        if not nome:
            messagebox.showerror("Erro de Validação", "O campo 'Nome' é obrigatório.", parent=self)
            return

        try:
            if self.selected_item_id is None:
                df = pd.DataFrame([{'nome': nome}])
                GenericRepository.write_dataframe_to_table(df, "tipos_linguagem")
                messagebox.showinfo("Sucesso", "Tipo cadastrado!", parent=self)
            else:
                GenericRepository.update_table("tipos_linguagem", {'nome': nome}, {'id': self.selected_item_id})
                messagebox.showinfo("Sucesso", "Tipo atualizado!", parent=self)

            self._clear_form()
            self._carregar_dados()
        except Exception as e:
            messagebox.showerror("Erro no Banco", f"Não foi possível salvar. O tipo já pode existir.\nDetalhe: {e}",
                                 parent=self)

    def _delete_item(self):
        if self.selected_item_id is None:
            messagebox.showwarning("Atenção", "Selecione um item na tabela para excluir.", parent=self)
            return

        if messagebox.askyesno("Confirmar", f"Deseja excluir o tipo ID {self.selected_item_id}?", icon='warning',
                               parent=self):
            try:
                GenericRepository.delete_from_table("tipos_linguagem", {'id': self.selected_item_id})
                self._clear_form()
                self._carregar_dados()
            except Exception as e:
                messagebox.showerror("Erro no Banco", f"Não foi possível excluir.\nDetalhe: {e}", parent=self)

    def _clear_form(self):
        self.selected_item_id = None
        self.nome_var.set("")
        self.tree.selection_set('')
        self.nome_entry.focus()

    def _on_item_select(self, event=None):
        selected_items = self.tree.selection()
        if not selected_items: return

        item = self.tree.item(selected_items[0])
        values = item['values']
        self.selected_item_id = values[0]
        self.nome_var.set(values[1])

    def _carregar_dados(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        df_tipos = GenericRepository.read_table_to_dataframe("tipos_linguagem")
        if not df_tipos.empty:
            for _, row in df_tipos.iterrows():
                self.tree.insert("", "end", values=list(row))
