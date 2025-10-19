import tkinter as tk
from tkinter import ttk, messagebox

class TiposVegetaisView(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Gerenciar Tipos de Vegetais")
        self.geometry("600x450")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        self.controller = None

        self._create_widgets()

                                    
                                                                            
                                                                
                                                             
        self.update_idletasks()
                                 

        self._center_window()
        self.nome_entry.focus_set()

    def set_controller(self, controller):
        self.controller = controller
        self.save_button.config(command=self.controller.save_item)
        self.delete_button.config(command=self.controller.delete_item)
        self.clear_button.config(command=self.controller.clear_form)
        self.tree.bind('<<TreeviewSelect>>', self.controller.on_item_select)

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)

        form_frame = ttk.LabelFrame(main_frame, text=" Cadastro de Tipo de Vegetal ", padding=15)
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

        self.save_button = ttk.Button(btn_frame, text="Salvar", style="Success.TButton")
        self.save_button.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.delete_button = ttk.Button(btn_frame, text="Excluir", style="Danger.TButton")
        self.delete_button.pack(side="left", expand=True, fill="x")

        self.clear_button = ttk.Button(parent, text="Limpar Formulário", style="Secondary.TButton")
        self.clear_button.pack(fill="x", pady=(10, 0))

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

    def populate_treeview(self, data):
        for item in self.tree.get_children():
            self.tree.delete(item)
        if not data.empty:
            for _, row in data.iterrows():
                self.tree.insert("", "end", values=list(row))

    def get_form_data(self):
        return {'nome': self.nome_var.get().strip()}

    def get_selected_item_id(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return None
        item = self.tree.item(selected_items[0])
        return item['values'][0]

    def set_form_data(self, data):
        self.nome_var.set(data.get('nome', ''))

    def clear_form_fields(self):
        self.nome_var.set("")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])
        self.nome_entry.focus()

    def get_selected_item_data(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return None
        item = self.tree.item(selected_items[0])
        return {'id': item['values'][0], 'nome': item['values'][1]}

    def show_error(self, title, message):
        messagebox.showerror(title, message, parent=self)

    def show_info(self, title, message):
        messagebox.showinfo(title, message, parent=self)

    def show_warning(self, title, message):
        messagebox.showwarning(title, message, parent=self)

    def ask_yes_no(self, title, message):
        return messagebox.askyesno(title, message, icon='warning', parent=self)

    def _center_window(self):
                                                              
        p_w, p_h = self.parent.winfo_width(), self.parent.winfo_height()
        p_x, p_y = self.parent.winfo_x(), self.parent.winfo_y()
        w, h = self.winfo_width(), self.winfo_height()
        x = p_x + (p_w // 2) - (w // 2)
        y = p_y + (p_h // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")