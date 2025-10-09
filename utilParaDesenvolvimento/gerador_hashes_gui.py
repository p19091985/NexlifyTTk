# gerador_hashes_gui.py (CORRIGIDO COM SELEÇÃO DE ARQUIVO)
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from pathlib import Path
import sys
import re
import logging

#  Configuração Inicial 
# Adiciona o diretório raiz do projeto ao path para garantir que a importação funcione
try:
    PROJECT_ROOT = Path(__file__).parent.resolve()
    sys.path.insert(0, str(PROJECT_ROOT))
    from persistencia.auth import hash_password
except ImportError:
    # Fallback para caso o script seja executado de forma que o import falhe
    try:
        from auth import hash_password

        PROJECT_ROOT = Path(__file__).parent.parent.resolve()
    except (ImportError, ModuleNotFoundError) as e:
        print(f"ERRO CRÍTICO: Não foi possível importar a função 'hash_password'.")
        print(f"Certifique-se de que este script está na pasta raiz do seu projeto.")
        print(f"Detalhe do erro: {e}")
        sys.exit(1)

# Dicionário de usuários e senhas em texto plano
SENHAS_PARA_GERAR = {
    'admin': 'admin',
    'diretor.op': 'dir123',
    'gerente.ti': 'ti123',
    'supervisor.prod': 'sup123',
    'operador': 'op123',
    'analista.dados': 'ana123'
}


class HashUpdaterApp(tk.Tk):
    """
    Interface gráfica para automatizar a atualização de hashes bcrypt
    em um arquivo de schema de banco de dados selecionado pelo usuário.
    """

    def __init__(self):
        super().__init__()
        self.title("Atualizador de Hashes para Arquivo SQL")
        self.geometry("700x550")
        self.resizable(False, False)

        # Variável para armazenar o caminho do arquivo selecionado
        self.selected_file_path = tk.StringVar()

        # Estilo
        self.style = ttk.Style(self)
        try:
            self.style.theme_use('clam')
        except tk.TclError:
            self.style.theme_use('default')

        #  Widgets 
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        #  NOVO: Frame de Seleção de Arquivo 
        file_frame = ttk.LabelFrame(main_frame, text=" 1. Selecione o Arquivo SQL ", padding=10)
        file_frame.pack(fill="x", pady=(0, 15))
        file_frame.columnconfigure(0, weight=1)

        file_entry = ttk.Entry(file_frame, textvariable=self.selected_file_path, state="readonly")
        file_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        select_button = ttk.Button(file_frame, text="Selecionar Arquivo...", command=self._select_schema_file)
        select_button.grid(row=0, column=1, sticky="e")

        # Botão principal - Inicia desabilitado
        self.update_button = ttk.Button(
            main_frame,
            text=" 2. Gerar Novos Hashes e Atualizar Arquivo ",
            command=self._run_update_process,
            state="disabled"  # Começa desabilitado
        )
        self.update_button.pack(fill="x", pady=(0, 15))
        self.style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'))
        self.update_button.configure(style='Accent.TButton')

        # Área de log para feedback
        log_label = ttk.Label(main_frame, text="Log do Processo:")
        log_label.pack(anchor="w")

        self.log_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, state="disabled", height=20)
        self.log_area.pack(fill="both", expand=True)

        self.log_area.tag_config('success', foreground='green', font=('Segoe UI', 9, 'bold'))
        self.log_area.tag_config('error', foreground='red', font=('Segoe UI', 9, 'bold'))
        self.log_area.tag_config('info', foreground='blue')

    def _select_schema_file(self):
        """Abre uma janela de diálogo para o usuário escolher o arquivo .sql."""
        filepath = filedialog.askopenfilename(
            title="Selecione o arquivo de schema SQL",
            filetypes=[("SQL Scripts", "*.sql"), ("Todos os arquivos", "*.*")]
        )
        if filepath:
            self.selected_file_path.set(filepath)
            self.update_button.config(state="normal")  # Habilita o botão principal
            self._log(f"Arquivo selecionado: {filepath}", "info")

    def _log(self, message: str, tag: str = 'normal'):
        """ Adiciona uma mensagem à área de texto de log. """
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, message + "\n", tag)
        self.log_area.config(state="disabled")
        self.log_area.see(tk.END)  # Auto-scroll
        self.update_idletasks()

    def _run_update_process(self):
        """ Orquestra todo o processo de leitura, atualização e salvamento. """
        self.update_button.config(state="disabled")
        self.log_area.config(state="normal")
        self.log_area.delete('1.0', tk.END)  # Limpa o log anterior
        self.log_area.config(state="disabled")

        target_file_path = self.selected_file_path.get()
        if not target_file_path:
            self._log("ERRO: Nenhum arquivo foi selecionado.", "error")
            # Reabilita o botão de seleção, mas não o de atualização
            return

        try:
            schema_file = Path(target_file_path)
            self._log(" INICIANDO PROCESSO DE ATUALIZAÇÃO ")
            self._log(f"Lendo o arquivo: {schema_file.name}", "info")

            sql_content = schema_file.read_text(encoding='utf-8')
            original_content = sql_content

            for username, plain_password in SENHAS_PARA_GERAR.items():
                self._log(f"\nProcessando usuário: '{username}'")
                new_hash = hash_password(plain_password)
                self._log(f"  -> Novo hash gerado: {new_hash}")

                pattern = re.compile(f"('{username}',\\s*').*?('\\s*,\\s*'.*\\))")
                replacement = f"\\1{new_hash}\\2"
                new_sql_content, num_subs = pattern.subn(replacement, sql_content)

                if num_subs > 0:
                    sql_content = new_sql_content
                    self._log(f"  -> Hash substituído com sucesso no conteúdo.", "info")
                else:
                    self._log(
                        f"  -> AVISO: Usuário '{username}' não encontrado no arquivo. Nenhum hash foi alterado para ele.",
                        "error")

            if sql_content != original_content:
                self._log("\nSalvando alterações no arquivo...", "info")
                schema_file.write_text(sql_content, encoding='utf-8')
                self._log("\n PROCESSO CONCLUÍDO COM SUCESSO! ", "success")
                self._log(f"O arquivo '{schema_file.name}' foi atualizado com os novos hashes.", "success")
            else:
                self._log("\n PROCESSO CONCLUÍDO ", "success")
                self._log("Nenhuma alteração foi necessária ou possível.", "success")

        except Exception as e:
            self._log(f"\n OCORREU UM ERRO! ", "error")
            self._log(f"Detalhes do erro: {e}", "error")
            logging.exception("Erro detalhado no console:")
        finally:
            self.update_button.config(state="normal")


if __name__ == "__main__":
    app = HashUpdaterApp()
    app.mainloop()