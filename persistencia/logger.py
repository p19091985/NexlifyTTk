                        
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


class StreamToLogger:
    def __init__(self, logger: logging.Logger, level: int):
        self.logger = logger
        self.level = level

    def write(self, buf: str):
        for line in buf.rstrip().splitlines():
            if line.strip():
                self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass


def setup_loggers():
    from config import LOG_LEVEL, LOG_FORMAT
    project_root = Path(__file__).parent.parent.resolve()
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    log_format = logging.Formatter(LOG_FORMAT)
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

    app_logger = logging.getLogger("main_app")
    app_logger.setLevel(log_level)
    app_logger.propagate = False

    app_handler = RotatingFileHandler(log_dir / "app.log", maxBytes=2 * 1024 * 1024, backupCount=5, encoding='utf-8')
    app_handler.setFormatter(log_format)
    app_logger.addHandler(app_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    app_logger.addHandler(console_handler)

    login_logger = logging.getLogger("login_attempts")
    login_logger.setLevel(log_level)
    login_logger.propagate = False

    login_handler = RotatingFileHandler(log_dir / "login.log", maxBytes=1 * 1024 * 1024, backupCount=3,
                                        encoding='utf-8')
    login_handler.setFormatter(log_format)
    login_logger.addHandler(login_handler)

    stdout_logger = logging.getLogger("stdout")
    stdout_logger.addHandler(app_handler)
    stdout_logger.setLevel(logging.INFO)

    stderr_logger = logging.getLogger("stderr")
    stderr_logger.addHandler(app_handler)
    stderr_logger.setLevel(logging.ERROR)

    logging.info("Sistema de logging configurado com rotação de arquivos para acesso seguro.")