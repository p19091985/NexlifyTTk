                      
import queue
import re
import sys
import threading
import logging
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, PhotoImage, messagebox
from typing import Type, Dict, List
from dataclasses import asdict
import pandas as pd

from common.base_suite import BaseTestSuite
from common.models import TestResult, TestStatus

from suites.suite_classic import ClassicTestSuite
from suites.suite_modern import ModernTestSuite
from suites.suite_parallel import ParallelDivineSuite
from suites.suite_supreme import SupremeTestSuite
from suites.suite_ultimate import UltimateTestSuite
from suites.suite_concurrency import ConcurrencyTestSuite
from suites.suite_database_stress import DatabaseStressTestSuite


                                     
class ToolTip:
    """
    Cria uma dica de ajuda (tooltip) para um widget tkinter.
    """

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.id = None
        self.widget.bind("<Enter>", self.schedule_show)
        self.widget.bind("<Leave>", self.schedule_hide)

    def schedule_show(self, event=None):
        self.id = self.widget.after(500, self.show_tip)

    def schedule_hide(self, event=None):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def show_tip(self, event=None):
        if self.tooltip_window:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 1

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip_window, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"), wraplength=300)
        label.pack(ipadx=1)


                                       
class UltimateTestDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🚀 Dashboard de Testes Supremo 🚀")
        self.attributes('-zoomed', True)
        self.minsize(1200, 700)

        self._setup_styles()
        self._setup_logging()

        self.test_queue = queue.Queue()
        self.results: List[TestResult] = []
        self.test_details_map: Dict[str, TestResult] = {}
        self.total_tests_in_suite = 0
        self.active_suite_button: ttk.Button | None = None
        self.suite_execution_queue: List[Type[BaseTestSuite]] = []
        self.total_suites_in_run_all = 0
        self.current_suite_index = 0

        self.available_suites: Dict[str, Type[BaseTestSuite]] = {
            "Clássica": ClassicTestSuite, "Moderna": ModernTestSuite, "Divina (Paralela)": ParallelDivineSuite,
            "Suprema": SupremeTestSuite, "Ultimate": UltimateTestSuite, "Acesso Concorrente": ConcurrencyTestSuite,
            "Estresse de BD": DatabaseStressTestSuite,
        }

        self._create_main_layout()
        self._setup_detail_text_styles()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.logger.info("Dashboard de Testes Supremo iniciado com sucesso.")

    def _setup_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        self.colors = {'success': '#28a745', 'danger': '#dc3545', 'warning': '#ffc107', 'info': '#17a2b8',
                       'primary': '#007bff', 'secondary': '#6c757d'}

        self.style.configure('TButton', padding=5)
        self.style.configure('Success.TButton', foreground='white', background=self.colors['success'])
        self.style.map('Success.TButton', background=[('active', '#218838')])
        self.style.configure('Info.TButton', foreground='white', background=self.colors['info'])
        self.style.map('Info.TButton', background=[('active', '#138496')])
        self.style.configure('Outline.TButton', foreground=self.colors['primary'], relief="solid", borderwidth=1)
        self.style.map('Outline.TButton',
                       foreground=[('active', 'white')],
                       background=[('active', self.colors['primary'])]
                       )

        for color_name, color_code in self.colors.items():
            self.style.configure(f'{color_name.capitalize()}.TLabel', foreground=color_code)

    def _setup_logging(self):
        log_filename = f"run_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
        self.logger = logging.getLogger('TestDashboard')
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.FileHandler(log_filename, encoding='utf-8')
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)

    def _create_main_layout(self):
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        sidebar_frame = ttk.Frame(main_pane, padding=10)
        main_pane.add(sidebar_frame, weight=1)
        self._create_sidebar(sidebar_frame)
        content_frame = ttk.Frame(main_pane, padding=10)
        main_pane.add(content_frame, weight=5)
        self._create_content_area(content_frame)

    def _create_sidebar(self, parent):
        self._create_logo(parent)
        ttk.Label(parent, text="Suítes de Teste", font=("-size 16 -weight bold")).pack(pady=(10, 20), anchor="w")
        run_all_btn = ttk.Button(parent, text="⚡ Executar Todas as Suítes", style="Success.TButton",
                                 command=self.run_all_suites)
        run_all_btn.pack(fill=tk.X, ipady=8, pady=5)
        ToolTip(run_all_btn, text="Executa todas as suítes de teste em sequência.")
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        self.run_buttons: Dict[str, ttk.Button] = {}
        for name, suite_class in self.available_suites.items():
            button = ttk.Button(parent, text=name, style="Outline.TButton",
                                command=lambda sc=suite_class, btn_name=name: self.run_suite(sc, btn_name))
            button.pack(fill=tk.X, ipady=5, pady=2)
            self.run_buttons[name] = button
            ToolTip(button, text=suite_class.description)                           
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        self._create_legend(parent)

    def _create_logo(self, parent):
        try:
            self.logo_image = PhotoImage(file="logo.png")
            ttk.Label(parent, image=self.logo_image).pack(pady=(0, 10))
        except tk.TclError:
            ttk.Label(parent, text="[LOGO]", font=("-size 12"), style="Secondary.TLabel").pack(pady=(10, 10))
            self.logger.warning("Arquivo 'logo.png' não encontrado.")

    def _create_legend(self, parent):
        legend_frame = ttk.LabelFrame(parent, text=" Legenda ", padding=10)
        legend_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(15, 0))
        legend_colors = {
            TestStatus.SUCCESS: self.colors['success'], TestStatus.FAIL: self.colors['danger'],
            TestStatus.ERROR: self.colors['warning'],
            TestStatus.DIVINE_PASS: self.colors['info'], TestStatus.GODLIKE: self.colors['primary'],
        }
        for status, color in legend_colors.items():
            frame = ttk.Frame(legend_frame)
            frame.pack(fill=tk.X, anchor="w", pady=1)
            ttk.Label(frame, text="●", foreground=color, font=("-weight bold")).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Label(frame, text=status.name.replace("_", " ").title()).pack(side=tk.LEFT)

    def _create_content_area(self, parent):
        metrics_container = ttk.Frame(parent)
        metrics_container.pack(fill=tk.X, pady=(0, 10))
        geral_frame = ttk.LabelFrame(metrics_container, text=" Visão Geral ", padding=10)
        geral_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self._create_geral_metrics_widgets(geral_frame)
        status_frame = ttk.LabelFrame(metrics_container, text=" Detalhamento de Status ", padding=10)
        status_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._create_status_metrics_widgets(status_frame)
        progress_frame = ttk.Frame(parent)
        progress_frame.pack(fill=tk.X, pady=(5, 15))
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, expand=True)
        self.progress_label = ttk.Label(progress_frame, text="Selecione uma suíte de teste para começar.",
                                        style="Info.TLabel")
        self.progress_label.pack(anchor="w", pady=(5, 0))
        results_pane = ttk.PanedWindow(parent, orient=tk.VERTICAL)
        results_pane.pack(fill=tk.BOTH, expand=True)
        results_frame = ttk.Frame(results_pane)
        results_pane.add(results_frame, weight=3)
        self._create_results_tree(results_frame)
        details_frame = ttk.LabelFrame(results_pane, text=" Detalhes do Teste Selecionado ", padding=10)
        results_pane.add(details_frame, weight=2)
        self.details_text = scrolledtext.ScrolledText(details_frame, wrap="word", font=("Courier New", 10),
                                                      state="disabled")
        self.details_text.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self._create_export_buttons(details_frame)

    def _create_geral_metrics_widgets(self, parent):
        parent.columnconfigure((0, 1, 2), weight=1)
        self.total_metric = self._create_metric_card(parent, "Total", "0", 0)
        self.rate_metric = self._create_metric_card(parent, "Taxa Suc.", "0%", 1, "Info")
        self.time_metric = self._create_metric_card(parent, "Tempo", "0.0s", 2, "Secondary")

    def _create_status_metrics_widgets(self, parent):
        parent.columnconfigure((0, 1, 2, 3, 4), weight=1)
        self.success_metric = self._create_metric_card(parent, "Success", "0", 0, "Success")
        self.fail_metric = self._create_metric_card(parent, "Fail", "0", 1, "Danger")
        self.error_metric = self._create_metric_card(parent, "Error", "0", 2, "Warning")
        self.divine_metric = self._create_metric_card(parent, "Divine", "0", 3, "Info")
        self.godlike_metric = self._create_metric_card(parent, "Godlike", "0", 4, "Primary")

    def _create_metric_card(self, parent, title, value, column, style="Default"):
        frame = ttk.Frame(parent)
        frame.grid(row=0, column=column, padx=5, pady=2, sticky="ew")
        ttk.Label(frame, text=title, font=("-weight bold")).pack()
        value_label = ttk.Label(frame, text=value, font=("-size 14"), style=f"{style.capitalize()}.TLabel")
        value_label.pack()
        return value_label

    def _create_results_tree(self, parent):
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        self.columns = ('status', 'suite', 'method', 'duration', 'severity')
        self.tree = ttk.Treeview(tree_frame, columns=self.columns, show='headings')
        for col in self.columns: self.tree.heading(col, text=col.replace('_', ' ').title(),
                                                   command=lambda c=col: self._sort_treeview(c, False))
        self.tree.column('status', width=120, stretch=False);
        self.tree.column('suite', width=150, stretch=False);
        self.tree.column('method', width=400);
        self.tree.column('duration', width=100, stretch=False, anchor='e');
        self.tree.column('severity', width=100, stretch=False, anchor='center')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self._on_result_select)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        for status in TestStatus:
                                                                
            color = self.colors.get(status.name.lower().replace("_pass", ""), 'black')
            self.tree.tag_configure(status.name, foreground=color)

    def _sort_treeview(self, col, reverse):
        try:
            data = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
            try:
                data.sort(key=lambda x: float(x[0]), reverse=reverse)
            except ValueError:
                data.sort(key=lambda x: x[0], reverse=reverse)
            for index, (val, item) in enumerate(data): self.tree.move(item, '', index)
            self.tree.heading(col, command=lambda: self._sort_treeview(col, not reverse))
        except tk.TclError:
            self.logger.warning(f"Não foi possível ordenar a coluna {col}.")

    def _create_export_buttons(self, parent):
        export_frame = ttk.Frame(parent)
        export_frame.pack(fill=tk.X, pady=(5, 0))
        self.copy_detail_btn = ttk.Button(export_frame, text="📋 Copiar", command=self.copy_test_detail,
                                          style="Outline.TButton", state="disabled")
        self.copy_detail_btn.pack(side=tk.RIGHT)
        self.export_detail_btn = ttk.Button(export_frame, text="Exportar Detalhe (.txt)",
                                            command=self.export_test_detail, style="Outline.TButton", state="disabled")
        self.export_detail_btn.pack(side=tk.RIGHT, padx=(0, 10))
        self.export_suite_btn = ttk.Button(export_frame, text="Exportar Resultados (CSV)",
                                           command=self.export_suite_results, style="Outline.TButton", state="disabled")
        self.export_suite_btn.pack(side=tk.RIGHT, padx=(0, 10))

    def _setup_detail_text_styles(self):
        self.details_text.tag_configure("header", font=("Courier New", 10, "bold"), foreground=self.colors['info'])

    def run_all_suites(self):
        self._reset_ui(is_run_all=True)
        self.suite_execution_queue = list(self.available_suites.items())
        self.total_suites_in_run_all = len(self.suite_execution_queue)
        self.current_suite_index = 0
        self._run_next_suite_in_queue()

    def _run_next_suite_in_queue(self):
        if self.suite_execution_queue:
            self.current_suite_index += 1
            name, suite_class = self.suite_execution_queue.pop(0)
            for item in self.tree.get_children(): self.tree.delete(item)
            self.total_tests_in_suite = 0
            self.run_suite(suite_class, name, is_part_of_run_all=True)

    def run_suite(self, suite_class: Type[BaseTestSuite], button_name: str, is_part_of_run_all: bool = False):
        if not is_part_of_run_all: self._reset_ui()
        self.active_suite_button = self.run_buttons.get(button_name)
        if self.active_suite_button: self.active_suite_button.config(text="Executando...", state="disabled",
                                                                     style="Info.TButton")
        suite_instance = suite_class(self.test_queue)
        self.logger.info(f"Iniciando suíte: {suite_instance.suite_name}")
        progress_text = f"Executando Suíte {self.current_suite_index}/{self.total_suites_in_run_all}: {suite_instance.suite_name}..." if is_part_of_run_all else f"Iniciando suíte: {suite_instance.suite_name}..."
        self.progress_label.config(text=progress_text)
        threading.Thread(target=suite_instance.run, daemon=True).start()
        self.after(100, self.process_queue)

    def process_queue(self):
        try:
            while True:
                msg = self.test_queue.get_nowait()
                msg_type = msg.get("type")
                if msg_type == "total_tests":
                    self.total_tests_in_suite = msg.get('count', 0)
                    if self.total_tests_in_suite > 0: self.progress_bar['maximum'] = self.total_tests_in_suite
                elif msg_type == "progress_update":
                    if 'value' in msg:
                        self.progress_bar.config(mode='determinate', maximum=1.0, value=msg['value'])
                    else:
                        self.progress_bar.config(mode='indeterminate');
                        self.progress_bar.start()
                    if 'text' in msg: self.progress_label.config(text=msg['text'])
                elif msg_type == "test_result":
                    if self.progress_bar['mode'] == 'indeterminate': self.progress_bar.stop(); self.progress_bar.config(
                        mode='determinate')
                    self._handle_test_result(msg["result"])
                elif msg_type == "suite_end":
                    self._handle_suite_completion()
                    return
                elif msg_type == "critical_error":
                    details = msg['details']
                    self.logger.critical(f"Erro crítico na suíte: {details}")
                    messagebox.showerror("Erro na Suíte", f"Erro Crítico:\n{details}", parent=self)
                    self._handle_suite_completion()
        except queue.Empty:
            self.after(100, self.process_queue)

    def _handle_test_result(self, result: TestResult):
        self.results.append(result)
        if result.status in [TestStatus.FAIL, TestStatus.ERROR]:
            self.logger.error(f"FALHA/ERRO no teste '{result.method_name}':\n{result.details}")
        else:
            self.logger.info(f"Resultado para '{result.method_name}': {result.status.name}.")
        values = (result.status.value, result.suite_name, result.method_name, f"{result.duration:.4f}",
                  result.severity.value)
        item_id = self.tree.insert("", "end", values=values, tags=(result.status.name,))
        self.test_details_map[item_id] = result
        self._update_metrics()
        self.progress_label.config(text=f"Concluído: {result.method_name}")

    def _update_metrics(self):
        total = len(self.results)
        if total == 0: return
        success_types = [TestStatus.SUCCESS, TestStatus.DIVINE_PASS, TestStatus.GODLIKE]
        passed_count = sum(1 for r in self.results if r.status in success_types)
        counts = {status: sum(1 for r in self.results if r.status == status) for status in TestStatus}
        rate = (passed_count / total * 100) if total > 0 else 0
        total_time = sum(r.duration for r in self.results)
        self.total_metric.config(text=str(total));
        self.rate_metric.config(text=f"{rate:.1f}%");
        self.time_metric.config(text=f"{total_time:.2f}s")
        self.success_metric.config(text=str(counts.get(TestStatus.SUCCESS, 0)));
        self.fail_metric.config(text=str(counts.get(TestStatus.FAIL, 0)));
        self.error_metric.config(text=str(counts.get(TestStatus.ERROR, 0)));
        self.divine_metric.config(text=str(counts.get(TestStatus.DIVINE_PASS, 0)));
        self.godlike_metric.config(text=str(counts.get(TestStatus.GODLIKE, 0)))
        if self.suite_execution_queue or self.total_suites_in_run_all > 0:
            self.progress_bar['value'] = len(self.tree.get_children())
        elif self.total_tests_in_suite > 0:
            self.progress_bar['value'] = len(self.results)

    def _handle_suite_completion(self):
        suite_name = self.results[-1].suite_name if self.results else 'desconhecida'
        self.logger.info(f"Suíte '{suite_name}' concluída.")
        if self.suite_execution_queue: self.after(500, self._run_next_suite_in_queue); return
        passed_count = sum(
            1 for r in self.results if r.status in [TestStatus.SUCCESS, TestStatus.DIVINE_PASS, TestStatus.GODLIKE])
        num_failures = len(self.results) - passed_count
        if num_failures > 0:
            self.progress_label.config(text=f"Execução finalizada com {num_failures} falha(s).", style="Danger.TLabel")
        else:
            self.progress_label.config(text="Todas as suítes concluídas com sucesso! ✨", style="Success.TLabel")
        if self.total_tests_in_suite > 0: self.progress_bar['value'] = self.progress_bar['maximum']
        for name, button in self.run_buttons.items(): button.config(text=name, state="normal", style="Outline.TButton")
        self.total_suites_in_run_all = 0;
        self.current_suite_index = 0
        if self.results: self.export_suite_btn.config(state="normal")

    def _reset_ui(self, is_run_all: bool = False):
        if not is_run_all:
            self.results.clear();
            self.test_details_map.clear()
            for metric in [self.total_metric, self.success_metric, self.fail_metric, self.error_metric,
                           self.divine_metric, self.godlike_metric]: metric.config(text="0")
            self.rate_metric.config(text="0%");
            self.time_metric.config(text="0.0s")
        for button in self.run_buttons.values(): button.config(state="disabled")
        self.tree.delete(*self.tree.get_children())
        self.details_text.config(state="normal");
        self.details_text.delete('1.0', "end");
        self.details_text.config(state="disabled")
        if not is_run_all:
            self.total_tests_in_suite = 0;
            self.progress_bar['value'] = 0
            self.progress_label.config(text="Aguardando execução...", style="Info.TLabel")
        self.export_suite_btn.config(state="disabled");
        self.export_detail_btn.config(state="disabled");
        self.copy_detail_btn.config(state="disabled")

    def _on_result_select(self, event=None):
        if not (selected_items := self.tree.selection()): return
        result = self.test_details_map.get(selected_items[0])
        if result:
            self.details_text.config(state="normal");
            self.details_text.delete('1.0', "end")
            ts_formatted = result.timestamp.strftime('%d/%m/%Y %H:%M:%S')
            self.details_text.insert('end', "--- DETALHES DO TESTE ---\n", "header")
            self.details_text.insert('end',
                                     f"Suíte:       {result.suite_name}\n"  f"Classe:      {result.class_name}\n"  f"Método:      {result.method_name}\n"  f"Status:      {result.status.value}\n"  f"Severidade:  {result.severity.value}\n"  f"Duração:     {result.duration:.6f}s\n"  f"Timestamp:   {ts_formatted}\n\n")
            self.details_text.insert('end', "--- METADADOS E PERFORMANCE ---\n", "header")
            self.details_text.insert('end',
                                     f"Retentativas:{result.retry_count}\n"  f"Metadados:   {result.metadata}\n\n")
            self.details_text.insert('end', "--- LOG E STACKTRACE ---\n", "header")
            self.details_text.insert('end', f"{result.details}\n")
            self.details_text.config(state="disabled")
            self.export_detail_btn.config(state="normal");
            self.copy_detail_btn.config(state="normal")

    def export_suite_results(self):
        if not self.results: messagebox.showwarning("Nenhum resultado para exportar.", parent=self); return
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            suite_name = self.results[0].suite_name.replace(" ", "_").lower()
            filepath = filedialog.asksaveasfilename(initialdir=os.getcwd(),
                                                    initialfile=f"resultados_{suite_name}_{timestamp}.csv",
                                                    defaultextension=".csv",
                                                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
            if not filepath: return
            df = pd.DataFrame([asdict(res) for res in self.results])
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            self.logger.info(f"Resultados da suíte exportados para: {filepath}")
            messagebox.showinfo("Exportação Concluída", f"Resultados exportados com sucesso para:\n{filepath}",
                                parent=self)
        except Exception as e:
            self.logger.error(f"Falha ao exportar resultados: {e}")
            messagebox.showerror("Erro de Exportação", f"Ocorreu um erro ao exportar:\n{e}", parent=self)

    def export_test_detail(self):
        content = self.details_text.get("1.0", "end-1c")
        if not content.strip(): messagebox.showwarning("Sem Detalhes", "Nenhum detalhe para exportar.",
                                                       parent=self); return
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            method_name = "detalhe_desconhecido"
            if selected_items := self.tree.selection():
                if result := self.test_details_map.get(selected_items[0]): method_name = re.sub(r'[\s()/]', '_',
                                                                                                result.method_name)
            filepath = filedialog.asksaveasfilename(initialdir=os.getcwd(),
                                                    initialfile=f"{method_name}_{timestamp}.txt",
                                                    defaultextension=".txt",
                                                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if not filepath: return
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.info(f"Detalhe do teste exportado para: {filepath}")
            messagebox.showinfo("Exportação Concluída", f"Detalhe salvo com sucesso em:\n{filepath}", parent=self)
        except Exception as e:
            self.logger.error(f"Falha ao exportar detalhe do teste: {e}")
            messagebox.showerror("Erro de Exportação", f"Ocorreu um erro ao salvar o arquivo:\n{e}", parent=self)

    def copy_test_detail(self):
        content = self.details_text.get("1.0", "end-1c").strip()
        if content:
            self.clipboard_clear();
            self.clipboard_append(content)
            self.logger.info("Conteúdo copiado com sucesso.")
            original_text = self.copy_detail_btn.cget("text")
            self.copy_detail_btn.config(text="Copiado!")
            self.after(2000, lambda: self.copy_detail_btn.config(text=original_text))
        else:
            self.logger.warning("Tentativa de copiar conteúdo vazio.")

    def on_close(self):
        self.logger.info("Dashboard encerrado pelo usuário.");
        self.destroy()


if __name__ == "__main__":
    app = UltimateTestDashboard()
    app.mainloop()

