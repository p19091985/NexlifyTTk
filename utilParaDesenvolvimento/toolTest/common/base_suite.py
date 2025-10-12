                      
import queue
import time
import traceback
from abc import ABC, abstractmethod
import psutil

from common.models import TestResult, TestStatus, TestSeverity


class BaseTestSuite(ABC):
    """Classe base ultra-poderosa para todas as suítes de toolTest."""
    suite_name: str = "Suíte Desconhecida"
    description: str = "Descrição não fornecida."

    def __init__(self, q: queue.Queue):
        self.q = q

    @abstractmethod
    def run(self):
        """O método principal que executa todos os testes da suíte."""
        raise NotImplementedError

    def _execute_and_report(self, method, *args, **kwargs):
        """
        MOTOR DE EXECUÇÃO UNIVERSAL.
        Executa um único toolTest com retentativas, monitoramento de performance,
        tratamento de exceções e envio de relatório para a fila.
        """
                                                  
        scenario_name = kwargs.pop('scenario_name', '')
        severity = kwargs.pop('severity', TestSeverity.MEDIUM)
        retries = kwargs.pop('retries', 0)
        method_name_report = f"{method.__name__} ({scenario_name})" if scenario_name else method.__name__

        last_exception = None
        for attempt in range(retries + 1):
            start_time = time.perf_counter()
            cpu_start = psutil.cpu_percent(interval=None)
            mem_start = psutil.virtual_memory().percent

            status = TestStatus.SUCCESS
            details = "Executado com sucesso."
            result_value = None

            try:
                result_value = method(*args, **kwargs)
                duration = time.perf_counter() - start_time

                                            
                if isinstance(result_value, TestStatus):
                    status = result_value
                elif result_value is True:
                    status = TestStatus.DIVINE_PASS
                elif duration < 0.001:
                    status = TestStatus.GODLIKE

                                                                                
                break

            except AssertionError as e:
                status, last_exception = TestStatus.FAIL, e
                details = f"Tentativa {attempt + 1}/{retries + 1}: Falha na asserção: {e}\n\n{traceback.format_exc()}"
            except Exception as e:
                status, last_exception = TestStatus.ERROR, e
                details = f"Tentativa {attempt + 1}/{retries + 1}: Exceção: {e}\n\n{traceback.format_exc()}"

                                                                                            
            if attempt < retries:
                wait_time = 0.1 * (2 ** attempt)
                time.sleep(wait_time)

                                                            
        duration = time.perf_counter() - start_time
        cpu_end = psutil.cpu_percent(interval=None)
        mem_end = psutil.virtual_memory().percent

        result = TestResult(
            suite_name=self.suite_name,
            class_name=self.__class__.__name__,
            method_name=method_name_report,
            status=status,
            duration=duration,
            details=details,
            severity=severity,
            retry_count=attempt
        )
        result.metadata.update({
            'cpu_usage': f"{cpu_end - cpu_start:.2f}%",
            'mem_usage_delta': f"{mem_end - mem_start:.2f}%",
            'mem_usage_abs': f"{psutil.virtual_memory().used / (1024 ** 2):.1f}MB",
        })

        self.q.put({"type": "test_result", "result": result})

    def _run_single_test_as_suite(self, method, severity=TestSeverity.CRITICAL):
        """Wrapper para suítes que consistem em um único e grande toolTest."""
        self.q.put({"type": "suite_start", "name": self.suite_name})
        self.q.put({"type": "total_tests", "count": 1})
        self._execute_and_report(method, severity=severity)
        self.q.put({"type": "suite_end", "name": self.suite_name})