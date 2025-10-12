# suites/suite_parallel.py
import queue
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

from common.base_suite import BaseTestSuite
from suites.mocks import MockAuth, MockDataService, MockRepository


class ParallelDivineSuite(BaseTestSuite):
    """Suíte que executa testes em paralelo usando ThreadPoolExecutor para máxima eficiência."""
    suite_name = "Backend (Divina/Paralela)"
    description = "Execução de testes em paralelo para alta performance."

    def __init__(self, q: queue.Queue):
        super().__init__(q)
        self.verify_user_credentials = MockAuth.verify_user_credentials
        self.DataService = MockDataService
        self.GenericRepository = MockRepository
        self.max_workers = 4

    def run(self):
        self.q.put({"type": "suite_start", "name": self.suite_name})
        all_tests = self.get_all_tests()
        self.q.put({"type": "total_tests", "count": len(all_tests)})

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self._execute_and_report, method, *args, scenario_name=name, **kwargs)
                for method, name, args, kwargs in all_tests
            ]
            for future in as_completed(futures):
                future.result()

        self.q.put({"type": "suite_end", "name": self.suite_name})

    def get_all_tests(self):
        """Prepara a lista de todos os testes a serem executados em paralelo."""
        auth_scenarios = {
            "sucesso": ('admin', 'admin', True),
            "senha_incorreta": ('admin', 'senha_errada', False)
        }
        tests = [(self.test_autenticacao, name, args, {}) for name, args in auth_scenarios.items()]
        tests.append((self.test_repository_crud_completo, "", (), {}))
        tests.append((self.test_data_service_transacao_sucesso, "", (), {}))
        return tests

    def test_autenticacao(self, username, password, should_succeed):
        """Testa o mock de autenticação."""
        user_data = self.verify_user_credentials(username, password)
        assert (user_data is not None) == should_succeed

    def test_repository_crud_completo(self):
        """Testa um ciclo CRUD simples no mock do repositório."""
        repo = self.GenericRepository
        repo._data = {}  # Isola os dados para este teste
        # CORRIGIDO: Usa a tabela 'tipos_vegetais' e a coluna 'NOME' em maiúsculas
        table = "tipos_vegetais"
        repo.write_dataframe_to_table(pd.DataFrame([{'NOME': 'Fruto'}]), table)
        df_read = repo.read_table_to_dataframe(table, where_conditions={'NOME': 'Fruto'})
        assert not df_read.empty, "CREATE/READ falhou"

    def test_data_service_transacao_sucesso(self):
        """Testa uma transação de sucesso no mock do serviço de dados."""
        sucesso, _ = self.DataService.rename_especie_gato_e_logar('Siamês', 'Gato Siamês', 'runner')
        assert sucesso, "Transação de sucesso falhou"