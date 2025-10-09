# credenciais_manager_gui.py
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import configparser
import re
from pathlib import Path
import sys
import shutil

#  Bloco de Inicialização e Importação Segura 
try:
    PROJECT_ROOT = Path(__file__).parent.parent.resolve()
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from persistencia.security import load_key, encrypt_message, decrypt_message
    # Adicionada a função de verificação de hash
    from persistencia.auth import hash_password, check_password_hash
except ImportError as e:
    messagebox.showerror(
        "Erro Crítico de Importação",
        f"Não foi possível importar módulos essenciais: {e}.\n\n"
        "Verifique se o script está na pasta correta e se a estrutura do projeto está intacta."
    )
    sys.exit(1)

#  Constantes 
APP_TITLE = "Nexlify DevTools - Gestor de Configuração e Segurança"
MAIN_GEOMETRY = "1050x800"
MIN_SIZE = (900, 650)
FONT_DEFAULT = ("Segoe UI", 10)
FONT_COURIER = ("Courier New", 9)
DB_CONFIG_KEYS = ["type", "host", "port", "dbname", "user", "password", "path"]


class ConnectionManagerFrame(ttk.Frame):
    """Aba para gerenciar a conexão ativa no arquivo banco.ini."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.ini_filepath = None
        self.ini_lines = []
        self.db_configs = {}

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        controls_frame = ttk.Frame(self)
        controls_frame.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(0, 10))

        load_btn = ttk.Button(controls_frame, text="Carregar banco.ini", command=self._load_ini)
        load_btn.pack(fill="x", pady=(0, 5))

        self.file_status_label = ttk.Label(controls_frame, text="Nenhum arquivo carregado.", style="secondary.TLabel")
        self.file_status_label.pack(fill="x", pady=(0, 15), anchor="w")

        self.db_options_frame = ttk.LabelFrame(controls_frame, text=" Gerenciar Conexão ", padding=10)
        self.db_options_frame.pack(fill="x")
        ttk.Label(self.db_options_frame, text="Carregue um arquivo .ini.").pack()

        preview_frame = ttk.LabelFrame(self, text=" Pré-visualização do banco.ini ", padding=10)
        preview_frame.grid(row=0, column=1, rowspan=2, sticky="nsew")
        preview_frame.rowconfigure(0, weight=1)
        preview_frame.columnconfigure(0, weight=1)

        self.ini_preview_area = scrolledtext.ScrolledText(preview_frame, wrap=tk.WORD, state="disabled",
                                                          font=FONT_COURIER)
        self.ini_preview_area.grid(row=0, column=0, sticky="nsew")

    def _load_ini(self):
        filepath = filedialog.askopenfilename(title="Selecione o arquivo banco.ini", filetypes=[("INI files", "*.ini")])
        if not filepath:
            return

        self.ini_filepath = Path(filepath)
        try:
            self.ini_lines = self.ini_filepath.read_text(encoding='utf-8').splitlines()
            self.file_status_label.config(text=f"Editando: {self.ini_filepath.name}", style="success.TLabel")
            self._parse_and_populate_ui()
            self._update_ini_preview()
        except Exception as e:
            messagebox.showerror("Erro de Leitura", f"Não foi possível ler o arquivo .ini:\n{e}", parent=self)
            self.file_status_label.config(text="Falha ao carregar.", style="danger.TLabel")

    def _parse_and_populate_ui(self):
        self.db_configs = {}
        active_db = None
        current_db = None
        marker_pattern = re.compile(r"\s*Configuração para\s+(.*?)\s*", re.IGNORECASE)
        for line in self.ini_lines:
            match = marker_pattern.search(line)
            if match:
                db_name = match.group(1).strip().lower().replace(' / interbase', '').replace('microsoft ', '')
                if 'sql server' in db_name: db_name = 'sqlserver'
                current_db = db_name
                if current_db not in self.db_configs:
                    self.db_configs[current_db] = {'active': False}
            clean_line = line.strip()
            if current_db and not clean_line.startswith(('#', ';')) and '=' in clean_line:
                key = clean_line.split('=', 1)[0].strip().lower()
                if key == 'type':
                    active_db = current_db
        if active_db:
            self.db_configs[active_db]['active'] = True
        for widget in self.db_options_frame.winfo_children():
            widget.destroy()
        if not self.db_configs:
            ttk.Label(self.db_options_frame, text="Nenhum bloco de config encontrado.").pack()
            return
        for db_type, config_info in sorted(self.db_configs.items()):
            card = ttk.Frame(self.db_options_frame)
            card.pack(fill="x", pady=2, anchor="w")
            ttk.Label(card, text=f"{db_type.capitalize()}:", width=12).pack(side="left")
            if config_info['active']:
                ttk.Label(card, text="ATIVO", style="success.TLabel").pack(side="left", padx=5)
            else:
                btn = ttk.Button(card, text="Ativar", style="outline.TButton",
                                 command=lambda dt=db_type: self._activate_db(dt))
                btn.pack(side="right")

    def _activate_db(self, db_to_activate: str):
        msg = f"Deseja ativar a conexão com '{db_to_activate.capitalize()}'?\n\nO arquivo será salvo e um backup (.bak) será criado."
        if not messagebox.askyesno("Confirmar Ativação", msg, parent=self):
            return
        new_lines = []
        current_db = None
        marker_pattern = re.compile(r"\s*Configuração para\s+(.*?)\s*", re.IGNORECASE)
        for line in self.ini_lines:
            match = marker_pattern.search(line)
            if match:
                db_name = match.group(1).strip().lower().replace(' / interbase', '').replace('microsoft ', '')
                if 'sql server' in db_name: db_name = 'sqlserver'
                current_db = db_name
            key_match = re.match(r"^\s*#?;?\s*([a-zA-Z_]+)\s*=", line)
            if current_db and key_match and key_match.group(1).lower() in DB_CONFIG_KEYS:
                clean_line = line.lstrip(' #;').strip()
                if current_db == db_to_activate:
                    new_lines.append(clean_line)
                else:
                    new_lines.append(f"#{clean_line}")
            else:
                new_lines.append(line)
        try:
            backup_path = self.ini_filepath.with_suffix('.ini.bak')
            shutil.copy(self.ini_filepath, backup_path)
            self.ini_filepath.write_text('\n'.join(new_lines), encoding='utf-8')
            self.ini_lines = new_lines
            self._parse_and_populate_ui()
            self._update_ini_preview()
            messagebox.showinfo("Sucesso",
                                f"Conexão '{db_to_activate.capitalize()}' ativada!\nBackup criado em: {backup_path.name}",
                                parent=self)
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar as alterações:\n{e}", parent=self)

    def _update_ini_preview(self):
        self.ini_preview_area.config(state="normal")
        self.ini_preview_area.delete("1.0", tk.END)
        self.ini_preview_area.insert("1.0", '\n'.join(self.ini_lines))
        self.ini_preview_area.config(state="disabled")


class CryptoManagerFrame(ttk.Frame):
    """Aba para criptografar credenciais e atualizar hashes de senha."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.rowconfigure(3, weight=1)
        self.columnconfigure(0, weight=1)
        ini_frame = ttk.LabelFrame(self, text=" Criptografar Credenciais (.ini) ", padding=10)
        ini_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Button(ini_frame, text="Selecionar e Criptografar banco.ini", command=self._encrypt_ini_file).pack(fill="x")
        sql_frame = ttk.LabelFrame(self, text=" Atualizar Hashes de Senha (.sql) ", padding=10)
        sql_frame.grid(row=1, column=0, sticky="ew", pady=10)
        ttk.Button(sql_frame, text="Selecionar e Atualizar Schema SQL", command=self._update_sql_hashes).pack(fill="x")
        hash_gen_frame = ttk.LabelFrame(self, text=" Gerador de Hash Bcrypt ", padding=10)
        hash_gen_frame.grid(row=2, column=0, sticky="ew", pady=10)
        hash_gen_frame.columnconfigure(1, weight=1)
        ttk.Label(hash_gen_frame, text="Senha:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.password_to_hash_entry = ttk.Entry(hash_gen_frame)
        self.password_to_hash_entry.grid(row=0, column=1, sticky="ew")
        ttk.Button(hash_gen_frame, text="Gerar Hash", command=self._generate_and_display_hash).grid(row=0, column=2,
                                                                                                    padx=5)
        ttk.Label(hash_gen_frame, text="Hash:").grid(row=1, column=0, padx=(0, 5), sticky="w", pady=(5, 0))
        self.generated_hash_entry = ttk.Entry(hash_gen_frame, state="readonly")
        self.generated_hash_entry.grid(row=1, column=1, sticky="ew", pady=(5, 0))
        ttk.Button(hash_gen_frame, text="Copiar", command=self._copy_generated_hash).grid(row=1, column=2, padx=5,
                                                                                          pady=(5, 0))
        log_frame = ttk.LabelFrame(self, text=" Log de Operações ", padding=10)
        log_frame.grid(row=3, column=0, sticky="nsew", pady=10)
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state="disabled", font=FONT_COURIER)
        self.log_area.grid(row=0, column=0, sticky="nsew")
        self.log_area.tag_config("success", foreground="green")
        self.log_area.tag_config("error", foreground="red")
        self.log_area.tag_config("info", foreground="blue")
        ttk.Button(log_frame, text="Copiar Log", command=self._copy_log).grid(row=1, column=0, sticky="ew",
                                                                              pady=(10, 0))

    def _generate_and_display_hash(self):
        password = self.password_to_hash_entry.get()
        if not password:
            messagebox.showwarning("Campo Vazio", "Por favor, digite uma senha para gerar o hash.", parent=self)
            return
        generated_hash = hash_password(password)
        self.generated_hash_entry.config(state="normal")
        self.generated_hash_entry.delete(0, tk.END)
        self.generated_hash_entry.insert(0, generated_hash)
        self.generated_hash_entry.config(state="readonly")
        self._log(f"Hash gerado para a senha '{password}'", "info")

    def _copy_generated_hash(self):
        content = self.generated_hash_entry.get()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            messagebox.showinfo("Sucesso", "Hash copiado para a área de transferências.", parent=self)
            self._log("Hash copiado.", "success")

    def _log(self, message, tag="info"):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, f"[{tag.upper()}] {message}\n", tag)
        self.log_area.config(state="disabled")
        self.log_area.see(tk.END)
        self.update_idletasks()

    def _copy_log(self):
        content = self.log_area.get("1.0", tk.END).strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            messagebox.showinfo("Sucesso", "Log copiado para a área de transferências.", parent=self)

    def _encrypt_ini_file(self):
        filepath = filedialog.askopenfilename(title="Selecione o banco.ini", filetypes=[("INI files", "*.ini")])
        if not filepath: return
        ini_path = Path(filepath)
        self._log(f"Processando {ini_path.name}...")
        try:
            key = load_key()
            lines = ini_path.read_text(encoding='utf-8').splitlines()
            new_lines = []
            changed = False
            for line in lines:
                key_match = re.match(r"^(\s*#?;?\s*)(user|password)(\s*=\s*)(.*)", line, re.IGNORECASE)
                if key_match:
                    prefix, key, separator, value = key_match.groups()
                    if value and not value.startswith("gAAAAA"):
                        encrypted_value = encrypt_message(value, key)
                        new_lines.append(f"{prefix}{key}{separator}{encrypted_value}")
                        self._log(f"Campo '{key}' criptografado.", "success")
                        changed = True
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            if changed:
                backup_path = ini_path.with_suffix('.ini.bak')
                shutil.copy(ini_path, backup_path)
                self._log(f"Backup de segurança criado em {backup_path.name}", "info")
                ini_path.write_text('\n'.join(new_lines), encoding='utf-8')
                self._log("Arquivo .ini salvo com sucesso!", "success")
            else:
                self._log("Nenhuma credencial em texto plano encontrada para criptografar.")
                messagebox.showinfo(
                    "Nenhuma Alteração",
                    "O arquivo já parece estar totalmente criptografado. Nenhuma alteração foi necessária.",
                    parent=self
                )
        except Exception as e:
            self._log(f"ERRO: {e}", "error")

    def _update_sql_hashes(self):
        filepath = filedialog.askopenfilename(title="Selecione o schema .sql", filetypes=[("SQL files", "*.sql")])
        if not filepath: return
        sql_path = Path(filepath)
        self._log(f"Processando {sql_path.name}...")
        try:
            content = sql_path.read_text(encoding='utf-8')
            pattern = re.compile(
                r"(INSERT\s+INTO\s+USUARIOS.*?VALUES\s*\(.*?,)\s*'(.*?)'(\s*,.*?\))",
                re.IGNORECASE | re.DOTALL
            )

            def replacer(match):
                prefix, password, suffix = match.groups()
                if not password.startswith('$2b$'):
                    new_hash = hash_password(password)
                    self._log(f"Senha '{password}' convertida para hash.", "success")
                    return f"{prefix} '{new_hash}'{suffix}"
                return match.group(0)

            content, count = pattern.subn(replacer, content)
            if count > 0:
                backup_path = sql_path.with_suffix('.sql.bak')
                shutil.copy(sql_path, backup_path)
                self._log(f"Backup de segurança criado em {backup_path.name}", "info")
                sql_path.write_text(content, encoding='utf-8')
                self._log(f"{count} senhas foram atualizadas para hash. Arquivo salvo!", "success")
            else:
                self._log("Nenhuma senha em texto plano encontrada nos comandos INSERT.")
                messagebox.showinfo(
                    "Nenhuma Alteração",
                    "Nenhuma senha em texto plano foi encontrada nos comandos INSERT. O arquivo não foi modificado.",
                    parent=self
                )
        except Exception as e:
            self._log(f"ERRO: {e}", "error")


