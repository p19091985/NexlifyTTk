# Windows e Linux

O aplicativo, instalador, configuração de banco e recuperação de administrador usam Python/Tkinter e caminhos relativos à raiz do projeto. Cada instalação seleciona um banco e cria seu próprio ambiente virtual.

## Instalação Windows

Instale Python 3.11 ou superior com pip e Tcl/Tk habilitados e o comando `python` disponível no terminal. Em uma pasta gravável pelo usuário:

```powershell
.\instalacao\setup.bat
.\iniciar.bat
```

Para instalar pelo terminal:

```powershell
.\instalacao\setup.bat --headless --profile dev --database sqlite
.\iniciar.bat --diagnose --no-db --check-gui
```

O alias `inciciar.bat` continua disponível. O `iniciar.ps1` também seleciona o interpretador local.

## Instalação Linux

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-tk
bash instalacao/setup.sh
bash iniciar.sh
```

Em outras distribuições, instale os pacotes equivalentes de Python, venv/pip e Tkinter. Os pacotes de Tkinter devem corresponder à versão do Python utilizada; o pip não instala o Tk do sistema. O instalador identifica módulos ausentes antes de criar a `.venv` e informa como corrigir.

Instalação pelo terminal e diagnóstico:

```bash
bash instalacao/setup.sh --headless --profile dev --database sqlite
bash iniciar.sh --diagnose --no-db --check-gui
```

A interface precisa de uma sessão gráfica. Tk no Linux usa X11; em desktops Wayland, disponibilize XWayland. Em WSL, use WSLg ou um servidor X. `--headless` permite instalar sem abrir janelas; não transforma o aplicativo desktop em serviço web.

Para testes gráficos em máquinas sem monitor:

```bash
sudo apt install xvfb xauth
xvfb-run -a .venv/bin/python -m pytest -q
```

## Bancos e arquivos

- SQLite funciona sem serviço externo nos dois sistemas.
- Os drivers Python de PostgreSQL, MySQL/MariaDB, SQL Server, Oracle e Firebird são selecionados pelo mesmo instalador nos dois sistemas.
- SQL Server requer Microsoft ODBC Driver 18 para o sistema operacional correspondente; no Linux também é necessário o gerenciador unixODBC (`libodbc.so.2`). Instalar apenas `pyodbc` não instala o driver da Microsoft.
- Firebird precisa da biblioteca cliente nativa correspondente ao sistema/arquitetura. Oracle usa o modo Thin, sem exigir Instant Client nessa configuração.
- As conexões reais com servidores externos precisam da [homologação de banco e TLS](BANCOS.md).
- Não copie `.venv` entre Windows e Linux. Use cópias separadas do projeto; preserve backups antes de substituir um ambiente antigo. O instalador recusa reaproveitar uma `.venv` de outro sistema.
- Reconfigure caminhos absolutos de banco e certificados ao mudar de máquina. Um caminho como `D:\dados\app.db` não representa o mesmo arquivo no Linux. SQLite relativo ao projeto é resolvido sem depender da pasta atual do terminal.
- Guarde o projeto em uma pasta gravável pelo usuário e proteja banco, configurações e segredos. Não execute a aplicação com `sudo` ou como administrador apenas para contornar permissões.

## Resultado completo mais recente — 15/10/2026

Após o controle de acesso por perfil: **273 aprovados e 2 pulados no Windows; 272 aprovados e 1 pulado no Ubuntu/WSL2 com Xvfb**. Não houve falhas. São 39 novos testes sobre a etapa anterior; os skips dependem de banco externo e de privilégio de symlink no Windows. Detalhes em [SEGURANCA.md](SEGURANCA.md).

As seções abaixo registram etapas anteriores e seus ambientes, sem substituir o resultado mais recente. A revisão de documentação não representa uma nova execução de toda a suíte ou homologação de serviços externos.

## Histórico: validação inicial em 15/10/2026

| Ambiente | Resultado |
| --- | --- |
| Windows, Python 3.14.6 | 138 testes aprovados, 2 pulados |
| Ubuntu 26.04.1 x86_64, WSL2, Python 3.14.4, Tk 8.6/Xvfb | 137 testes aprovados, 1 pulado |

Há dois testes adicionais de scripts Windows. O teste de servidor externo é pulado nos dois sistemas; o teste de criação de link simbólico exige privilégio ausente neste Windows e passou no Linux. A suíte exercita SQLite real, segurança, autenticação, autorização, transações, temas, os seis painéis e splash/primeiro acesso. Os scripts são executados a partir de outra pasta, em um projeto temporário com espaços e acentos, verificando argumentos, `.venv` e código de saída.

No Ubuntu, o instalador criou uma `.venv` nova em uma cópia isolada. Todos os drivers opcionais foram instalados e seus schemas compilados. `pip check`, diagnóstico com janela Tk e auditoria de dependências passaram. Nenhum banco local do usuário foi copiado ou alterado para esses testes.

O workflow de CI em `.github/workflows/platforms.yml`, disponível no repositório de desenvolvimento, prepara Windows e Ubuntu com Python 3.11 e 3.14, instala o perfil de desenvolvimento e os drivers de teste e executa a suíte, incluindo GUI com Xvfb no Linux. O arquivo foi preparado localmente; ainda não foi executado no GitHub. Configuração das actions: [checkout](https://github.com/actions/checkout) e [setup-python](https://github.com/actions/setup-python).

A execução Linux foi em WSL2 com Xvfb. Outras distribuições, arquiteturas e gerenciadores de janelas não foram ensaiados nesta máquina; valide-os antes da distribuição. A validação dos drivers não substitui testes de conexão com cada servidor externo.

## Verificação após implementação do relatório de segurança

Em 15/10/2026: 166 testes aprovados no Windows e 165 no Ubuntu/WSL2, incluindo GUI MFA, cliente/servidor HTTPS real, SSO/PKCE simulado, arquivos privados, backups e pacotes. Instalação limpa do pacote de servidor e migração SQLite executadas nos dois sistemas. Windows pula symlink sem privilégio; ambos pulam servidor de banco externo não configurado. O workflow remoto não foi executado. Detalhes em [SEGURANCA.md](SEGURANCA.md).


## MFA por e-mail

Validação da alteração em 15/10/2026: **194 testes aprovados no Windows e 193 no Ubuntu/WSL2**, incluindo GUI, confirmação por e-mail, recuperação durante indisponibilidade SMTP e importação dos pacotes local/cliente/servidor em caminho com espaços. Dois testes foram pulados no Windows (banco externo e privilégio de symlink) e um no Linux (banco externo). SMTP usa apenas a biblioteca padrão do Python com TLS verificado; a entrega foi simulada nos testes. A funcionalidade vem desligada nas configurações e nos pacotes. Configuração: [guia operacional](SEGURANCA_OPERACAO.md#mfa-senhas-e-reautenticação).


## Provedores SMTP e configuração no servidor

A configuração por interface e terminal, os dez presets SMTP e o modo personalizado passaram pela suíte de **234 testes no Windows e 233 no Linux**, em 15/10/2026. Os testes incluem TLS, credenciais criptografadas, renovação OAuth2, telas Tk e bloqueio de configuração entre processos nos dois sistemas. Não houve autenticação em contas reais dos provedores. Consulte [EMAIL.md](EMAIL.md) para configuração, exigências e homologação da conta.

### Controle de acesso por perfil

Em 15/10/2026, a suíte com autorização de páginas passou com **273 testes no Windows e 272 no Ubuntu/WSL2 com Xvfb**, incluindo 39 novos testes. A mesma política é usada nos dois sistemas, sem dependências novas. Menus, abertura direta, revogação de sessão e consulta do auditor foram exercitados com os sete perfis. Mantidos os skips de banco externo e de symlink sem privilégio no Windows. Consulte a [matriz de acesso](ACESSOS.md).
