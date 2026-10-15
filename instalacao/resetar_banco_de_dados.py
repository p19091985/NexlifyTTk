"""Reset explícito do SQLite de desenvolvimento, sempre precedido de backup verificado."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sqlite3
from datetime import datetime, timezone
import tkinter as tk
from tkinter import ttk, messagebox
from persistencia.auth import require_dev_mode
from persistencia.database import DatabaseManager
from persistencia.schema import metadata
from utils.paths import PROJECT_ROOT
from utils.secure_files import reject_link_path, private_directory
import os


def reset_development_database(confirmation):
    require_dev_mode()
    if confirmation != 'RECRIAR':
        raise ValueError('Digite RECRIAR para confirmar.')
    engine = DatabaseManager.get_engine()
    if engine.dialect.name != 'sqlite' or engine.url.database == ':memory:':
        raise ValueError('Este utilitário atende apenas SQLite local de desenvolvimento.')
    database = reject_link_path(engine.url.database).resolve()
    if not database.is_relative_to(PROJECT_ROOT.resolve()):
        raise ValueError('O banco deve ser um arquivo local dentro deste projeto.')
    directory = PROJECT_ROOT/'.runtime'/'backups'
    private_directory(directory)
    backup = directory/f'nexlify-{datetime.now(timezone.utc):%Y%m%d-%H%M%S-%f}.db'
    descriptor = os.open(backup, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(descriptor)
    with sqlite3.connect(database) as source, sqlite3.connect(backup) as target:
        source.backup(target)
        if target.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise RuntimeError('Backup não passou na verificação de integridade. Reset cancelado.')
    metadata.drop_all(engine)
    DatabaseManager.initialize_database(engine)
    return backup


def main():
    require_dev_mode()
    root = tk.Tk()
    root.title('Recriar SQLite — DEV')
    frame = ttk.Frame(root, padding=24)
    frame.pack()
    ttk.Label(frame, text='Feche todas as janelas do programa antes de continuar.\n'
              'Esta ação apaga os dados do template e cria um banco vazio.\n'
              'Um backup verificado será salvo em .runtime/backups.\n\nDigite RECRIAR para confirmar.', wraplength=500).pack()
    confirm = ttk.Entry(frame)
    confirm.pack(fill='x', pady=12)
    def run():
        try:
            backup = reset_development_database(confirm.get())
        except (PermissionError, ValueError) as error:
            messagebox.showerror('Reset cancelado', str(error), parent=root)
            return
        except Exception:
            messagebox.showerror('Falha', 'Reset não concluído. Consulte os backups antes de continuar.', parent=root)
            return
        messagebox.showinfo('Banco recriado', f'Backup: {backup}\nO próximo início solicitará um novo admin.', parent=root)
        root.destroy()
    ttk.Button(frame, text='Fazer backup e recriar banco', command=run).pack()
    root.mainloop()


if __name__ == '__main__':
    main()
