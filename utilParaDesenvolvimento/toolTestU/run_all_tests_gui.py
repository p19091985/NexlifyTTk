# run_all_tests_gui.py (Versão 2.2 - Import Corrigido)
import unittest
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import glob
import importlib
import os
import sys
import threading
import queue
from datetime import datetime
import logging
from pathlib import Path  # --- CORREÇÃO: Importa o módulo Path ---

# --- Configuração de Path ---
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
test_dir = os.path.dirname(__file__)
sys.path.insert(0, test_dir)

try:
    import ttkbootstrap as bstrap
    from ttkbootstrap.constants import *
except ImportError:
    bstrap = None


# --- Sistema de Log em Arquivo ---
def setup_file_logger():
    log_dir = Path(project_root) / "logs"
    log_dir.mkdir(exist_ok=True)
    log_filename = log_dir / f"test_run_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

    logger = logging.getLogger('TestRunnerLogger')
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.FileHandler(log_filename, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


class TestRunnerGUI(tk.Tk):
    """
    Interface gráfica "estado da arte" para execução de testes unitários.
    """

    def __init__(self):
        super().__init__()

        if bstrap:
            self.style = bstrap.Style(theme="superhero")
        else:
            self.style = ttk.Style()
        self.title("Painel de Controle de Testes Unitários")
        self.geometry("1200x800")
        self.minsize(900, 600)

        self.logger = setup_file_logger()
        self.test_queue = queue.Queue()
        self.worker_thread = None
        self.stop_event = threading.Event()
        self.discovered_tests = {}
        self.failed_tests = set()
        self.test_item_map = {}

        self._setup_styles()
        self._create_widgets()
        self._discover_tests()
        self.logger.info("Interface de Testes iniciada.")

    # (O restante do código permanece o mesmo da versão anterior, que já está robusto e funcional)
    def _setup_styles(self):
        if bstrap:
            colors = {
                'success': self.style.colors.success, 'fail': self.style.colors.danger,
                'error': self.style.colors.warning,
                'bg': self.style.colors.bg, 'fg': self.style.colors.fg, 'primary': self.style.colors.primary
            }
        else:
            colors = {'success': 'green', 'fail': 'red', 'error': 'orange', 'bg': 'white', 'fg': 'black',
                      'primary': '#0078D7'}

        self.style.map('Treeview', background=[('selected', colors['primary'])])
        self.style.configure("Treeview", background=colors['bg'], foreground=colors['fg'], fieldbackground=colors['bg'],
                             rowheight=25)
        self.style.configure('Success.TLabel', foreground=colors['success'], font=("Segoe UI", 10, "bold"))
        self.style.configure('Fail.TLabel', foreground=colors['fail'], font=("Segoe UI", 10, "bold"))
        self.style.configure('Error.TLabel', foreground=colors['error'], font=("Segoe UI", 10, "bold"))
        self.tag_colors = {'SUCCESS': colors['success'], 'FAIL': colors['fail'], 'ERROR': colors['error']}

    def _create_widgets(self):
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        left_frame = ttk.Frame(main_pane, padding=(5, 0, 10, 0))
        main_pane.add(left_frame, weight=1)

        ttk.Label(left_frame, text="Arquivos de Teste", font=("Segoe UI", 12, "bold")).pack(anchor='w', pady=(0, 5))
        self.test_tree = ttk.Treeview(left_frame, selectmode='browse', show='tree headings', columns=('module'))
        self.test_tree.heading("#0", text="Sel.")
        self.test_tree.column("#0", width=40, anchor='center', stretch=False)
        self.test_tree.heading('module', text="Módulo de Teste")
        self.test_tree.column('module', stretch=True)
        self.test_tree.pack(fill=tk.BOTH, expand=True)
        self.test_tree.bind('<Button-1>', self._toggle_checkbox, add='+')

        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=4)
        self._create_control_panel(right_frame)
        self._create_results_panel(right_frame)

    def _create_control_panel(self, parent):
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        logo_frame = ttk.Frame(top_frame)
        logo_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(logo_frame, text="🧪", font=("Segoe UI", 36, "bold")).pack()

        controls_group = ttk.Frame(top_frame)
        controls_group.pack(side=tk.LEFT, fill=tk.X, expand=True)

        buttons_frame = ttk.Frame(controls_group)
        buttons_frame.pack(fill=tk.X)
        self.run_all_btn = ttk.Button(buttons_frame, text="Executar Tudo", command=self._run_all_tests,
                                      style="success.TButton" if bstrap else "")
        self.run_all_btn.pack(side=tk.LEFT, padx=(0, 5), ipady=5)
        self.run_selected_btn = ttk.Button(buttons_frame, text="Executar Selecionados",
                                           command=self._run_selected_tests, style="primary.TButton" if bstrap else "")
        self.run_selected_btn.pack(side=tk.LEFT, padx=5, ipady=5)
        self.run_failed_btn = ttk.Button(buttons_frame, text="Executar Falhas", command=self._run_failed_tests,
                                         state=tk.DISABLED, style="warning.TButton" if bstrap else "")
        self.run_failed_btn.pack(side=tk.LEFT, padx=5, ipady=5)
        self.stop_btn = ttk.Button(buttons_frame, text="Parar", command=self._stop_tests, state=tk.DISABLED,
                                   style="danger.TButton" if bstrap else "")
        self.stop_btn.pack(side=tk.LEFT, padx=5, ipady=5)
        self.clear_btn = ttk.Button(buttons_frame, text="Limpar", command=self._clear_results,
                                    style="secondary.Outline.TButton" if bstrap else "")
        self.clear_btn.pack(side=tk.LEFT, padx=5, ipady=5)

        metrics_frame = ttk.Frame(controls_group)
        metrics_frame.pack(fill=tk.X, expand=True, pady=(10, 0))
        self.passed_label = ttk.Label(metrics_frame, text="Passou: 0", style='Success.TLabel')
        self.passed_label.pack(side=tk.LEFT, padx=10)
        self.failed_label = ttk.Label(metrics_frame, text="Falhou: 0", style='Fail.TLabel')
        self.failed_label.pack(side=tk.LEFT, padx=10)
        self.errors_label = ttk.Label(metrics_frame, text="Erros: 0", style='Error.TLabel')
        self.errors_label.pack(side=tk.LEFT, padx=10)
        self.total_label = ttk.Label(metrics_frame, text="Total: 0")
        self.total_label.pack(side=tk.LEFT, padx=10)

        if bstrap:
            self.rate_meter = bstrap.Meter(top_frame, metersize=80, padding=5, amounttotal=100,
                                           subtext="Sucesso", interactive=False, bootstyle='success',
                                           textright='%')
            self.rate_meter.pack(side=tk.RIGHT, padx=(20, 0))

        self.progress = ttk.Progressbar(parent, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)

    def _create_results_panel(self, parent):
        results_pane = ttk.PanedWindow(parent, orient=tk.VERTICAL)
        results_pane.pack(fill=tk.BOTH, expand=True)
        results_frame = ttk.Frame(results_pane)
        results_pane.add(results_frame, weight=3)
        cols = ('status', 'test', 'class', 'duration')
        self.results_tree = ttk.Treeview(results_frame, columns=cols, show='headings')
        self.results_tree.heading('status', text='Status');
        self.results_tree.column('status', width=80, anchor='center')
        self.results_tree.heading('test', text='Teste');
        self.results_tree.column('test', width=300)
        self.results_tree.heading('class', text='Classe');
        self.results_tree.column('class', width=250)
        self.results_tree.heading('duration', text='Duração (s)');
        self.results_tree.column('duration', width=100, anchor='e')
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        details_frame = ttk.Frame(results_pane, padding=(0, 10, 0, 0))
        results_pane.add(details_frame, weight=2)
        detail_header = ttk.Frame(details_frame)
        detail_header.pack(fill=tk.X)
        ttk.Label(detail_header, text="Detalhes e Saída do Teste", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        self.clipboard_btn = ttk.Button(detail_header, text="Copiar", command=self._copy_details, state=tk.DISABLED)
        self.clipboard_btn.pack(side=tk.RIGHT)
        self.details_text = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD, font=("Consolas", 9),
                                                      state="disabled")
        self.details_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        self.results_tree.bind('<<TreeviewSelect>>', self._show_details)
        self.results_tree.bind('<Double-1>', self._rerun_selected_test)
        for tag, color in self.tag_colors.items():
            self.results_tree.tag_configure(tag, foreground=color)

    def _discover_tests(self):
        for file in sorted(glob.glob("test_*.py")):
            module_name = file[:-3]
            item = self.test_tree.insert('', 'end', text="☑", values=(module_name,))
            self.discovered_tests[item] = module_name
        self.test_tree.heading('module', text=f" Módulos ({len(self.discovered_tests)})")

    def _toggle_checkbox(self, event):
        item_id = self.test_tree.identify_row(event.y)
        if not item_id: return

        column = self.test_tree.identify_column(event.x)
        if column == "#0":
            current_text = self.test_tree.item(item_id, 'text')
            new_text = "☐" if current_text == "☑" else "☑"
            self.test_tree.item(item_id, text=new_text)

    def _run_selected_tests(self):
        modules_to_run = [
            self.discovered_tests[item]
            for item in self.test_tree.get_children()
            if self.test_tree.item(item, 'text') == "☑"
        ]
        if not modules_to_run:
            messagebox.showwarning("Nenhum Teste Selecionado",
                                   "Por favor, selecione ao menos um arquivo de teste para executar.", parent=self)
            return
        self._start_test_run(modules_to_run)

    def _run_all_tests(self):
        modules_to_run = list(self.discovered_tests.values())
        self._start_test_run(modules_to_run)

    def _run_failed_tests(self):
        self._start_test_run(list(self.failed_tests))

    def _rerun_selected_test(self, event):
        if not (selected := self.results_tree.selection()): return
        item_id = selected[0]
        item_data = self.test_item_map.get(item_id)
        if item_data:
            module_to_run = item_data.get('module')
            test_id_to_run = item_data.get('id')
            if module_to_run and test_id_to_run:
                self._start_test_run([module_to_run], rerun_single=test_id_to_run)

    def _start_test_run(self, modules_to_run, rerun_single=None):
        self._toggle_controls(is_running=True)
        if not rerun_single:
            self._clear_results()
        self.stop_event.clear()

        self.worker_thread = threading.Thread(
            target=self._test_worker,
            args=(modules_to_run, self.test_queue, self.stop_event, rerun_single, self.logger),
            daemon=True
        )
        self.worker_thread.start()
        self.after(100, self._process_queue)

    def _stop_tests(self):
        self.stop_event.set()
        self.stop_btn.config(state=tk.DISABLED, text="Parando...")

    def _clear_results(self):
        self.failed_tests.clear()
        self.test_item_map.clear()
        self.results_tree.delete(*self.results_tree.get_children())
        self.details_text.config(state="normal");
        self.details_text.delete("1.0", tk.END);
        self.details_text.config(state="disabled")
        self.passed_label.config(text="Passou: 0")
        self.failed_label.config(text="Falhou: 0")
        self.errors_label.config(text="Erros: 0")
        self.total_label.config(text="Total: 0")
        self.progress['value'] = 0
        self.clipboard_btn.config(state=tk.DISABLED)
        if bstrap and hasattr(self, 'rate_meter'): self.rate_meter.configure(amountused=0)

    def _toggle_controls(self, is_running):
        state = tk.DISABLED if is_running else tk.NORMAL
        self.run_all_btn.config(state=state)
        self.run_selected_btn.config(state=state)
        self.clear_btn.config(state=state)
        self.run_failed_btn.config(state=tk.NORMAL if not is_running and self.failed_tests else tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL if is_running else tk.DISABLED, text="Parar")

    def _process_queue(self):
        try:
            while True:
                msg = self.test_queue.get_nowait()
                msg_type = msg['type']
                if msg_type == 'start':
                    self.progress['maximum'] = msg['total']
                elif msg_type == 'test_result':
                    self._update_test_result(msg['data'])
                elif msg_type == 'finish':
                    self._toggle_controls(is_running=False)
                    self.logger.info(
                        f"Execução de teste finalizada. Resultados: {self.total_label.cget('text')}, {self.passed_label.cget('text')}, {self.failed_label.cget('text')}, {self.errors_label.cget('text')}.")
                    break
        except queue.Empty:
            if self.worker_thread and self.worker_thread.is_alive():
                self.after(100, self._process_queue)
            else:
                self._toggle_controls(is_running=False)

    def _update_test_result(self, data):
        test_id = data['id']
        status = data['status']
        values = (status, data['short_name'], data['class_name'], f"{data['duration']:.4f}")

        if test_id in self.test_item_map:
            item_iid = self.test_item_map[test_id]['iid']
            self.results_tree.item(item_iid, values=values, tags=(status,))
            self.test_item_map[test_id]['output'] = data['output']
        else:
            item_iid = self.results_tree.insert('', 'end', iid=test_id, values=values, tags=(status,))
            self.test_item_map[test_id] = {'iid': item_iid, 'output': data['output'], 'module': data['module'],
                                           'id': test_id}

        if status in ('FAIL', 'ERROR'):
            self.failed_tests.add(data['module'])
        else:
            self.failed_tests.discard(data['module'])

        counts = {'SUCCESS': 0, 'FAIL': 0, 'ERROR': 0}
        total = len(self.test_item_map)
        for item_data in self.test_item_map.values():
            status = self.results_tree.item(item_data['iid'], 'values')[0]
            if status in counts: counts[status] += 1

        self.passed_label.config(text=f"Passou: {counts['SUCCESS']}")
        self.failed_label.config(text=f"Falhou: {counts['FAIL']}")
        self.errors_label.config(text=f"Erros: {counts['ERROR']}")
        self.total_label.config(text=f"Total: {total}")
        self.progress['value'] = total

        if bstrap and hasattr(self, 'rate_meter') and total > 0:
            rate = (counts['SUCCESS'] / total) * 100
            self.rate_meter.configure(amountused=rate)

    def _show_details(self, event):
        if not (selected := self.results_tree.selection()): return
        selected_iid = selected[0]
        output_to_show = self.test_item_map.get(selected_iid, {}).get('output', "")

        self.details_text.config(state="normal")
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert("1.0", output_to_show)
        self.details_text.config(state="disabled")
        self.clipboard_btn.config(state=tk.NORMAL if output_to_show else tk.DISABLED)

    def _copy_details(self):
        content = self.details_text.get("1.0", tk.END).strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            original_text = self.clipboard_btn.cget('text')
            self.clipboard_btn.config(text="Copiado!")
            self.after(1500, lambda: self.clipboard_btn.config(text=original_text))

    @staticmethod
    def _test_worker(modules_to_run, q, stop_event, rerun_single, logger):
        logger.info(f"Worker iniciado para executar: {rerun_single or modules_to_run}")
        suite = unittest.TestSuite()
        loader = unittest.TestLoader()

        if rerun_single:
            try:
                suite.addTest(loader.loadTestsFromName(rerun_single))
            except Exception:
                module_name = rerun_single.split('.')[0]
                modules_to_run = [module_name]
                rerun_single = None

        if not rerun_single or suite.countTestCases() == 0:
            for module_name in modules_to_run:
                try:
                    module = importlib.import_module(module_name)
                    importlib.reload(module)
                    suite.addTests(loader.loadTestsFromModule(module))
                except Exception as e:
                    error_data = {'id': f"loading.{module_name}", 'module': module_name, 'short_name': 'LOAD_ERROR',
                                  'class_name': module_name, 'status': 'ERROR', 'duration': 0,
                                  'output': f"ERRO FATAL AO CARREGAR O ARQUIVO: {module_name.upper()}\n{type(e).__name__}: {e}"}
                    q.put({'type': 'test_result', 'data': error_data})
                    logger.error(f"Falha ao carregar o módulo de teste: {module_name}", exc_info=True)

        total_tests = suite.countTestCases()
        q.put({'type': 'start', 'total': total_tests})
        result = CustomTestResult(q, stop_event, logger)
        suite.run(result)
        q.put({'type': 'finish'})


