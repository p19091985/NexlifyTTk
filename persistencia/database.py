# persistencia/database.py
import configparser
import logging
import pathlib
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, OperationalError

# Usando pathlib para uma abordagem mais moderna e robusta com caminhos de arquivo
project_root = pathlib.Path(__file__).parent.parent.resolve()
CONFIG_PATH = project_root / "banco.ini"
SCHEMA_PATH = project_root / "persistencia/sql_schema.sql"


class DatabaseManager:
    """
    Gerencia a conexão com múltiplos sistemas de banco de dados usando SQLAlchemy,
    com base em um arquivo de configuração 'banco.ini'.

    Tabela de Drivers Necessários para cada Banco de Dados:
    =====================================================================================
    | Banco de Dados         | `type` no banco.ini | Driver Recomendado | Comando de Instalação         |
    |------------------------|---------------------|--------------------|-------------------------------|
    | SQLite                 | sqlite              | (Nenhum - embutido)| N/A                           |
    | Microsoft SQL Server   | sqlserver           | pymssql            | pip install pymssql           |
    | PostgreSQL             | postgresql          | psycopg2           | pip install psycopg2-binary   |
    | MySQL                  | mysql               | PyMySQL            | pip install PyMySQL           |
    | Oracle                 | oracle              | oracledb           | pip install oracledb          |
    | MariaDB                | mariadb             | mariadb-connector  | pip install mariadb           |
    =====================================================================================
    """
    _engine = None

    @classmethod
    def get_engine(cls):
        """
        Cria e retorna a engine do SQLAlchemy com base no arquivo banco.ini.
        Usa o driver correto para cada tipo de banco de dados.
        """
        if cls._engine is None:
            if not CONFIG_PATH.is_file():
                logging.critical(f"Arquivo de configuração '{CONFIG_PATH}' não encontrado.")
                raise FileNotFoundError(f"Arquivo de configuração '{CONFIG_PATH}' não encontrado.")

            config = configparser.ConfigParser()
            config.read(CONFIG_PATH)

            if 'database' not in config:
                raise KeyError("A seção [database] não foi encontrada no arquivo banco.ini")

            db_config = config['database']
            db_type = db_config.get('type', 'sqlite').lower()
            connection_url = None

            logging.info(f"Tentando configurar conexão para o banco: '{db_type}'")

            try:
                if db_type == 'sqlite':
                    db_path = project_root / db_config.get('path', 'sistema.db')
                    connection_url = f"sqlite:///{db_path}"
                else:
                    user = db_config['user']
                    password = db_config['password']
                    host = db_config['host']
                    dbname = db_config['dbname']

                    if db_type == 'postgresql':
                        port = db_config.get('port', '5432')
                        connection_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

                    elif db_type == 'mysql':
                        port = db_config.get('port', '3306')
                        connection_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"

                    elif db_type == 'sqlserver':
                        port = db_config.get('port', '1433')
                        connection_url = f"mssql+pymssql://{user}:{password}@{host}:{port}/{dbname}"

                    elif db_type == 'oracle':
                        port = db_config.get('port', '1521')
                        # O dialeto oracle+oracledb é o mais moderno para Oracle
                        dsn = f"{host}:{port}/{dbname}"
                        connection_url = f"oracle+oracledb://{user}:{password}@{dsn}"

                    elif db_type == 'mariadb':
                        port = db_config.get('port', '3306')
                        # MariaDB usa um dialeto específico, mas a conexão é similar ao MySQL
                        connection_url = f"mariadb+mariadbconnector://{user}:{password}@{host}:{port}/{dbname}"

                    else:
                        raise ValueError(f"Tipo de banco de dados não suportado: '{db_type}'")

                cls._engine = create_engine(connection_url, echo=False)

                with cls._engine.connect() as connection:
                    logging.info(f"Conexão com '{db_type}' estabelecida com sucesso.")

            except ImportError as e:
                logging.error(f"Driver Python para '{db_type}' não encontrado. SQLAlchemy não pode conectar.")
                logging.error(f"Detalhe do erro: {e}")
                raise ModuleNotFoundError(
                    f"Para usar '{db_type}', instale a biblioteca necessária. "
                    f"Consulte a tabela de drivers no código para o comando 'pip install'."
                ) from e
            except (OperationalError, SQLAlchemyError) as e:
                logging.error(f"Erro ao conectar ao banco de dados '{db_type}': {e}")
                raise ConnectionError(
                    f"Não foi possível conectar ao banco '{db_type}'. "
                    "Verifique o servidor, firewall e credenciais no banco.ini."
                ) from e
            except KeyError as e:
                logging.error(f"Chave de configuração faltando no banco.ini para '{db_type}': {e}")
                raise KeyError(f"Parâmetro '{e}' faltando no banco.ini para a conexão '{db_type}'.") from e

        return cls._engine

    @classmethod
    def initialize_database(cls):
        # Este método não precisa ser alterado, pois ele já opera de forma
        # agnóstica ao banco de dados, usando a 'engine' criada acima.
        engine = cls.get_engine()
        if not engine:
            logging.error("Não foi possível inicializar o banco: engine não disponível.")
            return

        # Para bancos de dados remotos, não podemos checar o tamanho do arquivo,
        # então pulamos a verificação para qualquer tipo diferente de 'sqlite'.
        if engine.url.drivername != 'sqlite':
            logging.info("Verificação de inicialização pulada para banco de dados remoto.")
            # Em um cenário real, poderíamos checar a existência da tabela 'Usuarios' aqui.
            return

        db_path = project_root / "sistema.db"
        if db_path.exists() and db_path.stat().st_size > 0:
            logging.info("Banco de dados SQLite já parece estar inicializado.")
            return

        if not SCHEMA_PATH.is_file():
            logging.error(f"Arquivo de schema '{SCHEMA_PATH}' não encontrado.")
            raise FileNotFoundError(f"Arquivo de schema não encontrado em {SCHEMA_PATH}")

        logging.info(f"Inicializando banco de dados a partir de '{SCHEMA_PATH}'...")
        try:
            schema_sql = SCHEMA_PATH.read_text(encoding='utf-8')
            with engine.connect() as conn:
                for command in schema_sql.split(';'):
                    if command.strip():
                        conn.execute(text(command))
                conn.commit()
            logging.info("Banco de dados inicializado com sucesso a partir do script SQL.")
        except Exception as e:
            logging.error(f"Erro ao executar o script de inicialização do banco: {e}")
            raise