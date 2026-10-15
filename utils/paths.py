from pathlib import Path
import os
PROJECT_ROOT = Path(__file__).resolve().parents[1]
def venv_python(root=PROJECT_ROOT):
    return Path(root) / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
