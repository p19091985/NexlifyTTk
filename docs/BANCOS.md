# Banco por instalação

A seleção é feita no instalador e confirmada em `instalacao/config_banco_gui.py`. O instalador prepara o driver Python; não instala serviços de banco nem cria instâncias administrativas. O configurador testa a conexão antes de substituir `banco.local.ini` e pode criar as tabelas. Trocar a configuração não transfere dados entre servidores; migração de dados deve ser planejada e validada separadamente.

| Tipo | Driver instalado | Preparação externa |
| --- | --- | --- |
| SQLite | sqlite3 do Python | Nenhuma. Arquivo local relativo à raiz ou caminho absoluto explícito. |
| PostgreSQL | psycopg[binary] 3.3.6 | Banco e usuário; TLS e CA confiável. `sslmode=verify-full` obrigatório em produção. |
| MySQL | PyMySQL[rsa] 1.2.3 | Banco/usuário, charset utf8mb4 e TLS com certificado válido. |
| MariaDB | PyMySQL[rsa] 1.2.3 | Banco/usuário e TLS; protocolo compatível MySQL, dialeto MariaDB. |
| SQL Server | pyodbc 5.3.0 | Microsoft ODBC Driver 18 instalado no sistema, banco/usuário e certificado confiável. |
| Oracle | python-oracledb 4.0.2 | Serviço Oracle; modo Thin; TCPS obrigatório em produção. Campo de banco representa `service_name`. |
| Firebird | sqlalchemy-firebird 2.2.0 + firebird-driver | Firebird 4+ como alvo de homologação, banco existente e biblioteca cliente Firebird (`fbclient`). |

