# ✨ Nexus Tkinter Framework ✨ - Forjando Aplicações Desktop Robustas com Elegância

**Bem-vindo ao Nexus, um framework Python meticulosamente arquitetado para capacitar desenvolvedores na criação de aplicações desktop sofisticadas, seguras e orientadas a dados, utilizando o poder nativo do Tkinter/ttk com uma abordagem moderna e produtiva.**

Cansado da complexidade desnecessária ou da falta de estrutura em projetos Tkinter? O Nexus emerge como a solução definitiva, oferecendo uma **base MVC (Model-View-Controller) coesa**, **segurança integrada de ponta**, **suporte multi-banco flexível** e um **arsenal incomparável de ferramentas de desenvolvimento** que transmutam o tedioso em trivial.

---

## 🌟 Pilares Fundamentais do Framework

O Nexus foi construído sobre princípios que garantem excelência e longevidade aos seus projetos:

### 🏛️ 1. Arquitetura MVC Iluminada
* **Clareza Estrutural:** Separação rigorosa entre Interface (`View`), Lógica de Negócios (`Controller`) e Acesso a Dados (`Model`).
* **Manutenibilidade Celestial:** Modificações e expansões se tornam intuitivas, com baixo acoplamento entre componentes.
* **Testabilidade Pura:** Camadas isoladas facilitam a criação de testes unitários precisos e eficazes.
* **Escalabilidade Infinita:** A estrutura modular suporta o crescimento orgânico da aplicação sem sacrificar a organização.

### 🛡️ 2. Segurança Inabalável
* **Autenticação Robusta:** Senhas de usuário protegidas com **hashing bcrypt**, o padrão-ouro contra ataques de força bruta e rainbow tables.
* **Credenciais Sigilosas:** Chaves de acesso ao banco (`banco.ini`) resguardadas por criptografia **Fernet (AES)**, vinculadas a uma `secret.key` local, eliminando a exposição de dados sensíveis em texto plano.

### 🗄️ 3. Flexibilidade Multi-Banco Universal
* **SQLAlchemy Core:** Utiliza o poder do SQLAlchemy para uma comunicação agnóstica e eficiente com diversos SGBDs.
* **Configuração Simplificada:** Alterne entre bancos de dados com uma simples edição no arquivo `banco.ini`.
* **Suporte Abrangente:** Conecte-se nativamente a:
    * SQLite (`sqlite3`)
    * PostgreSQL (`psycopg2-binary`)
    * MySQL (`PyMySQL`)
    * MariaDB (`mariadb`)
    * Microsoft SQL Server (`pymssql`)
    * Oracle (`oracledb`) - *Requer instalação do driver específico*
    * Firebird (`fdb`) - *Requer instalação do driver específico*
* **Consistência Garantida:** A camada de persistência normaliza nomes de colunas para minúsculas, assegurando compatibilidade cross-SGBD.

### 🎨 4. Interface Nativa & Adaptável (ttk 'clam')
* **Visual Profissional:** Utiliza o tema `'clam'` do `ttk` como base para uma aparência limpa e moderna em diferentes sistemas operacionais.
* **Personalização Profunda:**
    * **Editor de Temas Avançado:** Uma ferramenta gráfica dedicada permite ajustar cores primárias, secundárias, fontes globais, tamanho de fonte e até detalhes como espessura de borda em tempo real.
    * **Persistência Simples:** Suas preferências de tema são salvas no arquivo `settings.json`, carregadas automaticamente ao iniciar.

### 💾 5. Camada de Persistência Abstrata e Inteligente
* **`GenericRepository`:** Centraliza e padroniza as operações CRUD (Create, Read, Update, Delete), desacoplando os Controllers dos detalhes do SQL.
* **`DataService`:** Orquestra transações complexas envolvendo múltiplas tabelas (ex: atualizar um registro e gravar um log de auditoria), garantindo **atomicidade** (ou tudo funciona, ou nada é alterado).

---

## 🛠️ O Arsenal do Desenvolvedor: Ferramentas Integradas

