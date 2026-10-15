"""Restrict existing local secrets, SQLite files, logs and recovery backups."""
from pathlib import Path
from utils.paths import PROJECT_ROOT
from utils.secure_files import reject_link_path, restrict_permissions


def harden(root=PROJECT_ROOT):
    root = reject_link_path(root).resolve()
    selected = [root / name for name in ('.secrets', 'logs', '.runtime/backups',
                '.venv/backup-before-evolution', 'banco.local.ini', 'config.local.ini')]
    selected.extend(root.glob('*.db'))
    selected.extend(root.glob('*.db-*'))
    changed = []
    for path in selected:
        if not path.exists():
            continue
        reject_link_path(path)
        if not path.resolve().is_relative_to(root):
            raise ValueError('Arquivo fora da instalação.')
        items = [path, *path.rglob('*')] if path.is_dir() else [path]
        for item in items:
            restrict_permissions(item)
            changed.append(str(item.relative_to(root)))
    return changed


def main():
    import json
    print(json.dumps({'protected': harden()}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
