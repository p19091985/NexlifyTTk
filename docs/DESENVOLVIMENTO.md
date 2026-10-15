# Desenvolvimento e arquitetura interna

Este guia descreve o código do template. Para instalar, consulte o [README principal](../README.md); para comportamento das contas, use a [matriz de acesso](ACESSOS.md).

## Preparar o ambiente

Na raiz, instale o perfil de desenvolvimento:

```powershell
.\instalacao\setup.bat --headless --profile dev --database sqlite
```

```bash
bash instalacao/setup.sh --headless --profile dev --database sqlite
```

Cada sistema precisa da própria `.venv`. Use uma base de desenvolvimento ou testes, sem apontar para produção. O perfil `dev` instala ferramentas, mas a interface só permite ferramentas DEV ao Administrador Global quando o ambiente é `development`, fora do modo cliente. O reset de administrador também exige desenvolvimento explícito.

## Responsabilidades dos módulos

| Camada | Arquivos principais | Responsabilidade |
| --- | --- | --- |
| Inicialização | `run.py`, `utils/startup_splash.py` | Diagnóstico, banco, splash, primeiro acesso e reinício controlado. |
| Aplicação | `app.py`, `theme.py`, `settings_manager.py` | Janela, menus, navegação, sessão e preferências. |
| Painéis | `panels/__init__.py`, `panels/base_panel.py`, controllers/views | Registro declarativo, importação tardia e widgets MVC. |
| Política | `persistencia/access_policy.py` | Regras de páginas, perfis, condições DEV e permissões de tabelas. |
| Autenticação | `persistencia/auth.py`, `passwords.py`, `mfa.py` | Senhas, sessão validada, bloqueio, autorização e MFA por e-mail. |
| Persistência | `schema.py`, `migrations.py`, `database.py`, `repository.py`, `data_service.py` em `persistencia/` | Schema, revisões, drivers, CRUD autorizado e transações de negócio. |
| Serviços | `services/api.py`, `client.py`, `sessions.py` | RPC HTTPS, token opaco, autorização no servidor e revogação. |
| Integrações | Módulos de e-mail, SSO e auditoria em `services/` | SMTP/OAuth2, OIDC opcional e entrega de eventos. |
| Operação | `instalacao/` | Instalação, configuração, provisionamento, backup e pacotes. |

Tk deve ser manipulado no thread principal. Painéis são instanciados sob demanda; não abra janelas ou conecte ao banco como efeito colateral de importar um controlador.

## Fluxo de autorização

1. O login produz a identidade da sessão. `current_user` na interface é uma cópia para apresentação, não uma fonte de autoridade.
2. `can_access_page` filtra menus usando a política declarada. `_guard_page` consulta `authorize_page` antes da navegação e dos callbacks protegidos.
3. `BasePanel` valida autorização antes de criar widgets. Páginas em cache passam novamente pela guarda ao serem abertas.
4. `authorize_page` usa a sessão validada. No modo cliente, chama o RPC `pages/authorize`; o servidor recebe somente o nome da página, não um perfil escolhido pelo cliente.
5. Repositório e serviços verificam leitura/escrita via `authorize` e `can_access_table`. Escritas revalidam a sessão dentro da transação.

Uma página sem regra explícita é negada. `PageAccessDenied` representa sessão válida sem permissão para a página. Falhas de validação da sessão fecham as janelas protegidas e exigem novo login. Senha provisória e cadastro obrigatório de MFA não permitem acessar páginas de dados.

O campo `read_only` orienta a apresentação do auditor. Esconder formulários não substitui a verificação do repositório/API. Código e banco locais ainda dependem da proteção da conta do sistema operacional; clientes não confiáveis devem usar a API central.

## Criar ou alterar um painel

