import gc
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
import pytest
from theme import C, set_active_theme_colors
from utils.ui_components import Tooltip
PASSWORD = 'Teste seguro do template 2026!'

pytestmark = pytest.mark.gui


@pytest.fixture(autouse=True)
def release_tk_objects_on_main_thread():
    # Destroyed widgets can retain cycles. Collect them before the next test
    # starts a worker, so Tk variable finalizers stay on their creating thread.
    yield
    gc.collect()


def test_mfa_enrollment_and_login_widgets(administrator, email_enabled, tmp_path, monkeypatch):
    from persistencia import security
    from dialogs.mfa_dialog import MfaDialog
    from dialogs.login_ui import LoginDialog
    from sqlalchemy import select
    from persistencia.schema import user_security
    monkeypatch.delenv('NEXLIFY_SECRET_KEY', raising=False)
    monkeypatch.setattr(security, 'KEY_PATH', tmp_path/'.secrets/secret.key')
    def fail(title, message, **kwargs):
        raise AssertionError(message)
    monkeypatch.setattr(messagebox, 'showerror', fail)
    monkeypatch.setattr(messagebox, 'showwarning', fail)
    root = tk.Tk()
    root.withdraw()
    try:
        dialog = MfaDialog(root)
        root.update()
        dialog.email.insert(0, 'admin@example.org')
        dialog.send()
        dialog.code.insert(0, email_enabled[-1][1])
        dialog.confirm()
        assert dialog.success
        recovery = dialog.recovery.get('1.0', 'end').splitlines()[-8:]
        assert len(recovery) == 8 and len(recovery[0]) >= 20
        dialog.destroy()
        login = LoginDialog(root)
        login.user_entry.insert(0, 'admin')
        login.pass_entry.insert(0, PASSWORD)
        assert not login.otp_entry.winfo_ismapped()
        login._on_login()
        assert login.user_info is None
        assert email_enabled[-1][0] == 'admin@example.org'
        login.otp_entry.insert(0, email_enabled[-1][1])
        login._on_login()
        assert login.user_info['username'] == 'admin'
    finally:
        root.destroy()


def test_app_panels_and_theme(administrator, tmp_path, monkeypatch):
    from persistencia import auth
    import dialogs.login_ui
    class LoginStub(tk.Toplevel):
        def __init__(self, parent):
            super().__init__(parent)
            self.user_info = auth.verify_user_credentials('admin', PASSWORD)
            self.after_idle(self.destroy)
    monkeypatch.setattr(dialogs.login_ui, 'LoginDialog', LoginStub)
    def fail(title, message, **kwargs):
        raise AssertionError(f'{title}: {message}')
    monkeypatch.setattr(messagebox, 'showerror', fail)
    from app import AplicacaoPrincipal
    app = AplicacaoPrincipal(str(tmp_path))
    try:
        app.update()
        assert len([value for value in app.panels.values() if value is not None]) == 1
        for name in app.panel_specs:
            app.switch_panel_by_name(name)
            app.update_idletasks()
            assert app.panels[name] is not None
        set_active_theme_colors('Drácula')
        app._on_theme_changed()
        assert app.cget('background') == C['bg_dark']
        app._apply_theme_settings(app.style, {'font_size':11, 'font_family':'Segoe UI', 'custom_colors':{}})
        app._save_window_position(notify=False)
        assert app.winfo_width() > 400
        # Expiration/revocation must close protected windows without waiting
        # for the user to dismiss a message box over still-visible data.
        monkeypatch.setattr(messagebox, 'showinfo', fail)
        auth.clear_session()
        app._check_session()
        assert app._restart_requested
        with pytest.raises(tk.TclError):
            app.winfo_exists()
    finally:
        try:
            app.destroy()
        except tk.TclError:
            pass
        set_active_theme_colors('Gato a Noite')


