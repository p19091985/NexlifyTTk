from tkinter import messagebox
import sys
import logging
import os

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from persistencia.logger import setup_loggers

setup_loggers()

import config
from persistencia.database import DatabaseManager
from app import AplicacaoPrincipal

def validar_configuracoes():
    """
    Verifica a consistência das flags de configuração antes de iniciar a aplicação.
    Retorna True se a configuração for válida, False caso contrário.
    """
                                                           
    if config.USE_LOGIN and not config.DATABASE_ENABLED:
        messagebox.showerror(
            "Erro de Configuração Inválida",
            "A aplicação não pode iniciar devido a uma configuração inconsistente.\n\n"
            "Problema Detectado:\n"
            "   • USE_LOGIN está definido como True\n"
            "   • DATABASE_ENABLED está definido como False\n\n"
            "Motivo: O sistema de login requer acesso ao banco de dados para verificar "
            "as credenciais dos usuários. É impossível autenticar com o banco desativado.\n\n"
            "Solução: Altere seu arquivo config.py para uma das opções abaixo:\n"
            "1. Habilite o banco de dados: DATABASE_ENABLED = True\n"
            "2. Desabilite o login: USE_LOGIN = False"
        )
        return False

    if config.INITIALIZE_DATABASE_ON_STARTUP and not config.DATABASE_ENABLED:
        messagebox.showerror(
            "Erro de Configuração Inválida",
            "A aplicação não pode iniciar devido a uma configuração inconsistente.\n\n"
            "Problema Detectado:\n"
            "   • INITIALIZE_DATABASE_ON_STARTUP está definido como True\n"
            "   • DATABASE_ENABLED está definido como False\n\n"
            "Motivo: O sistema não pode criar as tabelas do banco (schema) se o acesso "
            "ao banco de dados como um todo está desativado.\n\n"
            "Solução: Altere seu arquivo config.py para uma das opções abaixo:\n"
            "1. Habilite o banco de dados: DATABASE_ENABLED = True\n"
            "2. Desabilite a inicialização automática: INITIALIZE_DATABASE_ON_STARTUP = False"
        )
        return False

    return True

def main():
    main_logger = logging.getLogger("main_app")

    if not validar_configuracoes():
        main_logger.error("Validação de configuração falhou. A aplicação será encerrada.")
        return                                                        

    main_logger.info("=" * 20 + " Aplicação Iniciada " + "=" * 20)

    if not config.DATABASE_ENABLED:
        main_logger.warning("DATABASE_ENABLED está como False. O banco de dados não será utilizado.")

    if config.DATABASE_ENABLED and config.INITIALIZE_DATABASE_ON_STARTUP:
        try:
            main_logger.info("Inicializando verificação do banco de dados...")
            DatabaseManager.initialize_database()
            main_logger.info("Banco de dados pronto.")
        except Exception as e:
            main_logger.critical(f"Falha na inicialização do banco: {e}", exc_info=True)
            messagebox.showerror("Erro de Banco de Dados",
                                 f"Não foi possível inicializar ou conectar ao banco de dados.\n\nDetalhe: {e}")
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