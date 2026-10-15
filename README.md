# NexlifyTTk

Template desktop Python/Tkinter com MVC, autenticação, autorização na camada de dados, temas, instalação assistida e escolha de **um banco por instalação**.

As páginas, os menus e o acesso aos dados seguem o perfil do usuário. Veja a [matriz de permissões e como cadastrar novas páginas](docs/ACESSOS.md).

As melhorias de estrutura e ferramentas do Measurement Demonstrator foram adaptadas para este projeto. Os módulos de medição, câmera, calibração e IA não fazem parte do template. Veja o [mapa das evoluções](docs/EVOLUCOES.md).

## Documentação

| Para quem | Guia |
| --- | --- |
| Usuários e administradores de contas | [Uso do sistema](docs/GUIA_USUARIO.md) e [permissões por perfil](docs/ACESSOS.md) |
| Responsáveis pela instalação | [Windows/Linux](docs/MULTIPLATAFORMA.md), [bancos](docs/BANCOS.md) e [e-mail/SMTP](docs/EMAIL.md) |
| Responsáveis pela operação e segurança | [Operação segura](docs/SEGURANCA_OPERACAO.md) e [relatório de segurança](docs/SEGURANCA.md) |
| Desenvolvedores | [Arquitetura, extensão e testes](docs/DESENVOLVIMENTO.md) |

O [índice completo](docs/README.md) organiza os documentos. Dentro do aplicativo, **Guia de Configuração** apresenta um resumo de instalação, acesso e uso.

## Instalar

Requisitos: Python **3.11 ou superior**, pip, Tkinter e sessão gráfica para usar a aplicação. Instalação e testes de interface executados em **Windows e Ubuntu Linux (WSL2/Xvfb)** com Python 3.14. Veja os [ambientes validados e requisitos por sistema](docs/MULTIPLATAFORMA.md).

**Windows:**

```powershell
.\instalacao\setup.bat
```

**Linux:**

```bash
# Pré-requisitos no Ubuntu/Debian (uma vez):
sudo apt update
sudo apt install python3 python3-venv python3-tk
bash instalacao/setup.sh
```

O assistente cria/reutiliza `.venv`, instala as dependências e o driver escolhido, verifica os pacotes e abre a configuração do banco. Não apaga ambientes existentes. Na janela do banco, informe a conexão e escolha **Testar e salvar configuração**. O schema é criado sem apagar dados. Bancos externos precisam ter servidor, banco vazio e permissões preparados previamente.

| Perfil | Recursos |
| --- | --- |
| Operação (`core`) | Aplicação, temas, informações do computador e diagnóstico. Login e logs obrigatórios. |
| Desenvolvimento (`dev`) | Inclui pytest, pip-audit, central de testes, monitor e ferramentas locais de manutenção. |

Esses são perfis de **instalação**. As páginas e ferramentas disponíveis também dependem do perfil do **usuário**: instalar o perfil `dev` não transforma operadores em administradores. As ferramentas DEV da interface exigem Administrador Global, `environment = development`, instalação `dev` e modo local/servidor.

Instalação por terminal, sem assistente:

```powershell
python instalacao/install.py --headless --profile dev --database sqlite
```

No Linux, use `python3`. Para um banco externo, o comando instala o driver; complete os dados com `.venv/bin/python instalacao/config_banco_gui.py` ou `.\.venv\Scripts\python.exe instalacao\config_banco_gui.py`. O modo headless não inventa credenciais nem altera a conexão ativa.

## Iniciar

```powershell
.\iniciar.bat
```

```bash
bash iniciar.sh
```

Também existem `iniciar.ps1` (Windows PowerShell ou PowerShell 7) e o alias `inciciar.bat`, preservado por compatibilidade. O script PowerShell seleciona a `.venv` nativa do sistema; no Linux, prefira `iniciar.sh`. Os scripts usam o Python da `.venv` do próprio projeto, mesmo chamados de outra pasta ou em caminhos com espaços e acentos. No Linux, pode-se usar `chmod +x iniciar.sh` e depois `./iniciar.sh`.

Ambientes virtuais não são portáveis entre sistemas: crie uma `.venv` própria em cada máquina. Instalação manual continua disponível:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Primeiro acesso e recuperação em desenvolvimento

