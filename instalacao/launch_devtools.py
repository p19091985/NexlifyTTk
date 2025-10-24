import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
from pathlib import Path

try:
    INSTALL_DIR = Path(__file__).parent.resolve()
    PROJECT_ROOT = INSTALL_DIR.parent.resolve()

    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    SCRIPT_CONFIG_INI = INSTALL_DIR / "config_banco_gui.py"
    SCRIPT_CREDENCIAIS = INSTALL_DIR / "gerador_credenciais_gui.py"
    SCRIPT_CONFIG_PY = INSTALL_DIR / "config_gui.py"

    missing = []
    if not SCRIPT_CONFIG_INI.is_file(): missing.append(SCRIPT_CONFIG_INI.name)
    if not SCRIPT_CREDENCIAIS.is_file(): missing.append(SCRIPT_CREDENCIAIS.name)
    if not SCRIPT_CONFIG_PY.is_file(): missing.append(SCRIPT_CONFIG_PY.name)
    if missing:
        raise FileNotFoundError(f"Scripts não encontrados: {', '.join(missing)}")

except FileNotFoundError as e:
    messagebox.showerror("Erro Crítico",
                         f"Scripts essenciais não encontrados na pasta '{INSTALL_DIR}':\n\n{e}\n\nO lançador não pode continuar.")
    sys.exit(1)
except Exception as e:
    messagebox.showerror("Erro Crítico", f"Erro ao configurar caminhos: {e}")
    sys.exit(1)

def launch_script(script_path: Path):
    """Lança um script Python como um processo separado."""
    try:
        process = subprocess.Popen([sys.executable, str(script_path)], cwd=PROJECT_ROOT)
        print(f"Lançado: {script_path.name} (PID: {process.pid})")
    except Exception as e:
        messagebox.showerror("Erro ao Lançar", f"Não foi possível iniciar o script '{script_path.name}':\n{e}")

class LauncherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🚀 Lançador DevTools (Desktop) 🚀")

        w = 450                     
        h = 320

        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()

        x = (sw // 2) - (w // 2)
        y = (sh // 2) - (h // 2)

        self.geometry(f"{w}x{h}+{x}+{y}")

        self.minsize(400, 280)

        self._setup_styles()
        self._create_widgets()

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TButton", font=("Segoe UI", 11), padding=10)
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("Info.TLabel", font=("Segoe UI", 10), foreground="#333")

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Ferramentas de Desenvolvimento", style="Header.TLabel").pack(pady=(0, 15))
        ttk.Label(main_frame, text="Clique em um botão para abrir a ferramenta:", style="Info.TLabel").pack(pady=(0, 20))

        btn_config_ini = ttk.Button(main_frame, text="🗃️ Configurar Conexão (banco.ini)",
                                    command=lambda: launch_script(SCRIPT_CONFIG_INI))
        btn_config_ini.pack(fill="x", pady=6, ipady=4)

        btn_credenciais = ttk.Button(main_frame, text="🔑 Gerar Credenciais / Hashes",
                                     command=lambda: launch_script(SCRIPT_CREDENCIAIS))
        btn_credenciais.pack(fill="x", pady=6, ipady=4)

        btn_config_py = ttk.Button(main_frame, text="⚙️ Configurar Flags (config.py)",
                                   command=lambda: launch_script(SCRIPT_CONFIG_PY))
        btn_config_py.pack(fill="x", pady=6, ipady=4)

if __name__ == "__main__":
    app = LauncherApp()
    app.mainloop()