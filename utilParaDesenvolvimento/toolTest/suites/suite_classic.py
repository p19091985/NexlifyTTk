# suites/suite_classic.py
import queue
import pandas as pd

from common.base_suite import BaseTestSuite
from common.models import TestResult, TestStatus
from suites.mocks import MockAuth, MockDataService, MockRepository


class ClassicTestSuite(BaseTestSuite):
    """Suíte baseada no primeiro testador, com testes sequenciais e lógicos."""
    suite_name = "Backend (Clássica)"
    description = "Testes sequenciais de CRUD, transações e autenticação do backend."

    def __init__(self, q: queue.Queue):
        super().__init__(q)
        # Simula as dependências para esta suíte
        self.verify_user_credentials = MockAuth.verify_user_credentials
        self.DataService = MockDataService
        self.GenericRepository = MockRepository

    def run(self):
        self.q.put({"type": "suite_start", "name": self.suite_name})
        self.execute_all_tests()
        self.q.put({"type": "suite_end", "name": self.suite_name})

    def execute_all_tests(self):
        auth_scenarios = {
            "sucesso": ('admin', 'admin', True),
            "senha_incorreta": ('admin', 'senha_errada', False),
            "usuario_inexistente": ('nao_existe', 'qualquer', False),
        }
        tests_to_run = [
            (self.test_autenticacao_parametrizado, args, name)
            for name, args in auth_scenarios.items()
        ]
        tests_to_run.extend([
            (self.test_repository_crud_completo, (), ""),
            (self.test_data_service_transacao_sucesso, (), ""),
            (self.test_data_service_transacao_falha, (), ""),
        ])

        self.q.put({"type": "total_tests", "count": len(tests_to_run)})

        # MODIFICAÇÃO: A lógica de execução foi movida para a classe base.
        for method, args, scenario_name in tests_to_run:
            self._execute_and_report(method, *args, scenario_name=scenario_name)

    # REMOVIDO: O método _run_test_method foi removido pois sua lógica agora está na BaseTestSuite.

    def test_autenticacao_parametrizado(self, username, password, should_succeed):
        user_data = self.verify_user_credentials(username, password)
        if should_succeed:
            assert user_data is not None, "Autenticação deveria ter sucesso."
        else:
            assert user_data is None, "Autenticação deveria falhar."

    def test_repository_crud_completo(self):
        repo = self.GenericRepository
        repo._data = {}  # Reset mock data
        table = "tipos_linguagem"
        repo.write_dataframe_to_table(pd.DataFrame([{'nome': 'Visual'}]), table)
        df_read = repo.read_table_to_dataframe(table, where_conditions={'nome': 'Visual'})
        assert not df_read.empty, "CREATE/READ falhou."
        repo.update_table(table, {'nome': 'Visualização'}, {'nome': 'Visual'})
        df_updated = repo.read_table_to_dataframe(table, where_conditions={'nome': 'Visualização'})
        assert not df_updated.empty, "UPDATE falhou."
        repo.delete_from_table(table, where_conditions={'nome': 'Visualização'})
        df_deleted = repo.read_table_to_dataframe(table, where_conditions={'nome': 'Visualização'})
        assert df_deleted.empty, "DELETE falhou."

    def test_data_service_transacao_sucesso(self):
        sucesso, _ = self.DataService.rename_especie_gato_e_logar('Siamês', 'Gato Siamês', 'test_runner')
        assert sucesso, "Transação de sucesso falhou."

    def test_data_service_transacao_falha(self):
        try:
            self.DataService.rename_especie_gato_e_logar('Persa', 'Gato Persa com falha', 'test_runner')
            assert False, "A transação deveria ter lançado uma exceção."
        except ValueError:
            pass  # Sucesso, exceção esperada