# settings_manager.py
import json
import os
import logging
from typing import Dict, Any


class SettingsManager:
    """ Gerencia o carregamento e salvamento de configurações da aplicação. """

    def __init__(self, project_root: str, filename: str = "settings.json") -> None:
        self.filepath = os.path.join(project_root, filename)

        # --- MODIFICAÇÃO: Adicionadas as novas chaves de configuração ---
        self.default_settings = {
            "theme": "litera",
            "font_family": "Segoe UI",
            "font_size": 10,
            "custom_colors": {
                "primary": None,
                "secondary": None,
                "success": None,
                "info": None,
                "warning": None,
                "danger": None,
            },
            "border_width": 1,
            "border_radius": 8,
            "focus_ring": True
        }

    def load_settings(self) -> Dict[str, Any]:
        """ Carrega as configurações, garantindo que todas as novas chaves existam. """
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            is_dirty = False
            for key, value in self.default_settings.items():
                if key not in settings:
                    settings[key] = value
                    is_dirty = True
                elif isinstance(value, dict):
                    for sub_key in value:
                        if sub_key not in settings[key]:
                            settings[key][sub_key] = value[sub_key]
                            is_dirty = True

            if is_dirty:
                self.save_settings(settings)

            logging.info(f"Configurações carregadas de {self.filepath}")
            return settings
        except (FileNotFoundError, json.JSONDecodeError):
            logging.warning(f"Arquivo de configurações não encontrado. Usando e salvando padrões.")
            self.save_settings(self.default_settings)
            return self.default_settings.copy()

    def save_settings(self, settings: Dict[str, Any]) -> None:
        """ Salva o dicionário de configurações no arquivo JSON. """
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
            logging.info(f"Configurações salvas em {self.filepath}")
        except IOError as e:
            logging.error(f"Não foi possível salvar as configurações em {self.filepath}: {e}")