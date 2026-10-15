"""Um banco por instalação, drivers opcionais e schema comum."""
import configparser
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import create_engine, event, select, inspect
from sqlalchemy.engine import URL, make_url
import config
from utils.paths import PROJECT_ROOT
from .schema import metadata, schema_versions
from .security import decrypt_message
CONFIG_PATH = PROJECT_ROOT / 'banco.local.ini'
LEGACY_CONFIG_PATH = PROJECT_ROOT / 'banco.ini'
DRIVERS = {
    'sqlite': ('sqlite', None),
    'postgresql': ('postgresql+psycopg', 'psycopg[binary]==3.3.6'),
    'mysql': ('mysql+pymysql', 'PyMySQL[rsa]==1.2.3'),
    'mariadb': ('mariadb+pymysql', 'PyMySQL[rsa]==1.2.3'),
    'sqlserver': ('mssql+pyodbc', 'pyodbc==5.3.0'),
    'oracle': ('oracle+oracledb', 'oracledb==4.0.2'),
    'firebird': ('firebird+firebird', 'sqlalchemy-firebird==2.2.0'),
}

# URL overrides receive the same policy as the graphical configurator. Do not
# pass arbitrary DBAPI options (DSNs, init commands, files or TLS bypasses).
URL_QUERY_OPTIONS = {
    'sqlite': set(),
    'postgresql': {'sslmode', 'sslrootcert', 'sslcert', 'sslkey', 'application_name', 'connect_timeout'},
    'mysql': {'charset', 'ssl_ca', 'ssl_cert', 'ssl_key'},
    'mariadb': {'charset', 'ssl_ca', 'ssl_cert', 'ssl_key'},
    'mssql': {'driver', 'Encrypt', 'TrustServerCertificate'},
    'oracle': {'service_name', 'protocol'},
    'firebird': {'charset'},
}


def validate_database_url(url):
    if url.drivername not in {driver for driver, _ in DRIVERS.values()}:
        raise ValueError('Use um dos drivers homologados pelo instalador.')
    backend = url.get_backend_name()
    if set(url.query) - URL_QUERY_OPTIONS[backend] or any(not isinstance(value, str) for value in url.query.values()):
        raise ValueError('Opção de URL não permitida. Use o configurador de banco.')
    if backend == 'mssql':
        if url.query.get('Encrypt', 'yes').lower() != 'yes' or url.query.get('TrustServerCertificate', 'no').lower() != 'no':
            raise ValueError('SQL Server exige TLS e certificado verificado.')
    if backend == 'oracle' and (url.database or not url.query.get('service_name')):
        raise ValueError('Oracle requer service_name explícito; DSNs livres não são aceitos.')
    if backend != 'sqlite':
        import re
        if not url.host or not re.fullmatch(r'[A-Za-z0-9_.:%\\-]+', url.host):
            raise ValueError('Informe um hostname ou endereço IP válido, sem opções de conexão embutidas.')
    return url
def read_database_config(path=None):
    selected = Path(path) if path else CONFIG_PATH if CONFIG_PATH.exists() else LEGACY_CONFIG_PATH
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(selected, encoding='utf-8')
    if parser.has_section('database'):
        result = dict(parser['database'])
    else:
        result = {}
        for section in parser.sections():
            if parser.has_option(section, 'type'):
                if result:
                    raise ValueError('Mantenha somente um banco ativo na configuração.')
                result = dict(parser[section])
    return result or {'type': 'sqlite', 'path': 'NexlifyTTk.db'}
def build_url(options):
    kind = options.get('type', 'sqlite').lower()
    if kind not in DRIVERS:
        raise ValueError('Tipo de banco não suportado.')
    if kind == 'sqlite':
        path = options.get('path', 'NexlifyTTk.db')
        if path != ':memory:':
            path = str((PROJECT_ROOT / path).resolve())
        return URL.create('sqlite', database=path)
    password = options.get('password', '')
    if options.get('password_env'):
        password = os.environ.get(options['password_env'], '')
        if not password:
            raise ValueError('Variável de ambiente da senha não definida.')
    elif password:
        password = decrypt_message(password)
    username = options.get('user', '')
    if username.startswith(('ENC:', 'gAAAA')):
        username = decrypt_message(username)
    if not options.get('host') or not options.get('dbname') or not username:
        raise ValueError('Informe host, dbname e user para o banco selecionado.')
    port = int(options['port']) if options.get('port') else None
    query = {}
    if kind == 'postgresql':
        query['sslmode'] = options.get('sslmode', 'verify-full')
        if options.get('ssl_ca'):
            query['sslrootcert'] = options['ssl_ca']
    elif kind in {'mysql', 'mariadb'}:
        query['charset'] = 'utf8mb4'
    elif kind == 'sqlserver':
        query.update(driver=options.get('odbc_driver', 'ODBC Driver 18 for SQL Server'),
                     Encrypt='yes', TrustServerCertificate='no')
    elif kind == 'oracle':
        query['service_name'] = options['dbname']
    return URL.create(DRIVERS[kind][0], username=username, password=password,
                      host=options['host'], port=port,
                      database=None if kind == 'oracle' else options['dbname'], query=query)
