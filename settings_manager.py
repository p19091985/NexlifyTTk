# src/settings_manager.py
import json
import os
import logging
from typing import Dict, Any


class SettingsManager:
    """Gerencia o carregamento e salvamento de configurações em um arquivo JSON."""

    def __init__(self, filename: str = "settings.json") -> None:
        # __file__ é o caminho para este arquivo (dentro de src/)
        # os.path.dirname(...) pega o diretório (a pasta src/)
        # O '..' sobe um nível, para a pasta raiz do projeto
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.filepath = os.path.join(project_root, filename)

        self.default_settings = {
            "theme": "System Default"
        }

    # O resto do arquivo (load_settings, save_settings) permanece o mesmo
    def load_settings(self) -> Dict[str, Any]:
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                logging.info(f"Configurações carregadas de {self.filepath}")
                return settings
        except (FileNotFoundError, json.JSONDecodeError):
            logging.info("Arquivo de configurações não encontrado ou inválido. Usando padrões.")
            return self.default_settings

    def save_settings(self, settings: Dict[str, Any]) -> None:
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
            logging.info(f"Configurações salvas em {self.filepath}")
        except IOError as e:
            logging.error(f"Não foi possível salvar as configurações em {self.filepath}: {e}")