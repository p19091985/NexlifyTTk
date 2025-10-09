# persistencia/logger.py
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# --- Classes de Suporte ---

class StreamToLogger:
    """
    Um objeto 'file-like' que redireciona chamadas de 'write' para um logger.
    Usado para capturar stdout e stderr.
    """
    def __init__(self, logger: logging.Logger, level: int):
        self.logger = logger
        self.level = level
        self.linebuf = ''

    def write(self, buf: str):
        """Redireciona o buffer para o logger."""
        for line in buf.rstrip().splitlines():
            # Remove espaços em branco desnecessários e loga
            if line.strip():
                self.logger.log(self.level, line.rstrip())

    def flush(self):
        """Método flush, necessário para a interface de stream."""
        pass

# --- Função de Configuração ---

def setup_loggers():
    """
    Configura os loggers principais da aplicação, incluindo rotação de arquivos
    para segurança em acesso concorrente e controle de tamanho.
    """
    # Importa a configuração aqui para evitar importação circular
    from config import LOG_LEVEL, LOG_FORMAT

    # Garante que o diretório de logs exista usando pathlib (mais moderno)
    project_root = Path(__file__).parent.parent.resolve()
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)

    log_format = logging.Formatter(LOG_FORMAT)
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

    # --- Logger Principal da Aplicação (app.log) ---
    # Em vez de usar logging.basicConfig, configuramos loggers nomeados.
    # Isso evita conflitos com outras bibliotecas.
    app_logger = logging.getLogger("main_app")
    app_logger.setLevel(log_level)
    app_logger.propagate = False # Evita duplicar logs no logger root

    # Handler para arquivo com rotação (thread-safe e com controle de tamanho)
    # Rotação: 5 arquivos de no máximo 2MB cada.
    app_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=2*1024*1024, # 2 MB
        backupCount=5,
        encoding='utf-8'
    )
    app_handler.setFormatter(log_format)
    app_logger.addHandler(app_handler)

    # Handler para console (para depuração durante o desenvolvimento)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    app_logger.addHandler(console_handler)

    # --- Logger para Tentativas de Login (login.log) ---
    login_logger = logging.getLogger("login_attempts")
    login_logger.setLevel(log_level)
    login_logger.propagate = False

    # Handler de arquivo com rotação para o log de login
    login_handler = RotatingFileHandler(
        log_dir / "login.log",
        maxBytes=1*1024*1024, # 1 MB
        backupCount=3,
        encoding='utf-8'
    )
    login_handler.setFormatter(log_format)
    login_logger.addHandler(login_handler)

    # Loggers específicos para redirecionamento de stdout e stderr
    # Eles usarão o handler do logger principal para centralizar a saída
    stdout_logger = logging.getLogger("stdout")
    stdout_logger.addHandler(app_handler)
    stdout_logger.setLevel(logging.INFO)

    stderr_logger = logging.getLogger("stderr")
    stderr_logger.addHandler(app_handler)
    stderr_logger.setLevel(logging.ERROR)

    logging.info("Sistema de logging configurado com rotação de arquivos para acesso seguro.")