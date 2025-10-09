# dashboard_supremo.py
import queue
import sys
import threading
import logging
import os
from datetime import datetime
import tkinter as tk  # <--  Importação adicionada
from tkinter import ttk, scrolledtext, filedialog, PhotoImage

import pandas as pd
import ttkbootstrap as bstrap
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip

# Importa os modelos e a base das suítes
from common.base_suite import BaseTestSuite
from common.models import TestResult, TestStatus

# Importa individualmente cada suíte de teste
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
        self.results: list[TestResult] = []
        self.test_details_map = {}
        self.total_tests_in_suite = 0

        self.available_suites = {
            "Clássica": ClassicTestSuite,
            "Moderna": ModernTestSuite,
            "Divina (Paralela)": ParallelDivineSuite,
            "Suprema": SupremeTestSuite,
            "Ultimate": UltimateTestSuite,
            "Acesso Concorrente": ConcurrencyTestSuite,
            "Estresse de BD": DatabaseStressTestSuite,
        }

        self._create_main_layout()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.logger.info("Dashboard de Testes Supremo iniciado com sucesso.")

    def _setup_logging(self):
        """Configura o logging para registrar eventos em um arquivo com timestamp."""
        log_filename = f"run_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
        self.logger = logging.getLogger('TestDashboard')
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.FileHandler(log_filename, encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _create_main_layout(self):
        """Cria o layout principal com painel lateral e área de conteúdo."""
        main_pane = ttk.PanedWindow(self, orient=HORIZONTAL)
        main_pane.pack(fill=BOTH, expand=True, padx=10, pady=10)

        sidebar_frame = ttk.Frame(main_pane, padding=10)
        main_pane.add(sidebar_frame, weight=1)
        self._create_sidebar(sidebar_frame)

        content_frame = ttk.Frame(main_pane, padding=10)
        main_pane.add(content_frame, weight=5)
        self._create_content_area(content_frame)

    def _create_sidebar(self, parent):
        """Cria a barra lateral com logo, botões de suíte e legenda."""
        self._create_logo(parent)

        sidebar_label = ttk.Label(parent, text="Suítes de Teste", font=("-size 16 -weight bold"))
        sidebar_label.pack(pady=(10, 20), anchor="w")

        self.run_buttons = {}
        for name, suite_class in self.available_suites.items():
            button = ttk.Button(parent, text=name, bootstyle="primary-outline",
                                command=lambda sc=suite_class: self.run_suite(sc))
            button.pack(fill=X, ipady=5, pady=2)
            self.run_buttons[name] = button
            ToolTip(button, text=suite_class.description)
            ttk.Separator(parent, orient=HORIZONTAL).pack(fill=X, pady=10)

        self._create_legend(parent)

    def _create_logo(self, parent):
        """Cria e exibe o logo no topo da barra lateral."""
        try:
            # Para o logo funcionar, crie um arquivo 'logo.png' de 64x64 pixels
            # e coloque na mesma pasta deste script.
            self.logo_image = PhotoImage(file="logo.png")
            logo_label = ttk.Label(parent, image=self.logo_image)
            logo_label.pack(pady=(0, 10))
        except tk.TclError:
            # Se o arquivo de logo não for encontrado, apenas exibe um texto.
            placeholder = ttk.Label(parent, text="[LOGO]", font=("-size 12"), bootstyle="secondary")
            placeholder.pack(pady=(10, 10))
            self.logger.warning("Arquivo 'logo.png' não encontrado. Exibindo placeholder.")

    def _create_legend(self, parent):
        """Cria a legenda colorida de status dos testes."""
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
        """Cria a área principal com métricas, progresso e resultados."""
        metrics_frame = ttk.LabelFrame(parent, text=" Métricas da Execução ", padding=10)
        metrics_frame.pack(fill=X, pady=(0, 10))
        self._create_metrics_widgets(metrics_frame)

        progress_frame = ttk.Frame(parent)
        progress_frame.pack(fill=X, pady=(5, 15))
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=X, expand=True)
        ToolTip(self.progress_bar, text="Barra de progresso mostrando o andamento da suíte de testes atual.")

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
        ToolTip(details_frame,
                text="Exibe os detalhes completos, incluindo logs e erros, do teste selecionado na tabela acima.")

        self.details_text = scrolledtext.ScrolledText(details_frame, wrap="word", font=("Courier New", 10),
                                                      state="disabled")
        self.details_text.pack(fill=BOTH, expand=True, pady=(0, 5))

        self._create_export_buttons(details_frame)

    def _create_metrics_widgets(self, parent):
        """Cria os cartões detalhados de métricas."""
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=X, expand=True, pady=(0, 5))
        bottom_frame = ttk.Frame(parent)
        bottom_frame.pack(fill=X, expand=True)

        for i in range(3): top_frame.columnconfigure(i, weight=1)
        for i in range(5): bottom_frame.columnconfigure(i, weight=1)

        self.total_metric = self._create_metric_card(top_frame, "Total", "0", 0,
                                                     tooltip_text="Número total de testes executados na suíte.")
        self.rate_metric = self._create_metric_card(top_frame, "Taxa Suc.", "0%", 1, "info",
                                                    tooltip_text="Percentual de testes que passaram (incluindo Success, Divine e Godlike).")
        self.time_metric = self._create_metric_card(top_frame, "Tempo", "0.0s", 2, "secondary",
                                                    tooltip_text="Tempo total de execução de todos os testes da suíte.")

        self.success_metric = self._create_metric_card(bottom_frame, "Success", "0", 0, "success",
                                                       tooltip_text="Número de testes com status 'Success'.")
        self.fail_metric = self._create_metric_card(bottom_frame, "Fail", "0", 1, "danger",
                                                    tooltip_text="Número de testes que falharam devido a uma asserção.")
        self.error_metric = self._create_metric_card(bottom_frame, "Error", "0", 2, "warning",
                                                     tooltip_text="Número de testes que geraram um erro inesperado.")
        self.divine_metric = self._create_metric_card(bottom_frame, "Divine", "0", 3, "info",
                                                      tooltip_text="Número de testes com performance muito alta.")
        self.godlike_metric = self._create_metric_card(bottom_frame, "Godlike", "0", 4, "primary",
                                                       tooltip_text="Número de testes com performance excepcional.")

    def _create_metric_card(self, parent, title, value, column, style="default", tooltip_text=""):
        """Helper para criar um cartão de métrica individual."""
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
        """Cria a tabela (Treeview) para exibir os resultados."""
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=BOTH, expand=True)
        ToolTip(tree_frame, text="Tabela com os resultados de cada teste. Clique em uma linha para ver os detalhes.")

        columns = ('status', 'suite', 'method', 'duration', 'severity')
        self.tree = bstrap.Treeview(tree_frame, columns=columns, show='headings', bootstyle='primary')

        self.tree.heading('status', text='Status');
        self.tree.column('status', width=120, stretch=False)
        self.tree.heading('suite', text='Suíte');
        self.tree.column('suite', width=150, stretch=False)
        self.tree.heading('method', text='Método de Teste');
        self.tree.column('method', width=400)
        self.tree.heading('duration', text='Duração (s)', anchor='e');
        self.tree.column('duration', width=100, stretch=False, anchor='e')
        self.tree.heading('severity', text='Severidade');
        self.tree.column('severity', width=100, stretch=False, anchor='center')

        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self._on_result_select)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=RIGHT, fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Configuração das cores de fundo para as linhas (tags)
        self.tree.tag_configure(TestStatus.SUCCESS.name, background=self.style.colors.success)
        self.tree.tag_configure(TestStatus.FAIL.name, background=self.style.colors.danger)
        self.tree.tag_configure(TestStatus.ERROR.name, background=self.style.colors.warning)
        self.tree.tag_configure(TestStatus.SKIPPED.name, background=self.style.colors.secondary)
        self.tree.tag_configure(TestStatus.DIVINE_PASS.name, background=self.style.colors.info)
        self.tree.tag_configure(TestStatus.GODLIKE.name, background=self.style.colors.primary)

    def _create_export_buttons(self, parent):
        """Cria os botões de copiar e exportar abaixo dos detalhes."""
        export_frame = ttk.Frame(parent)
        export_frame.pack(fill=X, pady=(5, 0))

        self.copy_detail_btn = ttk.Button(export_frame, text="📋 Copiar", command=self.copy_test_detail,
                                          bootstyle="secondary-outline", state="disabled")
        self.copy_detail_btn.pack(side=RIGHT)
        ToolTip(self.copy_detail_btn, text="Copia os detalhes do teste selecionado para a área de transferência.")

        self.export_detail_btn = ttk.Button(export_frame, text="Exportar Detalhe (.txt)",
                                            command=self.export_test_detail, bootstyle="info-outline", state="disabled")
        self.export_detail_btn.pack(side=RIGHT, padx=(0, 10))
        ToolTip(self.export_detail_btn,
                text="Salva os detalhes do teste atualmente selecionado em um arquivo de texto (.txt).")

        self.export_suite_btn = ttk.Button(export_frame, text="Exportar Resultados (CSV)",
                                           command=self.export_suite_results, bootstyle="success-outline",
                                           state="disabled")
        self.export_suite_btn.pack(side=RIGHT, padx=(0, 10))
        ToolTip(self.export_suite_btn, text="Salva todos os resultados da tabela em um arquivo no formato CSV.")

    def run_suite(self, suite_class: type[BaseTestSuite]):
        """Inicia a execução de uma suíte de testes em uma thread separada."""
        self._reset_ui()
        suite_instance = suite_class(self.test_queue)
        self.logger.info(f"Iniciando suíte: {suite_instance.suite_name}")
        self.progress_label.config(text=f"Iniciando suíte: {suite_instance.suite_name}...")
        test_thread = threading.Thread(target=suite_instance.run, daemon=True)
        test_thread.start()
        self.after(100, self.process_queue)

    def process_queue(self):
        """Processa mensagens da fila de testes para atualizar a UI."""
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
                        self.progress_bar.config(mode='determinate')
                        self.progress_bar['maximum'] = 1.0
                        self.progress_bar['value'] = msg['value']
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
        """Adiciona um resultado de teste à tabela e atualiza as métricas."""
        self.results.append(result)

        log_message = f"Resultado para '{result.method_name}': {result.status.name}."
        if result.status in [TestStatus.FAIL, TestStatus.ERROR]:
            self.logger.error(f"FALHA/ERRO no teste '{result.method_name}':\n{result.details}")
        else:
            self.logger.info(log_message)

        values = (
            result.status.value,
            result.suite_name,
            result.method_name,
            f"{result.duration:.4f}",
            result.severity.value
        )
        # O ID do item é a tupla de valores para garantir unicidade simples
        item_id = self.tree.insert("", "end", values=values, tags=(result.status.name,))
        self.test_details_map[item_id] = result

        self._update_metrics()
        self.progress_label.config(text=f"Concluído: {result.method_name}")

    def _update_metrics(self):
        """Calcula e atualiza todos os cartões de métricas."""
        total = len(self.results)
        if total == 0: return

        success_types = [TestStatus.SUCCESS, TestStatus.DIVINE_PASS, TestStatus.GODLIKE]
        passed_count = sum(1 for r in self.results if r.status in success_types)
        counts = {status: sum(1 for r in self.results if r.status == status) for status in TestStatus}

        rate = (passed_count / total * 100)
        total_time = sum(r.duration for r in self.results)

        self.total_metric.config(text=str(total))
        self.rate_metric.config(text=f"{rate:.1f}%")
        self.time_metric.config(text=f"{total_time:.2f}s")

        self.success_metric.config(text=str(counts.get(TestStatus.SUCCESS, 0)))
        self.fail_metric.config(text=str(counts.get(TestStatus.FAIL, 0)))
        self.error_metric.config(text=str(counts.get(TestStatus.ERROR, 0)))
        self.divine_metric.config(text=str(counts.get(TestStatus.DIVINE_PASS, 0)))
        self.godlike_metric.config(text=str(counts.get(TestStatus.GODLIKE, 0)))

        if self.total_tests_in_suite > 0:
            self.progress_bar['value'] = total

    def _handle_suite_completion(self):
        """Finaliza a UI após a conclusão de uma suíte."""
        suite_name = self.results[-1].suite_name if self.results else 'desconhecida'
        self.logger.info(f"Suíte '{suite_name}' concluída.")

        passed_count = sum(
            1 for r in self.results if r.status in [TestStatus.SUCCESS, TestStatus.DIVINE_PASS, TestStatus.GODLIKE])
        num_failures = len(self.results) - passed_count

        if num_failures > 0:
            self.progress_label.config(text=f"Execução concluída com {num_failures} falha(s).", bootstyle="danger")
        else:
            self.progress_label.config(text="Execução concluída com sucesso! ✨", bootstyle="success")

        if self.total_tests_in_suite > 0:
            self.progress_bar['value'] = self.progress_bar['maximum']

        for button in self.run_buttons.values():
            button.config(state="normal")

        if self.results:
            self.export_suite_btn.config(state="normal")

    def _reset_ui(self):
        """Reseta toda a interface para uma nova execução."""
        for button in self.run_buttons.values():
            button.config(state="disabled")
        self.tree.delete(*self.tree.get_children())

        self.details_text.config(state="normal")
        self.details_text.delete('1.0', "end")
        self.details_text.config(state="disabled")

        self.results.clear()
        self.test_details_map.clear()
        self.total_tests_in_suite = 0

        self.total_metric.config(text="0");
        self.rate_metric.config(text="0%");
        self.time_metric.config(text="0.0s")
        self.success_metric.config(text="0");
        self.fail_metric.config(text="0");
        self.error_metric.config(text="0")
        self.divine_metric.config(text="0");
        self.godlike_metric.config(text="0")

        self.progress_bar['value'] = 0
        self.progress_label.config(text="Aguardando execução...", bootstyle="info")

        self.export_suite_btn.config(state="disabled")
        self.export_detail_btn.config(state="disabled")
        self.copy_detail_btn.config(state="disabled")

    def _on_result_select(self, event=None):
        """Exibe os detalhes de um teste quando selecionado na tabela."""
        if not (selected_items := self.tree.selection()): return
        item_id = selected_items[0]
        result = self.test_details_map.get(item_id)
        if result:
            self.details_text.config(state="normal")
            self.details_text.delete('1.0', "end")

            ts_formatted = datetime.fromtimestamp(result.timestamp).strftime('%d/%m/%Y %H:%M:%S')

            details_content = f""" DETALHES DO TESTE 
Suíte:       {result.suite_name}
Classe:      {result.class_name}
Método:      {result.method_name}
Status:      {result.status.value}
Severidade:  {result.severity.value}
Duração:     {result.duration:.6f}s
Timestamp:   {ts_formatted}

 METADADOS E PERFORMANCE 
Retentativas:{result.retry_count}
Metadados:   {result.metadata}

 LOG E STACKTRACE 
{result.details}"""
            self.details_text.insert('1.0', details_content)
            self.details_text.config(state="disabled")

            self.export_detail_btn.config(state="normal")
            self.copy_detail_btn.config(state="normal")

    def export_suite_results(self):
        """Exporta todos os resultados da suíte atual para um arquivo CSV."""
        if not self.results:
            bstrap.dialogs.Messagebox.show_warning("Nenhum resultado para exportar.", "Exportar Resultados",
                                                   parent=self)
            return

        try:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            suite_name = self.results[0].suite_name.replace(" ", "_").lower()

            filepath = filedialog.asksaveasfilename(
                initialdir=os.getcwd(),
                initialfile=f"resultados_{suite_name}_{timestamp}.csv",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if not filepath: return

            results_data = [res.to_dict() for res in self.results]
            df = pd.DataFrame(results_data)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')

            self.logger.info(f"Resultados da suíte exportados para: {filepath}")
            bstrap.dialogs.Messagebox.show_info(f"Resultados exportados com sucesso para:\n{filepath}",
                                                "Exportação Concluída", parent=self)
        except Exception as e:
            self.logger.error(f"Falha ao exportar resultados da suíte: {e}")
            bstrap.dialogs.Messagebox.show_error(f"Ocorreu um erro ao exportar:\n{e}", "Erro de Exportação",
                                                 parent=self)

    def export_test_detail(self):
        """Exporta o detalhe do teste selecionado para um arquivo .txt."""
        content = self.details_text.get("1.0", "end-1c")
        if not content.strip():
            bstrap.dialogs.Messagebox.show_warning("Nenhum detalhe para exportar.", "Exportar Detalhe", parent=self)
            return

        try:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            method_name = "detalhe_desconhecido"
            if selected_items := self.tree.selection():
                result = self.test_details_map.get(selected_items[0])
                if result: method_name = result.method_name.replace(" ", "_").replace("(", "").replace(")", "").replace(
                    "/", "_")

            filepath = filedialog.asksaveasfilename(
                initialdir=os.getcwd(),
                initialfile=f"{method_name}_{timestamp}.txt",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if not filepath: return

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            self.logger.info(f"Detalhe do teste exportado para: {filepath}")
            bstrap.dialogs.Messagebox.show_info(f"Detalhe salvo com sucesso em:\n{filepath}", "Exportação Concluída",
                                                parent=self)
        except Exception as e:
            self.logger.error(f"Falha ao exportar detalhe do teste: {e}")
            bstrap.dialogs.Messagebox.show_error(f"Ocorreu um erro ao salvar o arquivo:\n{e}", "Erro de Exportação",
                                                 parent=self)

    def copy_test_detail(self):
        """Copia o conteúdo detalhado do teste para a área de transferência."""
        content = self.details_text.get("1.0", "end-1c")
        self.logger.info(f"Tentando copiar {len(content)} caracteres para a área de transferência.")
        if content.strip():
            self.clipboard_clear()
            self.clipboard_append(content)
            self.update_idletasks()
            self.logger.info("Conteúdo copiado com sucesso.")
        else:
            self.logger.warning("Tentativa de copiar conteúdo vazio.")
            bstrap.dialogs.Messagebox.show_warning("Não há nada para copiar.", "Área de Transferência", parent=self)

    def on_close(self):
        """Encerra a aplicação."""
        self.logger.info("Dashboard encerrado pelo usuário.")
        self.destroy()


if __name__ == "__main__":
    app = UltimateTestDashboard()
    app.mainloop()