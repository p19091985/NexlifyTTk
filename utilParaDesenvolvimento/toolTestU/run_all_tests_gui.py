# run_all_tests_gui.py (Versão Corrigida)
import unittest
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import glob
import importlib
import os
import sys

# --- CORREÇÃO PRINCIPAL 1: Adiciona o diretório RAIZ do projeto ao PATH ---
# Isso garante que todos os testes consigam encontrar a pasta 'persistencia'.
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Agora, o diretório de testes também é adicionado
test_dir = os.path.dirname(__file__)
sys.path.insert(0, test_dir)


class TestRunnerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Executor de Testes Unitários")
        self.geometry("850x600")
        self._setup_style()
        self._create_widgets()
        self._import_mock_dependencies()

    def _setup_style(self):
        try:
            import ttkbootstrap as ttkb
            self.style = ttkb.Style(theme="cosmo")
        except ImportError:
            self.style = ttk.Style()
        finally:
            self.style.configure('Success.TLabel', foreground='white', background='#28a745')
            self.style.configure('Failure.TLabel', foreground='white', background='#dc3545')

    def _create_widgets(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill='x', padx=10, pady=10)
        self.title_label = ttk.Label(header_frame, text="Status Geral dos Testes", font=("Segoe UI", 14, "bold"))
        self.title_label.pack(side='left')
        ttk.Button(header_frame, text="Copiar Log", command=self._copy_log_to_clipboard).pack(side='right',
                                                                                              padx=(10, 0))
        ttk.Button(header_frame, text="Executar Todos os Testes", command=self.run_tests, style="primary.TButton").pack(
            side='right')

        self.result_text = scrolledtext.ScrolledText(self, wrap=tk.WORD, font=("Consolas", 10))
        self.result_text.pack(fill="both", expand=True, padx=10, pady=10)

        self.status_label = ttk.Label(self, text="Aguardando execução...", font=("Segoe UI", 11), anchor='center',
                                      padding=5)
        self.status_label.pack(fill='x', padx=10, pady=(0, 10))

    def _import_mock_dependencies(self):
        try:
            import mock_dependencies
            # Com o sys.path corrigido, a importação de persistencia.auth em mock_dependencies agora funciona
            mock_dependencies.setup_global_mocks()
        except Exception as e:
            self._log_result(f"ERRO CRÍTICO: Falha ao carregar 'mock_dependencies.py'.\nErro: {e}\n", "red")

    def _copy_log_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.result_text.get("1.0", tk.END))
        messagebox.showinfo("Sucesso", "Log copiado para o clipboard.", parent=self)

    # --- CORREÇÃO ADICIONAL: Adiciona o método _log_result que estava faltando ---
    def _log_result(self, message, tag):
        """Adiciona uma mensagem ao widget de texto com uma tag de cor."""
        self.result_text.insert(tk.END, message, (tag,))

    def run_tests(self):
        self.result_text.delete(1.0, tk.END)
        self.status_label.config(text="Executando testes...", style='TLabel')
        self.update_idletasks()

        suite = unittest.TestSuite()
        loader = unittest.TestLoader()

        # Procura por testes no diretório atual
        test_files = sorted(glob.glob("test_*.py"))
        for file in test_files:
            module_name = file[:-3]
            try:
                module = importlib.import_module(module_name)
                importlib.reload(module)
                suite.addTests(loader.loadTestsFromModule(module))
            except Exception as e:
                log_msg = f"--- ERRO FATAL AO CARREGAR O ARQUIVO: {module_name.upper()} ---\n{type(e).__name__}: {e}\n\n"
                self._log_result(log_msg, "red")

        proxy_stream = StreamProxy(self.result_text)
        runner = unittest.TextTestRunner(stream=proxy_stream, verbosity=2)
        result = runner.run(suite)
        self._update_final_status(result)

    def _update_final_status(self, result):
        failures = len(result.failures)
        errors = len(result.errors)
        total = result.testsRun
        final_text = f"Execução Finalizada. Total: {total}, Falhas: {failures}, Erros: {errors}."

        if result.wasSuccessful():
            self.status_label.config(text=final_text, style='Success.TLabel')
            self.title_label.config(text="SUCESSO GERAL! ✅")
        else:
            self.status_label.config(text=final_text, style='Failure.TLabel')
            self.title_label.config(text="FALHA GERAL! ❌")


class StreamProxy:
    def __init__(self, text_widget): self.text_widget = text_widget

    def write(self, text): self.text_widget.insert(tk.END, text)

    def flush(self): pass


if __name__ == "__main__":
    app = TestRunnerGUI()
    app.mainloop()