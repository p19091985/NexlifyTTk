"""Configuração assistida de um banco por instalação, com teste antes de salvar."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse
import configparser
import io
import os
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy import select, literal
from persistencia.database import CONFIG_PATH, DRIVERS, DatabaseManager, create_database_engine, read_database_config
from persistencia.security import encrypt_message
from utils.secure_files import atomic_write_private


def save_database_config(options, path=CONFIG_PATH):
    parser = configparser.ConfigParser(interpolation=None)
    parser['database'] = {key: str(value) for key, value in options.items() if value != ''}
    stream = io.StringIO()
    parser.write(stream)
    atomic_write_private(path, stream.getvalue())


class DatabaseConfigApp:
    def __init__(self, root, selected_type=None):
        self.root = root
        self.root.title('NexlifyTTk — Configurar banco')
        self.current = read_database_config()
        self.events = queue.Queue()
        self.busy = False
        frame = ttk.Frame(root, padding=24)
        frame.pack(fill='both', expand=True)
        frame.columnconfigure(1, weight=1)
        ttk.Label(frame, text='Banco desta instalação', font=('Segoe UI', 16, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w')
        ttk.Label(frame, text='SQLite funciona sem servidor. Para os demais, prepare o servidor e o banco vazio.\n'
                  'O teste usa conexão real; criar tabelas não apaga os dados existentes.', wraplength=620).grid(row=1, column=0, columnspan=2, pady=12, sticky='w')
        self.variables = {}
        fields = [('type','Tipo de banco'), ('path','Arquivo SQLite'), ('host','Servidor'), ('port','Porta'),
                  ('dbname','Banco / serviço Oracle'), ('user','Usuário'), ('password','Senha (vazia mantém a atual)'),
                  ('password_env','Ou variável de ambiente da senha'), ('ssl_ca','Certificado CA (PostgreSQL/MySQL)'),
                  ('sslmode','PostgreSQL sslmode'), ('odbc_driver','SQL Server driver ODBC'),
                  ('oracle_protocol','Oracle protocolo (tcps/tcp)')]
        self.entries = {}
        defaults = {'path':'NexlifyTTk.db','sslmode':'verify-full','odbc_driver':'ODBC Driver 18 for SQL Server','oracle_protocol':'tcps'}
        for row, (key, label) in enumerate(fields, 2):
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky='w', padx=(0, 12), pady=5)
            value = '' if key == 'password' else self.current.get(key, defaults.get(key, ''))
            if key == 'type' and selected_type:
                value = selected_type
            variable = tk.StringVar(root, value)
            self.variables[key] = variable
            if key == 'type':
                entry = ttk.Combobox(frame, textvariable=variable, values=tuple(DRIVERS), state='readonly', width=38)
                entry.bind('<<ComboboxSelected>>', self.refresh)
            else:
                entry = ttk.Entry(frame, textvariable=variable, show='•' if key == 'password' else '', width=40)
            entry.grid(row=row, column=1, sticky='ew')
            self.entries[key] = entry
        self.initialize = tk.BooleanVar(root, True)
        ttk.Checkbutton(frame, text='Criar/verificar tabelas após testar a conexão', variable=self.initialize).grid(row=14, column=0, columnspan=2, sticky='w', pady=8)
        self.status = tk.StringVar(root, 'A configuração atual é preservada até o teste passar.')
        ttk.Label(frame, textvariable=self.status, wraplength=620).grid(row=15, column=0, columnspan=2, sticky='w', pady=8)
        self.button = ttk.Button(frame, text='Testar e salvar configuração', command=self.start)
        self.button.grid(row=16, column=0, columnspan=2, sticky='e')
        self.refresh()
        root.protocol('WM_DELETE_WINDOW', lambda: None if self.busy else root.destroy())
        root.after(100, self.poll)

    def refresh(self, event=None):
        kind = self.variables['type'].get()
        for key, entry in self.entries.items():
            if key == 'type':
                continue
            enabled = key == 'path' if kind == 'sqlite' else key != 'path'
            if key in {'ssl_ca', 'sslmode', 'odbc_driver', 'oracle_protocol'}:
                enabled = (key == 'ssl_ca' and kind in {'postgresql','mysql','mariadb','oracle'}) or (key == 'sslmode' and kind == 'postgresql') or (key == 'odbc_driver' and kind == 'sqlserver') or (key == 'oracle_protocol' and kind == 'oracle')
            entry.configure(state='normal' if enabled else 'disabled')

    def start(self):
        options = {key: variable.get().strip() for key, variable in self.variables.items() if key != 'password'}
        password = self.variables['password'].get()
        kind = options['type']
        if kind == 'sqlite':
            options = {'type': kind, 'path': options['path']}
        elif not options.get('password_env'):
            options['password'] = encrypt_message(password) if password else self.current.get('password', '') if self.current.get('type') == kind else ''
        self.variables['password'].set('')
        self.busy = True
        self.button.state(['disabled'])
        self.status.set('Testando conexão e schema...')
        initialize = self.initialize.get()
        def worker():
            engine = None
            try:
                engine = create_database_engine(options)
                with engine.connect() as connection:
                    connection.execute(select(literal(1))).scalar_one()
                if initialize:
                    DatabaseManager.initialize_database(engine)
                save_database_config(options)
                self.events.put(('ok', options))
            except Exception as error:
                # Driver exceptions can contain usernames/URLs: do not display them.
                self.events.put(('error', type(error).__name__))
            finally:
                if engine is not None:
                    engine.dispose()
        threading.Thread(target=worker, daemon=True).start()

    def poll(self):
        try:
            kind, data = self.events.get_nowait()
            self.busy = False
            self.button.state(['!disabled'])
            if kind == 'ok':
                self.current = data
                self.status.set('Conexão verificada e configuração salva. Reinicie a aplicação para usar este banco.')
                messagebox.showinfo('Banco configurado', 'Pronto. Inicie o programa; bancos sem usuários solicitarão a criação do admin.', parent=self.root)
            else:
                self.status.set(f'Falha ({data}). Confira servidor, driver, certificado e credenciais. A configuração anterior foi preservada.')
        except queue.Empty:
            pass
        self.root.after(100, self.poll)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', choices=tuple(DRIVERS))
    args = parser.parse_args()
    root = tk.Tk()
    DatabaseConfigApp(root, args.type)
    root.mainloop()


if __name__ == '__main__':
    main()
