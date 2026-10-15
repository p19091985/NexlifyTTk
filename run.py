"""Entrada desktop e diagnóstico automatizável, independente da pasta atual."""
import sys
import logging
import threading
import time
from utils.paths import PROJECT_ROOT


def main():
    import argparse
    parser = argparse.ArgumentParser(description='NexlifyTTk')
    parser.add_argument('--diagnose', action='store_true')
    parser.add_argument('--no-db', action='store_true', help='Diagnóstico sem conectar ao banco')
    parser.add_argument('--check-gui', action='store_true', help='No diagnóstico, verifica também a criação de uma janela Tk')
    args = parser.parse_args()
    if args.diagnose:
        from utils.diagnostics import diagnose
        import json
        results = diagnose(check_database=not args.no_db, check_tk=args.check_gui)
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return int(any(row['status'] == 'FAIL' for row in results))
    import config
    from persistencia.logger import setup_loggers
    from persistencia.database import DatabaseManager
    import tkinter as tk
    from tkinter import messagebox
    from utils.startup_splash import StartupSplash
    splash = None
    try:
        config.validate()
        setup_loggers()
        splash = StartupSplash(str(PROJECT_ROOT), logging.getLogger('startup'))
        splash.set_status('Verificando banco e carregando módulos...')
        result = {}
        def prepare():
            try:
                if config.API_MODE != 'client' and config.DATABASE_ENABLED and config.INITIALIZE_DATABASE_ON_STARTUP:
                    DatabaseManager.initialize_database()
                from app import AplicacaoPrincipal
                result['app'] = AplicacaoPrincipal
            except Exception as error:
                result['error'] = error
        worker = threading.Thread(target=prepare, daemon=True)
        worker.start()
        while worker.is_alive():
            splash.pump()
            if splash.cancelled:
                return 0
            time.sleep(0.02)
        if 'error' in result:
            raise result['error']
        splash.close()
        splash = None
        if config.USE_LOGIN and config.API_MODE != 'client':
            from sqlalchemy import select, func
            from persistencia.schema import usuarios
            with DatabaseManager.get_engine().connect() as connection:
                empty = connection.execute(select(func.count()).select_from(usuarios)).scalar_one() == 0
            if empty:
                from dialogs.password_dialog import PasswordDialog
                root = tk.Tk()
                root.withdraw()
                dialog = PasswordDialog(root, mode='bootstrap')
                root.wait_window(dialog)
                success = dialog.success
                root.destroy()
                if not success:
                    return 0
        from theme import set_active_theme_colors
        from settings_manager import SettingsManager
        from persistencia.auth import clear_session
        while True:
            clear_session()
            settings = SettingsManager(str(PROJECT_ROOT)).load_settings()
            set_active_theme_colors(settings['active_theme'])
            app = result['app'](project_root=str(PROJECT_ROOT))
            try:
                if app.winfo_exists():
                    app.mainloop()
            except tk.TclError:
                pass
            if not getattr(app, '_restart_requested', False):
                break
        return 0
    except Exception as error:
        logging.getLogger('startup').error('Inicialização falhou (%s).', type(error).__name__)
        if splash:
            splash.close()
            splash = None
        try:
            root = tk.Tk()
            root.withdraw()
            detail = str(error) if isinstance(error, (ValueError, PermissionError)) else 'Verifique o banco, os drivers e as dependências pelo diagnóstico.'
            messagebox.showerror('Falha na inicialização', detail, parent=root)
            root.destroy()
        except tk.TclError:
            print('Não foi possível abrir a interface gráfica. Execute --diagnose.', file=sys.stderr)
        return 1
    finally:
        if splash:
            splash.close()
        DatabaseManager.dispose()


if __name__ == '__main__':
    raise SystemExit(main())
