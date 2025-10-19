import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path



from config import LOG_LEVEL, LOG_FORMAT, REDIRECT_CONSOLE_TO_LOG


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
    project_root = Path(__file__).parent.parent.resolve()
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    log_format = logging.Formatter(LOG_FORMAT)
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

                                   
    app_logger = logging.getLogger("main_app")
    app_logger.setLevel(log_level)
    app_logger.propagate = False

                                                                                   
    if app_logger.hasHandlers():
        app_logger.handlers.clear()

                                    
    app_handler = RotatingFileHandler(
        log_dir / "app.log", maxBytes=2 * 1024 * 1024, backupCount=5, encoding='utf-8'
    )
    app_handler.setFormatter(log_format)
    app_logger.addHandler(app_handler)

                                     
    login_logger = logging.getLogger("login_attempts")
    login_logger.setLevel(log_level)
    login_logger.propagate = False

    if login_logger.hasHandlers():
        login_logger.handlers.clear()

    login_handler = RotatingFileHandler(
        log_dir / "login.log", maxBytes=1 * 1024 * 1024, backupCount=3, encoding='utf-8'
    )
    login_handler.setFormatter(log_format)
    login_logger.addHandler(login_handler)


    if not REDIRECT_CONSOLE_TO_LOG:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_format)
        app_logger.addHandler(console_handler)
        logging.info("Sistema de logging configurado para saída no console.")
    else:

        stdout_logger = logging.getLogger("stdout")
        if not stdout_logger.hasHandlers():
            stdout_logger.addHandler(app_handler)
            stdout_logger.setLevel(logging.INFO)
            sys.stdout = StreamToLogger(stdout_logger, logging.INFO)

        stderr_logger = logging.getLogger("stderr")
        if not stderr_logger.hasHandlers():
            stderr_logger.addHandler(app_handler)
            stderr_logger.setLevel(logging.ERROR)
            sys.stderr = StreamToLogger(stderr_logger, logging.ERROR)

        logging.info("Redirecionamento do console para o arquivo de log está ATIVO.")


    logging.info("Sistema de logging configurado com sucesso.")