                                                        
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import unittest
import sys
import os
import glob
import importlib
import threading
import queue
import time
from datetime import datetime


class TestRunnerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Painel de Execução de Testes Unitários")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)

        self.test_queue = queue.Queue()
        self.worker_thread = None
        self.stop_event = threading.Event()

        self.discovered_tests = {}
        self.test_item_map = {}
        self.failed_tests_info = set()

                                               
        self.log_file_handler = None
        self.log_filename = ""

        self._setup_styles()
        self._create_widgets()
        self.root.after(100, self._discover_tests)

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))
        style.configure("Treeview", rowheight=25, font=('Segoe UI', 9))
        style.map('Treeview', background=[('selected', '#0078D7')])

        style.configure("Success.TLabel", foreground="green", font=('Segoe UI', 10, 'bold'))
        style.configure("Fail.TLabel", foreground="red", font=('Segoe UI', 10, 'bold'))
        style.configure("Error.TLabel", foreground="dark orange", font=('Segoe UI', 10, 'bold'))
        style.configure("Total.TLabel", foreground="black", font=('Segoe UI', 10, 'bold'))

    def _create_widgets(self):
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, weight=1)
        self._create_test_selection_area(left_frame)

        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=4)
        self._create_results_area(right_frame)

    def _create_test_selection_area(self, parent):
        container = ttk.LabelFrame(parent, text="Módulos de Teste", padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        self.test_tree = ttk.Treeview(container, columns=('module',), show='tree headings')
        self.test_tree.heading('#0', text='Sel.')
        self.test_tree.column('#0', width=40, anchor='center', stretch=False)
        self.test_tree.heading('module', text='Arquivo')
        self.test_tree.pack(fill=tk.BOTH, expand=True)
        self.test_tree.bind('<Button-1>', self._toggle_checkbox, add='+')

    def _create_results_area(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        control_panel = self._create_control_panel(parent)
        control_panel.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        results_panel = self._create_results_panel(parent)
        results_panel.grid(row=1, column=0, sticky="nsew")

    def _create_control_panel(self, parent):
        frame = ttk.Frame(parent)

        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(fill=tk.X, expand=True, pady=(0, 10))

        self.run_all_btn = ttk.Button(buttons_frame, text="Executar Tudo", command=self._run_all_tests)
        self.run_all_btn.pack(side=tk.LEFT, padx=(0, 5), ipady=5)

        self.run_selected_btn = ttk.Button(buttons_frame, text="Executar Selecionados",
                                           command=self._run_selected_tests)
        self.run_selected_btn.pack(side=tk.LEFT, padx=5, ipady=5)

        self.run_failed_btn = ttk.Button(buttons_frame, text="Executar Falhas", command=self._run_failed_tests,
                                         state=tk.DISABLED)
        self.run_failed_btn.pack(side=tk.LEFT, padx=5, ipady=5)

        self.stop_btn = ttk.Button(buttons_frame, text="Parar", command=self._stop_tests, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5, ipady=5)

        self.clear_btn = ttk.Button(buttons_frame, text="Limpar", command=self._clear_results)
        self.clear_btn.pack(side=tk.RIGHT, padx=5, ipady=5)

        metrics_frame = ttk.Frame(frame)
        metrics_frame.pack(fill=tk.X, expand=True, pady=(5, 5))

        self.passed_label = ttk.Label(metrics_frame, text="Passou: 0", style='Success.TLabel')
        self.passed_label.pack(side=tk.LEFT, padx=(0, 15))

        self.failed_label = ttk.Label(metrics_frame, text="Falhou: 0", style='Fail.TLabel')
        self.failed_label.pack(side=tk.LEFT, padx=(0, 15))

        self.errors_label = ttk.Label(metrics_frame, text="Erros: 0", style='Error.TLabel')
        self.errors_label.pack(side=tk.LEFT, padx=(0, 15))

        self.total_label = ttk.Label(metrics_frame, text="Total: 0", style='Total.TLabel')
        self.total_label.pack(side=tk.LEFT, padx=(0, 15))

        self.progress = ttk.Progressbar(frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.pack(fill=tk.X, expand=True, pady=(5, 0))

        self.status_label = ttk.Label(frame, text="Aguardando para iniciar...")
        self.status_label.pack(anchor='w', fill=tk.X, expand=True, pady=(5, 0))

        return frame

    def _create_results_panel(self, parent):
        pane = ttk.PanedWindow(parent, orient=tk.VERTICAL)

        results_container = ttk.LabelFrame(pane, text="Resultados", padding=10)
        pane.add(results_container, weight=3)

        cols = ('status', 'test', 'class', 'duration')
        self.results_tree = ttk.Treeview(results_container, columns=cols, show='headings')
        self.results_tree.heading('status', text='Status')
        self.results_tree.column('status', width=80, anchor='center')
        self.results_tree.heading('test', text='Teste')
        self.results_tree.column('test', width=300)
        self.results_tree.heading('class', text='Classe')
        self.results_tree.column('class', width=250)
        self.results_tree.heading('duration', text='Duração (s)')
        self.results_tree.column('duration', width=100, anchor='e')

        scrollbar = ttk.Scrollbar(results_container, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)

        results_container.rowconfigure(0, weight=1)
        results_container.columnconfigure(0, weight=1)
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.results_tree.tag_configure('SUCCESS', foreground='green')
        self.results_tree.tag_configure('FAIL', foreground='red')
        self.results_tree.tag_configure('ERROR', foreground='dark orange')

        details_container = ttk.LabelFrame(pane, text="Detalhes da Falha/Erro", padding=10)
        pane.add(details_container, weight=2)
        details_container.rowconfigure(1, weight=1)
        details_container.columnconfigure(0, weight=1)

                                            
        details_actions_frame = ttk.Frame(details_container)
        details_actions_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.copy_details_btn = ttk.Button(details_actions_frame, text="Copiar Detalhes para Área de Transferência",
                                           command=self._copy_details_to_clipboard, state="disabled")
        self.copy_details_btn.pack(side="left")

        self.details_text = scrolledtext.ScrolledText(details_container, wrap=tk.WORD, font=("Consolas", 9),
                                                      state="disabled")
        self.details_text.grid(row=1, column=0, sticky="nsew")

        self.results_tree.bind('<<TreeviewSelect>>', self._show_details)
        self.results_tree.bind('<Double-1>', self._rerun_selected_test)

        return pane

                                       
    def _copy_details_to_clipboard(self):
        content = self.details_text.get("1.0", tk.END).strip()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.status_label.config(text="Detalhes do erro copiados para a área de transferência.")
        else:
            self.status_label.config(text="Nenhum detalhe para copiar.")

    def _discover_tests(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)

        for file in sorted(glob.glob(os.path.join(current_dir, "test_*.py"))):
            module_name = os.path.basename(file)[:-3]
            item = self.test_tree.insert('', 'end', text="☑", values=(module_name,))
            self.discovered_tests[item] = module_name

        self.test_tree.heading('module', text=f'Arquivo ({len(self.discovered_tests)})')

    def _toggle_checkbox(self, event):
        item_id = self.test_tree.identify_row(event.y)
        if not item_id or self.test_tree.identify_column(event.x) != "#0":
            return

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
            messagebox.showwarning("Nenhum Teste Selecionado", "Selecione ao menos um módulo de teste.")
            return
        self._start_test_run(modules_to_run)

    def _run_all_tests(self):
        modules_to_run = list(self.discovered_tests.values())
        self._start_test_run(modules_to_run)

    def _run_failed_tests(self):
        self._start_test_run(test_ids_to_run=list(self.failed_tests_info))

    def _rerun_selected_test(self, event):
        selected = self.results_tree.selection()
        if not selected: return

        item_data = self.test_item_map.get(selected[0])
        if item_data and 'id' in item_data:
            self._start_test_run(test_ids_to_run=[item_data['id']])

    def _start_test_run(self, modules_to_run=None, test_ids_to_run=None):
        self._toggle_controls(is_running=True)

        if not test_ids_to_run:                                                                     
            self._clear_results()
                                           
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.log_filename = f"test_results_{timestamp}.log"
                self.log_file_handler = open(self.log_filename, 'w', encoding='utf-8')
                self.log_file_handler.write(f"Test Run Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                self.log_file_handler.write("=" * 80 + "\n\n")
            except IOError as e:
                messagebox.showerror("Erro de Log", f"Não foi possível criar o arquivo de log: {e}")
                self.log_file_handler = None

        self.stop_event.clear()

        self.worker_thread = threading.Thread(
            target=self._test_worker,
            args=(modules_to_run, test_ids_to_run, self.test_queue, self.stop_event),
            daemon=True
        )
        self.worker_thread.start()
        self.root.after(100, self._process_queue)

    def _stop_tests(self):
        if self.worker_thread and self.worker_thread.is_alive():
            self.stop_event.set()
            self.stop_btn.config(state=tk.DISABLED, text="Parando...")
            self.status_label.config(text="Sinal de parada enviado. Aguardando a conclusão do teste atual...")

    def _clear_results(self):
        self.failed_tests_info.clear()
        self.test_item_map.clear()
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        self.details_text.config(state="normal")
        self.details_text.delete("1.0", tk.END)
        self.details_text.config(state="disabled")
        self.copy_details_btn.config(state="disabled")                                

        self.passed_label.config(text="Passou: 0")
        self.failed_label.config(text="Falhou: 0")
        self.errors_label.config(text="Erros: 0")
        self.total_label.config(text="Total: 0")
        self.progress['value'] = 0
        self.status_label.config(text="Aguardando para iniciar...")

    def _toggle_controls(self, is_running):
        state = tk.DISABLED if is_running else tk.NORMAL
        self.run_all_btn.config(state=state)
        self.run_selected_btn.config(state=state)
        self.clear_btn.config(state=state)

        self.run_failed_btn.config(state=tk.NORMAL if not is_running and self.failed_tests_info else tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL if is_running else tk.DISABLED, text="Parar")

    def _process_queue(self):
        try:
            while True:
                msg = self.test_queue.get_nowait()
                msg_type = msg.get('type')

                if msg_type == 'start':
                    self.progress['maximum'] = msg['total']
                    self.status_label.config(text=f"Executando {msg['total']} testes...")
                elif msg_type == 'test_result':
                    self._update_test_result(msg['data'])
                elif msg_type == 'finish':
                    self._finalize_test_run()
                    break
        except queue.Empty:
            if self.worker_thread and self.worker_thread.is_alive():
                self.root.after(100, self._process_queue)
            else:
                self._finalize_test_run()

                                          
    def _finalize_test_run(self):
        self._toggle_controls(is_running=False)
        final_status = f"Execução finalizada. {self.total_label.cget('text')}."
                                                 
        if self.log_file_handler:
            try:
                summary = (f"\n{'=' * 80}\n"
                           f"Test Run Finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                           f"Summary: {self.passed_label.cget('text')}, {self.failed_label.cget('text')}, {self.errors_label.cget('text')}\n")
                self.log_file_handler.write(summary)
                self.log_file_handler.close()
                final_status += f" Resultados salvos em {self.log_filename}."
            except IOError:
                final_status += " (Falha ao escrever sumário no log)."
            finally:
                self.log_file_handler = None

        self.status_label.config(text=final_status)

    def _update_test_result(self, data):
        test_id = data['id']
        status = data['status']
        values = (status, data['short_name'], data['class_name'], f"{data['duration']:.4f}")

                                         
        if self.log_file_handler:
            try:
                log_entry = f"[{status:<7}] | {data['duration']:.4f}s | {data['id']}\n"
                self.log_file_handler.write(log_entry)
                if status in ('FAIL', 'ERROR'):
                    self.log_file_handler.write("-" * 80 + "\n")
                    self.log_file_handler.write(data['output'] + "\n")
                    self.log_file_handler.write("-" * 80 + "\n\n")
            except IOError:                                                          
                self.log_file_handler = None
                self.status_label.config(text="ERRO: Perda do handle do arquivo de log. Logging interrompido.")

        if test_id in self.test_item_map:
            item_iid = self.test_item_map[test_id]['iid']
            self.results_tree.item(item_iid, values=values, tags=(status,))
            self.test_item_map[test_id].update(data)
        else:
            item_iid = self.results_tree.insert('', 'end', iid=test_id, values=values, tags=(status,))
            self.test_item_map[test_id] = {'iid': item_iid, **data}

        if status in ('FAIL', 'ERROR'):
            self.failed_tests_info.add(test_id)
        else:
            self.failed_tests_info.discard(test_id)

        self._update_metrics()

    def _update_metrics(self):
        counts = {'SUCCESS': 0, 'FAIL': 0, 'ERROR': 0}
        total_processed = len(self.test_item_map)
        for item_data in self.test_item_map.values():
            status = item_data['status']
            if status in counts:
                counts[status] += 1

        self.passed_label.config(text=f"Passou: {counts['SUCCESS']}")
        self.failed_label.config(text=f"Falhou: {counts['FAIL']}")
        self.errors_label.config(text=f"Erros: {counts['ERROR']}")
        self.total_label.config(text=f"Total: {total_processed}")
        if self.progress['maximum'] > 0:
            self.progress['value'] = total_processed

    def _show_details(self, event):
        selected = self.results_tree.selection()
        if not selected:
            self.copy_details_btn.config(state="disabled")
            return

        output_to_show = self.test_item_map.get(selected[0], {}).get('output', "")

        self.details_text.config(state="normal")
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert("1.0", output_to_show)
        self.details_text.config(state="disabled")

                                                             
        self.copy_details_btn.config(state="normal" if output_to_show else "disabled")

    @staticmethod
    def _test_worker(modules_to_run, test_ids_to_run, q, stop_event):
        suite = unittest.TestSuite()
        loader = unittest.TestLoader()

        if test_ids_to_run:
            suite.addTests(loader.loadTestsFromNames(list(test_ids_to_run)))                                 
        elif modules_to_run:
            for module_name in modules_to_run:
                try:
                    module = importlib.import_module(module_name)
                    importlib.reload(module)
                    suite.addTests(loader.loadTestsFromModule(module))
                except Exception as e:
                    error_data = {
                        'id': f"loading_error.{module_name}",
                        'status': 'ERROR', 'short_name': 'LOAD_ERROR',
                        'class_name': module_name, 'duration': 0,
                        'output': f"ERRO CRÍTICO AO CARREGAR MÓDULO '{module_name}':\n\n{type(e).__name__}: {e}"
                    }
                    q.put({'type': 'test_result', 'data': error_data})

        total_tests = suite.countTestCases()
        if total_tests > 0:
                                                                       
            if not test_ids_to_run or len(test_ids_to_run) == total_tests:
                q.put({'type': 'start', 'total': total_tests})

            result = CustomTestResult(q, stop_event)
            suite.run(result)

        q.put({'type': 'finish'})


class CustomTestResult(unittest.TestResult):
    def __init__(self, q, stop_event):
        super().__init__()
        self.q = q
        self.stop_event = stop_event
        self.start_time = 0

    def startTest(self, test):
        super().startTest(test)
        self.start_time = time.perf_counter()

    def stopTest(self, test):
        if self.stop_event.is_set():
            self.stop()
        super().stopTest(test)

    def addSuccess(self, test):
        super().addSuccess(test)
        self._report_result(test, 'SUCCESS')

    def addFailure(self, test, err):
        super().addFailure(test, err)
        output = self._exc_info_to_string(err, test)
        self._report_result(test, 'FAIL', output)

    def addError(self, test, err):
        super().addError(test, err)
        output = self._exc_info_to_string(err, test)
        self._report_result(test, 'ERROR', output)

    def _report_result(self, test, status, output=''):
        duration = time.perf_counter() - self.start_time
        test_id = test.id()
        class_name = test.__class__.__name__
        short_name = test.shortDescription() or test._testMethodName

                                                        
        full_output = f"{status}: {test_id}\n\n{output}" if output else f"{status}: {test_id}"

        data = {
            'id': test_id, 'short_name': short_name, 'class_name': class_name,
            'status': status, 'duration': duration, 'output': output.strip()
        }
        self.q.put({'type': 'test_result', 'data': data})


def main():
    if sys.platform == "win32":
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)

    root = tk.Tk()
    app = TestRunnerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()