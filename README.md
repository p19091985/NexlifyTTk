
# **Painel de Controle Moderno com Python e Tkinter**

Este projeto é um framework robusto para a construção de aplicações de desktop modernas e orientadas a dados, utilizando Python, a biblioteca gráfica Tkinter e o theming avançado do ttkbootstrap. Ele foi projetado com uma arquitetura limpa (MVC), funcionalidades de segurança integradas e um conjunto poderoso de ferramentas para acelerar o desenvolvimento.

## **Principais Funcionalidades**

  - **Arquitetura MVC (Model-View-Controller):** Código organizado com uma clara separação entre a lógica de negócios (Controller), a interface gráfica (View) e o acesso aos dados (Model), facilitando a manutenção e a escalabilidade.
  - **Suporte a Múltiplos Bancos de Dados:** Graças ao SQLAlchemy e a um sistema de configuração flexível (`banco.ini`), a aplicação pode se conectar a SQLite, PostgreSQL, MySQL, SQL Server, MariaDB e outros com pouca ou nenhuma alteração de código.
  - **Segurança Integrada:**
      - **Autenticação Segura:** Senhas são armazenadas usando hashing `bcrypt`.
      - **Credenciais Criptografadas:** As credenciais de acesso ao banco de dados no arquivo `banco.ini` são criptografadas usando a biblioteca `cryptography` (Fernet), protegidas por uma chave local (`secret.key`).
  - **Interface Moderna e Personalizável:**
      - Utiliza **ttkbootstrap** para aplicar temas modernos e consistentes.
      - Inclui um painel avançado para **personalização de temas em tempo real**, permitindo que o usuário ajuste cores, fontes e estilos da aplicação.
  - **Ferramentas de Desenvolvedor Inclusas:**
      - **Gerador de Código:** Uma ferramenta gráfica que cria automaticamente novos painéis e janelas modais (CRUD MVC) a partir de um template, inspecionando o banco de dados para gerar os campos necessários.
      - **Gestor de Credenciais e Configuração:** Uma GUI para gerenciar o arquivo `banco.ini`, criptografar credenciais e atualizar hashes de senha em scripts SQL.
      - **Dashboard de Testes:** Duas ferramentas gráficas para execução e visualização de testes, incluindo um executor de testes unitários e um dashboard avançado para testes de estresse e concorrência.
  - **Camada de Persistência Abstrata:** O `GenericRepository` padroniza as operações de CRUD, tornando o código imune a variações de maiúsculas/minúsculas nos nomes das colunas do banco de dados.

## **Arquitetura do Projeto**

O projeto segue uma arquitetura em camadas para garantir a separação de responsabilidades:

  - **`run.py` & `app.py` (Camada de Apresentação Principal):** Ponto de entrada da aplicação. Gerencia a janela principal, o ciclo de vida da UI, o login e a navegação entre os painéis.
  - **`panels/` (Módulos da UI):** Cada subdiretório ou arquivo aqui representa uma tela ou funcionalidade da aplicação, seguindo o padrão Controller/View.
  - **`modals/` & `dialogs/` (Componentes de UI):** Contêm as janelas modais e diálogos, como a tela de login, a janela "Sobre" e os formulários de cadastro secundários, também seguindo o padrão MVC.
  - **`models/` (Modelos de Dados):** Encapsula a lógica de acesso aos dados para uma funcionalidade específica, servindo como a ponte entre o Controller e a camada de persistência.
  - **`persistencia/` (Camada de Acesso a Dados):** A camada mais baixa, responsável por toda a comunicação com o banco de dados.
      - `database.py`: Gerencia a criação da conexão (engine) do SQLAlchemy.
      - `repository.py`: Fornece métodos genéricos para CRUD (Create, Read, Update, Delete).
      - `data_service.py`: Orquestra operações complexas que envolvem múltiplos passos em uma única transação atômica.
      - `auth.py`: Lida com a verificação de credenciais de usuários.
      - `security.py`: Fornece as funções para criptografia e descriptografia.

## **Pré-requisitos**

  - Python 3.9 ou superior
  - `pip` (gerenciador de pacotes do Python)

## **Instalação e Configuração**

**1. Clone o Repositório**

```bash
git clone <url-do-seu-repositorio>
cd <nome-do-repositorio>
```

**2. Crie e Ative um Ambiente Virtual**

É altamente recomendado usar um ambiente virtual para isolar as dependências do projeto.

```bash
# Criar o ambiente virtual
python -m venv venv

# Ativar no Windows
.\venv\Scripts\activate

# Ativar no macOS/Linux
source venv/bin/activate
```

**3. Instale as Dependências**

Crie um arquivo `requirements.txt` na raiz do projeto com o seguinte conteúdo e execute o comando `pip install`.

**`requirements.txt`:**

```
ttkbootstrap
sqlalchemy
pandas
bcrypt
cryptography
psutil
gputil
jinja2
black

# Drivers de banco (instale apenas os que for usar)
# pymysql # para MySQL
# psycopg2-binary # para PostgreSQL
# pymssql # para SQL Server
# mariadb # para MariaDB
# fdb # para Firebird
# oracledb # para Oracle
```

**Comando de instalação:**

```bash
pip install -r requirements.txt
```