class CredentialViewerFrame(ttk.Frame):
    """Aba para visualizar credenciais em arquivos .ini e .sql."""

    #  
    # Dicionário com as senhas conhecidas para verificação.
    SENHAS_CONHECIDAS = {
        'admin': 'admin', 'diretor.op': 'dir123', 'gerente.ti': 'ti123',
        'ana.supervisor': 'sup123', 'bruno.operador': 'op123', 'carla.analista': 'ana123',
        'davi.auditor': 'auditor123', 'elisa.op': 'op456', 'felipe.gerente': 'ti456',
        'gabi.analista': 'ana456', 'hugo.diretor': 'dir456', 'isa.supervisor': 'sup456',
        'joao.operador': 'op789', 'lara.admin': 'admin456', 'mateus.auditor': 'auditor456'
    }

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        ttk.Button(self, text="Analisar Arquivo de Credenciais (.ini ou .sql)", command=self._analyze_file).grid(row=0,
                                                                                                                 column=0,
                                                                                                                 sticky="ew",
                                                                                                                 pady=(
                                                                                                                     0,
                                                                                                                     10))
        tree_frame = ttk.LabelFrame(self, text=" Credenciais Encontradas ", padding=10)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        columns = ('source', 'section', 'user', 'value', 'decrypted')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        self.tree.heading('source', text='Origem')
        self.tree.heading('section', text='Seção/Comando')
        self.tree.heading('user', text='Usuário/Chave')
        self.tree.heading('value', text='Valor (Senha/Hash)')
        self.tree.heading('decrypted', text='Valor Decifrado')

        for col in columns: self.tree.column(col, anchor='w')
        self.tree.column('source', width=80)
        self.tree.column('section', width=150)
        self.tree.column('user', width=150)
        self.tree.grid(row=0, column=0, sticky="nsew")

    def _analyze_file(self):
        filepath = filedialog.askopenfilename(
            title="Analisar Arquivo",
            filetypes=[
                ("Arquivos Suportados", "*.ini *.sql"),
                ("Arquivos INI", "*.ini"),
                ("Arquivos SQL", "*.sql"),
                ("Todos os arquivos", "*.*")
            ]
        )
        if not filepath: return

        for item in self.tree.get_children(): self.tree.delete(item)
        file = Path(filepath)

        if file.suffix == '.ini':
            self._analyze_ini(file)
        elif file.suffix == '.sql':
            self._analyze_sql(file)

    def _analyze_ini(self, file: Path):
        try:
            key = load_key()
            config = configparser.ConfigParser(allow_no_value=True, comment_prefixes=('#', ';'),
                                               inline_comment_prefixes=('#', ';'))
            config.read(file, encoding='utf-8')

            for section in config.sections():
                for option, value in config.items(section):
                    if option in ['user', 'password'] and value:
                        decrypted = decrypt_message(value, key) if value.startswith("gAAAAA") else ""
                        self.tree.insert("", "end", values=(file.name, f"[{section}]", option, value, decrypted))
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao analisar o arquivo .ini: {e}", parent=self)

    def _analyze_sql(self, file: Path):
        try:
            content = file.read_text(encoding='utf-8')
            found_users = False

            # Lógica para INSERT INTO USUARIOS (Estratégia de 2 passos)
            insert_block_match = re.search(
                r"INSERT\s+INTO\s+USUARIOS.*?VALUES.*?;",
                content,
                re.IGNORECASE | re.DOTALL
            )

            if insert_block_match:
                insert_block_text = insert_block_match.group(0)
                user_tuple_pattern = re.compile(
                    r"\(\s*'([^']*)'\s*,\s*'([^']*)'\s*,\s*'[^']*'\s*,\s*'[^']*'\s*\)",
                    re.IGNORECASE
                )
                for match in user_tuple_pattern.finditer(insert_block_text):
                    login, hash_senha = match.groups()

                    # : Lógica de verificação 
                    decrypted_value = "N/A (Hash Bcrypt)"
                    if login in self.SENHAS_CONHECIDAS:
                        known_password = self.SENHAS_CONHECIDAS[login]
                        try:
                            if check_password_hash(known_password, hash_senha):
                                decrypted_value = known_password
                            else:
                                decrypted_value = "SENHA NÃO CONFERE!"
                        except Exception:
                            # Trata casos onde o hash pode ser inválido para a verificação
                            decrypted_value = "HASH INVÁLIDO"

                    self.tree.insert("", "end",
                                     values=(file.name, "INSERT USUARIOS", login, hash_senha, decrypted_value))
                    found_users = True

            # Lógica para CREATE USER
            create_pattern = re.compile(
                r"(CREATE\s+(USER|LOGIN))\s+.*?['\"](.*?)['\"].*?(IDENTIFIED\s+BY|WITH\s+PASSWORD)\s*=?\s*['\"](.*?)['\"]",
                re.IGNORECASE)

            for match in create_pattern.finditer(content):
                command, _, user, _, password = match.groups()
                self.tree.insert("", "end", values=(file.name, command.strip(), user, password, password))
                found_users = True

            if not found_users:
                messagebox.showinfo("Análise Concluída",
                                    "Nenhuma credencial de usuário reconhecida foi encontrada no arquivo.",
                                    parent=self)

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao analisar o arquivo .sql: {e}", parent=self)