O Nexus transcende ser apenas um framework; ele é um **ecossistema de produtividade**. As ferramentas gráficas inclusas foram projetadas para **eliminar tarefas repetitivas e acelerar drasticamente** o ciclo de vida do desenvolvimento:

### ✨ [1] Gerador de Código MVC Divino (`toolsDev`)
* **Propósito:** Automatizar a criação da estrutura básica para novos painéis ou modais CRUD.
* **Funcionalidades:**
    * Conecta-se ao banco de dados configurado.
    * Inspeciona a estrutura (colunas, chaves) da tabela selecionada.
    * Utiliza **templates Jinja2** para gerar:
        * Arquivo `_controller.py` (com lógica CRUD básica, validações e chamadas ao Repository).
        * Arquivo `_view.py` (com formulário ttk, Treeview e botões pré-configurados).
        * Arquivo `_model.py` (se lógica de dados específica for necessária, além do Repository).
    * Configura automaticamente `PANEL_NAME`, `PANEL_ICON` e `ALLOWED_ACCESS`.
    * Registra o novo painel no `panels/__init__.py`.
* **Resultado:** Criação de módulos CRUD funcionais em segundos, liberando o desenvolvedor para focar na lógica de negócios específica.

### 🔑 [2] Gestor de Configuração e Segurança (`credenciais_manager_gui.py`)
* **Propósito:** Gerenciar de forma segura e visual as configurações sensíveis e scripts SQL.
* **Funcionalidades:**
    * **Gerenciador `banco.ini`:** Ativa/desativa diferentes configurações de banco com um clique, comentando/descomentando seções automaticamente.
    * **Criptografador de Credenciais:** Criptografa `user` e `password` em texto plano no `banco.ini` usando a `secret.key`.
    * **Atualizador de Hashes SQL:** Lê arquivos `.sql` (schemas), encontra senhas em texto plano em comandos `INSERT INTO usuarios` e as substitui por hashes **bcrypt** seguros.
    * **Visualizador/Decifrador:** Permite inspecionar `banco.ini` ou `.sql`, exibindo credenciais criptografadas/hasheadas e tentando decifrá-las (usando `secret.key` para .ini ou senhas conhecidas para .sql).
* **Resultado:** Manutenção segura das configurações, migração facilitada de senhas inseguras e auditoria de credenciais.

### 🧪 [3] Executor de Testes Unitários (`toolTestU`)
* **Propósito:** Interface gráfica para descobrir, executar e analisar testes `unittest`.
* **Funcionalidades:**
    * **Descoberta Automática:** Encontra todos os arquivos `test_*.py` no diretório `toolTestU/`.
    * **Execução Flexível:** Roda todos os testes, apenas os selecionados, ou re-executa apenas os que falharam na última execução.
    * **Resultados Detalhados:** Exibe o status (Sucesso, Falha, Erro), duração e nome de cada teste em uma Treeview.
    * **Análise de Falhas:** Mostra o traceback completo e logs de erro para testes que falharam.
    * **Log de Execução:** Gera um arquivo de log (`.log`) detalhado para cada execução.
* **Resultado:** Facilita a execução regular de testes unitários e a identificação rápida de regressões.

### 🧠 [4] Dashboard de Testes Supremo (`toolTest`)
* **Propósito:** Plataforma avançada para testes de integração, estresse, concorrência e resiliência, com foco em performance e comportamento sob carga.
* **Funcionalidades:**
    * **Suítes Pré-definidas:** Inclui suítes como Clássica (sequencial), Moderna (parametrizada), Paralela (ThreadPool), Estresse de BD (simulação de usuários), Concorrência (locks, race conditions) e mais.
    * **Execução Individual ou Total:** Roda suítes específicas ou todas em sequência.
    * **Métricas Abrangentes:** Exibe resultados individuais com status especiais (✨DIVINE, ⚡GODLIKE para performance extrema), duração, severidade, logs detalhados e *métricas de sistema* (uso de CPU/RAM durante o teste via `psutil`).
    * **Visualização Clara:** Dashboard com resumo geral (Total, Taxa Sucesso, Tempo), contagem por status e tabela detalhada dos resultados.
    * **Exportação CSV:** Exporta todos os dados e metadados dos resultados para análise externa.
