# dashboard_supremo.py (Versão Final "Divina" - Bug Corrigido)
import queue
import sys
import threading
import logging
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, PhotoImage
from typing import Type, Dict, List
from dataclasses import asdict

import pandas as pd
import ttkbootstrap as bstrap
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip

from common.base_suite import BaseTestSuite
from common.models import TestResult, TestStatus

from suites.suite_classic import ClassicTestSuite
from suites.suite_modern import ModernTestSuite
from suites.suite_parallel import ParallelDivineSuite
from suites.suite_supreme import SupremeTestSuite
from suites.suite_ultimate import UltimateTestSuite
from suites.suite_concurrency import ConcurrencyTestSuite
from suites.suite_database_stress import DatabaseStressTestSuite


class UltimateTestDashboard(bstrap.Window):
    """
    Uma interface gráfica unificada para executar e visualizar
    diferentes suítes de testes de backend, construída com foco em UX e robustez.
    """

    def __init__(self):
        super().__init__(themename="superhero", title="🚀 Dashboard de Testes Supremo 🚀")
        self.attributes('-zoomed', True)
        self.minsize(1200, 700)

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
            "Clássica": ClassicTestSuite,
            "Moderna": ModernTestSuite,
            "Divina (Paralela)": ParallelDivineSuite,
            "Suprema": SupremeTestSuite,
            "Ultimate": UltimateTestSuite,
            "Acesso Concorrente": ConcurrencyTestSuite,
            "Estresse de BD": DatabaseStressTestSuite,
        }

        self._create_main_layout()
        self._setup_detail_text_styles()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.logger.info("Dashboard de Testes Supremo iniciado com sucesso.")

    def _setup_logging(self):
        log_filename = f"run_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
        self.logger = logging.getLogger('TestDashboard')
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.FileHandler(log_filename, encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _create_main_layout(self):
        main_pane = ttk.PanedWindow(self, orient=HORIZONTAL)
        main_pane.pack(fill=BOTH, expand=True, padx=10, pady=10)
        sidebar_frame = ttk.Frame(main_pane, padding=10)
        main_pane.add(sidebar_frame, weight=1)
        self._create_sidebar(sidebar_frame)
        content_frame = ttk.Frame(main_pane, padding=10)
        main_pane.add(content_frame, weight=5)
        self._create_content_area(content_frame)

    def _create_sidebar(self, parent):
        self._create_logo(parent)
        sidebar_label = ttk.Label(parent, text="Suítes de Teste", font=("-size 16 -weight bold"))
        sidebar_label.pack(pady=(10, 20), anchor="w")

        run_all_btn = ttk.Button(parent, text="⚡ Executar Todas as Suítes", bootstyle="success",
                                 command=self.run_all_suites)
        run_all_btn.pack(fill=X, ipady=8, pady=5)
        ToolTip(run_all_btn, text="Executa todas as suítes de teste em sequência.")
        ttk.Separator(parent, orient=HORIZONTAL).pack(fill=X, pady=10)

        self.run_buttons: Dict[str, ttk.Button] = {}
        for name, suite_class in self.available_suites.items():
            button = ttk.Button(parent, text=name, bootstyle="primary-outline",
                                command=lambda sc=suite_class, btn_name=name: self.run_suite(sc, btn_name))
            button.pack(fill=X, ipady=5, pady=2)
            self.run_buttons[name] = button
            ToolTip(button, text=suite_class.description)

        ttk.Separator(parent, orient=HORIZONTAL).pack(fill=X, pady=10)
        self._create_legend(parent)

    def _create_logo(self, parent):
        try:
            self.logo_image = PhotoImage(file="logo.png")
            logo_label = ttk.Label(parent, image=self.logo_image)
            logo_label.pack(pady=(0, 10))
        except tk.TclError:
            placeholder = ttk.Label(parent, text="[LOGO]", font=("-size 12"), bootstyle="secondary")
            placeholder.pack(pady=(10, 10))
            self.logger.warning("Arquivo 'logo.png' não encontrado. Exibindo placeholder.")

    def _create_legend(self, parent):
        legend_frame = ttk.LabelFrame(parent, text=" Legenda ", padding=10)
        legend_frame.pack(fill=X, side=BOTTOM, pady=(15, 0))
        tooltips = {
            TestStatus.SUCCESS: "O teste foi executado e todas as asserções passaram.",
            TestStatus.FAIL: "O teste foi executado, mas uma asserção (`assert`) falhou.",
            TestStatus.ERROR: "O teste não pôde ser concluído devido a um erro inesperado no código.",
            TestStatus.DIVINE_PASS: "Sucesso com alta performance (execução muito rápida).",
            TestStatus.GODLIKE: "Sucesso com performance excepcional (execução extremamente rápida)."
        }
        legend_colors = {
            TestStatus.SUCCESS: self.style.colors.success,
            TestStatus.FAIL: self.style.colors.danger,
            TestStatus.ERROR: self.style.colors.warning,
            TestStatus.DIVINE_PASS: self.style.colors.info,
            TestStatus.GODLIKE: self.style.colors.primary,
        }
        for status, color in legend_colors.items():
            frame = ttk.Frame(legend_frame)
            frame.pack(fill=X, anchor="w", pady=1)
            icon = ttk.Label(frame, text="●", foreground=color, font=("-weight bold"))
            icon.pack(side=LEFT, padx=(0, 5))
            text = ttk.Label(frame, text=status.name.replace("_", " ").title())
            text.pack(side=LEFT)
            ToolTip(frame, text=tooltips.get(status, ""))

    def _create_content_area(self, parent):
        metrics_container = ttk.Frame(parent)
        metrics_container.pack(fill=X, pady=(0, 10))
        geral_frame = ttk.LabelFrame(metrics_container, text=" Visão Geral ", padding=10)
        geral_frame.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        self._create_geral_metrics_widgets(geral_frame)
        status_frame = ttk.LabelFrame(metrics_container, text=" Detalhamento de Status ", padding=10)
        status_frame.pack(side=LEFT, fill=X, expand=True)
        self._create_status_metrics_widgets(status_frame)
        progress_frame = ttk.Frame(parent)
        progress_frame.pack(fill=X, pady=(5, 15))
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=X, expand=True)
        ToolTip(self.progress_bar, text="Barra de progresso da suíte de testes atual.")
        self.progress_label = ttk.Label(progress_frame, text="Selecione uma suíte de teste para começar.",
                                        bootstyle="info")
        self.progress_label.pack(anchor="w", pady=(5, 0))
        results_pane = ttk.PanedWindow(parent, orient=VERTICAL)
        results_pane.pack(fill=BOTH, expand=True)
        results_frame = ttk.Frame(results_pane)
        results_pane.add(results_frame, weight=3)
        self._create_results_tree(results_frame)
        details_frame = ttk.LabelFrame(results_pane, text=" Detalhes do Teste Selecionado ", padding=10)
        results_pane.add(details_frame, weight=2)
        ToolTip(details_frame, text="Exibe detalhes, logs e erros do teste selecionado na tabela.")
        self.details_text = scrolledtext.ScrolledText(details_frame, wrap="word", font=("Courier New", 10),
                                                      state="disabled")
        self.details_text.pack(fill=BOTH, expand=True, pady=(0, 5))
        self._create_export_buttons(details_frame)

    def _create_geral_metrics_widgets(self, parent):
        parent.columnconfigure((0, 1, 2), weight=1)
        self.total_metric = self._create_metric_card(parent, "Total", "0", 0,
                                                     tooltip_text="Número total de testes executados.")
        self.rate_metric = self._create_metric_card(parent, "Taxa Suc.", "0%", 1, "info",
                                                    tooltip_text="Percentual de testes que passaram.")
        self.time_metric = self._create_metric_card(parent, "Tempo", "0.0s", 2, "secondary",
                                                    tooltip_text="Tempo total de execução.")

    def _create_status_metrics_widgets(self, parent):
        parent.columnconfigure((0, 1, 2, 3, 4), weight=1)
        self.success_metric = self._create_metric_card(parent, "Success", "0", 0, "success",
                                                       tooltip_text="Testes com status 'Success'.")
        self.fail_metric = self._create_metric_card(parent, "Fail", "0", 1, "danger",
                                                    tooltip_text="Testes que falharam.")
        self.error_metric = self._create_metric_card(parent, "Error", "0", 2, "warning",
                                                     tooltip_text="Testes que geraram um erro.")
        self.divine_metric = self._create_metric_card(parent, "Divine", "0", 3, "info",
                                                      tooltip_text="Testes com performance muito alta.")
        self.godlike_metric = self._create_metric_card(parent, "Godlike", "0", 4, "primary",
                                                       tooltip_text="Testes com performance excepcional.")

    def _create_metric_card(self, parent, title, value, column, style="default", tooltip_text=""):
        frame = ttk.Frame(parent)
        frame.grid(row=0, column=column, padx=5, pady=2, sticky="ew")
        title_label = ttk.Label(frame, text=title, font=("-weight bold"))
        title_label.pack()
        value_label = ttk.Label(frame, text=value, font=("-size 14"), bootstyle=style)
        value_label.pack()
        if tooltip_text:
            ToolTip(frame, text=tooltip_text)
        return value_label

    def _create_results_tree(self, parent):
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=BOTH, expand=True)
        ToolTip(tree_frame,
                text="Tabela com os resultados de cada teste. Clique em um cabeçalho para ordenar ou em uma linha para ver detalhes.")
        self.columns = ('status', 'suite', 'method', 'duration', 'severity')
        self.tree = bstrap.Treeview(tree_frame, columns=self.columns, show='headings', bootstyle='primary')
        for col in self.columns:
            self.tree.heading(col, text=col.replace('_', ' ').title(),
                              command=lambda c=col: self._sort_treeview(c, False))
        self.tree.column('status', width=120, stretch=False)
        self.tree.column('suite', width=150, stretch=False)
        self.tree.column('method', width=400)
        self.tree.column('duration', width=100, stretch=False, anchor='e')
        self.tree.column('severity', width=100, stretch=False, anchor='center')
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self._on_result_select)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=RIGHT, fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.tag_configure(TestStatus.SUCCESS.name, background=self.style.colors.success)
        self.tree.tag_configure(TestStatus.FAIL.name, background=self.style.colors.danger)
        self.tree.tag_configure(TestStatus.ERROR.name, background=self.style.colors.warning)
        self.tree.tag_configure(TestStatus.SKIPPED.name, background=self.style.colors.secondary)
        self.tree.tag_configure(TestStatus.DIVINE_PASS.name, background=self.style.colors.info)
        self.tree.tag_configure(TestStatus.GODLIKE.name, background=self.style.colors.primary)

    def _sort_treeview(self, col, reverse):
        try:
            data = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
            try:
                data.sort(key=lambda x: float(x[0]), reverse=reverse)
            except ValueError:
                data.sort(key=lambda x: x[0], reverse=reverse)
            for index, (val, item) in enumerate(data):
                self.tree.move(item, '', index)
            self.tree.heading(col, command=lambda: self._sort_treeview(col, not reverse))
        except tk.TclError:
            self.logger.warning(f"Não foi possível ordenar a coluna {col}.")

    def _create_export_buttons(self, parent):
        export_frame = ttk.Frame(parent)
        export_frame.pack(fill=X, pady=(5, 0))
        self.copy_detail_btn = ttk.Button(export_frame, text="📋 Copiar", command=self.copy_test_detail,
                                          bootstyle="secondary-outline", state="disabled")
        self.copy_detail_btn.pack(side=RIGHT)
        ToolTip(self.copy_detail_btn, text="Copia os detalhes do teste selecionado.")
        self.export_detail_btn = ttk.Button(export_frame, text="Exportar Detalhe (.txt)",
                                            command=self.export_test_detail, bootstyle="info-outline", state="disabled")
        self.export_detail_btn.pack(side=RIGHT, padx=(0, 10))
        ToolTip(self.export_detail_btn, text="Salva os detalhes do teste selecionado em um arquivo de texto.")
        self.export_suite_btn = ttk.Button(export_frame, text="Exportar Resultados (CSV)",
                                           command=self.export_suite_results, bootstyle="success-outline",
                                           state="disabled")
        self.export_suite_btn.pack(side=RIGHT, padx=(0, 10))
        ToolTip(self.export_suite_btn, text="Salva todos os resultados da tabela em um arquivo CSV.")

    def _setup_detail_text_styles(self):
        self.details_text.tag_configure("header", font=("Courier New", 10, "bold"), foreground=self.style.colors.info)

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
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.total_tests_in_suite = 0
            self.run_suite(suite_class, name, is_part_of_run_all=True)

    def run_suite(self, suite_class: Type[BaseTestSuite], button_name: str, is_part_of_run_all: bool = False):
        if not is_part_of_run_all:
            self._reset_ui()

        self.active_suite_button = self.run_buttons.get(button_name)
        if self.active_suite_button:
            self.active_suite_button.config(text="Executando...", state="disabled", bootstyle="info")

        suite_instance = suite_class(self.test_queue)
        self.logger.info(f"Iniciando suíte: {suite_instance.suite_name}")

        if is_part_of_run_all:
            progress_text = f"Executando Suíte {self.current_suite_index}/{self.total_suites_in_run_all}: {suite_instance.suite_name}..."
        else:
            progress_text = f"Iniciando suíte: {suite_instance.suite_name}..."
        self.progress_label.config(text=progress_text)

        test_thread = threading.Thread(target=suite_instance.run, daemon=True)
        test_thread.start()
        self.after(100, self.process_queue)

    def process_queue(self):
        try:
            while True:
                msg = self.test_queue.get_nowait()
                msg_type = msg.get("type")
                if msg_type == "total_tests":
                    self.total_tests_in_suite = msg.get('count', 0)
                    if self.total_tests_in_suite > 0:
                        self.progress_bar['maximum'] = self.total_tests_in_suite
                elif msg_type == "progress_update":
                    if 'value' in msg:
                        self.progress_bar.config(mode='determinate', maximum=1.0, value=msg['value'])
                    else:
                        self.progress_bar.config(mode='indeterminate')
                        self.progress_bar.start()
                    if 'text' in msg:
                        self.progress_label.config(text=msg['text'])
                elif msg_type == "test_result":
                    if self.progress_bar['mode'] == 'indeterminate':
                        self.progress_bar.stop()
                        self.progress_bar.config(mode='determinate')
                    self._handle_test_result(msg["result"])
                elif msg_type == "suite_end":
                    self._handle_suite_completion()
                    return
                elif msg_type == "critical_error":
                    details = msg['details']
                    self.logger.critical(f"Erro crítico na suíte: {details}")
                    bstrap.dialogs.Messagebox.show_error(f"Erro Crítico:\n{details}", "Erro na Suíte", parent=self)
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
        self.total_metric.config(text=str(total))
        self.rate_metric.config(text=f"{rate:.1f}%")
        self.time_metric.config(text=f"{total_time:.2f}s")
        self.success_metric.config(text=str(counts.get(TestStatus.SUCCESS, 0)))
        self.fail_metric.config(text=str(counts.get(TestStatus.FAIL, 0)))
        self.error_metric.config(text=str(counts.get(TestStatus.ERROR, 0)))
        self.divine_metric.config(text=str(counts.get(TestStatus.DIVINE_PASS, 0)))
        self.godlike_metric.config(text=str(counts.get(TestStatus.GODLIKE, 0)))

        if self.suite_execution_queue or self.total_suites_in_run_all > 0:
            self.progress_bar['value'] = len(self.tree.get_children())
        else:
            if self.total_tests_in_suite > 0:
                self.progress_bar['value'] = len(self.results)

    def _handle_suite_completion(self):
        suite_name = self.results[-1].suite_name if self.results else 'desconhecida'
        self.logger.info(f"Suíte '{suite_name}' concluída.")

        if self.suite_execution_queue:
            self.after(500, self._run_next_suite_in_queue)
            return

        passed_count = sum(
            1 for r in self.results if r.status in [TestStatus.SUCCESS, TestStatus.DIVINE_PASS, TestStatus.GODLIKE])
        num_failures = len(self.results) - passed_count

        if num_failures > 0:
            self.progress_label.config(text=f"Execução finalizada com {num_failures} falha(s).", bootstyle="danger")
        else:
            self.progress_label.config(text="Todas as suítes concluídas com sucesso! ✨", bootstyle="success")

        if self.total_tests_in_suite > 0:
            self.progress_bar['value'] = self.progress_bar['maximum']

        for name, button in self.run_buttons.items():
            button.config(text=name, state="normal", bootstyle="primary-outline")

        self.total_suites_in_run_all = 0
        self.current_suite_index = 0

        if self.results:
            self.export_suite_btn.config(state="normal")

    def _reset_ui(self, is_run_all: bool = False):
        if not is_run_all:
            self.results.clear()
            self.test_details_map.clear()
            for metric in [self.total_metric, self.success_metric, self.fail_metric, self.error_metric,
                           self.divine_metric, self.godlike_metric]:
                metric.config(text="0")
            self.rate_metric.config(text="0%")
            self.time_metric.config(text="0.0s")

        for button in self.run_buttons.values():
            button.config(state="disabled")

        self.tree.delete(*self.tree.get_children())
        self.details_text.config(state="normal")
        self.details_text.delete('1.0', "end")
        self.details_text.config(state="disabled")

        if not is_run_all:
            self.total_tests_in_suite = 0
            self.progress_bar['value'] = 0
            self.progress_label.config(text="Aguardando execução...", bootstyle="info")

        self.export_suite_btn.config(state="disabled")
        self.export_detail_btn.config(state="disabled")
        self.copy_detail_btn.config(state="disabled")

    def _on_result_select(self, event=None):
        if not (selected_items := self.tree.selection()):
            return

        item_id = selected_items[0]
        result = self.test_details_map.get(item_id)

        if result:
            self.details_text.config(state="normal")
            self.details_text.delete('1.0', "end")

            # --- BUG FIX: Chamar strftime diretamente no objeto datetime ---
            ts_formatted = result.timestamp.strftime('%d/%m/%Y %H:%M:%S')

            self.details_text.insert('end', "--- DETALHES DO TESTE ---\n", "header")
            self.details_text.insert('end', f"Suíte:       {result.suite_name}\n")
            self.details_text.insert('end', f"Classe:      {result.class_name}\n")
            self.details_text.insert('end', f"Método:      {result.method_name}\n")
            self.details_text.insert('end', f"Status:      {result.status.value}\n")
            self.details_text.insert('end', f"Severidade:  {result.severity.value}\n")
            self.details_text.insert('end', f"Duração:     {result.duration:.6f}s\n")
            self.details_text.insert('end', f"Timestamp:   {ts_formatted}\n\n")
            self.details_text.insert('end', "--- METADADOS E PERFORMANCE ---\n", "header")
            self.details_text.insert('end', f"Retentativas:{result.retry_count}\n")
            self.details_text.insert('end', f"Metadados:   {result.metadata}\n\n")
            self.details_text.insert('end', "--- LOG E STACKTRACE ---\n", "header")
            self.details_text.insert('end', f"{result.details}\n")

            self.details_text.config(state="disabled")
            self.export_detail_btn.config(state="normal")
            self.copy_detail_btn.config(state="normal")

    def export_suite_results(self):
        if not self.results:
            bstrap.dialogs.Messagebox.show_warning("Nenhum resultado para exportar.", parent=self)
            return
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            suite_name = self.results[0].suite_name.replace(" ", "_").lower()
            filepath = filedialog.asksaveasfilename(
                initialdir=os.getcwd(), initialfile=f"resultados_{suite_name}_{timestamp}.csv",
                defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if not filepath: return
            results_data = [asdict(res) for res in self.results]
            df = pd.DataFrame(results_data)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            self.logger.info(f"Resultados da suíte exportados para: {filepath}")
            bstrap.dialogs.Messagebox.show_info(f"Resultados exportados com sucesso para:\n{filepath}", parent=self)
        except Exception as e:
            self.logger.error(f"Falha ao exportar resultados da suíte: {e}")
            bstrap.dialogs.Messagebox.show_error(f"Ocorreu um erro ao exportar:\n{e}", parent=self)

    def export_test_detail(self):
        content = self.details_text.get("1.0", "end-1c")
        if not content.strip():
            bstrap.dialogs.Messagebox.show_warning("Nenhum detalhe para exportar.", parent=self)
            return
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            method_name = "detalhe_desconhecido"
            if selected_items := self.tree.selection():
                if result := self.test_details_map.get(selected_items[0]):
                    method_name = result.method_name.replace(" ", "_").replace("(", "").replace(")", "").replace("/",
                                                                                                                 "_")
            filepath = filedialog.asksaveasfilename(
                initialdir=os.getcwd(), initialfile=f"{method_name}_{timestamp}.txt",
                defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if not filepath: return
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.info(f"Detalhe do teste exportado para: {filepath}")
            bstrap.dialogs.Messagebox.show_info(f"Detalhe salvo com sucesso em:\n{filepath}", parent=self)
        except Exception as e:
            self.logger.error(f"Falha ao exportar detalhe do teste: {e}")
            bstrap.dialogs.Messagebox.show_error(f"Ocorreu um erro ao salvar o arquivo:\n{e}", parent=self)

    def copy_test_detail(self):
        content = self.details_text.get("1.0", "end-1c").strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            self.logger.info("Conteúdo copiado com sucesso.")
            original_text = self.copy_detail_btn.cget("text")
            self.copy_detail_btn.config(text="Copiado!", bootstyle="success-outline")
            self.after(2000, lambda: self.copy_detail_btn.config(text=original_text, bootstyle="secondary-outline"))
        else:
            self.logger.warning("Tentativa de copiar conteúdo vazio.")

    def on_close(self):
        self.logger.info("Dashboard encerrado pelo usuário.")
        self.destroy()


if __name__ == "__main__":
    app = UltimateTestDashboard()
    app.mainloop()