**4. Configure a Conexão com o Banco de Dados**

O coração da configuração está no arquivo `banco.ini`.

a.  **Escolha um Banco:** Abra o `banco.ini` e descomente (remova o `#` do início) o bloco de configuração correspondente ao banco de dados que você deseja usar. Deixe todos os outros blocos comentados.

b.  **Preencha as Credenciais:** No bloco ativo, preencha `host`, `port`, `dbname`, `user` e `password` com os dados do seu banco. **Deixe a senha em texto plano por enquanto.**

c.  **Criptografe as Credenciais:** Execute a ferramenta de gerenciamento de credenciais para criptografar o arquivo `banco.ini` de forma segura.

````
```bash
python -m utilParaDesenvolvimento.credenciais_manager_gui
```

Na aba **"Criptografia e Hashes"**, clique em **"Selecionar e Criptografar banco.ini"** e escolha o seu arquivo. A ferramenta irá criptografar os campos `user` e `password` e criar um backup (`.ini.bak`). A chave de criptografia será gerada automaticamente no arquivo `secret.key` na primeira execução.
````

**5. Inicialize o Banco de Dados**

a.  **Script SQL:** Certifique-se de que o script SQL correspondente ao seu banco (ex: `persistencia/sql_schema_PostgreSQL.sql`) está correto e atualizado.

b.  **Flag de Configuração:** No arquivo `config.py`, verifique se a flag `INITIALIZE_DATABASE_ON_STARTUP` está como `True`.

c.  **Primeira Execução:** Ao rodar a aplicação pela primeira vez com um banco de dados SQLite, as tabelas serão criadas automaticamente. Para bancos de dados externos (PostgreSQL, MySQL, etc.), você deve executar o script SQL manualmente no seu servidor de banco de dados.

## **Executando a Aplicação Principal**

Após a instalação e configuração, inicie a aplicação com o seguinte comando:

```bash
python run.py
```

## **Ferramentas de Desenvolvimento**

A pasta `utilParaDesenvolvimento/` contém ferramentas poderosas para auxiliar no desenvolvimento e manutenção.

### **1. Gerador de Código MVC**

Cria a estrutura completa de arquivos (Model, View, Controller) para um novo painel ou modal CRUD.

  - **Como executar:**
    ```bash
    python -m utilParaDesenvolvimento.toolsDev.run_generator
    ```
  - **Funcionalidades:**
      - Conecta-se ao banco de dados para listar as tabelas disponíveis.
      - Inspeciona as colunas e chaves primárias da tabela selecionada.
      - Gera os arquivos `.py` com base em templates Jinja2, já com todo o código boilerplate para as operações CRUD.
      - Registra automaticamente novos painéis no `panels/__init__.py`.

### **2. Dashboard de Testes Supremo**

Uma interface gráfica para executar suítes de testes complexas que simulam concorrência, estresse de banco de dados e cenários variados.

  - **Como executar:**
    ```bash
    python -m utilParaDesenvolvimento.toolTest.dashboard_supremo
    ```
  - **Funcionalidades:**
      - Execução de diferentes suítes de teste com um clique.
      - Visualização de resultados em tempo real.
      - Métricas detalhadas de performance (duração, CPU, memória).
      - Exportação de resultados para CSV e logs de testes para TXT.

### **3. Executor de Testes Unitários**

Uma GUI simples para rodar todos os testes unitários (`test_*.py`) localizados na pasta `toolTestU/`.

  - **Como executar:**
    ```bash
    python -m utilParaDesenvolvimento.toolTestU.run_all_tests_gui
    ```
  - **Funcionalidades:**
      - Descobre e executa todos os testes unitários.
      - Exibe a saída do `unittest` de forma clara.
      - Apresenta um resumo de sucessos, falhas e erros.

## **Estrutura de Diretórios**

```
.
├── logs/                 # Arquivos de log gerados pela aplicação
├── modals/               # Módulos para janelas modais (padrão MVC)
├── models/               # Camada de Modelos, com a lógica de dados
├── panels/               # Módulos para os painéis principais (padrão MVC)
├── persistencia/         # Camada de acesso a dados e segurança
│   ├── auth.py           # Lógica de autenticação de usuários
│   ├── database.py       # Gerenciamento da conexão com o banco
│   ├── data_service.py   # Orquestração de transações atômicas
│   ├── repository.py     # Métodos genéricos de CRUD
│   ├── security.py       # Funções de criptografia/descriptografia
│   └── sql_schema_*.sql  # Scripts de criação de tabelas para diferentes SGBDs
├── utilParaDesenvolvimento/ # Ferramentas para auxiliar o desenvolvimento
│   ├── toolTest/         # Dashboard de testes avançado
│   ├── toolTestU/        # Testes unitários com executor gráfico
│   └── toolsDev/         # Gerador de código MVC
├── app.py                # Classe principal da aplicação (AplicacaoPrincipal)
├── banco.ini             # Arquivo de configuração das conexões de banco de dados
├── config.py             # Configurações globais e flags de controle
├── README.md             # Este arquivo
├── requirements.txt      # Lista de dependências Python
├── run.py                # Ponto de entrada para iniciar a aplicação
└── secret.key            # Chave de criptografia (gerada automaticamente)
```
