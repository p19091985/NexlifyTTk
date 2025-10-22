import logging
import sys
import os
from pathlib import Path

# Importa as variáveis de configuração
try:
    # Estas variáveis vêm do arquivo config.py
    from config import LOG_LEVEL, LOG_FORMAT, REDIRECT_CONSOLE_TO_LOG
except ImportError as e:
    print(f"Erro fatal: Não foi possível importar configurações do logger: {e}", file=sys.stderr)
    print("Verifique se o arquivo config.py existe e define LOG_LEVEL, LOG_FORMAT e REDIRECT_CONSOLE_TO_LOG.",
          file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Erro inesperado ao importar config: {e}", file=sys.stderr)
    sys.exit(1)


class LogRedirector:
    """
    Uma classe para redirecionar saídas padrão (stdout, stderr) para um
    objeto logger.
    """

    def __init__(self, logger_instance, log_level=logging.INFO):
        self.logger = logger_instance
        self.log_level = log_level
        self.line_buffer = ''

    def write(self, buf):
        """Redireciona cada linha do buffer para o logger."""
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        """Necessário para a interface de 'file-like object'."""
        pass


def setup_loggers():
    """
    Configura e inicializa os handlers de log (console e arquivo)
    para a aplicação.
    """

    # --- A CORREÇÃO ESTÁ AQUI ---
    # A variável LOG_LEVEL importada de config.py JÁ É UM INTEIRO
    # (ex: logging.DEBUG, logging.INFO, etc.).
    # Nós apenas a utilizamos diretamente, sem fazer .upper() ou getattr().

    log_level = LOG_LEVEL

    # --- FIM DA CORREÇÃO ---

    # Configura o formato da mensagem de log
    formatter = logging.Formatter(LOG_FORMAT)

    # Obtém o logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Limpa handlers existentes para evitar logs duplicados ao reiniciar
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # 1. Handler do Console (StreamHandler)
    # Sempre envia para sys.stdout
    try:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    except Exception as e:
        print(f"Erro ao configurar o logger do console: {e}", file=sys.stderr)

    # 2. Handler de Arquivo (FileHandler)
    try:
        # Define o caminho para a pasta 'logs' na raiz do projeto
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file_path = log_dir / "app.log"

        # Cria o handler que escreve no arquivo (modo 'a' = append)
        file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    except Exception as e:
        # Se falhar, pelo menos o log do console funcionará
        root_logger.error(f"Não foi possível criar o handler de arquivo de log em '{log_file_path}': {e}")

    # 3. Redirecionamento (Opcional)
    # Se configurado, captura todos os 'print()' e os envia para o log
    if REDIRECT_CONSOLE_TO_LOG:
        root_logger.info("Redirecionando stdout e stderr para os handlers de log...")
        sys.stdout = LogRedirector(logging.getLogger("STDOUT"), logging.INFO)
        sys.stderr = LogRedirector(logging.getLogger("STDERR"), logging.ERROR)

    root_logger.info("=" * 30)
    root_logger.info("Sistema de loggers configurado com sucesso.")
    root_logger.debug(f"Nível de log definido como: {logging.getLevelName(log_level)} ({log_level})")