class DevToolsApp(tk.Tk):
    """Janela principal da aplicação de ferramentas de desenvolvimento."""

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(MAIN_GEOMETRY)
        self.minsize(*MIN_SIZE)

        self.style = ttk.Style(self)
        try:
            self.style.theme_use('litera')
        except tk.TclError:
            print("Tema 'litera' do ttkbootstrap não encontrado. Usando tema padrão.")

        self.style.configure('TLabel', font=FONT_DEFAULT)
        self.style.configure('TButton', font=FONT_DEFAULT)
        self.style.configure('TNotebook.Tab', font=FONT_DEFAULT)
        self.style.configure('TLabelframe.Label', font=(FONT_DEFAULT[0], FONT_DEFAULT[1], 'bold'))
        self.style.configure('success.TLabel', foreground="green", font=(FONT_DEFAULT[0], FONT_DEFAULT[1], 'bold'))
        self.style.configure('danger.TLabel', foreground="red")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        conn_tab = ConnectionManagerFrame(notebook, padding=10)
        crypto_tab = CryptoManagerFrame(notebook, padding=10)
        viewer_tab = CredentialViewerFrame(notebook, padding=10)

        notebook.add(conn_tab, text=" Gestor de Conexão (.ini) ")
        notebook.add(crypto_tab, text=" Criptografia e Hashes ")
        notebook.add(viewer_tab, text=" Visualizador de Credenciais ")


if __name__ == "__main__":
    app = DevToolsApp()
    app.mainloop()