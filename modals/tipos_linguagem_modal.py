# modals/tipos_linguagem_modal.py
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import ttkbootstrap as bstrap
from persistencia.repository import GenericRepository

class TiposLinguagemModal(bstrap.Toplevel):
    """
    Janela modals para gerenciar os Tipos de Linguagem.
    """
    def __init__(self, parent, on_close_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.on_close_callback = on_close_callback
        self.selected_item_id = None

        self.title("Gerenciar Tipos de Linguagem")
        self.geometry("600x450")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        self._create_widgets()
        self._carregar_dados()
        self._center_window()
        self.nome_entry.focus_set()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)

        form_frame = ttk.LabelFrame(main_frame, text=" Cadastro de Tipo ", padding=15)
        form_frame.pack(side="left", fill="y", padx=(0, 10))
        self._create_form_widgets(form_frame)

        table_frame = ttk.LabelFrame(main_frame, text=" Tipos Cadastrados ", padding=15)
        table_frame.pack(side="right", fill="both", expand=True)
        self._create_table_widgets(table_frame)

    def _create_form_widgets(self, parent):
        ttk.Label(parent, text="Nome do Tipo:").pack(anchor="w")
        self.nome_var = tk.StringVar()
        self.nome_entry = ttk.Entry(parent, textvariable=self.nome_var, width=30)
        self.nome_entry.pack(anchor="w", pady=(5, 15))

        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill="x")

        self.save_button = ttk.Button(btn_frame, text="Salvar", command=self._save_item, style="success.TButton")
        self.save_button.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.delete_button = ttk.Button(btn_frame, text="Excluir", command=self._delete_item, style="danger.TButton")
        self.delete_button.pack(side="left", expand=True, fill="x")

        ttk.Button(parent, text="Limpar Formulário", command=self._clear_form, style="secondary.TButton").pack(fill="x", pady=(10, 0))

    def _create_table_widgets(self, parent):
        inner_frame = ttk.Frame(parent)
        inner_frame.pack(fill="both", expand=True)
        columns = ('id', 'nome')
        self.tree = ttk.Treeview(inner_frame, columns=columns, show='headings', selectmode='browse')
        self.tree.heading('id', text='ID'); self.tree.heading('nome', text='Nome')
        self.tree.column('id', width=50, anchor='center'); self.tree.column('nome', width=200)
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
            if self.on_close_callback: self.on_close_callback()
        except Exception:
            messagebox.showerror("Erro de Banco de Dados", "Não foi possível salvar.\nO nome do tipo já pode existir ou ocorreu uma falha.", parent=self)

    def _delete_item(self):
        if self.selected_item_id is None:
            messagebox.showwarning("Atenção", "Selecione um item para excluir.", parent=self)
            return
        if messagebox.askyesno("Confirmar", f"Deseja excluir o tipo ID {self.selected_item_id}?", icon='warning', parent=self):
            try:
                GenericRepository.delete_from_table("tipos_linguagem", {'id': self.selected_item_id})
                self._clear_form()
                self._carregar_dados()
                if self.on_close_callback: self.on_close_callback()
            except Exception:
                messagebox.showerror("Erro de Banco de Dados", "Não foi possível excluir.\nEle pode estar em uso por uma linguagem.", parent=self)

    def _clear_form(self):
        self.selected_item_id = None
        self.nome_var.set("")
        self.tree.selection_set('')
        self.nome_entry.focus()

    def _on_item_select(self, event=None):
        selected_items = self.tree.selection()
        if not selected_items: return
        item = self.tree.item(selected_items[0])
        self.selected_item_id = item['values'][0]
        self.nome_var.set(item['values'][1])

    def _carregar_dados(self):
        try:
            for item in self.tree.get_children(): self.tree.delete(item)
            df_tipos = GenericRepository.read_table_to_dataframe("tipos_linguagem")
            if not df_tipos.empty:
                for _, row in df_tipos.iterrows(): self.tree.insert("", "end", values=list(row))
        except Exception:
            messagebox.showerror("Erro de Carga", "Não foi possível carregar a lista de tipos.", parent=self)

    def _center_window(self):
        self.update_idletasks()
        p_w, p_h = self.parent.winfo_width(), self.parent.winfo_height()
        p_x, p_y = self.parent.winfo_x(), self.parent.winfo_y()
        w, h = self.winfo_width(), self.winfo_height()
        x = p_x + (p_w // 2) - (w // 2)
        y = p_y + (p_h // 2) - (h // 2)
        self.geometry(f"+{x}+{y}")