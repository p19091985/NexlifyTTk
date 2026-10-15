import json
import subprocess
import sys
from pathlib import Path
import pytest
from settings_manager import SettingsManager
from utils.installation_profile import load_installation_profile, write_installation_profile_marker
from instalacao.install import DRIVER_REQUIREMENTS, install
from persistencia.database import DRIVERS


def test_profile_is_explicit_and_local(tmp_path):
    assert load_installation_profile(tmp_path)['id'] == 'core'
    write_installation_profile_marker(tmp_path, 'dev')
    assert load_installation_profile(tmp_path)['id'] == 'dev'
    (tmp_path/'.runtime/installation.json').write_text('{broken')
    assert load_installation_profile(tmp_path)['id'] == 'core'


def test_installer_driver_catalog_matches_runtime():
    assert set(DRIVERS) == set(DRIVER_REQUIREMENTS)
    for kind, (_, requirement) in DRIVERS.items():
        assert DRIVER_REQUIREMENTS[kind] == ([requirement] if requirement else [])


def test_installer_rejects_invalid_profile_before_mutations(tmp_path):
    with pytest.raises(ValueError):
        install('invalid','sqlite',root=tmp_path)
    assert not list(tmp_path.iterdir())


def test_installer_reports_missing_tk_before_creating_venv(tmp_path, monkeypatch):
    import instalacao.install as installer
    real_import = installer.importlib.import_module
    def missing_tk(name):
        if name == 'tkinter':
            raise ModuleNotFoundError(name)
        return real_import(name)
    monkeypatch.setattr(installer.importlib, 'import_module', missing_tk)
    with pytest.raises(RuntimeError, match='tkinter'):
        install('core', 'sqlite', root=tmp_path)
    assert not list(tmp_path.iterdir())


def test_settings_recover_invalid_json_without_losing_original(tmp_path):
    (tmp_path/'settings.json').write_text('{broken')
    manager = SettingsManager(str(tmp_path))
    settings = manager.load_settings()
    assert settings['active_theme']
    assert (tmp_path/'settings.json.corrupt').read_text() == '{broken'
    assert not list(tmp_path.glob('.settings-*.tmp'))
    settings['custom_colors']['primary'] = '#000000'
    assert manager.load_settings()['custom_colors']['primary'] != '#000000'


def test_registry_import_is_lazy():
    command = 'import sys, panels; assert not any(n.startswith("panels.painel_") for n in sys.modules)'
    subprocess.run([sys.executable, '-c', command], check=True)