def create_database_engine(options=None, *, provisioning=False):
    explicit_options = options is not None
    options = options if explicit_options else read_database_config()
    url = make_url(os.environ['NEXLIFY_DATABASE_URL']) if not explicit_options and os.environ.get('NEXLIFY_DATABASE_URL') else build_url(options)
    url = validate_database_url(url)
    backend = url.get_backend_name()
    if config.ENVIRONMENT == 'production' and not provisioning and (url.username or '').casefold() in {'root', 'sa', 'sys', 'system', 'postgres', 'sysdba'}:
        raise ValueError('Use uma conta de runtime limitada; contas administrativas não são permitidas.')
    if backend == 'postgresql':
        mode = url.query.get('sslmode', 'verify-full')
        if config.ENVIRONMENT == 'production' and mode != 'verify-full':
            raise ValueError('PostgreSQL em produção requer sslmode=verify-full.')
        url = url.update_query_dict({'sslmode': mode, 'connect_timeout': '10'})
    elif backend == 'mssql':
        url = url.update_query_dict({'driver': url.query.get('driver', 'ODBC Driver 18 for SQL Server'), 'Encrypt': 'yes', 'TrustServerCertificate': 'no'})
    kwargs = {'pool_pre_ping': True, 'hide_parameters': True}
    if url.get_backend_name() == 'sqlite':
        kwargs['connect_args'] = {'timeout': 15}
    elif url.get_backend_name() in {'mysql', 'mariadb'}:
        import ssl
        # PyMySQL's dictionary SSL options disable hostname matching when no
        # CA path is supplied. Pass a verified context with system roots instead.
        context = ssl.create_default_context(cafile=url.query.get('ssl_ca') or options.get('ssl_ca') or None)
        if url.query.get('ssl_cert'):
            context.load_cert_chain(url.query['ssl_cert'], keyfile=url.query.get('ssl_key'))
        kwargs['connect_args'] = {'ssl': context, 'ssl_disabled': False,
                                  'local_infile': False, 'connect_timeout': 10}
    elif backend == 'oracle':
        import ssl
        protocol = url.query.get('protocol', options.get('oracle_protocol', 'tcps'))
        if config.ENVIRONMENT == 'production' and protocol != 'tcps':
            raise ValueError('Oracle em produção requer TCPS.')
        kwargs['connect_args'] = {'protocol': protocol, 'ssl_server_dn_match': True, 'tcp_connect_timeout': 10}
        if protocol == 'tcps':
            kwargs['connect_args']['ssl_context'] = ssl.create_default_context(cafile=options.get('ssl_ca') or None)
    try:
        engine = create_engine(url, **kwargs)
    except ImportError as error:
        raise RuntimeError('Driver ausente. Execute o instalador e selecione o banco desejado.') from error
    if backend == 'firebird':
        @event.listens_for(engine, 'do_connect')
        def firebird_secure_config(dialect, connection_record, arguments, parameters):
            from firebird.driver import driver_config
            selected = driver_config.get_database(parameters.get('database')) or driver_config.db_defaults
            selected.config.value = 'WireCrypt = Required'
            selected.auth_plugin_list.value = 'Srp256'
    if url.get_backend_name() == 'sqlite':
        @event.listens_for(engine, 'connect')
        def sqlite_foreign_keys(connection, _record):
            cursor = connection.cursor()
            cursor.execute('PRAGMA foreign_keys=ON')
            cursor.close()
            if url.database and url.database != ':memory:':
                from utils.secure_files import restrict_permissions
                restrict_permissions(url.database)
    return engine
class DatabaseManager:
    _engine = None
    @classmethod
    def get_engine(cls):
        if config.API_MODE == 'client':
            raise PermissionError('Cliente remoto não pode abrir conexão direta com o banco.')
        if not config.DATABASE_ENABLED:
            return None
        if cls._engine is None:
            cls._engine = create_database_engine()
        return cls._engine
    @classmethod
    def dispose(cls):
        if cls._engine is not None:
            cls._engine.dispose()
            cls._engine = None
    @classmethod
    def initialize_database(cls, engine=None, *, provisioned=False):
        engine = engine or cls.get_engine()
        if engine is None:
            raise RuntimeError('Banco desabilitado.')
        from .migrations import upgrade, current_version, LATEST_VERSION
        if current_version(engine) < LATEST_VERSION and engine.dialect.name != 'sqlite' and config.ENVIRONMENT == 'production' and not provisioned:
            raise PermissionError('Execute a migração explícita com a conta de instalação antes de iniciar o runtime.')
        if current_version(engine) < LATEST_VERSION and engine.dialect.name == 'sqlite':
            database = engine.url.database
            if database and database != ':memory:' and Path(database).is_file():
                from instalacao.backup import create_sqlite_backup
                create_sqlite_backup(Path(database), Path(database).parent / '.runtime' / 'backups')
        version = upgrade(engine)
        logging.getLogger(__name__).info('Schema revision %s pronto (%s).', version, engine.dialect.name)
