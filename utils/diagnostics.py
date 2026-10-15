"""Diagnósticos sem publicar URLs, credenciais ou conteúdo dos dados."""
import importlib
import platform
import sys
from pathlib import Path


def diagnose(check_database=True, check_tk=False):
    results = []
    def record(name, callback):
        try:
            detail = callback()
            results.append({'check': name, 'status': 'OK', 'detail': str(detail)})
        except Exception as error:
            results.append({'check': name, 'status': 'FAIL', 'detail': type(error).__name__})
    record('Python', lambda: platform.python_version())
    results.append({'check': 'Ambiente virtual', 'status': 'OK' if sys.prefix != sys.base_prefix else 'FAIL',
                    'detail': 'Python isolado' if sys.prefix != sys.base_prefix else 'Use a .venv'})
    import config
    modules = ['pandas', 'sqlalchemy', 'bcrypt', 'cryptography', 'psutil', 'argon2', 'httpx']
    if config.API_MODE != 'server':
        modules.append('tkinter')
    for module in modules:
        record(module, lambda name=module: getattr(importlib.import_module(name), '__version__', 'Disponível'))
    import config
    record('Configuração', lambda: config.validate() or 'Válida')
    if check_tk:
        def window():
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            root.update_idletasks()
            root.destroy()
            return 'Janela criada'
        record('Janela Tk', window)
    if check_database and config.API_MODE == 'client':
        def remote():
            import httpx
            from services.transport import validate_service_url, tls_context
            response = httpx.get(validate_service_url(config.API_URL) + '/health', verify=tls_context(config.API_CA), timeout=10, trust_env=False)
            response.raise_for_status()
            return 'API disponível; cliente sem conexão direta ao banco'
        record('Conexão com API', remote)
    elif check_database and config.DATABASE_ENABLED:
        def database():
            from persistencia.database import DatabaseManager
            from sqlalchemy import select, literal, inspect
            engine = DatabaseManager.get_engine()
            with engine.connect() as connection:
                connection.execute(select(literal(1))).scalar_one()
            return f'{engine.dialect.name}; {len(inspect(engine).get_table_names())} tabelas'
        record('Conexão com banco', database)
    return results
