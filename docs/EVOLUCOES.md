# Evoluções incorporadas

Escopo confirmado: estrutura e ferramentas do Measurement Demonstrator, mantendo o NexlifyTTk como template. Referência adicional: fluxo gráfico de definição de senha em `AI-Residency-PPE-Detector-V.2/componentes_auxiliares/operacao`.

| Capacidade da referência | Implementação no template |
| --- | --- |
| Shell desktop com barra superior, sidebar adaptativa e seleção ativa | `app.py`, conservando login e papéis do NexlifyTTk. |
| Temas centralizados, contraste, estilos ttk e escala DPI | `theme.py`, `modals/theme_selector.py`; mudança seguida de reinício controlado e novo login. |
| Preferências de fontes e cores | Integração do diálogo avançado existente com o novo shell. |
| Registro declarativo e importação tardia dos painéis | `panels/__init__.py`; os seis exemplos atuais foram preservados. |
| Controle de páginas por perfil | `persistencia/access_policy.py`, guardas na navegação e no `BasePanel`, autorização de dados e RPC no servidor. Painel Modelo restrito ao administrador em DEV. |
| Splash e carregamento inicial sem congelar a janela | `utils/startup_splash.py`, bootstrap em worker, Tk no thread principal. |
| Geometria da janela, múltiplos monitores e ajuste ao conteúdo | Métodos de captura/restauração do shell, corrigindo coordenadas negativas. |
| Tooltip, comportamento modal e ícone compartilhado | `utils/ui_components.py`, `modals/dialog_utils.py`, `utils/window_icon.py`. O ícone institucional não foi copiado. |
| Cache de preferências e merge profundo | `settings_manager.py`; acrescentadas gravação atômica e preservação de JSON inválido. |
| Relatório de CPU, RAM, discos e GPU | `utils/system_report.py`, diálogo com copiar/atualizar. Removidas as dependências de câmeras. |
| Instalação por perfil com progresso e diagnóstico | `instalacao/install.py`, perfis Operação/Desenvolvimento, GUI e CLI. Reutiliza a venv sem apagá-la. |
| Informações do perfil ativo e capacidades | `.runtime/installation.json`, `utils/installation_profile.py`, diálogo de perfil. Sem inferir autorização a partir de pacotes instalados. |
| Configuradores, monitor e manutenção local | Configuração de ambiente/banco, monitor somente leitura, limpeza explícita de logs e recriação SQLite com backup. |
| Central de testes e diagnóstico pós-instalação | Execução em processo separado com saída na interface; CLI `--diagnose`. |
| Logs com buffer de linhas | Logger adaptado e ampliado com rotação de arquivo. |
| Testes de temas, preferências, interface e persistência | Testes portados quando genéricos e novos testes para segurança, schema, instalador e CRUD. |

O perfil experimental de IA, download de modelos, registro de calibrações, medição, câmeras, tabuleiros e relatórios de medição foram excluídos conforme o escopo confirmado. Os exemplos de vegetais, auditoria, espécies e usuários continuam disponíveis.

## Melhorias adicionais solicitadas

- Escolha de SQLite, PostgreSQL, MySQL, MariaDB, SQL Server, Oracle ou Firebird por instalação.
- Drivers opcionais instalados pelo assistente; teste de conexão antes de salvar credenciais.
- Schema SQLAlchemy comum, revisão inicial e adoção não destrutiva do banco antigo.
- Criação inicial de administrador sem senha padrão e reset exclusivo de desenvolvimento na raiz.
- Autorização nas operações de dados, proteção do último administrador, auditoria de CRUD e bloqueio persistente de login.
- Remoção da chave versionada e das senhas compartilhadas dos scripts de instalação.
- Modos local, cliente HTTPS e servidor, com tokens opacos e validação de permissões no servidor.
- MFA por e-mail, desligado por padrão, com recuperação e SMTP configurável: dez presets e servidor personalizado.
- Matriz dos sete perfis, consulta do auditor, bloqueio de páginas desconhecidas e revalidação de páginas em cache.
- Migrações até a revisão 3, locks de dependências, pacotes sem segredos e guias de uso/desenvolvimento.

## Compatibilidade e limites

As APIs dos controladores de exemplo continuam usando `GenericRepository`. Consultas genéricas de extensões devem usar expressões `select` do SQLAlchemy. A gestão de usuários ficou exclusiva do Administrador Global para impedir elevação de privilégios pelo Gerente de TI. Consultas e alterações passam por autorização, mesmo se chamadas fora do menu.

O template oferece aplicação desktop local e cliente de API HTTPS central. No modo cliente, a aplicação não recebe credenciais do banco; autorização e persistência ficam no servidor. No modo local, o perfil de desenvolvimento e os controles Python não defendem contra alguém com permissão para editar código, banco SQLite ou arquivos locais. A configuração centralizada está descrita em [SEGURANCA_OPERACAO.md](SEGURANCA_OPERACAO.md).

As antigas listas `ALLOWED_ACCESS` dos controladores foram substituídas pela política central de páginas e dados. A extensão do template está em [DESENVOLVIMENTO.md](DESENVOLVIMENTO.md), e as permissões atuais em [ACESSOS.md](ACESSOS.md). A última suíte completa após essa alteração aprovou 273 testes no Windows e 272 no Linux, incluindo 39 novos testes de autorização e interface; os resultados anteriores representam etapas da implementação.

As validações e riscos restantes estão em [SEGURANCA.md](SEGURANCA.md). Os servidores externos exigem a [homologação descrita em BANCOS.md](BANCOS.md).
