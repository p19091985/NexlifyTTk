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
        """
        Executa todos os testes em um pool de threads e aguarda a conclusão
        de todos antes de finalizar a suíte.
        """
        self.q.put({"type": "suite_start", "name": self.suite_name})
        all_tests = self.get_all_tests()
        self.q.put({"type": "total_tests", "count": len(all_tests)})

        # --- CORREÇÃO CRÍTICA ---
        # Usamos um executor para submeter todas as tarefas e depois
        # esperamos explicitamente que cada uma delas termine.
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Mapeia cada chamada de teste a um 'future'
            futures = [
                executor.submit(self._execute_and_report, method, *args, scenario_name=name, **kwargs)
                for method, name, args, kwargs in all_tests
            ]
            # O laço 'as_completed' garante que vamos processar os resultados
            # à medida que ficam prontos, e o bloco 'with' só termina quando
            # o último 'future' for concluído.
            for future in as_completed(futures):
                # Apenas para garantir que exceções no futuro sejam levantadas, se houver
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
        repo.write_dataframe_to_table(pd.DataFrame([{'nome': 'Visual'}]), "tipos_linguagem")
        df_read = repo.read_table_to_dataframe("tipos_linguagem", where_conditions={'nome': 'Visual'})
        assert not df_read.empty, "CREATE/READ falhou"

    def test_data_service_transacao_sucesso(self):
        """Testa uma transação de sucesso no mock do serviço de dados."""
        sucesso, _ = self.DataService.rename_especie_gato_e_logar('Siamês', 'Gato Siamês', 'runner')
        assert sucesso, "Transação de sucesso falhou"