# suites/suite_ultimate.py
import queue
import pandas as pd

from common.base_suite import BaseTestSuite
from common.models import TestSeverity
from suites.mocks import MockAuth, MockDataService, MockRepository


class UltimateTestSuite(BaseTestSuite):
    """A suíte definitiva com monitoramento de sistema, retentativas e status GODLIKE."""
    suite_name = "Backend (Ultimate)"
    description = "A mais completa: retry, monitoramento de sistema (CPU/RAM) e scores de performance."

    def __init__(self, q: queue.Queue):
        super().__init__(q)
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
            "senha_incorreta": ('admin', 'x', False),
            "usuario_inexistente": ('ghost', 'x', False),
        }

        tests = [
            (self.test_autenticacao, args, name, TestSeverity.HIGH) for name, args in auth_scenarios.items()
        ]
        tests.extend([
            (self.test_repository_crud, (), "", TestSeverity.MEDIUM),
            (self.test_repository_edge_cases, (), "", TestSeverity.LOW),
        ])

        self.q.put({"type": "total_tests", "count": len(tests)})

        for method, args, name, severity in tests:
            # --- CORREÇÃO: Chamando o método correto da classe base ---
            self._execute_and_report(method, *args, scenario_name=name, severity=severity, retries=2)

    def test_autenticacao(self, username, password, should_succeed):
        data = self.verify_user_credentials(username, password)
        if should_succeed:
            assert data is not None, "Login deveria passar"
        else:
            assert data is None, "Login deveria falhar"

    def test_repository_crud(self):
        repo = self.GenericRepository
        repo._data = {}
        table = "tipos_linguagem"
        repo.write_dataframe_to_table(pd.DataFrame([{'nome': 'Visual'}]), table)
        df = repo.read_table_to_dataframe(table, where_conditions={'nome': 'Visual'})
        assert not df.empty, "CREATE/READ falhou"

    def test_repository_edge_cases(self):
        rows_updated = self.GenericRepository.update_table('gatos', {'temperamento': 'Fantasma'}, {'nome': 'Inexistente'})
        assert rows_updated == 0, "UPDATE não deveria afetar linhas"