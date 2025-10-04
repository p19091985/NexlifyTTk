# utilParaDesenvolvimento/testador_supremo.py
import os
import sys
import pandas as pd
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from unittest.mock import patch, MagicMock

# --- Configuração de Caminho ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
# -----------------------------

# --- Importações dos Módulos da Aplicação ---
from persistencia.database import DatabaseManager
from persistencia.repository import GenericRepository
from persistencia.data_service import DataService
from persistencia import auth
import config
from panels.base_panel import BasePanel
from panels.painel_01_controller import PainelVisualizacaoDados


# █████████████████████████████████████████████████████████████████████████████████
# --- TESTES DE BACKEND (PERSISTÊNCIA) ---
# █████████████████████████████████████████████████████████████████████████████████

class TestBackend:
    def __init__(self, q: queue.Queue):
        self.q = q

    def run(self):
        self.q.put(("INICIANDO SUÍTE DE TESTES DE BACKEND", "HEADER"))
        self.test_setup_banco()
        self.test_database_connection()
        self.test_autenticacao()
        self.test_repository_crud()
        self.test_data_service_transacao()
        self.q.put(("SUÍTE DE TESTES DE BACKEND FINALIZADA\n", "HEADER"))

    def test_setup_banco(self):
        self.q.put(("--- Teste: Recriação do Banco de Dados ---", "INFO"))
        db_path = os.path.join(project_root, "sistema.db")
        if os.path.exists(db_path): os.remove(db_path)
        config.INITIALIZE_DATABASE_ON_STARTUP = True
        DatabaseManager._engine = None
        DatabaseManager.initialize_database()
        config.INITIALIZE_DATABASE_ON_STARTUP = False
        self.q.put(("✅ Banco de dados recriado com sucesso.", "SUCCESS"))

    def test_database_connection(self):
        self.q.put(("--- Teste: Conexão (DatabaseManager) ---", "INFO"))
        engine = DatabaseManager.get_engine()
        assert engine is not None, "A engine do banco de dados não foi obtida."
        self.q.put(("✅ Engine obtida com sucesso.", "SUCCESS"))

    def test_autenticacao(self):
        self.q.put(("--- Teste: Autenticação (auth.py) ---", "INFO"))
        user_data = auth.verify_user_credentials('admin', 'senha123')
        assert user_data and user_data['username'] == 'admin', "Login correto falhou."
        self.q.put(("✅ Login bem-sucedido verificado.", "SUCCESS"))

        user_data_fail = auth.verify_user_credentials('admin', 'senha_errada')
        assert user_data_fail is None, "Senha incorreta foi aceite."
        self.q.put(("✅ Falha com senha incorreta verificada.", "SUCCESS"))

    def test_repository_crud(self):
        self.q.put(("--- Teste: CRUD (GenericRepository) ---", "INFO"))
        table = "especie_gatos"
        nova_especie = {'nome_especie': 'Abissínio', 'pais_origem': 'Etiópia', 'temperamento': 'Inteligente'}
        GenericRepository.write_dataframe_to_table(pd.DataFrame([nova_especie]), table)
        df = GenericRepository.read_table_to_dataframe(table, where_conditions={'nome_especie': 'Abissínio'})
        assert not df.empty, "CREATE falhou, registo não encontrado."
        self.q.put(("✅ CREATE bem-sucedido.", "SUCCESS"))

        update_values = {'temperamento': 'Muito Inteligente e Ativo'}
        GenericRepository.update_table(table, update_values, {'nome_especie': 'Abissínio'})
        df_updated = GenericRepository.read_table_to_dataframe(table, where_conditions={'nome_especie': 'Abissínio'})
        assert df_updated.iloc[0]['temperamento'] == 'Muito Inteligente e Ativo', "UPDATE falhou."
        self.q.put(("✅ UPDATE bem-sucedido.", "SUCCESS"))

        GenericRepository.delete_from_table(table, where_conditions={'nome_especie': 'Abissínio'})
        df_deleted = GenericRepository.read_table_to_dataframe(table, where_conditions={'nome_especie': 'Abissínio'})
        assert df_deleted.empty, "DELETE falhou, registo ainda existe."
        self.q.put(("✅ DELETE bem-sucedido.", "SUCCESS"))

    def test_data_service_transacao(self):
        self.q.put(("--- Teste: Transação (DataService) ---", "INFO"))
        sucesso, _ = DataService.rename_especie_gato_e_logar('Persa', 'Gato Persa', 'test_runner')
        assert sucesso, "Transação de renomear falhou."
        df_gato = GenericRepository.read_table_to_dataframe('especie_gatos',
                                                            where_conditions={'nome_especie': 'Gato Persa'})
        df_log = GenericRepository.read_table_to_dataframe('log_alteracoes', where_conditions={
            'acao': "Renomeou a espécie de gato de 'Persa' para 'Gato Persa'"})
        assert not df_gato.empty and not df_log.empty, "A transação não atualizou ou não logou corretamente."
        self.q.put(("✅ Transação com sucesso (commit) verificada.", "SUCCESS"))

        sucesso_fail, _ = DataService.rename_especie_gato_e_logar('Gato Inexistente', 'Fantasma', 'test_runner')
        assert not sucesso_fail, "Transação que deveria falhar teve sucesso."
        df_gato_fantasma = GenericRepository.read_table_to_dataframe('especie_gatos',
                                                                     where_conditions={'nome_especie': 'Fantasma'})
        assert df_gato_fantasma.empty, "O rollback da transação falhou, dados foram inseridos."
        self.q.put(("✅ Transação com falha (rollback) verificada.", "SUCCESS"))


