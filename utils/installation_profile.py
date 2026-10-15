"""Perfis explícitos: dependências instaladas não concedem ferramentas de dev."""
from datetime import datetime, timezone
from pathlib import Path
import json
import os
from utils.secure_files import atomic_write_private, private_directory

CAPABILITY_CORE_PANELS = 'core.panels'
CAPABILITY_VISUAL_TESTS = 'dev.visual_tests'
CAPABILITY_DEV_TOOLS = 'dev.tools'
PROFILES = {'core': 'Operação', 'dev': 'Desenvolvimento'}


def load_installation_profile(project_root):
    try:
        record = json.loads((Path(project_root) / '.runtime' / 'installation.json').read_text(encoding='utf-8'))
        if not isinstance(record, dict):
            record = {}
    except (OSError, ValueError):
        record = {}
    profile = record if isinstance(record, str) else record.get('id', 'core')
    profile = profile if profile in PROFILES else 'core'
    return {'id': profile, 'title': PROFILES[profile], 'record': record}


def profile_info_has_capability(info, capability):
    return capability == CAPABILITY_CORE_PANELS or (info or {}).get('id') == 'dev'


def panel_visible_for_profile(spec, profile_id):
    return spec.get('visible', True) and profile_info_has_capability(
        {'id': profile_id}, spec.get('requires_capability', CAPABILITY_CORE_PANELS))


def write_installation_profile_marker(project_root, profile_id, diagnostics=None):
    if profile_id not in PROFILES:
        raise ValueError('Perfil inválido.')
    directory = Path(project_root) / '.runtime'
    private_directory(directory)
    record = {'id': profile_id, 'installed_at': datetime.now(timezone.utc).isoformat(), 'diagnostics': diagnostics or []}
    atomic_write_private(directory / 'installation.json', json.dumps(record, indent=2))
