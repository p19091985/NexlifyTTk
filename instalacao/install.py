"""Instalador GUI/CLI sem dependências externas antes de criar a .venv."""
from pathlib import Path
import argparse
import configparser
import importlib
import io
import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import venv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from utils.secure_files import atomic_write_private
DATABASES = ('sqlite', 'postgresql', 'mysql', 'mariadb', 'sqlserver', 'oracle', 'firebird')
DRIVER_REQUIREMENTS = {
    'sqlite': [], 'postgresql': ['psycopg[binary]==3.3.6'],
    'mysql': ['PyMySQL[rsa]==1.2.3'], 'mariadb': ['PyMySQL[rsa]==1.2.3'],
    'sqlserver': ['pyodbc==5.3.0'], 'oracle': ['oracledb==4.0.2'],
    'firebird': ['sqlalchemy-firebird==2.2.0'],
}


def python_path(root=ROOT):
    return Path(root) / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def check_prerequisites(create_venv=False, with_tk=True):
    if sys.version_info < (3, 11):
        raise RuntimeError('Instale Python 3.11 ou superior.')
    for module in (['tkinter'] if with_tk else []) + (['ensurepip'] if create_venv else []):
        try:
            importlib.import_module(module)
        except ImportError as error:
            if sys.platform.startswith('linux'):
                detail = ('Ubuntu/Debian: sudo apt install python3-venv python3-tk. '
                          'Fedora: sudo dnf install python3-tkinter python3-pip. '
                          'Use os pacotes correspondentes à versão do seu Python.')
            else:
                detail = 'Reinstale o Python com pip e Tcl/Tk habilitados.'
            raise RuntimeError(f'Pré-requisito ausente: {module}. {detail}') from error


