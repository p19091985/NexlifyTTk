                         
import queue
import pandas as pd
from common.base_suite import BaseTestSuite
from common.models import TestSeverity
from suites.mocks import MockAuth, MockDataService, MockRepository

class SupremeTestSuite(BaseTestSuite):
    suite_name = "Backend (Suprema)"
    description = "Testes com status especiais (Divino) e análise de resiliência."

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
        tests = [
            (self.test_autenticacao_cosmica, ('admin', 'admin', True), 'sucesso', TestSeverity.HIGH),
            (self.test_autenticacao_cosmica, ('admin', 'errada', False), 'falha', TestSeverity.HIGH),
            (self.test_crud_universal, (), '', TestSeverity.MEDIUM),
        ]
        self.q.put({"type": "total_tests", "count": len(tests)})

        for method, args, name, severity in tests:
            self._execute_and_report(method, *args, scenario_name=name, severity=severity)

    def test_autenticacao_cosmica(self, username, password, should_succeed):
        result = self.verify_user_credentials(username, password)
        assert (result is not None) == should_succeed
        if should_succeed:
            return True                                                     

    def test_crud_universal(self):
        repo = self.GenericRepository; repo._data = {}
        repo.write_dataframe_to_table(pd.DataFrame([{'name': 'Entidade'}]), 'divine_entities')
        result_df = repo.read_table_to_dataframe('divine_entities', where_conditions={'name': 'Entidade'})
        assert not result_df.empty
        return True