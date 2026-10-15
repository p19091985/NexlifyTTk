from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tkinter as tk
from tkinter import ttk
import psutil
from utils.paths import PROJECT_ROOT


class ProcessMonitor(tk.Toplevel):
    """Monitor somente leitura; não expõe a linha de comando nem segredos."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title('NexlifyTTk — Monitor de processos')
        self.geometry('680x360')
        self.tree = ttk.Treeview(self, columns=('pid','name','cpu','ram'), show='headings')
        for key, title in [('pid','PID'),('name','Processo'),('cpu','CPU %'),('ram','RAM MB')]:
            self.tree.heading(key, text=title)
            self.tree.column(key, width=140)
        self.tree.pack(fill='both', expand=True, padx=16, pady=16)
        self.processes = {}
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for process in psutil.process_iter(['pid','name','cwd']):
            try:
                cwd = process.info.get('cwd')
                if not cwd or not Path(cwd).resolve().is_relative_to(PROJECT_ROOT):
                    continue
                cached = self.processes.setdefault(process.pid, process)
                self.tree.insert('', 'end', values=(process.pid, process.info['name'], cached.cpu_percent(),
                                                     round(cached.memory_info().rss / 1024**2, 1)))
            except (psutil.Error, OSError):
                continue
        self.after(1500, self.refresh)


if __name__ == '__main__':
    from persistencia.auth import require_dev_mode
    require_dev_mode()
    root = tk.Tk()
    root.withdraw()
    dialog = ProcessMonitor(root)
    root.wait_window(dialog)
    root.destroy()
