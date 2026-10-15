from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import subprocess
import tkinter as tk
from tkinter import ttk
from persistencia.auth import require_dev_mode
from utils.paths import PROJECT_ROOT


def main():
    require_dev_mode()
    root = tk.Tk()
    root.title('NexlifyTTk — Ferramentas de desenvolvimento')
    frame = ttk.Frame(root, padding=24)
    frame.pack(fill='both', expand=True)
    def launch(script):
        subprocess.Popen([sys.executable, str(PROJECT_ROOT / 'instalacao' / script)], cwd=PROJECT_ROOT,
                         creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    for title, script in [('Configurar banco', 'config_banco_gui.py'), ('Configurar ambiente', 'config_gui.py'),
                          ('Configurar envio de e-mail', 'config_email.py'),
                          ('Monitor de processos', 'monitor_processo.py'), ('Gerenciar logs', 'limpa_logs.py'),
                          ('Backup e recriação do SQLite de dev', 'resetar_banco_de_dados.py')]:
        ttk.Button(frame, text=title, command=lambda s=script: launch(s)).pack(fill='x', pady=5)
    ttk.Label(frame, text='O reset de senha do admin é uma ferramenta separada na raiz.', wraplength=360).pack(pady=12)
    root.mainloop()


if __name__ == '__main__':
    main()
