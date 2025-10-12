import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
import time
import traceback
import sys                       

try:
    import GPUtil
except ImportError:
    GPUtil = None

                                                                           
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from persistencia.database import DatabaseManager


class SystemCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ferramenta de Diagnóstico do Sistema (Health Check)")
        self.root.geometry("800x700")
        self.root.minsize(700, 500)
        self.setup_styles()
        self.create_widgets()
        self.log("Aguardando início do diagnóstico...")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Title.TLabel", font=('Segoe UI', 14, 'bold'))
        style.configure("Header.TLabel", font=('Segoe UI', 11, 'bold'))
        style.configure("Action.TButton", font=('Segoe UI', 10, 'bold'))

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        ttk.Label(control_frame, text="Diagnóstico do Ambiente", style="Title.TLabel").pack(side=tk.LEFT, anchor="w")

        action_buttons_frame = ttk.Frame(control_frame)
        action_buttons_frame.pack(side=tk.RIGHT, anchor="e")

        self.clear_log_btn = ttk.Button(action_buttons_frame, text="Limpar Log", command=self.clear_log)
        self.clear_log_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.copy_log_btn = ttk.Button(action_buttons_frame, text="Copiar Log", command=self.copy_log_to_clipboard)
        self.copy_log_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.run_btn = ttk.Button(action_buttons_frame, text="Executar Todos os Testes",
                                  command=self.run_all_checks, style="Action.TButton")
        self.run_btn.pack(side=tk.LEFT)

        paned_window = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        paned_window.grid(row=1, column=0, sticky="nsew")

        results_frame = ttk.LabelFrame(paned_window, text=" Resultados do Diagnóstico ", padding=10)
        paned_window.add(results_frame, weight=3)

        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        columns = ('check', 'status', 'details')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', selectmode='browse')
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.tree.heading('check', text='Verificação')
        self.tree.heading('status', text='Status')
        self.tree.heading('details', text='Detalhes')
        self.tree.column('check', width=200)
        self.tree.column('status', width=100, anchor='center')
        self.tree.column('details', width=400)
        self.tree.tag_configure("SUCCESS", foreground='green')
        self.tree.tag_configure("FAIL", foreground='red')
        self.tree.tag_configure("WARNING", foreground='dark orange')

        scrollbar_tree = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_tree.set)
        scrollbar_tree.grid(row=0, column=1, sticky="ns")

        log_frame = ttk.LabelFrame(paned_window, text=" Log de Execução Detalhado ", padding=10)
        paned_window.add(log_frame, weight=2)

        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD, font=("Consolas", 9))
        self.log_text.grid(row=0, column=0, sticky="nsew")
        self.log_text.tag_config("SUCCESS", foreground="green")
        self.log_text.tag_config("FAIL", foreground="red")
        self.log_text.tag_config("WARNING", foreground="dark orange")
        self.log_text.tag_config("INFO", foreground="gray")
        self.log_text.config(state=tk.DISABLED)

    def log(self, message, level="info"):
        level_upper = level.upper()
        def _log_update():
            self.log_text.config(state=tk.NORMAL)
            timestamp = time.strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"{timestamp} [{level_upper}] {message}\n", (level_upper,))
            self.log_text.config(state=tk.DISABLED)
            self.log_text.see(tk.END)
        self.root.after(0, _log_update)

    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log("Log limpo.")

    def copy_log_to_clipboard(self):
        try:
            content = self.log_text.get(1.0, tk.END)
            if content.strip():
                self.root.clipboard_clear()
                self.root.clipboard_append(content)
                self.log("Conteúdo do log copiado para a área de transferência!", "success")
            else:
                self.log("Não há conteúdo no log para copiar.", "warning")
        except Exception as e:
            self.log(f"Erro ao copiar para a área de transferência: {e}", "fail")

    def run_in_thread(self, target_func):
        thread = threading.Thread(target=target_func, daemon=True)
        thread.start()

    def update_ui(self, result):
        status = result['status']
        tags = (status,)
        summary_details = result['details'].splitlines()[0]
        self.tree.insert("", "end", values=(result['name'], status, summary_details), tags=tags)
        log_message = f"Teste '{result['name']}' concluído com status: {status}"
        if status in ['FAIL', 'WARNING']:
            log_message += f"\n DETALHES \n{result['details']}\n-"
        self.log(log_message, level=status.lower())

    def run_all_checks(self):
        self.run_btn.config(state=tk.DISABLED)
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.log("--")
        self.log("Iniciando diagnóstico completo do sistema...")
        self.run_in_thread(self._run_all_checks_thread)

    def _run_all_checks_thread(self):
        try:
            for result in self._check_project_integrity():
                self.root.after(0, self.update_ui, result)
                time.sleep(0.05)
            gpu_result = self._check_gpu()
            self.root.after(0, self.update_ui, gpu_result)
            time.sleep(0.05)
            db_result = self._check_database()
            self.root.after(0, self.update_ui, db_result)
            self.log("Diagnóstico concluído.", "success")
        except Exception as e:
            self.log(f"Ocorreu um erro inesperado durante os testes: {traceback.format_exc()}", "fail")
        finally:
            self.root.after(0, lambda: self.run_btn.config(state=tk.NORMAL))

    def _check_project_integrity(self):
        self.log("Iniciando verificação de integridade do projeto...")
        yield {'name': 'Diretório Raiz do Projeto', 'status': 'SUCCESS', 'details': f'Raiz encontrada em: {project_root}'}
        essential_paths = ["run.py", "app.py", "banco.ini", "settings.json", "panels/", "persistencia/", "dialogs/", "persistencia/database.py", "persistencia/repository.py"]
        for path in essential_paths:
            full_path = os.path.join(project_root, path)
            status, details = ('SUCCESS', 'Encontrado') if os.path.exists(full_path) else ('FAIL', 'Não encontrado!')
            yield {'name': f'Arquivo/Pasta: {path}', 'status': status, 'details': details}

    def _check_gpu(self):
        self.log("Iniciando verificação de GPU...")
        if GPUtil is None:
            return {'name': 'Placa de Vídeo (GPU)', 'status': 'WARNING', 'details': "Biblioteca 'gputil' não instalada. Instale com: pip install gputil"}
        try:
            gpus = GPUtil.getGPUs()
            if not gpus:
                return {'name': 'Placa de Vídeo (GPU)', 'status': 'WARNING', 'details': 'Nenhuma GPU dedicada detectada.'}
            else:
                gpu_info = [f"{gpu.name} (Load: {gpu.load * 100:.1f}%)" for gpu in gpus]
                return {'name': 'Placa de Vídeo (GPU)', 'status': 'SUCCESS', 'details': ', '.join(gpu_info)}
        except Exception as e:
            detailed_error = traceback.format_exc()
            return {'name': 'Placa de Vídeo (GPU)', 'status': 'FAIL', 'details': f'Erro ao acessar informações da GPU: {e}\n\n{detailed_error}'}

    def _check_database(self):
        self.log("Iniciando verificação de conexão com o banco de dados...")
        try:
            from sqlalchemy import text
            DatabaseManager._engine = None
            engine = DatabaseManager.get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    db_type = engine.url.drivername
                    return {'name': 'Conexão com Banco de Dados', 'status': 'SUCCESS', 'details': f'Conectado com sucesso ao banco do tipo: {db_type}'}
                else:
                    raise Exception("A consulta de teste não retornou o resultado esperado.")
        except Exception as e:
            detailed_error = traceback.format_exc()
            return {'name': 'Conexão com Banco de Dados', 'status': 'FAIL', 'details': f'Falha na conexão: {e}\n\n{detailed_error}'}


def main():
    try:
        root = tk.Tk()
        app = SystemCheckerApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Erro fatal ao iniciar a aplicação: {e}")
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Erro Fatal", f"Ocorreu um erro inesperado: {e}")
        except tk.TclError:
            pass

if __name__ == "__main__":
    main()