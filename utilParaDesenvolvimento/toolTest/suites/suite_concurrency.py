# suites/suite_concurrency.py
import queue
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

from common.base_suite import BaseTestSuite
from common.models import TestSeverity
from suites.mocks import MockAuth


class ConcurrencyTestSuite(BaseTestSuite):
    """Simula o acesso simultâneo de múltiplos usuários."""
    suite_name = "Acesso Concorrente"
    description = "Simula 300 logins simultâneos para validar a resposta do sistema sob estresse."

    def __init__(self, q: queue.Queue):
        super().__init__(q)
        self.verify_user_credentials = MockAuth.verify_user_credentials

    def _login_worker(self, username, password):
        result = self.verify_user_credentials(username, password)
        return (result and result.get('username') == username)

    def test_300_concurrent_logins(self):
        """Orquestra o toolTest de carga com 300 usuários."""
        NUM_USERS = 300;
        VALID_RATIO = 0.1;
        MAX_WORKERS = 50;
        PERFORMANCE_THRESHOLD_SECONDS = 5.0
        num_valid = int(NUM_USERS * VALID_RATIO);
        num_invalid = NUM_USERS - num_valid

        tasks = [("admin", "admin")] * num_valid + [(f"user{i}", "wrong") for i in range(num_invalid)]
        random.shuffle(tasks)

        results = []
        start_time = time.perf_counter()

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(self._login_worker, user, pwd) for user, pwd in tasks]
            for future in as_completed(futures):
                results.append(future.result())

        duration = time.perf_counter() - start_time
        success_count = sum(1 for r in results if r is True)
        fail_count = len(results) - success_count

        details = (f"Teste de Carga Concluído em {duration:.4f}s.\n"
                   f"Total de Requisições: {NUM_USERS}\n"
                   f"  - Sucessos: {success_count} (Esperado: {num_valid})\n"
                   f"  - Falhas: {fail_count} (Esperado: {num_invalid})")

        assert success_count == num_valid, f"Esperado {num_valid} sucessos, obteve {success_count}."
        assert fail_count == num_invalid, f"Esperado {num_invalid} falhas, obteve {fail_count}."
        assert duration < PERFORMANCE_THRESHOLD_SECONDS, f"Teste excedeu o limite de {PERFORMANCE_THRESHOLD_SECONDS}s."
        return details

    def run(self):
        """ Usa o novo wrapper da classe base para executar o toolTest único."""
        self._run_single_test_as_suite(self.test_300_concurrent_logins, severity=TestSeverity.CRITICAL)