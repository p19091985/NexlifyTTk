import logging
from logging.handlers import RotatingFileHandler
import sys
import os
from pathlib import Path
from utils.secure_files import reject_link_path, private_directory, restrict_permissions


class PrivateRotatingFileHandler(RotatingFileHandler):
    def _open(self):
        path = reject_link_path(self.baseFilename)
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, 'O_NOFOLLOW', 0), 0o600)
        try:
            restrict_permissions(path)
        except Exception:
            os.close(descriptor)
            raise
        return os.fdopen(descriptor, self.mode, encoding=self.encoding, errors=self.errors)

try:

    from config import LOGGING_ENABLED as ENABLE_LOGGING, LOG_LEVEL, LOG_FORMAT, REDIRECT_CONSOLE_TO_LOG
except ImportError as e:
    print(f"Erro fatal: Não foi possível importar configurações do logger: {e}", file=sys.stderr)
    print("Verifique se o arquivo config.py existe e define ENABLE_LOGGING, LOG_LEVEL, LOG_FORMAT e REDIRECT_CONSOLE_TO_LOG.",
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
        if not buf:
            return 0

        self.line_buffer += buf
        while "\n" in self.line_buffer:
            line, self.line_buffer = self.line_buffer.split("\n", 1)
            line = line.rstrip()
            if line:
                self.logger.log(self.log_level, line)
        return len(buf)

    def flush(self):
        """Necessário para a interface de 'file-like object'."""
        pending = self.line_buffer.rstrip()
        if pending:
            self.logger.log(self.log_level, pending)
        self.line_buffer = ''

def setup_loggers():
    """
    Configura e inicializa os handlers de log (console e arquivo)
    para a aplicação.
    """

    root_logger = logging.getLogger()
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
        handler.close()

    if not ENABLE_LOGGING:
        logging.disable(logging.CRITICAL)
        root_logger.addHandler(logging.NullHandler())
        return

    logging.disable(logging.NOTSET)

    log_level = LOG_LEVEL
    formatter = logging.Formatter(LOG_FORMAT)
    root_logger.setLevel(log_level)

    try:
        console_handler = logging.StreamHandler(sys.__stdout__ if isinstance(sys.stdout, LogRedirector) else sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    except Exception as e:
        print(f"Erro ao configurar o logger do console: {e}", file=sys.stderr)

    log_dir = Path(os.environ.get('NEXLIFY_LOG_DIR', str(Path(__file__).parent.parent / 'logs')))
    log_file_path = log_dir / "app.log"

    try:

        private_directory(log_dir)

        file_handler = PrivateRotatingFileHandler(log_file_path, maxBytes=2_000_000, backupCount=5, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    except Exception as e:
        import config
        if config.ENVIRONMENT == 'production':
            raise RuntimeError('Não foi possível abrir o log obrigatório. Verifique as permissões da pasta logs.') from None
        root_logger.error('Não foi possível abrir o log de arquivo (%s).', type(e).__name__)

    if REDIRECT_CONSOLE_TO_LOG:
        root_logger.info("Redirecionando stdout e stderr para os handlers de log...")
        sys.stdout = LogRedirector(logging.getLogger("STDOUT"), logging.INFO)
        sys.stderr = LogRedirector(logging.getLogger("STDERR"), logging.ERROR)

    root_logger.info("=" * 30)
    root_logger.info("Sistema de loggers configurado com sucesso.")
    root_logger.debug(f"Nível de log definido como: {logging.getLevelName(log_level)} ({log_level})")
