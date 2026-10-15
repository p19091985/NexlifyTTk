"""Exercise the real OS launchers in a fresh venv and a path with spaces/accents."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv

import pytest

from utils.paths import PROJECT_ROOT


@pytest.fixture(scope='module')
def launcher_project(tmp_path_factory):
    root = tmp_path_factory.mktemp('launchers') / 'Projeto com espaços'
    root.mkdir()
    venv.EnvBuilder(with_pip=False).create(root / '.venv')
    for pattern in ('*.bat', '*.sh', '*.ps1'):
        for script in PROJECT_ROOT.glob(pattern):
            shutil.copy2(script, root / script.name)
    probe = (
        'import json, os, sys\n'
        'print(json.dumps({"cwd": os.getcwd(), "prefix": sys.prefix, '
        '"args": sys.argv[1:], "entry": os.path.basename(__file__)}, ensure_ascii=False))\n'
        'raise SystemExit(23)\n'
    )
    for entry in ('run.py', 'reset_admin.py'):
        (root / entry).write_text(probe, encoding='utf-8')
    return root


SCRIPTS = (('iniciar.bat', 'inciciar.bat', 'reset_admin.bat', 'iniciar.ps1')
           if os.name == 'nt' else ('iniciar.sh', 'reset_admin.sh'))


@pytest.mark.parametrize('script', SCRIPTS)
def test_native_launcher_venv_cwd_arguments_and_exit_code(launcher_project, tmp_path, script):
    path = launcher_project / script
    if script.endswith('.bat'):
        # cmd.exe /s requires an outer pair of quotes around a quoted program path.
        command = f'"{os.environ["COMSPEC"]}" /d /s /c ""{path}" --probe "argumento com espaços""'
    elif script.endswith('.ps1'):
        command = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                   str(path), '--probe', 'argumento com espaços']
    else:
        command = ['bash', str(path), '--probe', 'argumento com espaços']
    result = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True,
                            encoding='utf-8', timeout=30)
    assert result.returncode == 23, result.stdout + result.stderr
    data = json.loads(result.stdout)
    assert Path(data['cwd']).resolve() == launcher_project.resolve()
    assert Path(data['prefix']).resolve() == (launcher_project / '.venv').resolve()
    assert data['args'] == ['--probe', 'argumento com espaços']
    assert data['entry'] == ('reset_admin.py' if script.startswith('reset') else 'run.py')
