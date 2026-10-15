"""Manutenção explícita de logs locais, restrita ao desenvolvimento."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tkinter as tk
from tkinter import ttk, messagebox
from utils.paths import PROJECT_ROOT
from persistencia.auth import require_dev_mode


def main():
    require_dev_mode()
    root = tk.Tk()
    root.title('Gerenciar logs locais — DEV')
    frame = ttk.Frame(root, padding=24)
    frame.pack()
    ttk.Label(frame, text='Limpar os arquivos de log rotacionados?\nFeche a aplicação antes de continuar.\nA auditoria do banco não será apagada.').pack(pady=12)
    def clean():
        if not messagebox.askyesno('Confirmar', 'Apagar somente app.log e suas rotações locais?', parent=root):
            return
        directory = PROJECT_ROOT / 'logs'
        if directory.is_symlink():
            messagebox.showerror('Operação bloqueada', 'A pasta de logs não pode ser um link.', parent=root)
            return
        count = 0
        try:
            for path in directory.glob('app.log*'):
                if path.is_symlink() or path.parent.resolve() != directory.resolve() or not path.is_file():
                    continue
                if path.name not in {'app.log', *(f'app.log.{i}' for i in range(1,6))}:
                    continue
                path.unlink()
                count += 1
        except OSError:
            messagebox.showerror('Arquivo em uso', 'Feche o programa e tente novamente.', parent=root)
            return
        messagebox.showinfo('Concluído', f'{count} arquivo(s) removido(s).', parent=root)
    ttk.Button(frame, text='Limpar logs', command=clean).pack(pady=12)
    root.mainloop()


if __name__ == '__main__':
    main()