Um banco vazio solicita a criação da senha do usuário `admin` no primeiro início. **Não existe senha padrão.** Use uma frase-senha com pelo menos 15 caracteres e até 1024 bytes UTF-8. Novas senhas usam Argon2id. O MFA usa código de seis dígitos por e-mail e vem **desabilitado por padrão**, inclusive em produção. Para ativar, configure SMTP e `mfa_enabled = True`; veja [MFA por e-mail](docs/SEGURANCA_OPERACAO.md#mfa-senhas-e-reautenticação).

No banco herdado, usuários com o hash compartilhado publicado no template antigo não podem mais entrar. Seus registros são preservados. Para recuperar `admin` nesta instalação de desenvolvimento:

```powershell
.\reset_admin.bat
```

```bash
bash reset_admin.sh
```

Defina a senha na janela, entre no sistema e faça a troca obrigatória solicitada. O reset exige simultaneamente o perfil **Desenvolvimento** e `environment = development`; não há botão de reset na aplicação. Depois, redefina as senhas das demais contas em Gestão de Usuários ou remova as contas de exemplo desnecessárias. A alteração de uma senha revoga as sessões anteriores.

Em produção, use um procedimento de recuperação controlado pelo responsável pelo banco, com auditoria e acesso restrito. Não habilite o perfil de desenvolvimento apenas para disponibilizar essa ferramenta aos operadores.

Sessões expiram após 15 minutos sem interação ou 8 horas desde o login. Mudanças de senha/perfil exigem nova autenticação. Os limites `session_idle_seconds` e `session_max_seconds` podem ser ajustados em `config.local.ini`, dentro das faixas validadas. Desabilitar login também exige perfil explícito `dev`. A troca da senha atual está sujeita ao bloqueio persistente de tentativas.

## Páginas e perfis de acesso

O Administrador Global atribui um dos sete perfis em **Gestão de Usuários → Perfil de Acesso**. A [matriz completa](docs/ACESSOS.md) define quais páginas cada perfil pode abrir e quais dados pode alterar. A atribuição usa as contas existentes, sem migração adicional do banco.

- Gestão de Usuários é exclusiva do Administrador Global.
- Cadastro de Vegetais é permitido a Administrador, Diretor de Operações, Gerente de TI e Analista de Dados.
- Supervisor e Operador acessam Gestão de Espécies e o Guia de Configuração.
- Auditor Externo consulta espécies e Vegetais e Auditoria, sem ações de gravação.
- Painel Modelo e ferramentas DEV ficam restritos ao administrador nas condições de desenvolvimento descritas acima.

Menus ocultam páginas não autorizadas; a abertura direta, páginas já carregadas, repositório e API também validam permissões. Páginas sem regra explícita são negadas. Mudanças de perfil revogam a sessão e exigem novo login. No modo cliente, atualize cliente e servidor juntos para disponibilizar a validação `pages/authorize`.

## Bancos e arquivos locais

SQLite, PostgreSQL, MySQL, MariaDB, SQL Server, Oracle e Firebird compartilham o schema SQLAlchemy. Veja [configuração e homologação dos bancos](docs/BANCOS.md) para drivers, TLS e requisitos externos.

| Arquivo | Uso |
| --- | --- |
| `banco.ini` | Padrão público SQLite, sem credenciais. |
| `banco.local.ini` | Conexão local salva pelo configurador; ignorada pelo Git. |
| `config_settings.ini` / `config.local.ini` | Padrões e sobrescritas locais. O instalador escreve apenas o arquivo local. |
| `.runtime/installation.json` | Perfil local explícito; instalar pytest não habilita ferramentas de desenvolvimento. |
| `.secrets/secret.key` | Chave local criada quando necessária; nunca versionada. |
| `.secrets/email.json` | Configuração SMTP com credenciais criptografadas; exclusiva da instalação local/servidor. |
| `settings.json` | Tema, fontes e geometria, com gravação atômica. Não contém senhas. |
| `logs/app.log` | Logs com rotação: 2 MB por arquivo, cinco cópias. |

Variáveis opcionais: `NEXLIFY_DATABASE_URL` substitui a conexão em tempo de execução; `NEXLIFY_SECRET_KEY` fornece a chave Fernet por um canal externo; `NEXLIFY_ENV` define `production` ou `development`. Proteja essas variáveis e não coloque senhas na linha de comando. O configurador testa seus campos explicitamente, mesmo se houver URL de ambiente definida.

## Estrutura e extensão

```text
run.py                         splash, inicialização e diagnóstico
app.py / theme.py              navegação, temas e janela principal
panels/                       registro lazy + exemplos MVC
dialogs/ / modals/            login, senhas, temas e informações
persistencia/schema.py        schema portável e revisão inicial
persistencia/database.py      configuração, drivers e ciclo de conexão
persistencia/auth.py          login, bloqueio, sessão e permissões
persistencia/access_policy.py política de páginas, perfis e leitura/escrita
persistencia/repository.py    CRUD parametrizado e auditado
persistencia/data_service.py  transações de negócio
persistencia/migrations.py    revisões explícitas do banco (atual: 3)
services/                    API HTTPS, cliente, sessões, e-mail, SSO e auditoria
utils/                        configuração de perfil, ícone e diagnóstico
instalacao/                   assistentes e manutenção
tests/                        regressões funcionais, segurança e GUI
docs/                         guias de uso, desenvolvimento e operação
reset_admin.py                recuperação local exclusiva de dev
```

Para criar um painel, derive de `BasePanel`, separe view/controller e registre módulo, classe, nome e ícone em `panels/__init__.py`. Defina os perfis em `PAGE_RULES`, dentro de `persistencia/access_policy.py`, usando exatamente o `PANEL_NAME`. As antigas listas `ALLOWED_ACCESS` não são usadas. O controlador só será importado quando o painel for aberto e sua construção verifica a sessão. Proteja também as operações no serviço/repositório. O [guia de desenvolvimento](docs/DESENVOLVIMENTO.md) descreve o fluxo completo.

O repositório aceita somente tabelas/colunas conhecidas e exige filtros para UPDATE/DELETE. `execute_query_to_dataframe` recebe uma expressão SQLAlchemy `select`, não SQL textual. Para novas entidades, amplie `schema.py`, a lista de tabelas e a política de autorização, acrescente uma revisão de migração e teste em banco temporário. A revisão 1 adota tabelas legadas; a revisão 2 adiciona MFA, sessões da API, outbox de auditoria e vínculos SSO. A revisão 3 adiciona os endereços e desafios de MFA por e-mail. Migrações futuras exigem revisão explícita e restauração validada.

As consultas genéricas aceitam um subconjunto validado de expressões: tabelas originais do schema, joins, aliases, subconsultas e agregações permitidas. SQL textual/literal, funções arbitrárias, hints e CTEs de escrita são recusados; hashes de senha nunca são retornados. Colunas calculadas novas precisam de revisão explícita da política. Filtros e valores de CRUD devem ser escalares, nunca expressões SQLAlchemy.

A interface permite temas, fontes, posição da janela, informações da máquina e diagnóstico. Um `ico.png` opcional na raiz personaliza o ícone de todas as janelas. A restauração visual preserva banco e perfil. A recriação do SQLite fica nas ferramentas de desenvolvimento e exige confirmação textual e backup verificado.

Informações da máquina e diagnóstico são permitidos ao Administrador e ao Gerente de TI. SMTP é exclusivo do Administrador na aplicação local/servidor. Temas e preferências ficam disponíveis aos perfis autenticados quando o menu de temas está habilitado.

## Validar

No Windows:

```powershell
.\.venv\Scripts\python.exe run.py --diagnose
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pip_audit
.\.venv\Scripts\python.exe -m bandit -r app.py run.py reset_admin.py config.py settings_manager.py theme.py persistencia instalacao utils dialogs modals panels -ll
```

No Linux, substitua `.\.venv\Scripts\python.exe` por `.venv/bin/python`. Em servidores sem ambiente gráfico, use `pytest -q -m "not gui"`. O teste externo é opcional e exige `NEXLIFY_TEST_DATABASE_URL` para um banco dedicado. Ele cria/remove somente uma tabela com nome aleatório; nunca use uma URL de produção.

Para verificar também a abertura de janelas, execute `iniciar.bat --diagnose --no-db --check-gui` ou `bash iniciar.sh --diagnose --no-db --check-gui`. No Linux sem monitor, instale `xvfb` e `xauth` e rode `xvfb-run -a .venv/bin/python -m pytest -q`. No repositório, `.github/workflows/platforms.yml` configura testes nos dois sistemas com Python 3.11 e 3.14; sua execução remota depende do envio ao GitHub com Actions habilitado.

O [relatório de segurança](docs/SEGURANCA.md) descreve correções, evidências, limitações e as ações que ainda cabem ao responsável pela instalação.

Última execução completa, após o controle de páginas em **15/10/2026**: **273 testes aprovados e 2 pulados no Windows; 272 aprovados e 1 pulado no Ubuntu/WSL2 com Xvfb**. Inclui 39 novos testes de acesso. Os skips dependem de banco externo ou privilégio de symlink; há um aviso conhecido de depreciação do adaptador HTTP de testes. Esses resultados são da validação do código, não uma nova homologação dos serviços externos durante a revisão documental.

## Segurança implementada e operação centralizada

O template oferece modos local, cliente HTTPS e servidor. O instalador aceita `--mode client --api-url https://api.sua-empresa.example` ou `--mode server`, além de seleção gráfica. Clientes da API não recebem credenciais de banco.

Argon2id, MFA, reautenticação, SSO OIDC, auditoria externa, permissões Windows/Linux, migrações/restauração e distribuição sem ferramentas DEV estão documentados em [SEGURANCA.md](docs/SEGURANCA.md) e [SEGURANCA_OPERACAO.md](docs/SEGURANCA_OPERACAO.md). Dependências transitivas são instaladas a partir de locks com SHA-256.

O scanner encontrou 68 ocorrências de segredos/hashes no histórico antigo; a árvore atual está limpa. As credenciais afetadas precisam ser tratadas como expostas. O workflow não ignora esses achados nem reescreve o histórico automaticamente.


### Envio de e-mail e provedores SMTP

Configure em **Configurações → Envio de e-mail / SMTP** (administrador na aplicação local) ou execute `python -m instalacao.config_email` na máquina do servidor. Para terminal sem interface gráfica: `python -m instalacao.config_email --headless`. Há dez presets — Gmail, Outlook/Hotmail, Yahoo, iCloud, Zoho, AOL, GMX, mail.com, Fastmail e Yandex — e SMTP personalizado. Credenciais criptografadas no servidor, TLS verificado, teste de envio e OAuth2 Microsoft com renovação estão disponíveis. Configurar o SMTP não ativa o MFA. Veja [configuração completa de e-mail](docs/EMAIL.md).
