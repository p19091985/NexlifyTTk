# Acesso às páginas por perfil

As permissões são definidas em `persistencia/access_policy.py`. A escolha do perfil continua em **Gestão de Usuários → Perfil de Acesso**, disponível somente ao Administrador Global. Não é necessário migrar o banco nem alterar os usuários existentes.

## Matriz padrão

**Editar** permite consultar e alterar dados; **Consultar** não permite gravações; **Acessar** é uma página informativa; **—** significa acesso negado.

| Perfil | Cadastro de Vegetais | Espécies (Gatos) | Gestão de Usuários | Guia de Configuração | Vegetais e Auditoria | Painel Modelo |
| --- | --- | --- | --- | --- | --- | --- |
| Administrador Global | Editar | Editar | Editar | Acessar | Editar | DEV |
| Diretor de Operações | Editar | Editar | — | Acessar | Editar | — |
| Gerente de TI | Editar | Editar | — | Acessar | Editar | — |
| Supervisor de Produção | — | Editar | — | Acessar | — | — |
| Operador de Linha | — | Editar | — | Acessar | — | — |
| Analista de Dados | Editar | Editar | — | Acessar | Editar | — |
| Auditor Externo | — | Consultar | — | Acessar | Consultar | — |

Os quatro perfis que já tinham acesso ao cadastro de vegetais mantêm esse acesso. Supervisor e operador continuam com a página de espécies. O auditor passa a consultar também Vegetais e Auditoria. Nenhum perfil pode alterar ou excluir eventos de auditoria pelo CRUD: eventos são registrados internamente nas transações.

| Configuração ou ferramenta | Perfis permitidos |
| --- | --- |
| Tipos de vegetais, inclusive atalhos nos painéis | Administrador, Diretor, Gerente de TI e Analista |
| Envio de e-mail / SMTP | Administrador, em instalação local/servidor |
| Informações do computador e diagnóstico | Administrador e Gerente de TI |
| Tema, fontes, ajuda e informações da instalação | Todos os sete perfis |
| Painel Modelo, central de testes, monitor de processos, ferramentas de configuração e restauração visual | Apenas Administrador, com instalação `dev`, ambiente `development` e fora do modo cliente |

O perfil de instalação (`core`/`dev`) é diferente do perfil do usuário. Instalar ferramentas DEV não concede permissões administrativas. Troca de senha e MFA são operações da própria conta; suas validações existentes continuam ativas.

## Como a proteção funciona

- A barra lateral e o menu Painéis mostram somente as páginas permitidas.
- Navegação, callbacks dos menus e construção de painéis verificam autorização. Páginas já carregadas também verificam a sessão ao reabrir.
- Páginas novas ou perfis desconhecidos são bloqueados por padrão. Uma lista vazia não significa acesso público.
- A identidade vem da sessão validada no banco, não do dicionário de usuário da interface. Revogação, expiração, senha provisória e exigência de cadastro MFA impedem acesso.
- Alterar o perfil de um usuário revoga sua sessão. Na próxima navegação ou verificação periódica, as janelas são fechadas e um novo login é necessário.
- Repositório e serviços validam leitura/escrita, inclusive nas transações. Esconder um botão não é a barreira de segurança.
- No modo cliente, `pages/authorize` consulta o servidor com token de sessão. O servidor não aceita um perfil enviado pelo cliente e protege também chamadas diretas de leitura e escrita. Instale esta versão no cliente e no servidor; não há liberação automática se a API estiver indisponível.
- O auditor vê as tabelas e a opção de atualizar a consulta. Formulários e ações de gravação ficam ocultos; gravações diretas também são negadas.

O controle protege os acessos pela aplicação. Em instalações locais, quem tem controle do sistema operacional ou acesso direto ao arquivo do banco pode alterar código/dados; para clientes não confiáveis, utilize a API central e restrinja credenciais e arquivos no servidor.

## Adicionar uma página ou ajustar a matriz

1. Crie um controlador derivado de `BasePanel` e sua view; defina `PANEL_NAME` e `PANEL_ICON`.
2. Registre o controlador em `panels/__init__.py`.
3. Cadastre exatamente o `PANEL_NAME` em `PAGE_RULES`, com uma lista explícita de perfis. Não use as antigas listas `ALLOWED_ACCESS` nos controladores.
4. Atualize `can_access_table` para os recursos necessários à página, respeitando a diferença entre consulta e escrita. Registre novas tabelas também na lista permitida do repositório.
5. Para callbacks adicionais no aplicativo, use `@protected_page(...)`. Se a janela acessa dados, mantenha a verificação no controlador e no serviço/repositório.
6. Atualize a matriz acima e os testes de autorização, API e interface. Não basta mudar apenas a visibilidade do menu.

## Executar os testes

Windows:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_page_access.py tests/test_ui.py -q
```

Linux com sessão gráfica:

```bash
.venv/bin/python -m pytest tests/test_page_access.py tests/test_ui.py -q
```

Linux sem sessão gráfica: use `xvfb-run -a .venv/bin/python -m pytest tests/test_page_access.py tests/test_ui.py -q`. Os testes usam bancos temporários e contas de teste; não modificam os usuários reais.

Validação em 15/10/2026: **39 testes novos** cobrindo os sete perfis, permissões de tabelas, menus, construção direta dos controladores, páginas em cache, revogação por mudança de perfil, senha provisória, cadastro obrigatório de MFA, consulta do auditor, ferramentas DEV e autorização no servidor. Suíte completa: **273 aprovados e 2 pulados no Windows; 272 aprovados e 1 pulado no Ubuntu/WSL2 com Xvfb**. Os testes pulados exigem banco externo de homologação ou privilégio de symlink no Windows. Nenhuma falha; um aviso já existente de depreciação da biblioteca de testes HTTP.
