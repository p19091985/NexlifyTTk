import json
import os
import tempfile
from pathlib import Path
import re
import logging
from copy import deepcopy
from typing import Dict, Any, MutableMapping

def _deep_merge_defaults(source: MutableMapping, defaults: MutableMapping) -> bool:
    is_dirty = False
    for key, value in defaults.items():
        if key not in source:
            source[key] = deepcopy(value)
            is_dirty = True

        elif isinstance(value, MutableMapping) and isinstance(source.get(key), MutableMapping):
            if _deep_merge_defaults(source[key], value):
                is_dirty = True

        elif isinstance(value, MutableMapping) and not isinstance(source.get(key), MutableMapping):
            source[key] = deepcopy(value)
            is_dirty = True

    return is_dirty

class SettingsManager:
    def __init__(self, project_root: str, filename: str = "settings.json") -> None:
        self.filepath = os.path.join(project_root, filename)
        self._cache: Dict[str, Any] | None = None

        self.default_settings = {
            "font_family": "Segoe UI",
            "font_size": 10,
            "active_theme": "Gato a Noite",
            "installation_profile": None,
            "custom_colors": {
                'primary': '#4fc3f7', 'secondary': '#3e3e3e', 'success': '#4CAF50',
                'info': '#4fc3f7', 'warning': '#FF9800', 'danger': '#dc3545'
            },
            "border_width": 1,
            "border_radius": 0
        }

    def load_settings(self, force_reload: bool = False) -> Dict[str, Any]:
        if self._cache is not None and not force_reload:
            return deepcopy(self._cache)

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            if not isinstance(settings, dict):
                raise ValueError('Configurações devem ser um objeto JSON.')
            geometry = settings.get('window_geometry')
            if geometry and not re.fullmatch(r'\d+x\d+[+-]\d+[+-]\d+', str(geometry)):
                settings.pop('window_geometry', None)
            if not isinstance(settings.get('font_size', 10), int) or not 6 <= settings.get('font_size', 10) <= 36:
                settings['font_size'] = 10
            if _deep_merge_defaults(settings, self.default_settings):
                self.save_settings(settings)
                logging.debug("Novas chaves/estruturas de configuração padrão foram adicionadas/corrigidas no settings.json.")
            else:
                self._cache = deepcopy(settings)
            logging.debug("Configurações carregadas de %s", self.filepath)
            return deepcopy(self._cache)
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            logging.warning(f"Arquivo de configurações não encontrado ou inválido ({self.filepath}). Usando e salvando padrões.")

            path = Path(self.filepath)
            if path.exists():
                backup = path.with_name(path.name + '.corrupt')
                if not backup.exists():
                    backup.write_bytes(path.read_bytes())
            defaults_copy = deepcopy(self.default_settings)
            self.save_settings(defaults_copy)
            return deepcopy(self._cache)

    def save_settings(self, settings: Dict[str, Any]) -> None:
        normalized_settings = deepcopy(settings)
        path = Path(self.filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_name = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                             prefix='.settings-', suffix='.tmp', delete=False) as stream:
                temp_name = stream.name
                json.dump(normalized_settings, stream, ensure_ascii=False, indent=4)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, path)
            self._cache = deepcopy(normalized_settings)
        finally:
            if temp_name and os.path.exists(temp_name):
                os.unlink(temp_name)
