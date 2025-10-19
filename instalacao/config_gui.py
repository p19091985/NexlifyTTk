import tkinter as tk
from tkinter import ttk, messagebox
import os
import re
import sys
import shutil
from pathlib import Path

try:
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent.resolve()
    config_py_path = project_root / "config.py"
    if not config_py_path.is_file():
        raise FileNotFoundError
except Exception:
    messagebox.showerror("Erro Crítico",
                         f"Não foi possível localizar o arquivo 'config.py' na pasta raiz do projeto ({project_root}). Verifique a estrutura de pastas.")
    sys.exit(1)


class ConfigApp(tk.Tk):
    def __init__(self, config_path):
        super().__init__()
        self.config_path = config_path
        self.title("Configurador Inteligente (config.py)")

        # --- INÍCIO DA CORREÇÃO ---
        # Lógica para centralizar a janela na TELA
        w = 600  # Largura da janela
        h = 650  # Altura da janela (ajustada para caber no minsize)

        # Obter dimensões da tela
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()

        # Calcular posição x, y
        x = (sw // 2) - (w // 2)
        y = (sh // 2) - (h // 2)

        self.geometry(f"{w}x{h}+{x}+{y}")
        # --- FIM DA CORREÇÃO ---

        # O minsize estava 550x650, 
        # então ajustei a altura (h) acima para 650
        self.minsize(550, 650)

        self.db_enabled_var = tk.BooleanVar()
        self.init_db_var = tk.BooleanVar()
        self.use_login_var = tk.BooleanVar()
        self.redirect_log_var = tk.BooleanVar()
        self.enable_theme_var = tk.BooleanVar()

        self.vars_map = {
            "DATABASE_ENABLED": self.db_enabled_var,
            "INITIALIZE_DATABASE_ON_STARTUP": self.init_db_var,
            "USE_LOGIN": self.use_login_var,
            "REDIRECT_CONSOLE_TO_LOG": self.redirect_log_var,
            "ENABLE_THEME_MENU": self.enable_theme_var
        }

        self._setup_styles()
        self._create_widgets()
        self._load_initial_values()
        self._on_db_setting_change()

    def _setup_styles(self):
        """Configura estilos visuais, incluindo os novos labels de status."""
        style = ttk.Style(self)
        style.configure("Success.TButton", foreground="white", background="#28a745", font=("-weight", "bold"))
        style.map("Success.TButton", background=[('active', '#218838')])

        style.configure("Success.TLabel", foreground="#28a745", font=("-size", 9, "-weight", "bold"))
        style.configure("Warning.TLabel", foreground="#ff8c00", font=("-size", 9, "-weight", "bold"))

        style.configure("TLabel", font=("-size", 10))
        style.configure("Help.TLabel", font=("-size", 9), foreground="#555")
        style.configure("Header.TLabel", font=("-size", 14, "-weight", "bold"))
        style.configure("TLabelframe.Label", font=("-size", 11, "-weight", "bold"), foreground="#005a9e")

    def _create_widgets(self):
        """Cria a interface de usuário redesenhada com feedback em tempo real."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Configurações Principais (config.py)", style="Header.TLabel").pack(pady=(0, 15),
                                                                                                       anchor="w")

        db_frame = ttk.LabelFrame(main_frame, text="🎲 Conexão Principal", padding=15)
        db_frame.pack(fill=tk.X, expand=False, pady=5)

        self.db_enabled_check = ttk.Checkbutton(db_frame,
                                                text="Habilitar Banco de Dados (DATABASE_ENABLED)",
                                                variable=self.db_enabled_var,
                                                command=self._on_db_setting_change)
        self.db_enabled_check.pack(anchor="w")
        ttk.Label(db_frame,
                  text="Controla se a aplicação se conecta a um banco de dados.",
                  style="Help.TLabel", wraplength=500).pack(anchor="w", padx=20, pady=(0, 5))

        dependent_frame = ttk.LabelFrame(main_frame, text="⚙️ Módulos Dependentes", padding=15)
        dependent_frame.pack(fill=tk.X, expand=False, pady=10)

        self.dependency_status_label = ttk.Label(dependent_frame, text="", style="Warning.TLabel", justify="center")
        self.dependency_status_label.pack(fill='x', pady=(0, 10))

        self.init_db_check = ttk.Checkbutton(dependent_frame,
                                             text="Inicializar Banco ao Iniciar (INITIALIZE_DATABASE_ON_STARTUP)",
                                             variable=self.init_db_var)
        self.init_db_check.pack(anchor="w", pady=(5, 0))
        ttk.Label(dependent_frame,
                  text="Se ativo, cria o schema do banco (SQLite). Depende do DB Habilitado.",
                  style="Help.TLabel", wraplength=500).pack(anchor="w", padx=20, pady=(0, 5))

        self.use_login_check = ttk.Checkbutton(dependent_frame,
                                               text="Exigir Login de Usuário (USE_LOGIN)",
                                               variable=self.use_login_var)
        self.use_login_check.pack(anchor="w", pady=(5, 0))
        ttk.Label(dependent_frame,
                  text="Se ativo, exige autenticação. Depende do DB Habilitado.",
                  style="Help.TLabel", wraplength=500).pack(anchor="w", padx=20, pady=(0, 5))

        general_frame = ttk.LabelFrame(main_frame, text="🔧 Configurações Gerais", padding=15)
        general_frame.pack(fill=tk.X, expand=False, pady=5)

        self.redirect_log_check = ttk.Checkbutton(general_frame,
                                                  text="Redirecionar Console para Log (REDIRECT_CONSOLE_TO_LOG)",
                                                  variable=self.redirect_log_var)
        self.redirect_log_check.pack(anchor="w")
        ttk.Label(general_frame,
                  text="Se ativo, a saída do console (print) vai para arquivos de log.",
                  style="Help.TLabel", wraplength=500).pack(anchor="w", padx=20, pady=(0, 5))

        self.enable_theme_check = ttk.Checkbutton(general_frame,
                                                  text="Habilitar Menu de Temas (ENABLE_THEME_MENU)",
                                                  variable=self.enable_theme_var)
        self.enable_theme_check.pack(anchor="w", pady=(5, 0))
        ttk.Label(general_frame,
                  text="Adiciona a opção 'Personalizar Tema...' no menu de Configurações.",
                  style="Help.TLabel", wraplength=500).pack(anchor="w", padx=20, pady=(0, 5))

        self.save_button = ttk.Button(main_frame, text="Salvar Configurações", command=self._save_settings,
                                      style="Success.TButton")
        self.save_button.pack(pady=(20, 5), fill=tk.X, ipady=5)

        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.pack(pady=(5, 0))

    def _on_db_setting_change(self, *args):
        """Atualiza estado dos checkbuttons dependentes."""
        is_db_enabled = self.db_enabled_var.get()
        if is_db_enabled:
            self.init_db_check.config(state="normal")
            self.use_login_check.config(state="normal")
            self.dependency_status_label.config(
                text="Banco HABILITADO. Opções dependentes disponíveis.",
                style="Success.TLabel"
            )
        else:
            self.init_db_check.config(state="disabled")
            self.use_login_check.config(state="disabled")
            self.init_db_var.set(False)
            self.use_login_var.set(False)
            self.dependency_status_label.config(
                text="Banco DESABILITADO. Login e Inicialização foram desativados.",
                style="Warning.TLabel"
            )

    def _load_initial_values(self):
        """Lê o config.py e define o estado inicial."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            missing_flags = []
            for flag_name, tk_var in self.vars_map.items():
                match = re.search(fr"^\s*{flag_name}\s*=\s*(True|False)", content, re.MULTILINE)
                if match:
                    tk_var.set(match.group(1) == "True")
                else:
                    tk_var.set(False)
                    missing_flags.append(flag_name)

            if missing_flags:
                missing_str = ", ".join(missing_flags)
                self._update_status(f"Aviso: Flags não encontradas: {missing_str}. Assumindo False.", "orange")

        except Exception as e:
            messagebox.showerror("Erro ao Ler", f"Não foi possível ler '{self.config_path}':\n{e}", parent=self)
            self.save_button.config(state="disabled")

        self._on_db_setting_change()

    def _save_settings(self):
        """Salva as novas configurações no arquivo config.py."""
        try:
            backup_path = self.config_path.with_suffix(".py.bak")
            shutil.copy2(self.config_path, backup_path)

            with open(self.config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            new_lines = []
            modified_flags = set()

            for line in lines:
                matched = False
                for flag_name, tk_var in self.vars_map.items():
                    pattern = fr"^\s*{flag_name}\s*=\s*(?:True|False)"
                    if re.match(pattern, line):
                        new_value = tk_var.get()
                        new_line = re.sub(r"(=\s*)(True|False)", fr"\1{new_value}", line)
                        new_lines.append(new_line.rstrip() + os.linesep)
                        modified_flags.add(flag_name)
                        matched = True
                        break
                if not matched:
                    new_lines.append(line.rstrip() + os.linesep)

            if len(modified_flags) != len(self.vars_map):
                missing = [f for f in self.vars_map if f not in modified_flags]
                self._update_status(f"Aviso: Flags não encontradas/modificadas: {', '.join(missing)}.", "orange")

            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

            self._update_status(f"Salvo! Backup: {backup_path.name}", "green")

        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar '{self.config_path}':\n{e}", parent=self)
            self._update_status(f"Erro ao salvar: {e}", "red")

    def _update_status(self, message, color):
        """Atualiza o label de status principal."""
        self.status_label.config(text=message, foreground=color)


if __name__ == "__main__":
    app = ConfigApp(config_py_path)
    app.mainloop()