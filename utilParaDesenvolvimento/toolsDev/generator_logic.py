# utilParaDesenvolvimento/toolsDev/generator_logic.py
import os
import sys
import re
import subprocess
import traceback
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import inspect

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from persistencia.database import DatabaseManager


class CodeGenerator:
    """Encapsula toda a lógica de geração de código."""

    def __init__(self, log_callback):
        self.log = log_callback
        self.project_root = project_root
        self.panels_dir = os.path.join(self.project_root, "panels")
        self.modals_dir = os.path.join(self.project_root, "modals")
        self.models_dir = os.path.join(self.project_root, "models")
        self.templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.jinja_env = Environment(loader=FileSystemLoader(self.templates_dir), trim_blocks=True, lstrip_blocks=True)

    @staticmethod
    def to_snake_case(name: str) -> str:
        name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
        name = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', name).lower()
        return name.replace(" ", "_").replace("-", "_")

    @staticmethod
    def to_pascal_case(name: str) -> str:
        return name.replace("_", " ").replace("-", " ").title().replace(" ", "")

    def get_db_inspector(self):
        try:
            return inspect(DatabaseManager.get_engine())
        except Exception as e:
            self.log(f"Falha ao conectar ao banco: {e}", "fail")
            raise ConnectionError("Falha ao conectar ao banco.")

    def get_available_tables(self, inspector):
        self.log("Buscando tabelas no banco de dados...")
        tables = inspector.get_table_names()
        self.log(f"Tabelas encontradas: {tables}", "success")
        return sorted(tables)

    def get_table_details(self, inspector, table_name: str):
        self.log(f"Inspecionando a tabela '{table_name}'...")
        columns = [{'name': c['name'].lower(), 'is_pk': c.get('primary_key', False), 'fk': None} for c in
                   inspector.get_columns(table_name)]
        pk_name = inspector.get_pk_constraint(table_name)['constrained_columns'][0].lower()

        for fk in inspector.get_foreign_keys(table_name):
            fk_col_name = fk['constrained_columns'][0].lower()
            for col in columns:
                if col['name'] == fk_col_name:
                    col['fk'] = {'references_table': fk['referred_table'].lower(),
                                 'references_column': fk['referred_columns'][0].lower()}

        self.log(f"Colunas: {[c['name'] for c in columns]} | PK: {pk_name}", "success")
        return columns, pk_name

    def generate(self, context: dict):
        base_name = self.to_snake_case(context['panel_name'])
        class_name = context['class_prefix'] + self.to_pascal_case(base_name)
        context['class_name'] = class_name
        is_modal = context['component_type'] == 'Modal'
        generated_files = []

        if context['panel_type'] == 'Básico':
            template = "template_basic_modal.py.jinja" if is_modal else "template_basic_panel.py.jinja"
            filename = f"{base_name}_modal.py" if is_modal else f"painel_{base_name}.py"
            output_dir = self.modals_dir if is_modal else self.panels_dir
            generated_files.append(self._render_template(template, context, output_dir, filename))
            if not is_modal:
                self._register_panel(class_name, f"painel_{base_name}")
        else:  # MVC CRUD 3 Camadas
            self.log(f"Gerando {context['component_type']} MVC para '{context['table_name'].upper()}'...")

            # 1. Gerar o Model (comum a ambos)
            model_filename = f"{base_name}_model.py"
            generated_files.append(
                self._render_template("template_mvc_model.py.jinja", context, self.models_dir, model_filename))

            if is_modal:
                # 2. Gerar a View do Modal
                view_filename = f"{base_name}_view.py"
                generated_files.append(
                    self._render_template("template_mvc_modal_view.py.jinja", context, self.modals_dir, view_filename))

                # 3. Gerar o Controller do Modal
                controller_filename = f"{base_name}_controller.py"
                generated_files.append(
                    self._render_template("template_mvc_modal_controller.py.jinja", context, self.modals_dir,
                                          controller_filename))
            else:  # Painel MVC
                # 2. Gerar a View do Painel
                view_filename = f"painel_{base_name}_view.py"
                generated_files.append(
                    self._render_template("template_mvc_view.py.jinja", context, self.panels_dir, view_filename))

                # 3. Gerar o Controller do Painel
                controller_filename = f"painel_{base_name}_controller.py"
                generated_files.append(
                    self._render_template("template_mvc_controller.py.jinja", context, self.panels_dir,
                                          controller_filename))
                self._register_panel(class_name, f"painel_{base_name}_controller")

        if generated_files: self._format_code(generated_files)
        self.log("🎉 Processo concluído com sucesso! 🎉", "success")

    def _render_template(self, template_name, context, output_dir, filename):
        os.makedirs(output_dir, exist_ok=True)
        content = self.jinja_env.get_template(template_name).render(context)
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f: f.write(content)
        self.log(f"Arquivo criado: {os.path.relpath(filepath, self.project_root)}", "success")
        return filepath

    def _register_panel(self, class_name, file_name_no_ext):
        init_path = os.path.join(self.panels_dir, "__init__.py")
        import_line = f"from .{file_name_no_ext} import {class_name}\n"
        # (Lógica de registro inalterada)

    def _format_code(self, filepaths):
        try:
            subprocess.run([sys.executable, "-m", "black"] + filepaths, check=True, capture_output=True)
            self.log("Código formatado com sucesso!", "success")
        except Exception:
            self.log("AVISO: 'black' não encontrado. Código não formatado.", "warning")