def install(profile, database, emit=print, root=ROOT, *, mode=None, api_url=None):
    root = Path(root)
    if profile not in {'core', 'dev'} or database not in DATABASES:
        raise ValueError('Perfil ou banco inválido.')
    if profile == 'dev' and not (root / 'requirements-dev.lock').is_file():
        raise ValueError('Este pacote de operação não inclui ferramentas DEV; use o checkout de desenvolvimento.')
    defaults = configparser.ConfigParser(interpolation=None)
    defaults.read(root / 'config_settings.ini', encoding='utf-8')
    defaults.read(root / 'config.local.ini', encoding='utf-8')
    mode = mode or defaults.get('Settings', 'api_mode', fallback='local')
    api_url = api_url if api_url is not None else defaults.get('Settings', 'api_url', fallback='')
    if mode not in {'local', 'client', 'server'}:
        raise ValueError('Modo inválido.')
    if mode == 'client':
        if any((root / name).exists() for name in ('banco.local.ini', '.secrets', 'secret.key', '.venv/backup-before-evolution')) or list(root.glob('*.db')):
            raise ValueError('Instale o cliente em uma pasta limpa, usando o pacote client; esta pasta contém dados ou segredos de servidor.')
        from urllib.parse import urlsplit
        parsed = urlsplit(api_url)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError('Informe --api-url HTTPS sem credenciais.')
    python = python_path(root)
    check_prerequisites(create_venv=not python.exists(), with_tk=mode != 'server')
    if not python.exists():
        if (root / '.venv').exists():
            raise RuntimeError('A .venv existente pertence a outro sistema ou está incompleta. Preserve-a e crie um ambiente local.')
        emit('Criando .venv...')
        venv.EnvBuilder(with_pip=True).create(root / '.venv')
    def run(arguments):
        process = subprocess.Popen([str(python), *arguments], cwd=root, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace',
                                   env=dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8'),
                                   creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        for line in process.stdout:
            emit(line.rstrip())
        if process.wait():
            raise RuntimeError('Uma etapa falhou. Consulte a saída da instalação e execute novamente.')
    emit('Atualizando pip e instalando o perfil selecionado...')
    requirements = 'requirements-dev.lock' if profile == 'dev' else 'requirements-server.lock' if mode == 'server' else 'requirements-core.lock'
    run(['-m', 'pip', 'install', '--only-binary=:all:', '--require-hashes', '-r', 'requirements/pip.lock'])
    run(['-m', 'pip', 'install', '--only-binary=:all:', '--require-hashes', '-r', requirements])
    if mode != 'client' and database != 'sqlite':
        driver = 'mysql' if database == 'mariadb' else database
        run(['-m', 'pip', 'install', '--only-binary=:all:', '--require-hashes', '-r', f'requirements/{driver}.lock'])
    run(['-m', 'pip', 'check'])
    cfg_path = root / 'config.local.ini'
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.read(root / 'config_settings.ini', encoding='utf-8')
    cfg.read(cfg_path, encoding='utf-8')
    if not cfg.has_section('Settings'):
        cfg.add_section('Settings')
    if not cfg.has_option('Settings', 'mfa_enabled'):
        cfg['Settings']['mfa_enabled'] = 'False'
    cfg['Settings']['api_mode'] = mode
    cfg['Settings']['api_url'] = api_url
    if mode == 'client':
        cfg['Settings']['initialize_database_on_startup'] = 'False'
    cfg['Settings']['environment'] = 'development' if profile == 'dev' else 'production'
    if profile == 'core':
        cfg['Settings']['use_login'] = 'True'
        cfg['Settings']['database_enabled'] = 'True'
        cfg['Settings']['logging_enabled'] = 'True'
    stream = io.StringIO()
    cfg.write(stream)
    atomic_write_private(cfg_path, stream.getvalue())
    run(['-c', 'from utils.installation_profile import write_installation_profile_marker; import sys; write_installation_profile_marker(sys.argv[1], sys.argv[2])', str(root), profile])
    run(['run.py', '--diagnose', '--no-db'])
    emit('Dependências verificadas. Configure e teste o banco antes do primeiro uso.')
    return python


def gui(mode=None, api_url=None):
    import tkinter as tk
    from tkinter import ttk, messagebox
    root = tk.Tk()
    root.title('Instalar NexlifyTTk')
    root.geometry('800x760')
    frame = ttk.Frame(root, padding=24)
    frame.pack(fill='both', expand=True)
    ttk.Label(frame, text='NexlifyTTk — Instalação', font=('Segoe UI', 19, 'bold')).pack(anchor='w')
    free = shutil.disk_usage(ROOT).free / 1024**3
    ttk.Label(frame, text=f'Python {sys.version.split()[0]} | espaço livre: {free:.1f} GB\n'
              'Recomendado: 4 GB de RAM e 1 GB livre. O servidor de banco externo é instalado separadamente.',
              wraplength=700).pack(anchor='w', pady=12)
    defaults = configparser.ConfigParser(interpolation=None)
    defaults.read(ROOT / 'config_settings.ini', encoding='utf-8')
    selected_mode = tk.StringVar(root, mode or defaults.get('Settings', 'api_mode', fallback='local'))
    selected_url = tk.StringVar(root, api_url or defaults.get('Settings', 'api_url', fallback=''))
    ttk.Label(frame, text='Modo: local, cliente da API ou servidor').pack(anchor='w')
    ttk.Combobox(frame, textvariable=selected_mode, values=('local', 'client', 'server'), state='readonly').pack(fill='x')
    ttk.Label(frame, text='Endereço HTTPS da API (somente cliente)').pack(anchor='w')
    ttk.Entry(frame, textvariable=selected_url).pack(fill='x', pady=4)
    profile = tk.StringVar(root, 'core')
    for value, title, detail in [('core','Operação','Aplicação, temas e diagnóstico; login obrigatório.'),
                                ('dev','Desenvolvimento','Inclui pytest, auditoria, monitor e ferramentas locais de manutenção.')]:
        box = ttk.LabelFrame(frame, text=title, padding=12)
        box.pack(fill='x', pady=4)
        ttk.Radiobutton(box, text=detail, variable=profile, value=value,
                        state='disabled' if value == 'dev' and not (ROOT / 'requirements-dev.lock').exists() else 'normal').pack(anchor='w')
    ttk.Label(frame, text='Banco desta instalação').pack(anchor='w', pady=(12, 4))
    database = tk.StringVar(root, 'sqlite')
    ttk.Combobox(frame, textvariable=database, values=DATABASES, state='readonly').pack(anchor='w')
    output = tk.Text(frame, height=13, wrap='word', state='disabled')
    output.pack(fill='both', expand=True, pady=12)
    events = queue.Queue()
    state = {'running': False}
    def worker(selected_profile, selected_database, mode_value, url_value):
        try:
            python = install(selected_profile, selected_database, lambda text: events.put(('log', text)), mode=mode_value, api_url=url_value)
            events.put(('done', (python, selected_database, mode_value)))
        except Exception as error:
            events.put(('error', str(error)))
    def start():
        state['running'] = True
        button.state(['disabled'])
        threading.Thread(target=worker, args=(profile.get(), database.get(), selected_mode.get(), selected_url.get()), daemon=True).start()
    button = ttk.Button(frame, text='Instalar e configurar banco', command=start)
    button.pack(anchor='e')
    def poll():
        try:
            while True:
                kind, value = events.get_nowait()
                if kind == 'log':
                    output.configure(state='normal')
                    output.insert('end', value + '\n')
                    output.see('end')
                    output.configure(state='disabled')
                else:
                    state['running'] = False
                    button.state(['!disabled'])
                    if kind == 'error':
                        messagebox.showerror('Instalação interrompida', value, parent=root)
                    else:
                        python, selected, completed_mode = value
                        if completed_mode == 'client':
                            messagebox.showinfo('Cliente instalado', 'Use iniciar.bat ou iniciar.sh. As credenciais do banco permanecem no servidor.', parent=root)
                            continue
                        if completed_mode == 'server':
                            messagebox.showinfo('Servidor instalado', 'Provisione o banco e configure TLS/auditoria conforme docs/SEGURANCA_OPERACAO.md.', parent=root)
                            continue
                        subprocess.Popen([str(python), str(ROOT/'instalacao/config_banco_gui.py'), '--type', selected], cwd=ROOT,
                                         creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                        messagebox.showinfo('Dependências instaladas', 'Conclua a configuração na janela do banco e depois use iniciar.bat ou iniciar.sh.', parent=root)
        except queue.Empty:
            pass
        root.after(100, poll)
    def close():
        if state['running']:
            messagebox.showinfo('Instalação em andamento', 'Aguarde o término para fechar.', parent=root)
        else:
            root.destroy()
    root.protocol('WM_DELETE_WINDOW', close)
    poll()
    root.mainloop()
    return 0


def main():
    parser = argparse.ArgumentParser(description='Instalador do template')
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--mode', choices=('local', 'client', 'server'))
    parser.add_argument('--api-url')
    parser.add_argument('--profile', choices=('core', 'dev'), default='core')
    parser.add_argument('--database', choices=DATABASES, default='sqlite')
    args = parser.parse_args()
    try:
        if not args.headless:
            check_prerequisites()
            try:
                return gui(args.mode, args.api_url)
            except importlib.import_module('tkinter').TclError:
                raise RuntimeError('Interface gráfica indisponível. Abra uma sessão desktop ou use --headless para instalar pelo terminal.') from None
        install(args.profile, args.database, mode=args.mode, api_url=args.api_url)
        return 0
    except Exception as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
