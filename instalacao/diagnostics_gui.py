import queue
import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk
from utils.paths import PROJECT_ROOT


class DiagnosticsDialog(tk.Toplevel):
    def __init__(self, parent, run_tests=False):
        super().__init__(parent)
        self.title('Central de testes' if run_tests else 'Diagnóstico da instalação')
        self.geometry('820x520')
        self.events = queue.Queue()
        self.output = tk.Text(self, wrap='word', font=('Consolas', 10), state='disabled')
        self.output.pack(fill='both', expand=True, padx=16, pady=16)
        ttk.Button(self, text='Fechar', command=self.destroy).pack(pady=(0, 12))
        if run_tests:
            from persistencia.auth import require_dev_mode
            require_dev_mode()
        def worker():
            command = [sys.executable, '-m', 'pytest', '-q', '-m', 'not gui'] if run_tests else [sys.executable, str(PROJECT_ROOT / 'run.py'), '--diagnose']
            try:
                process = subprocess.Popen(command, cwd=PROJECT_ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                           env=dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8'),
                                           text=True, encoding='utf-8', errors='replace', creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                for line in process.stdout:
                    self.events.put(line)
                self.events.put(f'\nProcesso concluído com código {process.wait()}.\n')
            except Exception as error:
                self.events.put(f'Não foi possível iniciar o diagnóstico: {type(error).__name__}.\n')
        threading.Thread(target=worker, daemon=True).start()
        self.after(100, self.poll)

    def poll(self):
        try:
            while True:
                line = self.events.get_nowait()
                self.output.configure(state='normal')
                self.output.insert('end', line)
                self.output.see('end')
                self.output.configure(state='disabled')
        except queue.Empty:
            pass
        self.after(100, self.poll)
