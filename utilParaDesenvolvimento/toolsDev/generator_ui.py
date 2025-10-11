# toolsDev/generator_ui.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import traceback
from .generator_logic import CodeGenerator

class GeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("✨ Assistente de Geração de Código ✨")
        self.geometry("950x800")
        self.minsize(850, 700)
        self.generator = CodeGenerator(self.log)
        self.user_roles = ['Administrador Global', 'Diretor de Operações', 'Gerente de TI', 'Supervisor de Produção', 'Operador de Linha', 'Analista de Dados', 'Auditor Externo']
        self._setup_styles()
        self._create_widgets()

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("Success.TButton", foreground="white", background="#28a745")
        style.map("Success.TButton", background=[('active', '#218838')])

    def _create_widgets(self):
        main_pane = ttk.PanedWindow(self, orient=tk.VERTICAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        form_pane = ttk.Frame(main_pane)
        main_pane.add(form_pane, weight=2)
        log_pane = ttk.LabelFrame(main_pane, text=" Log de Geração em Tempo Real ", padding=10)
        main_pane.add(log_pane, weight=1)
        self._create_form_widgets(form_pane)
        self._create_log_widgets(log_pane)

    def _create_form_widgets(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        panel_tab = ttk.Frame(notebook, padding=15)
        notebook.add(panel_tab, text="  Painel Principal  ")
        modal_tab = ttk.Frame(notebook, padding=15)
        notebook.add(modal_tab, text="  Janela Modal  ")
        ComponentBuilder(panel_tab, self, "Painel")
        ComponentBuilder(modal_tab, self, "Modal")

    def _create_log_widgets(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        self.log_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, font=("Consolas", 9), state="disabled")
        self.log_text.grid(row=0, column=0, sticky="nsew")
        self.log_text.tag_config("SUCCESS", foreground="#00a86b")
        self.log_text.tag_config("FAIL", foreground="#e53935")
        self.log_text.tag_config("WARNING", foreground="#f9a825")
        self.log_text.tag_config("INFO", foreground="#29b6f6")

    def log(self, message, level="info"):
        level_upper = level.upper()
        def _update():
            self.log_text.config(state="normal")
            timestamp = time.strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"{timestamp} [{level_upper}] {message}\n", (level_upper,))
            self.log_text.config(state="disabled")
            self.log_text.see(tk.END)
        self.after(0, _update)

class ComponentBuilder(ttk.Frame):
    def __init__(self, parent, app, component_type, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)
        self.app = app
        self.generator = app.generator
        self.component_type = component_type
        self.columnconfigure(1, weight=1)
        self._create_basic_info_widgets()
        self._create_access_control_widgets()
        self._create_crud_widgets()
        self._create_action_button()
        self.toggle_crud_section()

    def _create_basic_info_widgets(self):
        frame = ttk.LabelFrame(self, text=f" 1. Informações do {self.component_type} ", padding=15)
        frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        frame.columnconfigure(1, weight=1)
        self.panel_type_var = tk.StringVar(value="Básico")
        self.panel_name_var = tk.StringVar()
        self.panel_icon_var = tk.StringVar(value="✨")
        ttk.Label(frame, text="Tipo:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Combobox(frame, textvariable=self.panel_type_var, values=["Básico", "MVC CRUD"], state="readonly").grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.panel_type_var.trace_add("write", self.toggle_crud_section)
        ttk.Label(frame, text="Nome de Exibição:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.panel_name_var).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        if self.component_type == "Painel":
            ttk.Label(frame, text="Ícone:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
            ttk.Entry(frame, textvariable=self.panel_icon_var).grid(row=2, column=1, sticky="ew", padx=5, pady=5)

    def _create_access_control_widgets(self):
        frame = ttk.LabelFrame(self, text=" 2. Controle de Acesso (Apenas Painéis) ", padding=15)
        frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 15))
        self.access_vars = {}
        for i, role in enumerate(self.app.user_roles):
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(frame, text=role, variable=var)
            chk.grid(row=i // 3, column=i % 3, sticky="w", padx=10, pady=2)
            self.access_vars[role] = var
        if self.component_type == "Modal":
            for child in frame.winfo_children(): child.config(state="disabled")

    def _create_crud_widgets(self):
        self.crud_frame = ttk.LabelFrame(self, text=" 3. Configuração do CRUD ", padding=15)
        self.crud_frame.columnconfigure(1, weight=1)
        ttk.Button(self.crud_frame, text="Carregar Tabelas do Banco de Dados", command=self.load_tables_from_db).grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=10)
        self.table_name_var = tk.StringVar()
        self.table_combo = ttk.Combobox(self.crud_frame, textvariable=self.table_name_var, state="readonly")
        self.table_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.table_combo.bind("<<ComboboxSelected>>", self.on_table_select)
        ttk.Label(self.crud_frame, text="Tabela Alvo:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.columns_text = scrolledtext.ScrolledText(self.crud_frame, height=5, width=40, state="disabled", font=("Consolas", 9))
        self.columns_text.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(self.crud_frame, text="Preview da Tabela:").grid(row=2, column=0, sticky="nw", padx=5, pady=5)

    def _create_action_button(self):
        self.generate_btn = ttk.Button(self, text=f"🚀 Gerar {self.component_type}", style="Success.TButton", command=self.run_generation)
        self.generate_btn.grid(row=4, column=0, columnspan=2, sticky="ew", ipady=10, pady=10)

    def run_in_thread(self, target, *args):
        threading.Thread(target=target, args=args, daemon=True).start()

    def toggle_crud_section(self, *args):
        if self.panel_type_var.get() == "MVC CRUD":
            self.crud_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(0, 15))
        else:
            self.crud_frame.grid_forget()

    def load_tables_from_db(self):
        self.table_combo.set("")
        self.table_combo['values'] = []
        self.columns_text.config(state="normal"); self.columns_text.delete("1.0", tk.END); self.columns_text.config(state="disabled")
        self.run_in_thread(self._load_tables_thread)

    def _load_tables_thread(self):
        try:
            inspector = self.generator.get_db_inspector()
            tables = self.generator.get_available_tables(inspector) if inspector else []
            self.after(0, lambda: self.table_combo.config(values=tables))
        except Exception as e:
            self.app.log(f"Falha ao carregar tabelas: {e}", "fail")

    def on_table_select(self, event=None):
        if table_name := self.table_name_var.get():
            self.run_in_thread(self._on_table_select_thread, table_name)

    def _on_table_select_thread(self, table_name):
        try:
            inspector = self.generator.get_db_inspector()
            columns, pk_name = self.generator.get_table_details(inspector, table_name)
            def _update_preview():
                self.columns_text.config(state="normal")
                self.columns_text.delete("1.0", tk.END)
                preview_text = f"Chave Primária: {pk_name}\n\nColunas:\n"
                for col in columns:
                    fk_info = f" -> {col['fk']['references_table']}" if col.get('fk') else ""
                    preview_text += f"- {col['name']}{fk_info}\n"
                self.columns_text.insert(tk.END, preview_text)
                self.columns_text.config(state="disabled")
            self.after(0, _update_preview)
        except Exception as e:
            self.app.log(f"Falha ao inspecionar '{table_name}': {e}", "fail")

    def run_generation(self):
        panel_name = self.panel_name_var.get().strip()
        if not panel_name:
            messagebox.showwarning("Validação", "O Nome de Exibição é obrigatório.", parent=self)
            return
        context = {'component_type': self.component_type, 'class_prefix': 'Painel' if self.component_type == "Painel" else '', 'panel_type': self.panel_type_var.get(), 'panel_name': panel_name, 'panel_icon': self.panel_icon_var.get().strip(), 'allowed_access': [role for role, var in self.access_vars.items() if var.get()]}
        if context['panel_type'] == "MVC CRUD":
            table_name = self.table_name_var.get()
            if not table_name:
                messagebox.showwarning("Validação", "Selecione uma Tabela Alvo para o CRUD.", parent=self)
                return
            context['table_name'] = table_name
        self.generate_btn.config(state="disabled")
        self.app.log(f"Iniciando geração do {self.component_type.lower()} '{panel_name}'...")
        self.run_in_thread(self._run_generation_thread, context)

    def _run_generation_thread(self, context):
        try:
            if context['panel_type'] == "MVC CRUD":
                inspector = self.generator.get_db_inspector()
                columns, pk_name = self.generator.get_table_details(inspector, context['table_name'])
                context['columns'] = columns
                context['primary_key'] = pk_name
            self.generator.generate(context)
        except Exception as e:
            self.app.log(f"ERRO CRÍTICO DURANTE A GERAÇÃO: {e}\n{traceback.format_exc()}", "fail")
        finally:
            self.after(0, lambda: self.generate_btn.config(state="normal"))