def test_page_navigation_menus_and_direct_access_for_every_role(access_user, tmp_path, monkeypatch):
    from importlib import import_module
    from persistencia import auth
    from persistencia.access_policy import PageAccessDenied
    from panels import ALL_PANELS
    from utils.installation_profile import write_installation_profile_marker
    import dialogs.login_ui
    write_installation_profile_marker(tmp_path, 'dev')
    class LoginStub(tk.Toplevel):
        def __init__(self, parent):
            super().__init__(parent)
            self.user_info = auth.verify_user_credentials('profile_test', PASSWORD)
            self.after_idle(self.destroy)
    monkeypatch.setattr(dialogs.login_ui, 'LoginDialog', LoginStub)
    warnings = []
    monkeypatch.setattr(messagebox, 'showwarning', lambda *args, **kwargs: warnings.append(args))
    def fail(title, message, **kwargs):
        pytest.fail(f'{title}: {message}')
    monkeypatch.setattr(messagebox, 'showerror', fail)
    from app import AplicacaoPrincipal
    app = AplicacaoPrincipal(str(tmp_path))
    try:
        app.update()
        assert set(app.sidebar_buttons) == access_user['pages']
        menu = app.topbar_menus['Painéis']
        assert {menu.entrycget(i, 'label') for i in range(menu.index('end') + 1)} == access_user['pages']
        role = access_user['user']['access_level']
        assert ('Desenvolvimento' in app.topbar_menus) == (role == auth.ADMIN)
        settings = app.topbar_menus['Configurações']
        labels = {settings.entrycget(i, 'label') for i in range(settings.index('end') + 1)}
        assert ('Envio de e-mail / SMTP' in labels) == (role == auth.ADMIN)
        assert ('Diagnóstico da instalação' in labels) == (role in {auth.ADMIN, 'Gerente de TI'})
        for spec in ALL_PANELS:
            name = spec['name']
            if name in access_user['pages']:
                app.switch_panel_by_name(name)
                app.update()
                assert app.current_panel_name == name
                assert app.panels[name].winfo_ismapped()
                if role == 'Auditor Externo' and name != 'Guia de Configuração':
                    assert app.panels[name].read_only
                    def visible_buttons(widget):
                        result = []
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Button) and child.winfo_ismapped():
                                result.append(child.cget('text'))
                            result.extend(visible_buttons(child))
                        return result
                    assert visible_buttons(app.panels[name]) == [
                        'Atualizar lista' if name == 'Gestão de Espécies (Gatos)' else 'Atualizar tabelas']
            else:
                previous = app.current_panel_name
                # Mesmo adulterando o registro local, a sessão não ganha acesso.
                app.panel_specs[name] = spec
                app.switch_panel_by_name(name)
                assert app.current_panel_name == previous
                assert app._instantiate_panel(name) is None
                assert not app.panels.get(name)
                panel_class = getattr(import_module(spec['module']), spec['class_name'])
                with pytest.raises(PageAccessDenied):
                    panel_class(app.content_frame, app)
        if role != auth.ADMIN:
            before = len(warnings)
            app._open_email_settings()
            app._open_devtools()
            app._open_process_monitor()
            app._open_visual_test()
            app._open_factory_reset()
            assert len(warnings) == before + 5
        if role in {'Supervisor de Produção', 'Operador de Linha', 'Auditor Externo'}:
            from modals.tipos_vegetais_controller import TiposVegetaisController
            with pytest.raises(PageAccessDenied):
                TiposVegetaisController(app)
        # O painel já criado também precisa de uma sessão válida para reabrir.
        cached = app.current_panel_name
        auth.clear_session()
        app.switch_panel_by_name(cached)
        assert app._restart_requested
        with pytest.raises(tk.TclError):
            app.winfo_exists()
    finally:
        try:
            app.destroy()
        except tk.TclError:
            pass


def test_role_change_closes_cached_admin_page(administrator, tmp_path, monkeypatch):
    from persistencia import auth
    from persistencia.schema import usuarios
    from sqlalchemy import update
    import dialogs.login_ui
    class LoginStub(tk.Toplevel):
        def __init__(self, parent):
            super().__init__(parent)
            self.user_info = auth.verify_user_credentials('admin', PASSWORD)
            self.after_idle(self.destroy)
    monkeypatch.setattr(dialogs.login_ui, 'LoginDialog', LoginStub)
    from app import AplicacaoPrincipal
    app = AplicacaoPrincipal(str(tmp_path))
    try:
        app.switch_panel_by_name('Gestão de Usuários')
        assert app.panels['Gestão de Usuários'] is not None
        with administrator.begin() as connection:
            connection.execute(update(usuarios).values(tipo_acesso='Auditor Externo'))
        app.switch_panel_by_name('Gestão de Usuários')
        assert app._restart_requested
        with pytest.raises(tk.TclError):
            app.winfo_exists()
    finally:
        try:
            app.destroy()
        except tk.TclError:
            pass


