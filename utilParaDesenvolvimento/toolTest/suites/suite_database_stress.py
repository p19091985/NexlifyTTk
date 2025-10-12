                                 
import queue
import time
import random
import threading
import pandas as pd
from collections import Counter
import logging

from common.base_suite import BaseTestSuite
from common.models import TestSeverity
from suites.mocks import MockRepository as GenericRepository
from suites.mocks import MockDataService as DataService


class DatabaseStressTestSuite(BaseTestSuite):
    """Simula uma carga de trabalho mista e concorrente no banco de dados."""
    suite_name = "Estresse de Banco de Dados"
    description = "Simula usuários realizando operações de CRUD e Transações por um período."

    def __init__(self, q: queue.Queue):
        super().__init__(q)
        self.repo = GenericRepository
        self.service = DataService
                                                  
        self.actions = [self._action_read_tipos_vegetais, self._action_read_join, self._action_insert_delete_gato,
                        self._action_transaction_success, self._action_transaction_rollback]
        self.repo._data = {}

                                              
    def _action_read_tipos_vegetais(self):
        """Lê a tabela de tipos de vegetais."""
        try:
            self.repo.read_table_to_dataframe("tipos_vegetais")
            return "READ_TIPOS_VEGETAIS_SUCCESS"
        except Exception:
            logging.exception("Erro em _action_read_tipos_vegetais")
            return "ACTION_ERROR"

    def _action_read_join(self):
        """Simula a leitura de uma view ou join complexo."""
        try:
            self.repo.read_table_to_dataframe("especie_gatos")
            return "READ_JOIN_SUCCESS"
        except Exception:
            logging.exception("Erro em _action_read_join")
            return "ACTION_ERROR"

    def _action_insert_delete_gato(self):
        """Insere e deleta um gato para simular escrita."""
        gato_nome = f"GatoDeTeste_{threading.get_ident()}_{random.randint(1000, 9999)}"
        try:
            df = pd.DataFrame([{'NOME_ESPECIE': gato_nome, 'PAIS_ORIGEM': 'Teste', 'TEMPERAMENTO': 'Volátil'}])
            self.repo.write_dataframe_to_table(df, "especie_gatos")
            time.sleep(0.02)
            self.repo.delete_from_table("especie_gatos", where_conditions={'NOME_ESPECIE': gato_nome})
            return "INSERT_DELETE_SUCCESS"
        except Exception:
            logging.exception("Erro em _action_insert_delete_gato")
            return "ACTION_ERROR"

    def _action_transaction_success(self):
        """Executa uma transação que deve ter sucesso."""
        try:
            nome_antigo = f'Siamês_{random.randint(0, 100)}'
            nome_novo = f'GatoSiamês_{random.randint(0, 100)}'
            self.service.rename_especie_gato_e_logar(nome_antigo, nome_novo, 'stress_tester')
            return "TRANSACTION_SUCCESS"
        except Exception:
            logging.exception("Erro em _action_transaction_success")
            return "ACTION_ERROR"

    def _action_transaction_rollback(self):
        """Executa uma transação que deve falhar e dar rollback."""
        try:
            self.service.rename_especie_gato_e_logar('Persa', 'Gato Persa com falha', 'stress_tester')
        except ValueError:
            return "TRANSACTION_ROLLBACK"
        except Exception:
            logging.exception("Erro inesperado em _action_transaction_rollback")
            return "ACTION_ERROR"
        return "TRANSACTION_ROLLBACK_FAIL"

    def _user_simulation_worker(self, stop_event, results_list, lock):
        """Simula o comportamento de um usuário executando ações aleatórias."""
        while not stop_event.is_set():
            try:
                action = random.choice(self.actions)
                result = action()
                with lock:
                    results_list.append((result, time.perf_counter()))
                time.sleep(random.uniform(0.05, 0.2))
            except Exception:
                with lock:
                    results_list.append(("WORKER_DIED", time.perf_counter()))

    def _cleanup_test_data(self):
        self.repo._data = {}
        logging.info("Dados de teste limpos.")

    def test_sustained_db_load(self):
        TEST_DURATION_SECONDS = 15
        NUM_CONCURRENT_USERS = 30
        stop_event = threading.Event()
        results_list = []
        lock = threading.Lock()
        threads = []

        self.q.put({"type": "progress_update", "text": f"Simulando {NUM_CONCURRENT_USERS} usuários por {TEST_DURATION_SECONDS}s..."})
        start_time = time.perf_counter()

        for _ in range(NUM_CONCURRENT_USERS):
            thread = threading.Thread(target=self._user_simulation_worker, args=(stop_event, results_list, lock))
            threads.append(thread)
            thread.start()

        elapsed_time = 0
        while elapsed_time < TEST_DURATION_SECONDS:
            time.sleep(1)
            elapsed_time = time.perf_counter() - start_time
            progress_percent = (elapsed_time / TEST_DURATION_SECONDS)
            with lock:
                req_count = len(results_list)
            self.q.put({"type": "progress_update", "value": progress_percent, "text": f"Em andamento... {int(elapsed_time)}s de {TEST_DURATION_SECONDS}s | {req_count} ops."})

        stop_event.set()
        for thread in threads:
            thread.join()

        duration = time.perf_counter() - start_time
        self.q.put({"type": "progress_update", "text": "Analisando resultados..."})
        self._cleanup_test_data()

        total_ops = len(results_list)
        op_counts = Counter(res[0] for res in results_list)

        details = f"Teste de Estresse Concluído em {duration:.2f}s.\n\n"
        details += f"Total de Operações: {total_ops} ({total_ops / duration:.2f} ops/s)\n"
        details += "Contagem por Operação:\n" + "\n".join([f"  - {op}: {count}" for op, count in sorted(op_counts.items())])

        assert "ACTION_ERROR" not in op_counts, "Houveram erros inesperados durante as ações."
        assert "WORKER_DIED" not in op_counts, "Um ou mais threads de simulação falharam."
        return details

    def run(self):
        self._run_single_test_as_suite(self.test_sustained_db_load, severity=TestSeverity.CRITICAL)