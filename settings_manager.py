import json
import os
import logging
from typing import Dict, Any, MutableMapping

def _deep_merge_defaults(source: MutableMapping, defaults: MutableMapping) -> bool:
    is_dirty = False
    for key, value in defaults.items():
        if key not in source:
            source[key] = value
            is_dirty = True
                                                                       
        elif isinstance(value, MutableMapping) and isinstance(source.get(key), MutableMapping):   
            if _deep_merge_defaults(source[key], value):   
                is_dirty = True
                                                                                          
        elif isinstance(value, MutableMapping) and not isinstance(source.get(key), MutableMapping):
            source[key] = value                                                
            is_dirty = True
                                                                                                      

    return is_dirty

class SettingsManager:
    def __init__(self, project_root: str, filename: str = "settings.json") -> None:
        self.filepath = os.path.join(project_root, filename)
                                                            
        self.default_settings = {
            "font_family": "Segoe UI",   
            "font_size": 10,   
            "custom_colors": {                            
                'primary': '#007bff', 'secondary': '#6c757d', 'success': '#28a745',
                'info': '#17a2b8', 'warning': '#ffc107', 'danger': '#dc3545'
            },
            "border_width": 1,
            "border_radius": 0
        }   

    def load_settings(self) -> Dict[str, Any]:
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                                                                              
            if _deep_merge_defaults(settings, self.default_settings):
                self.save_settings(settings)
                logging.info("Novas chaves/estruturas de configuração padrão foram adicionadas/corrigidas no settings.json.")                     
            logging.info(f"Configurações carregadas de {self.filepath}")
            return settings
        except (FileNotFoundError, json.JSONDecodeError):
            logging.warning(f"Arquivo de configurações não encontrado ou inválido ({self.filepath}). Usando e salvando padrões.")                     
                                                                        
            defaults_copy = self.default_settings.copy()
                                                          
            for key, value in defaults_copy.items():
                if isinstance(value, MutableMapping):
                    defaults_copy[key] = value.copy()
            self.save_settings(defaults_copy)
            return defaults_copy                  

    def save_settings(self, settings: Dict[str, Any]) -> None:
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
            logging.info(f"Configurações salvas em {self.filepath}")
        except IOError as e:   
            logging.error(f"Não foi possível salvar as configurações em {self.filepath}: {e}")   