# run.py
import tkinter as tk
from tkinter import messagebox
import sys
import logging
import os

# Adiciona o diretório do projeto ao sys.path para garantir imports consistentes
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Importa e configura os loggers primeiro
from persistencia.logger import setup_loggers, StreamToLogger
setup_loggers()

# Agora importa os outros módulos
import config
from persistencia.database import DatabaseManager
from persistencia.login_ui import LoginDialog
from app import AplicacaoPrincipal


def _run_login_process() -> dict | None:
    """
    Encapsula todo o fluxo de exibição da janela de login.
    Retorna as informações do usuário em caso de sucesso, ou None.
    """
    login_logger = logging.getLogger("login_attempts")
    try:
        root = tk.Tk()
        root.withdraw()

        login_logger.debug("Criando a janela de diálogo de login.")
        login_dialog = LoginDialog(root)
        root.wait_window(login_dialog)

        user_info = login_dialog.user_info
        root.destroy()
        return user_info

    except Exception as e:
        login_logger.critical(f"Erro fatal no processo de login: {e}", exc_info=True)
        messagebox.showerror("Erro Crítico", f"Ocorreu um erro inesperado no login: {e}")
        return None


def main():
    """
    Função principal da aplicação.
    """
    if config.REDIRECT_CONSOLE_TO_LOG:
        sys.stdout = StreamToLogger(logging.getLogger("stdout"), logging.INFO)
        sys.stderr = StreamToLogger(logging.getLogger("stderr"), logging.ERROR)
        print("Redirecionamento de console para log ativado.")

    main_logger = logging.getLogger("main_app")
    main_logger.info("=" * 20 + " Aplicação Iniciada " + "=" * 20)

    if config.USE_DATABASE:
        main_logger.info("Inicializando conexão com o banco de dados...")
        try:
            DatabaseManager.initialize_database()
            main_logger.info("Banco de dados pronto.")
        except Exception as e:
            main_logger.critical(f"Falha crítica na inicialização do banco: {e}", exc_info=True)
            messagebox.showerror("Erro de Banco de Dados", "Não foi possível inicializar o banco. Verifique os logs.")
            return

    user_info = None
    if config.USE_LOGIN:
        main_logger.info("Iniciando processo de login...")
        user_info = _run_login_process()

        if user_info == "max_attempts_failed":
            main_logger.error("Login bloqueado por excesso de tentativas.")
            sys.exit(1)
        elif not user_info:
            main_logger.info("Login cancelado pelo usuário ou falhou. Encerrando.")
            sys.exit(0)
    else:
        main_logger.warning("Executando em modo de desenvolvimento (sem login).")
        user_info = {"name": "Desenvolvedor", "access_level": "Administrador Global", "username": "dev"}

    main_logger.info(f"Iniciando aplicação para o usuário: '{user_info.get('name')}'")
    try:
        app = AplicacaoPrincipal(user_info)
        app.mainloop()
        main_logger.info("Aplicação finalizada normalmente.")
    except Exception as e:
        main_logger.critical(f"Erro fatal na aplicação principal: {e}", exc_info=True)
        messagebox.showerror("Erro Crítico", f"A aplicação encontrou um erro fatal e precisa ser fechada: {e}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        logging.info(f"Aplicação encerrada com código de saída: {e.code}")
    except Exception as e:
        logging.getLogger("main_app").critical(f"Erro não tratado no escopo global: {e}", exc_info=True)
    finally:
        logging.info("=" * 20 + " Execução Finalizada " + "=" * 20 + "\n")