def test_tooltip_uses_active_theme():
    root = tk.Tk()
    root.withdraw()
    tooltip = None
    try:
        button = tk.Button(root, text='Teste')
        tooltip = Tooltip(button, 'Ajuda', delay=0)
        tooltip._show()
        assert tooltip._tipwindow.cget('background') == C['bg_toolbar']
    finally:
        if tooltip:
            tooltip._hide()
        root.destroy()


def test_password_dialog_fields_and_cancel(database):
    from dialogs.password_dialog import PasswordDialog
    root = tk.Tk()
    root.withdraw()
    try:
        dialog = PasswordDialog(root, mode='bootstrap')
        root.update_idletasks()
        assert len(dialog.fields) == 2
        assert all(field.cget('show') for field in dialog.fields)
        assert not dialog.success
        dialog.destroy()
    finally:
        root.destroy()


def test_login_shake_accepts_negative_coordinates(monkeypatch):
    from dialogs.login_ui import LoginDialog
    import dialogs.login_ui as login
    root = tk.Tk()
    root.withdraw()
    try:
        dialog = LoginDialog(root)
        monkeypatch.setattr(dialog, 'winfo_x', lambda: -20)
        monkeypatch.setattr(dialog, 'winfo_y', lambda: -10)
        monkeypatch.setattr(login.time, 'sleep', lambda seconds: None)
        dialog._shake_window()
        dialog.destroy()
    finally:
        root.destroy()


def test_first_run_splash_and_admin_dialog_can_be_cancelled(database, tmp_path, monkeypatch):
    import run
    import dialogs.password_dialog as passwords
    import persistencia.logger as logger
    from sqlalchemy import select, func
    from persistencia.schema import usuarios
    original = passwords.PasswordDialog
    opened = []
    class CancelBootstrap(original):
        def __init__(self, parent, mode):
            super().__init__(parent, mode)
            opened.append(mode)
            self.after(100, self.destroy)
    monkeypatch.setattr(passwords, 'PasswordDialog', CancelBootstrap)
    monkeypatch.setattr(run, 'PROJECT_ROOT', tmp_path)
    monkeypatch.setattr(run.sys, 'argv', ['run.py'])
    monkeypatch.setattr(logger, 'setup_loggers', lambda: None)
    assert run.main() == 0
    assert opened == ['bootstrap']
    with database.connect() as connection:
        assert connection.execute(select(func.count()).select_from(usuarios)).scalar_one() == 0


def test_email_unavailable_still_allows_recovery_in_login(administrator, email_enabled, monkeypatch):
    from persistencia import mfa
    from dialogs.login_ui import LoginDialog
    mfa.begin_enrollment('admin@example.org')
    recovery = mfa.confirm_enrollment(email_enabled[-1][1])
    def offline(*args):
        raise ConnectionError('offline')
    monkeypatch.setattr(mfa, 'send_code', offline)
    root = tk.Tk()
    root.withdraw()
    try:
        login = LoginDialog(root)
        login.user_entry.insert(0, 'admin')
        login.pass_entry.insert(0, PASSWORD)
        login._on_login()
        root.update()
        assert login.user_info is None
        assert login.otp_entry.winfo_ismapped()
        assert 'SMTP' in login.mfa_status.cget('text')
        login.otp_entry.insert(0, recovery[0])
        login._on_login()
        assert login.user_info['username'] == 'admin'
    finally:
        root.destroy()


def test_reauth_ui_does_not_ask_for_code_when_disabled(administrator, monkeypatch):
    import time
    from persistencia import auth
    from dialogs import mfa_dialog
    auth._session.set(dict(auth._session.get(), _reauthenticated_at=time.monotonic()-301))
    prompts = []
    def ask(title, prompt, **kwargs):
        prompts.append(prompt)
        return PASSWORD
    monkeypatch.setattr(mfa_dialog.simpledialog, 'askstring', ask)
    assert mfa_dialog.ensure_recent_auth(None)
    assert prompts == ['Senha atual:']