# █████████████████████████████████████████████████████████████████████████████████
# --- TESTES DE FRONTEND (PAINÉIS) ---
# █████████████████████████████████████████████████████████████████████████████████

class TestFrontend:
    def __init__(self, q: queue.Queue, tk_root):
        self.q = q
        self.tk_root = tk_root
        self.panel = None

    def run(self):
        self.q.put(("INICIANDO SUÍTE DE TESTES DE FRONTEND (com Mocks)", "HEADER"))
        self.test_painel01_carregamento_e_submissao()
        self.q.put(("SUÍTE DE TESTES DE FRONTEND FINALIZADA\n", "HEADER"))

    def setup_panel(self):
        mock_app = MagicMock()
        mock_app.get_current_user.return_value = {'username': 'test_runner'}
        self.test_window = tk.Toplevel(self.tk_root)
        self.test_window.withdraw()
        self.panel = PainelVisualizacaoDados(self.test_window, mock_app)
        self.panel.pack(fill="both", expand=True)
        self.tk_root.update()

    def teardown_panel(self):
        if self.test_window:
            self.test_window.destroy()
        self.tk_root.update()

    @patch('persistencia.data_service.DataService', new_callable=MagicMock)
    @patch('persistencia.repository.GenericRepository', new_callable=MagicMock)
    def test_painel01_carregamento_e_submissao(self, mock_repo, mock_service):
        self.q.put(("--- Teste: Painel01 Carregamento e Submissão ---", "INFO"))
        try:
            mock_repo.read_linguagens_com_tipo.return_value = pd.DataFrame(
                columns=['id', 'nome', 'tipo', 'ano_criacao', 'categoria'])
            mock_repo.read_table_to_dataframe.return_value = pd.DataFrame({'id': [1], 'nome': ['Dinâmica']})
            self.setup_panel()
            self.q.put(("✅ O painel foi instanciado com sucesso (com mocks).", "SUCCESS"))

            self.panel.nome_var.set("Nova Linguagem via Teste")
            self.panel.tipo_var.set("Dinâmica")
            self.panel.ano_var.set(2025)
            self.panel.categoria_var.set("Teste Automatizado")
            self.q.put(("ℹ️ Formulário preenchido programaticamente.", "INFO"))

            self.panel.view.save_button.invoke()
            self.tk_root.update()
            self.q.put(("ℹ️ Botão 'Salvar' invocado.", "INFO"))

            mock_repo.write_dataframe_to_table.assert_called_once()
            self.q.put(("✅ Método 'write_dataframe_to_table' do mock foi chamado.", "SUCCESS"))

            call_args = mock_repo.write_dataframe_to_table.call_args
            df_arg = call_args[0][0]
            assert df_arg.iloc[0]['nome'] == "Nova Linguagem via Teste"
            assert df_arg.iloc[0]['id_tipo'] == 1
            self.q.put(("✅ Dados corretos foram passados para o mock.", "SUCCESS"))
        finally:
            self.teardown_panel()


