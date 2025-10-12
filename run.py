from tkinter import messagebox
import sys
import logging
import os

# 1. Adiciona a pasta raiz do projeto ao path do Python.
#    Isso permite que o script encontre os pacotes como 'persistencia', 'app', etc.
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 2. Agora, com o path configurado, as importações são feitas de forma "absoluta"
#    a partir da raiz do projeto, o que funciona corretamente.
from persistencia.logger import setup_loggers, StreamToLogger
setup_loggers()

import config
from persistencia.database import DatabaseManager
from app import AplicacaoPrincipal

def main():
    if config.REDIRECT_CONSOLE_TO_LOG:
        sys.stdout = StreamToLogger(logging.getLogger("stdout"), logging.INFO)
        sys.stderr = StreamToLogger(logging.getLogger("stderr"), logging.ERROR)
        print("Redirecionamento de console para log ativado.")

    main_logger = logging.getLogger("main_app")
    main_logger.info("=" * 20 + " Aplicação Iniciada " + "=" * 20)

    if config.INITIALIZE_DATABASE_ON_STARTUP:
        try:
            # 3. A chamada ao DatabaseManager permanece. É AQUI DENTRO que a
            #    descriptografia acontece, de forma encapsulada e segura.
            DatabaseManager.initialize_database()
            main_logger.info("Banco de dados pronto.")
        except Exception as e:
            main_logger.critical(f"Falha na inicialização do banco: {e}", exc_info=True)
            messagebox.showerror("Erro de Banco de Dados", "Não foi possível inicializar o banco.")
            return

    main_logger.info("Iniciando a aplicação principal...")
    try:
        app = AplicacaoPrincipal(project_root=project_root)
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