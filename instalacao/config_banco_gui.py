import tkinter as tk
from tkinter import ttk, messagebox
import os
import re
from pathlib import Path
import sys                                                      

BLOCK_DEFINITIONS = {
    'sqlserver': ['type', 'host', 'port', 'dbname', 'user', 'password'],
    'sqlite': ['type', 'path'],
    'postgresql': ['type', 'host', 'port', 'dbname', 'user', 'password'],
    'mysql': ['type', 'host', 'port', 'dbname', 'user', 'password'],
    'mariadb': ['type', 'host', 'port', 'dbname', 'user', 'password']
}


class DatabaseConfigManager:
    BLOCK_DEFINITIONS = BLOCK_DEFINITIONS

    def __init__(self, filepath='banco.ini'):
        self.filepath = Path(filepath)
        self.lines = []
        self.blocks = []
        self.current_active_block_name = None

    def load_config(self):
        if not self.filepath.is_file():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {self.filepath}\nVerifique se 'banco.ini' está na pasta raiz do projeto.")

        with open(self.filepath, 'r', encoding='utf-8') as f:
            self.lines = f.readlines()

        self.blocks = []
        self.current_active_block_name = None
        type_regex = re.compile(r"^\s*(#)?\s*type\s*=\s*(\w+)")

        for i, line in enumerate(self.lines):
            match = type_regex.match(line)
            if match:
                is_commented = match.group(1) is not None
                db_type = match.group(2)

                if db_type in self.BLOCK_DEFINITIONS:
                    keys_for_this_block = self.BLOCK_DEFINITIONS[db_type]
                    indices = []
                    key_idx = 0
                    current_scan_line = i

                    while key_idx < len(keys_for_this_block) and current_scan_line < len(self.lines):
                        scan_line = self.lines[current_scan_line].strip()
                        clean_scan_line = scan_line.lstrip('#').strip()
                        if clean_scan_line.startswith(keys_for_this_block[key_idx]):
                            indices.append(current_scan_line)
                            key_idx += 1
                        current_scan_line += 1

                    block_name = f"{db_type} (Linha {i + 1})"
                    self.blocks.append({'name': block_name, 'indices': indices})

                    if not is_commented:
                        self.current_active_block_name = block_name

    def get_all_dbs(self):
        return [block['name'] for block in self.blocks]

    def get_active_db(self):
        return self.current_active_block_name

    def activate_db(self, name_to_activate):
        for block in self.blocks:
            is_target_block = (block['name'] == name_to_activate)
            for line_index in block['indices']:
                original_line = self.lines[line_index]
                stripped_line = original_line.lstrip()
                indent_space = original_line[:len(original_line) - len(stripped_line)]
                content = stripped_line.lstrip('#').lstrip()
                if is_target_block:
                    new_line = f"{indent_space}{content}"
                else:
                    new_line = f"{indent_space}#{content}"
                self.lines[line_index] = new_line.rstrip() + os.linesep

    def save_config(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.writelines(self.lines)


class App(tk.Tk):
    def __init__(self, manager: DatabaseConfigManager):
        super().__init__()
        self.manager = manager

        self.title("Configurador de Conexão (banco.ini)")

                                    
                                                  
        w = 500                     
        h = 400                    

                                 
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()

                               
        x = (sw // 2) - (w // 2)
        y = (sh // 2) - (h // 2)

        self.geometry(f"{w}x{h}+{x}+{y}")
                                 

        self.minsize(450, 350)

        self._setup_styles()

        self.selected_db = tk.StringVar()
        self.status_label = ttk.Label(self, text="", style="Status.TLabel")

        main_container = ttk.Frame(self, padding=15)
        main_container.pack(fill="both", expand=True)

        self.create_widgets(main_container)
        self._load_and_populate()

    def _setup_styles(self):
        """Configura estilos ttk."""
        style = ttk.Style(self)
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"), foreground="#005a9e")
        style.configure("TButton", font=("Segoe UI", 10), padding=5)
        style.configure("Success.TButton", foreground="white", background="#28a745", font=("Segoe UI", 10, "bold"))
        style.map("Success.TButton", background=[('active', '#218838')])
        style.configure("Status.TLabel", font=("Segoe UI", 9))

    def _load_and_populate(self):
        """Carrega dados e popula a UI, tratando erros."""
        try:
            self.manager.load_config()
            self._update_radio_buttons()
            active_db = self.manager.get_active_db()
            if active_db:
                self.selected_db.set(active_db)
                self.status_label.config(text=f"Atualmente ativo: {active_db}", foreground="blue")
            else:
                self.status_label.config(text="Nenhum banco ativo detectado no arquivo.", foreground="orange")
            self.save_button.config(state="normal")

        except FileNotFoundError as e:
            self.show_error(str(e))
            self.save_button.config(state="disabled")
        except Exception as e:
            self.show_error(f"Erro inesperado ao carregar banco.ini: {e}")
            self.save_button.config(state="disabled")

    def create_widgets(self, parent):
        ttk.Label(parent, text="Selecione a conexão de banco de dados para ATIVAR:", style="Header.TLabel").pack(
            anchor="w", pady=(0, 5))

        self.radio_frame = ttk.LabelFrame(parent, text="Conexões Encontradas", relief="sunken", borderwidth=1,
                                          padding=15)
        self.radio_frame.pack(fill="both", expand=True, pady=10)

        self.save_button = ttk.Button(parent, text="Salvar e Ativar Selecionado", command=self.save_selection,
                                      style="Success.TButton", state="disabled")
        self.save_button.pack(pady=5, fill="x", ipady=5)

        reload_button = ttk.Button(parent, text="Recarregar banco.ini", command=self._load_and_populate)
        reload_button.pack(pady=5, fill="x")

        self.status_label.pack(pady=(10, 0))

    def _update_radio_buttons(self):
        """Limpa e recria os radio buttons com base nos dados carregados."""
        for widget in self.radio_frame.winfo_children():
            widget.destroy()

        all_dbs = self.manager.get_all_dbs()

        if not all_dbs:
            ttk.Label(self.radio_frame, text="Nenhum bloco de configuração válido foi encontrado.",
                      foreground="red").pack()
            self.save_button.config(state="disabled")
            return

        for db_name in all_dbs:
            rb = ttk.Radiobutton(
                self.radio_frame,
                text=db_name,
                variable=self.selected_db,
                value=db_name
            )
            rb.pack(anchor="w", pady=2)

    def save_selection(self):
        chosen_db = self.selected_db.get()
        if not chosen_db:
            self.show_error("Nenhum banco de dados foi selecionado.")
            return

        try:
            self.manager.activate_db(chosen_db)
            self.manager.save_config()
            self.status_label.config(text=f"Sucesso! '{chosen_db}' agora está ativo no arquivo banco.ini.",
                                     foreground="green")

            self.manager.load_config()
            self.selected_db.set(self.manager.get_active_db())
            self._update_radio_buttons()

        except Exception as e:
            self.show_error(f"Erro ao salvar: {e}")

    def show_error(self, message):
        self.status_label.config(text=message, foreground="red")
        messagebox.showerror("Erro", message, parent=self)


if __name__ == "__main__":
    try:
        script_dir = Path(__file__).parent.resolve()
        root_dir = script_dir.parent.resolve()
        ini_path = root_dir / "banco.ini"

        if not ini_path.is_file():
            try:
                ini_content = """[database] # 
# ====================================================================== # 
# INSTRUÇÕES DE USO: # 
# Para usar um banco de dados, descomente a seção correspondente # 
# (removendo o '#' do início de cada linha) e comente as outras. # 
# Apenas UMA configuração de banco de dados deve estar ativa por vez. # 
# ====================================================================== # 

#  Configuração para Microsoft SQL Server # 
#type = sqlserver # 
#host = 10.77.77.189 # 
#port = 1433 # 
#dbname = NexlifyTTk # 
#user = gato # 
#password = -Vladmir!5Anos- # 

#  Configuração para SQLite # 
type = sqlite # 
path = NexlifyTTk.db # 

#  Configuração para PostgreSQL # 
#type = postgresql # 
#host = 10.77.77.185 # 
#port = 5432 # 
#dbname = NexlifyTTk # 
#user = gato # 
#password = -Vladmir!5Anos- # 

#  Configuração para MySQL # 
#type = mysql # 
#host = localhost # 
#port = 3306 # 
#dbname = NexlifyTTk # 
#user = gato # 
#password = -Vladmir!5Anos- # 

#  Configuração para MariaDB # 
#type = mariadb # 
#host = 10.77.77.189 # 
#port = 3306 # 
#dbname = NexlifyTTk # 
#user = gAAAAABo52D7Wefg0RLLMr62vnJinZeI5CMPv46SR-QgTHB18DdC9RmvR53QM4MBQOlLj_bUo0Rouzp8LuMWJfW2FjP4Du387w== # 
#password = gAAAAABo52D7sEBmtfcCv2shxybef66zojupLPMP25CTQ8Z5TzQMw8gw8CHLwJ_CN1qsg3kkIgypYqpMmsRiRuH0X5QXjhvMXQ== # 
"""
                with open(ini_path, 'w', encoding='utf-8') as f:
                    f.write(ini_content)
            except Exception as e:
                messagebox.showerror("Erro Crítico", f"Não foi possível criar 'banco.ini' em {ini_path}: {e}")
                sys.exit(1)

        config_manager = DatabaseConfigManager(filepath=str(ini_path))
        app = App(config_manager)
        app.mainloop()

    except Exception as main_error:
        messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao iniciar o configurador:\n{main_error}")
        sys.exit(1)