1. Crie controller e view; derive o controlador de `BasePanel` e defina `PANEL_NAME` e `PANEL_ICON`.
2. Adicione nome, ícone, módulo, classe e visibilidade a `ALL_PANELS` em `panels/__init__.py`.
3. Registre o mesmo nome em `PAGE_RULES`, em `persistencia/access_policy.py`, com perfis explícitos. `development_only` e `local_only` restringem o contexto; `read_only_roles` orienta a view. Listas `ALLOWED_ACCESS` nos controladores não são usadas.
4. Ajuste `can_access_table` para os recursos da página. Se várias páginas compartilham uma tabela, considere os acessos legítimos de todas elas; ações diferentes exigem proteção no serviço correspondente.
5. Use `@protected_page('identificador')` para novos callbacks de janelas no aplicativo. Controllers acessíveis por outros atalhos também precisam validar acesso antes de carregar dados.
6. Utilize o repositório ou serviço autorizado. Não execute SQL diretamente na view nem use valores do formulário como identidade do usuário.
7. Teste perfil permitido, perfil negado, construção direta, leitura/escrita, revogação, sessão expirada e comportamento da API. Atualize a matriz e a ajuda interna.

## Entidades e migrações

A revisão atual é **3**: revisão 1 adota as tabelas legadas e o estado de autenticação; revisão 2 adiciona segurança de usuário, sessões da API, outbox e vínculos SSO; revisão 3 adiciona `email_mfa`. O controle de páginas não acrescenta tabela nem migração.

Para novas entidades, altere `persistencia/schema.py`, registre tabelas e colunas permitidas no repositório, defina a política e crie uma revisão explícita em `persistencia/migrations.py`. Não use `create_all` como substituto de migração de colunas. Teste adoção, atualização, recusa de revisão futura e restauração de backup. Ajuste o gerador de privilégios do banco quando necessário.

`execute_query_to_dataframe` recebe expressões SQLAlchemy permitidas, nunca SQL textual. Filtros e valores de CRUD são escalares. Dados de contas não podem expor hashes. Escritas administrativas mantêm reautenticação e proteção do último administrador. Detalhes de provisionamento: [BANCOS.md](BANCOS.md).

## Testes e diagnóstico

Use o Python da `.venv`. No Windows:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest tests/test_page_access.py tests/test_ui.py -q
.\.venv\Scripts\python.exe run.py --diagnose --no-db --check-gui
```

No Linux:

```bash
.venv/bin/python -m pytest -q
xvfb-run -a .venv/bin/python -m pytest tests/test_page_access.py tests/test_ui.py -q
.venv/bin/python run.py --diagnose --no-db --check-gui
```

O comando normal de GUI precisa de sessão gráfica. Em Linux sem monitor, use Xvfb para a suíte completa também. Para executar somente testes sem GUI, use `-m "not gui"`.

`tests/conftest.py` prepara bancos SQLite temporários e contas isoladas. `test_page_access.py` cobre política, sessão, API e acesso a dados; `test_ui.py` exercita menus e widgets reais, os sete perfis e páginas em cache. A conexão externa exige `NEXLIFY_TEST_DATABASE_URL` apontando para um banco exclusivo de homologação. Não transforme skips de infraestrutura em sucesso de homologação.

Última suíte completa do código: 273 aprovados no Windows e 272 no Ubuntu/WSL2; detalhes e skips em [SEGURANCA.md](SEGURANCA.md). Python 3.11 e 3.14 estão previstos no workflow do repositório, mas execução remota de CI deve ser confirmada separadamente.

## Documentação e distribuição

Ao alterar uma funcionalidade, atualize o README, o guia do usuário, o documento técnico relacionado e, quando aplicável, o texto de `panels/painel_guia_config_view.py`. Alterações de autorização exigem atualização de [ACESSOS.md](ACESSOS.md). Mantenha resultados históricos identificados por etapa; não declare testes ou homologações que não foram executados.

Inclua novos documentos no índice e na lista explícita de `instalacao/package_release.py`, para que os links funcionem nos pacotes. O gerador exclui credenciais, bancos, `.venv`, testes e ferramentas DEV; documentação técnica não concede acesso às ferramentas. Confira integridade com `--verify` e use um nome de arquivo novo, pois pacotes existentes não são sobrescritos. O procedimento de entrega está em [SEGURANCA_OPERACAO.md](SEGURANCA_OPERACAO.md#distribuição-e-ci).
