from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import configparser
import io
import os
import tkinter as tk
from tkinter import ttk, messagebox
from utils.paths import PROJECT_ROOT
from utils.secure_files import atomic_write_private


def main():
    from persistencia.auth import require_dev_mode
    require_dev_mode()
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.read([PROJECT_ROOT/'config_settings.ini', PROJECT_ROOT/'config.local.ini'], encoding='utf-8')
    if not cfg.has_section('Settings'):
        cfg.add_section('Settings')
    root = tk.Tk()
    root.title('Configuração local — Desenvolvimento')
    frame = ttk.Frame(root, padding=24)
    frame.pack()
    flags = {}
    for key, title, default in [('database_enabled','Habilitar banco',True),
                                ('initialize_database_on_startup','Verificar/criar schema ao iniciar',True),
                                ('mfa_enabled','MFA por e-mail (requer SMTP configurado)',False),
                                ('use_login','Exigir login',True), ('logging_enabled','Habilitar logs',True),
                                ('enable_theme_menu','Menu de temas',True)]:
        flags[key] = tk.BooleanVar(root, cfg.getboolean('Settings', key, fallback=default))
        ttk.Checkbutton(frame, text=title, variable=flags[key]).pack(anchor='w', pady=6)
    ttk.Label(frame, text='As alterações são locais e exigem reiniciar a aplicação.\nPara produção, use o perfil Operação do instalador.', wraplength=420).pack(pady=12)
    def save():
        if not flags['database_enabled'].get() and (flags['use_login'].get() or flags['initialize_database_on_startup'].get()):
            messagebox.showerror('Configuração inválida', 'Login e inicialização de schema requerem banco habilitado.', parent=root)
            return
        for key, variable in flags.items():
            cfg['Settings'][key] = str(variable.get())
        stream = io.StringIO()
        cfg.write(stream)
        atomic_write_private(PROJECT_ROOT/'config.local.ini', stream.getvalue())
        messagebox.showinfo('Configuração salva', 'Reinicie a aplicação.', parent=root)
    ttk.Button(frame, text='Salvar', command=save).pack(anchor='e')
    root.mainloop()


if __name__ == '__main__':
    main()
