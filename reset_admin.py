"""Recuperação local do admin, exclusivamente no ambiente de desenvolvimento."""
import sys


def main():
    from persistencia.auth import require_dev_mode
    try:
        require_dev_mode()
    except PermissionError as error:
        print(str(error), file=sys.stderr)
        return 1
    import tkinter as tk
    from dialogs.password_dialog import PasswordDialog
    from persistencia.database import DatabaseManager
    from persistencia.logger import setup_loggers
    from theme import apply_dark_theme
    from tkinter import ttk, messagebox
    setup_loggers()
    root = tk.Tk()
    root.withdraw()
    try:
        DatabaseManager.initialize_database()
        apply_dark_theme(ttk.Style(root))
        dialog = PasswordDialog(root, mode='reset')
        root.wait_window(dialog)
        return 0 if dialog.success else 1
    except Exception:
        messagebox.showerror('Reset não realizado', 'Verifique a configuração e a disponibilidade do banco.', parent=root)
        return 1
    finally:
        root.destroy()
        DatabaseManager.dispose()


if __name__ == '__main__':
    raise SystemExit(main())
