                        
import queue
import pandas as pd
from common.base_suite import BaseTestSuite
from suites.mocks import MockAuth, MockDataService, MockRepository

class ModernTestSuite(BaseTestSuite):
    suite_name = "Backend (Moderna)"
    description = "Testes com cenários parametrizados e casos de limite."

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
            "senha_incorreta": ('admin', 'senha_errada', False),
        }
        tests_to_run = [(self.test_autenticacao_parametrizado, args, name) for name, args in auth_scenarios.items()]
        tests_to_run.extend([
            (self.test_repository_crud_completo, (), ""),
            (self.test_repository_casos_limite, (), ""),
        ])
        self.q.put({"type": "total_tests", "count": len(tests_to_run)})

        for method, args, scenario_name in tests_to_run:
            self._execute_and_report(method, *args, scenario_name=scenario_name)

    def test_autenticacao_parametrizado(self, username, password, should_succeed):
        user_data = self.verify_user_credentials(username, password)
        assert (user_data is not None) == should_succeed

    def test_repository_crud_completo(self):
        repo = self.GenericRepository
        repo._data = {}
                                                                                  
        table = "tipos_vegetais"
        repo.write_dataframe_to_table(pd.DataFrame([{'NOME': 'Folha'}]), table)
        df_read = repo.read_table_to_dataframe(table, where_conditions={'NOME': 'Folha'})
        assert not df_read.empty

    def test_repository_casos_limite(self):
                                                                
        rows_updated = self.GenericRepository.update_table('ESPECIE_GATOS', {}, {'NOME_ESPECIE': 'Inexistente'})
        assert rows_updated == 0