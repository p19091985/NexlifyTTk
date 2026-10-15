"""Verified SQLite snapshots and non-destructive restoration drills."""
from pathlib import Path
import argparse
import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from utils.secure_files import private_directory, reject_link_path, restrict_permissions, atomic_write_private


def verify_sqlite(path):
    path = reject_link_path(path).resolve()
    with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as connection:
        if connection.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('Backup SQLite inválido.')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_sqlite_backup(source, directory):
    source = reject_link_path(source).resolve()
    directory = private_directory(directory)
    destination = directory / f'backup-{datetime.now(timezone.utc):%Y%m%dT%H%M%S}-{uuid.uuid4().hex[:8]}.db'
    destination.touch(exist_ok=False)
    restrict_permissions(destination)
    with sqlite3.connect(source.as_uri() + '?mode=ro', uri=True) as original, sqlite3.connect(destination) as backup:
        original.backup(backup)
    checksum = verify_sqlite(destination)
    atomic_write_private(destination.with_suffix('.json'), json.dumps({'sha256': checksum, 'source_name': source.name, 'created_at': datetime.now(timezone.utc).isoformat()}))
    return destination


def restore_to_new_file(backup, destination):
    backup = reject_link_path(backup).resolve()
    destination = reject_link_path(destination)
    expected = json.loads(backup.with_suffix('.json').read_text(encoding='utf-8'))['sha256']
    if verify_sqlite(backup) != expected:
        raise ValueError('Checksum do backup não confere.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.touch(exist_ok=False)  # Never overwrite a live database.
    restrict_permissions(destination)
    with sqlite3.connect(backup.as_uri() + '?mode=ro', uri=True) as original, sqlite3.connect(destination) as restored:
        original.backup(restored)
    verify_sqlite(destination)
    return destination


def main():
    parser = argparse.ArgumentParser(description='Backup e ensaio de restauração SQLite')
    parser.add_argument('operation', choices=['backup', 'restore'])
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    result = (create_sqlite_backup if args.operation == 'backup' else restore_to_new_file)(args.source, args.destination)
    print(f'Arquivo verificado: {result}')


if __name__ == '__main__':
    main()