SQL Server usa `Encrypt=yes` e `TrustServerCertificate=no`. MySQL/MariaDB verificam certificado e identidade do servidor. Oracle usa contexto TLS com verificação de identidade; uma CA privada pode ser indicada no configurador. Não desative essas verificações para corrigir um certificado mal configurado. Em Firebird, o cliente exige `WireCrypt = Required` e `Srp256`; configure também o servidor e restrinja a rede: a negociação de criptografia desse protocolo precisa ser comprovada na homologação. [Orientação OWASP para proteção do banco](https://cheatsheetseries.owasp.org/cheatsheets/Database_Security_Cheat_Sheet.html).

Requisitos e comportamento de cada dialeto dependem do servidor e do driver. Consulte a [documentação SQLAlchemy](https://docs.sqlalchemy.org/en/20/dialects/) e, para Oracle, a [configuração python-oracledb](https://docs.sqlalchemy.org/en/20/dialects/oracle.html#module-sqlalchemy.dialects.oracle.oracledb).

## Credenciais

O configurador criptografa a senha informada com uma chave exclusiva em `.secrets/secret.key`. Alternativamente, informe o **nome** de uma variável de ambiente em `password_env`; o arquivo não conterá a senha. Não é aceito texto puro no campo `password` de `banco.local.ini`.

Exemplo público sem segredos:

```ini
[database]
type = postgresql
host = db.exemplo.local
port = 5432
dbname = nexlify
user = nexlify_app
password_env = NEXLIFY_DB_PASSWORD
sslmode = verify-full
```

Configure `NEXLIFY_DB_PASSWORD` no ambiente por um mecanismo seguro do sistema, não pelo histórico do terminal. Para CAs privadas, preencha `ssl_ca` com o caminho explícito do certificado. A criptografia do arquivo não impede acesso por quem também controla a chave ou executa código com a mesma conta do sistema.

## Schema e permissões

`NEXLIFY_DATABASE_URL` aceita somente os drivers da tabela acima e opções permitidas. DSNs livres (`odbc_connect` e aliases Oracle), `ssl_disabled`, `local_infile`, comandos de inicialização e opções desconhecidas são recusados. Para Oracle, use host/porta e `service_name`; para SQL Server, `Encrypt=yes` e `TrustServerCertificate=no` também são obrigatórios pela URL.

MySQL/MariaDB recebem contexto TLS explícito, com verificação de hostname inclusive ao usar CAs do sistema. Corrija certificados não confiáveis ou emitidos para outro servidor; não há fallback para conexão sem TLS.

`DatabaseManager.initialize_database()` cria tabelas ausentes, verifica colunas esperadas e aplica as revisões explícitas até a revisão **3**, que acrescenta `email_mfa`. Não executa DROP, não cria contas com senha fixa e recusa revisões mais novas. As tabelas legadas são preservadas. Novas mudanças de coluna exigem migração explícita com backup e ensaio; `create_all` não substitui esse processo.

O perfil do usuário da aplicação é independente da conta de conexão ao banco. A política de páginas e leitura/escrita é validada pelo repositório e pela API; permissões de banco complementam essa proteção. A implementação de acesso às páginas usa os perfis já existentes, sem acrescentar tabelas. Consulte [ACESSOS.md](ACESSOS.md). No modo cliente HTTPS, a conexão ao banco pertence ao servidor.

Prepare o schema com uma credencial de instalação, depois configure uma conta de runtime com os privilégios mínimos e desligue `initialize_database_on_startup` em `config.local.ini`. Prefira separar privilégios de DDL, DML e auditoria. A conta normal da aplicação não precisa conceder privilégios nem administrar o servidor. [Princípio do menor privilégio no banco](https://cheatsheetseries.owasp.org/cheatsheets/Database_Security_Cheat_Sheet.html).

## Validação realizada e pendente

Foram exercitados SQLite real, preservação do banco legado, autenticação, CRUD, chaves estrangeiras, transações e rollback. Os sete drivers foram instalados e os schemas compilados para seus dialetos; a compilação offline Firebird declara versão 4, pois sem conexão não há descoberta da versão do servidor.

**Não houve conexão real com PostgreSQL, MySQL, MariaDB, SQL Server, Oracle ou Firebird nesta máquina.** Certificados, autenticação do servidor, bibliotecas nativas e diferenças de collation/permissões devem ser homologados antes de uso real.

Para o ensaio externo, prepare um banco exclusivo de teste, forneça `NEXLIFY_TEST_DATABASE_URL` por ambiente e execute:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_external_database.py
```

No Linux, use `.venv/bin/python`. O ensaio cria uma tabela `nexlify_test_<aleatório>`, verifica identidade automática, insert/select/update/delete e rollback, e remove somente essa tabela ao terminar. Depois, teste também a aplicação completa com o configurador apontando para uma instalação de homologação.

## Backup e recuperação

O banco local anterior à evolução foi copiado e verificado em `.venv/backup-before-evolution/NexlifyTTk.db`. Há nesse diretório uma cópia da configuração e da chave antiga para recuperação: trate todo o diretório como confidencial.

O utilitário `instalacao/resetar_banco_de_dados.py` exige ambiente/perfil de desenvolvimento, SQLite dentro do projeto e confirmação `RECRIAR`. Ele verifica um backup em `.runtime/backups` antes de apagar as tabelas conhecidas e iniciar um banco vazio. Feche todas as instâncias antes de usá-lo. O assistente não remove tabelas externas ao schema do template.

Para servidores externos, use a ferramenta nativa do fornecedor e teste a restauração em outra instância. Não há backup remoto automático neste template.

## Provisionamento seguro

Use `python -m instalacao.provision migrate` com conta de instalação e depois uma conta limitada no runtime. Migração externa em produção não é executada automaticamente pela aplicação. Gere GRANTs para revisão pelo DBA com `python -m instalacao.db_permissions --database postgresql --user nexlify_app --schema public` (ajuste o dialeto). Concessões anteriores precisam ser removidas pelo DBA.

A revisão 2 acrescenta `user_security`, `api_sessions`, `audit_outbox` e `external_identities`; a revisão 3 adiciona os endereços e desafios de MFA por e-mail em `email_mfa`. Backup/ensaio SQLite: `python -m instalacao.backup`; para bancos externos, use ferramentas nativas e forneça a evidência de restauração ao provisionamento. Veja [SEGURANCA_OPERACAO.md](SEGURANCA_OPERACAO.md).