* **Resultado:** Permite validar a robustez, performance e escalabilidade da aplicação sob condições realistas e extremas.

### 🩺 [5] Ferramenta de Diagnóstico (Health Check) (`toolTest/health_check_gui.py`)
* **Propósito:** Verificação rápida do ambiente de desenvolvimento e dependências essenciais.
* **Funcionalidades:**
    * **Verificação Estrutural:** Confirma a existência de arquivos e diretórios cruciais do projeto.
    * **Teste de Conexão:** Tenta conectar ao banco de dados atualmente configurado no `banco.ini`.
    * **Checagem de Bibliotecas:** Verifica a presença de dependências opcionais importantes (ex: `GPUtil` para monitoramento de GPU, se aplicável).
    * **Log Detalhado:** Registra cada passo da verificação.
* **Resultado:** Ajuda a diagnosticar rapidamente problemas de configuração de ambiente ou dependências ausentes.

---

## 🗺️ Arquitetura e Fluxo de Dados

O framework adota uma abordagem em camadas clara, promovendo organização e baixo acoplamento:

```mermaid
graph LR
    A[Usuário] -- Interage --> B(View - Tkinter/ttk);
    B -- Evento --> C{Controller};
    C -- Solicita/Envia Dados --> D[Model];
    D -- Lê/Escreve --> E((Banco de Dados));
    D -- Retorna Dados --> C;
    C -- Atualiza --> B;

    subgraph Camada de Apresentação
        B
    end

    subgraph Camada de Controle
        C
    end

    subgraph Camada de Modelo/Persistência
        D(GenericRepository / DataService)
        E
    end

    style D fill:#f9f,stroke:#333,stroke-width:2px
Exemplo de Fluxo — Salvando um Novo Usuário:
Usuário preenche os campos na GestaoUsuariosView (View).

Clica no botão "Salvar".

A View aciona o método salvar_usuario no PainelGestaoUsuariosController (Controller).

O Controller obtém os dados das tk.StringVar, valida as entradas (campos obrigatórios, etc.).

O Controller chama persistencia.auth.hash_password para gerar o hash da senha.

O Controller monta um DataFrame Pandas com os dados do novo usuário (incluindo o hash).

O Controller chama GenericRepository.write_dataframe_to_table("usuarios", df) (Model).

O GenericRepository usa SQLAlchemy para gerar e executar o INSERT no banco de dados configurado (Banco de Dados).

Se a inserção for bem-sucedida, o GenericRepository retorna.

O Controller recebe a confirmação e chama messagebox.showinfo.

O Controller chama seu próprio método carregar_dados para atualizar a lista.

carregar_dados chama GenericRepository.read_table_to_dataframe("usuarios").

O GenericRepository executa o SELECT.

O DataFrame com a lista atualizada retorna ao Controller.

O Controller instrui a GestaoUsuariosView (View) a limpar e repopular a ttk.Treeview.

A View exibe a tabela atualizada para o Usuário.

Ficheiros e Diretórios Essenciais
/
├── run.py                     # Ponto de entrada da aplicação, valida config, inicializa DB
├── app.py                     # Classe principal da aplicação Tkinter (janela, sidebar, menubar)
├── config.py                  # Configurações globais (flags booleanas, logs, etc.)
├── banco.ini                  # Configurações de conexão com bancos de dados (ATIVAR APENAS UMA)
├── settings.json              # Configurações de tema e UI salvas pelo usuário
├── secret.key                 # Chave de criptografia (gerada automaticamente) - NÃO COMPARTILHAR!
│
├── panels/                    # Módulos dos painéis principais (interface e lógica)
│   ├── __init__.py            # Registra todos os painéis disponíveis
│   ├── base_panel.py          # Classe base abstrata para todos os painéis
│   ├── *_controller.py        # Lógica de controle de cada painel
│   └── *_view.py              # Construção da interface (widgets) de cada painel
│
├── modals/                    # Módulos para janelas modais (Toplevels) com lógica própria
│   ├── *_controller.py
│   ├── *_view.py
│   └── *_model.py             # Lógica de dados específica do modal (se necessário)
│
├── dialogs/                   # Módulos para diálogos simples (Toplevels sem controller complexo)
│   ├── login_ui.py            # Diálogo de login
│   ├── about_dialog.py        # Diálogo "Sobre"
│   └── advanced_theme_dialog.py # Diálogo de personalização de tema
│
├── persistencia/              # Camada de acesso e manipulação de dados
│   ├── database.py            # Gerencia a conexão com o banco (lê banco.ini)
│   ├── repository.py          # CRUD genérico usando SQLAlchemy Core e Pandas
│   ├── data_service.py        # Orquestra transações atômicas e regras de negócio
│   ├── auth.py                # Verifica credenciais, faz hashing/verificação de senhas (bcrypt)
│   ├── security.py            # Gera/carrega secret.key, criptografa/descriptografa (Fernet)
│   ├── logger.py              # Configura o sistema de logging (arquivos rotativos, console)
│   └── sql_schema_*.sql       # Scripts SQL para criação de tabelas em diferentes SGBDs
│
└── utilParaDesenvolvimento/   # Ferramentas auxiliares para o desenvolvedor
    ├── credenciais_manager_gui.py # (Ver Ferramenta 2)
    ├── toolsDev/                  # (Ver Ferramenta 1 - Gerador de Código)
    │   ├── run_generator.py
    │   ├── generator_ui.py
    │   ├── generator_logic.py
    │   └── templates_jinja/       # Templates Jinja2 para geração de código
    ├── toolTest/                  # (Ver Ferramenta 4 - Dashboard Supremo)
    │   ├── dashboard_supremo.py
    │   ├── health_check_gui.py    # (Ver Ferramenta 5 - Health Check)
    │   └── suites/                # Suítes de teste para o Dashboard Supremo
    └── toolTestU/                 # (Ver Ferramenta 3 - Testes Unitários)
        ├── run_all_tests_gui.py
        ├── mock_dependencies.py   # Mocks para isolar testes unitários
        └── test_*.py              # Arquivos de teste unittest
⚙️ Configuração e Execução Detalhada
Pré-requisitos Celestiais
Python: Versão 3.9 ou superior é recomendada.

Pip: O instalador de pacotes do Python (geralmente incluído).

Git: Para clonar o repositório.

1️⃣ Evocação (Clone)
Abra seu terminal ou prompt de comando:

Bash

git clone <URL_DO_SEU_REPOSITORIO>
cd <NOME_DO_REPOSITORIO>
2️⃣ Criação do Santuário (Ambiente Virtual)
É altamente recomendado usar um ambiente virtual para isolar as dependências deste projeto:

Bash

# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
(Você verá (.venv) no início do seu prompt se funcionou.)

3️⃣ Instalação dos Artefatos (Dependências)
Instale as bibliotecas essenciais para a aplicação:

Bash

pip install pandas sqlalchemy cryptography bcrypt ttkbootstrap
(Nota: ttkbootstrap pode ser usado opcionalmente para temas mais avançados, mas o código atual foca no 'clam' nativo. Adapte se necessário.)

Instale as dependências opcionais para as Ferramentas do Desenvolvedor:

Bash

pip install jinja2 psutil gputil
(Nota: gputil é opcional e requer drivers NVIDIA/CUDA configurados para funcionar.)

Instale o driver específico para o banco de dados que você usará (escolha apenas um):

Bash

# Para PostgreSQL:
pip install psycopg2-binary

# Para MySQL:
pip install PyMySQL

# Para MariaDB:
pip install mariadb

# Para SQL Server:
pip install pymssql

# Para Oracle: (Requer instalação adicional do Oracle Instant Client)
# pip install oracledb

# Para Firebird: (Requer instalação adicional do driver Firebird)
# pip install fdb
💡 Consulte os comentários no arquivo banco.ini ou a documentação do SQLAlchemy para os drivers recomendados e suas dependências.

4️⃣ Alinhamento Cósmico (Configuração do Banco)
Abra o arquivo banco.ini na raiz do projeto.

Localize a seção correspondente ao seu banco de dados (ex: [postgresql]).

Remova o # do início de cada linha dessa seção (ex: type = postgresql, host = ..., etc.).

Adicione # no início de todas as linhas das outras seções de banco de dados para desativá-las. Apenas UMA seção pode estar ativa!

Ajuste os valores de host, port, dbname, user e password conforme necessário.

Lembre-se: Se user e password estiverem criptografados (começando com gAAAAA...), use a Ferramenta 2 (credenciais_manager_gui.py) para gerar novas credenciais criptografadas se precisar alterá-los.

Para SQLite: Apenas descomente a seção [sqlite]. O arquivo (.db) será criado automaticamente na primeira execução se INITIALIZE_DATABASE_ON_STARTUP = True em config.py.

Para outros bancos: Certifique-se de que o banco de dados (dbname) e o usuário (user) já existam no seu servidor SGBD. Você pode usar os scripts persistencia/sql_schema_*.sql como guia para criar a estrutura (execute-os usando uma ferramenta apropriada como psql, mysql, SQL Server Management Studio, etc., antes de rodar a aplicação pela primeira vez).

5️⃣ A Manifestação (Execução)
Certifique-se de que seu ambiente virtual (.venv) está ativado e execute:

Bash

python run.py
A aplicação deverá iniciar, possivelmente mostrando a tela de login se USE_LOGIN = True.

✨ Criando Seu Primeiro Painel: O Caminho do Artesão
Existem duas sendas para adicionar novas funcionalidades (painéis):

Senda 1: A Forja Manual (Usando o Painel Modelo)
Duplique os Arquétipos: Copie panels/painel_modelo_controller.py e panels/painel_modelo_view.py.

Renomeie com Propósito: Altere os nomes dos arquivos e das classes internas (ex: PainelGerenciarProdutos, GerenciarProdutosView).

Defina a Essência (Controller): Ajuste as constantes de classe:

PANEL_NAME: O nome que aparecerá no menu/sidebar (ex: "Gerenciar Produtos").

PANEL_ICON: Um emoji para identificação visual (ex: "📦").

ALLOWED_ACCESS: Lista de perfis que podem ver este painel (lista vazia [] significa acesso livre).

Molde a Interface (View): Em _create_widgets (ou método similar na View), adicione os ttk.Label, ttk.Entry, ttk.Button, ttk.Treeview, etc., necessários.

Infunda a Lógica (Controller): Crie métodos no Controller para responder a eventos da View (ex: _on_salvar_click), interagir com o GenericRepository ou DataService, e atualizar a View.

Registre a Criação: Abra panels/__init__.py, importe sua nova classe Controller e adicione-a à lista ALL_PANELS.

Senda 2: A Conjuração Automática (Usando o Gerador de Código)
Invoque o Gerador: Execute a ferramenta:

Bash

python utilParaDesenvolvimento/toolsDev/run_generator.py
Siga o Ritual:

Na interface do gerador, selecione "Painel" como tipo de componente.

Escolha a opção "MVC CRUD a partir do Banco".

Clique em "Carregar Tabelas" e selecione a tabela desejada (ex: produtos).

Preencha o Nome de Exibição (ex: "Gerenciar Produtos") e o Ícone (ex: "📦").

Selecione os Perfis de Acesso permitidos.

Clique em "Gerar Painel".

Contemple a Criação: O gerador criará os arquivos _controller.py, _view.py, registrará o painel em __init__.py e fornecerá uma estrutura CRUD básica funcional. Você só precisa refinar a View e adicionar lógicas específicas.

##📜 Licença

(Adicione aqui a sua licença, ex: MIT, GPL, etc.)

Exemplo: Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.