# █████████████████████████████████████████████████████████████████████████████████
# --- APLICAÇÃO GRÁFICA DO TESTADOR ---
# █████████████████████████████████████████████████████████████████████████████████

class TestRunnerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Interface de Testes Integrada (Padrão ttk)")
        self.geometry("900x700")
        self.test_queue = queue.Queue()
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)

        control_frame = ttk.LabelFrame(main_frame, text=" Controlo dos Testes ", padding=10)
        control_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        control_frame.columnconfigure(0, weight=1)

        self.run_button = ttk.Button(control_frame, text="Executar Todos os Testes", command=self.run_all_tests)
        self.run_button.grid(row=0, column=0, sticky="ew", padx=5, ipady=5)

        clear_button = ttk.Button(control_frame, text="Limpar Log", command=self.clear_log)
        clear_button.grid(row=0, column=1, sticky="ew", padx=5)

        # --- NOVO BOTÃO ---
        copy_button = ttk.Button(control_frame, text="Copiar Log", command=self._copy_log_to_clipboard)
        copy_button.grid(row=0, column=2, sticky="ew", padx=5)

        self.progress = ttk.Progressbar(control_frame, mode='indeterminate')
        self.progress.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=(10, 0))

        log_frame = ttk.LabelFrame(main_frame, text=" Log de Execução em Tempo Real ", padding=10)
        log_frame.grid(row=1, column=0, sticky="nsew")

        self.log_text = ScrolledText(log_frame, wrap="word", font=("Courier New", 10))
        self.log_text.pack(fill="both", expand=True)
        self.log_text['state'] = 'disabled'

        self.log_text.tag_config("HEADER", foreground='blue', font=("Courier New", 10, "bold underline"))
        self.log_text.tag_config("SUCCESS", foreground='green')
        self.log_text.tag_config("FAIL", foreground='red')
        self.log_text.tag_config("INFO", foreground='black')

    # --- NOVO MÉTODO ---
    def _copy_log_to_clipboard(self):
        """Copia o conteúdo do log para a área de transferência do sistema."""
        try:
            log_content = self.log_text.get("1.0", tk.END).strip()
            if log_content:
                self.clipboard_clear()
                self.clipboard_append(log_content)
                messagebox.showinfo("Sucesso", "O conteúdo do log foi copiado para a área de transferência.",
                                    parent=self)
            else:
                messagebox.showwarning("Aviso", "O log está vazio. Nada para copiar.", parent=self)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível copiar o log: {e}", parent=self)

    def run_all_tests(self):
        self.run_button.config(state="disabled")
        self.clear_log()
        self.progress.start()
        self.test_thread = threading.Thread(target=self._worker_thread_run_tests, daemon=True)
        self.test_thread.start()
        self.after(100, self.process_queue)

    def _worker_thread_run_tests(self):
        try:
            backend_tester = TestBackend(self.test_queue)
            backend_tester.run()

            frontend_tester = TestFrontend(self.test_queue, self)
            frontend_tester.run()
        except Exception as e:
            self.test_queue.put((f"❌ ERRO CRÍTICO NA EXECUÇÃO DOS TESTES: {e}", "FAIL"))
        finally:
            self.test_queue.put(("__DONE__", "FINISH"))

    def process_queue(self):
        try:
            while True:
                message, style = self.test_queue.get_nowait()
                if style == "FINISH":
                    self.run_button.config(state="normal")
                    self.progress.stop()
                    self.log_message("\n--- Todos os desafios foram concluídos. ---", "HEADER")
                    return
                else:
                    self.log_message(str(message), style)
        except queue.Empty:
            self.after(100, self.process_queue)

    def log_message(self, message, style):
        self.log_text['state'] = 'normal'
        self.log_text.insert(tk.END, message + "\n", style)
        self.log_text['state'] = 'disabled'
        self.log_text.yview(tk.END)

    def clear_log(self):
        self.log_text['state'] = 'normal'
        self.log_text.delete('1.0', tk.END)
        self.log_text['state'] = 'disabled'

    def on_close(self):
        self.quit()
        self.destroy()


if __name__ == "__main__":
    app = TestRunnerApp()
    app.mainloop()