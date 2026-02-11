from tkinter import messagebox
import sys
import logging
import os

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from persistencia.logger import setup_loggers

setup_loggers()

from app import AplicacaoPrincipal

def main():
    main_logger = logging.getLogger("main_app")
    main_logger.info("=" * 20 + " Aplicação Iniciada " + "=" * 20)

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