class CustomTestResult(unittest.TestResult):
    def __init__(self, q, stop_event, logger):
        super().__init__()
        self.q = q
        self.stop_event = stop_event
        self.logger = logger
        self.start_time = 0

    def startTest(self, test):
        super().startTest(test)
        self.start_time = datetime.now().timestamp()
        self.logger.info(f"Iniciando teste: {test.id()}")

    def stopTest(self, test):
        if self.stop_event.is_set():
            self.stop()
        super().stopTest(test)

    def addSuccess(self, test):
        super().addSuccess(test)
        self.logger.info(f"SUCESSO: {test.id()}")
        self._report_result(test, 'SUCCESS')

    def addFailure(self, test, err):
        super().addFailure(test, err)
        output = self._exc_info_to_string(err, test)
        self.logger.warning(f"FALHA: {test.id()}\n{output}")
        self._report_result(test, 'FAIL', output)

    def addError(self, test, err):
        super().addError(test, err)
        output = self._exc_info_to_string(err, test)
        self.logger.error(f"ERRO: {test.id()}\n{output}")
        self._report_result(test, 'ERROR', output)

    def _report_result(self, test, status, output=''):
        end_time = datetime.now().timestamp()
        duration = end_time - self.start_time
        test_id = test.id()
        module_name = test.__class__.__module__
        class_name = test.__class__.__name__
        short_name = test.shortDescription() or test._testMethodName
        full_output = f"{status}: {test_id}\n\n{output}"
        data = {'id': test_id, 'module': module_name, 'short_name': short_name, 'class_name': class_name,
                'status': status, 'duration': duration, 'output': full_output.strip()}
        self.q.put({'type': 'test_result', 'data': data})


if __name__ == "__main__":
    app = TestRunnerGUI()
    app.mainloop()