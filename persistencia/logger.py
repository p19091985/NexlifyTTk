# persistencia/logger.py
import logging
import sys
import os


class StreamToLogger:
    """
    Um objeto 'file-like' que redireciona chamadas de 'write' para um logger.
    Usado para capturar stdout e stderr.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        """Redireciona o buffer para o logger."""
        for line in buf.rstrip().splitlines():
            # Remove espaços em branco desnecessários e loga
            if line.strip():
                self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        """Método flush, necessário para a interface de stream."""
        pass


def setup_loggers():
    """
    Configura os loggers principais da aplicação.
    """
    # Importa a configuração aqui para evitar importação circular
    from config import LOG_LEVEL, LOG_FORMAT

    # Garante que o diretório de logs exista
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)

    log_file_path = os.path.join(log_dir, 'app.log')

    # Configuração do logger raiz
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(log_file_path, encoding='utf-8'),
            logging.StreamHandler(sys.stdout) # Também mostra no console
        ]
    )

    # Configuração de um logger específico para tentativas de login
    login_logger = logging.getLogger("login_attempts")
    login_file_handler = logging.FileHandler(os.path.join(log_dir, 'login.log'), encoding='utf-8')
    login_file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    login_logger.addHandler(login_file_handler)
    login_logger.setLevel(logging.INFO)
    login_logger.propagate = False # Evita que o log de login vá para o app.log

    logging.info("Loggers configurados com sucesso.")