# **✨ nexlifyttk ✨ \- Framework Desktop Python com Arquitetura em Camadas**

**nexlifyttk** é um *boilerplate* Python projetado para o desenvolvimento de aplicações desktop robustas, seguras e orientadas a dados, utilizando o *toolkit* nativo **Tkinter/ttk**. O foco principal é a aplicação rigorosa de padrões de projeto que garantem baixo acoplamento, alta coesão e facilidade de manutenção e teste.

Este documento detalha a arquitetura em camadas e os padrões de software implementados.

## **🏛️ 1\. Arquitetura em Camadas e Padrões de Projeto**

O nexlifyttk adota a **Arquitetura em Camadas (Layered Architecture)**, separando o software em responsabilidades bem definidas, que comunicam-se de cima para baixo (apresentação \-\> domínio/serviço \-\> persistência).

| Camada | Módulos Principais | Padrões de Projeto Aplicados | Responsabilidade Primária |
| :---- | :---- | :---- | :---- |
| **Apresentação (UI)** | app.py, panels/\*\_view.py | **Model-View-Controller (MVC)**, **Front Controller** | Gerenciamento de eventos de UI e renderização. |
| **Controle (Lógica da UI)** | panels/\*\_controller.py, app.py | **Model-View-Controller (MVC)**, **Facade** | Mapear interações do usuário à lógica de negócio/serviços. |
| **Serviço (Negócio)** | persistencia/data\_service.py | **Service Layer (Camada de Serviço)**, **Transação Atômica** | Orquestrar lógica de negócio complexa e garantir integridade transacional. |
| **Persistência (Dados)** | persistencia/repository.py | **Repository**, **Data Mapper (Implícito)** | Abstrair a fonte de dados, fornecendo operações CRUD genéricas. |
| **Infraestrutura** | persistencia/database.py, persistencia/security.py, persistencia/auth.py | **Strategy**, **Adapter**, **Singleton** | Gerenciamento de conexão, segurança, hashing e logging. |

### **1.1. Padrão Model-View-Controller (MVC)**

O MVC é aplicado na camada de Apresentação/Controle para desacoplar a interface (View) da lógica de manipulação de dados (Controller).

* **View (\*view.py)**: Responsável unicamente por desenhar os widgets (Tkinter/ttk), coletar a entrada do usuário e exibir os dados. **Não contém lógica de negócio**.  
* **Controller (\*controller.py)**: Interage com a View (recebe eventos), traduz esses eventos em chamadas ao Service Layer e atualiza a View com os resultados.  
* **Model**: No contexto deste Tkinter MVC, o "Model" é representado pela camada de persistência (GenericRepository) e pelas classes de Serviço (DataService).

### **1.2. Padrão Repository e Data Mapper**

O GenericRepository (em persistencia/repository.py) implementa o Padrão Repository:

* **Finalidade**: Cria uma camada de abstração que permite à camada de Controle trabalhar com objetos de domínio (neste caso, pandas.DataFrame ou dicionários) sem ter conhecimento sobre o SQL subjacente, o tipo de banco de dados, ou a biblioteca SQLAlchemy.  
* **Data Mapper**: A biblioteca **SQLAlchemy Core** atua como um Data Mapper implícito, manipulando a conversão de estruturas de dados Python/Pandas para o formato SQL do banco de dados e vice-versa, garantindo que o banco de dados e o domínio de aplicação permaneçam isolados.

### **1.3. Padrão Service Layer (Camada de Serviço)**

O DataService (em persistencia/data\_service.py) implementa o Padrão Service Layer:

* **Finalidade**: Centraliza a lógica de negócio que envolve múltiplas operações de repositório. O DataService garante que operações complexas, como reclassificar\_vegetal\_e\_logar, sejam **Transações Atômicas** (ou seja, ou todas as etapas são concluídas com sucesso, ou nenhuma é).  
* **Integridade**: Utiliza o gerenciamento de transações do SQLAlchemy para executar COMMIT ou ROLLBACK em caso de falha, mantendo a integridade referencial e a trilha de auditoria.

## **🛡️ 2\. Padrões de Segurança e Infraestrutura**

A segurança e as preocupações de infraestrutura são encapsuladas, aderindo ao princípio **Strategy Pattern**.

### **2.1. Hashing e Autenticação (Strategy Pattern)**

O módulo persistencia/auth.py utiliza o **Strategy Pattern** para implementar a verificação de credenciais:

* **Algoritmo de Hashing (Estratégia)**: O **bcrypt** é a estratégia escolhida devido à sua resistência a ataques de força bruta, por ser um algoritmo lento por design e que incorpora *salt* automaticamente, protegendo senhas de usuários na tabela usuarios.

### **2.2. Criptografia de Credenciais (Strategy Pattern)**

O módulo persistencia/security.py utiliza o **Strategy Pattern** para proteger as credenciais de conexão do banco de dados:

* **Algoritmo de Criptografia (Estratégia)**: A biblioteca **Fernet**, que implementa AES-128 em modo CBC (sincronizado com um HMAC), é usada para criptografar as credenciais sensíveis no arquivo banco.ini, usando uma chave mestra armazenada em secret.key. Isso impede a exposição de senhas em texto puro.

### **2.3. Gerenciamento de Conexão (Singleton Implícito)**

O DatabaseManager (em persistencia/database.py) atua como um **Singleton implícito** ao garantir que apenas uma instância do motor de conexão (Engine do SQLAlchemy) seja criada e compartilhada por toda a aplicação. Isso otimiza recursos e gerencia a conexão com o banco de dados configurado no banco.ini de forma centralizada.

## **🔄 3\. Detalhamento do Fluxo de Controle**

O fluxo de dados e controle segue uma cadeia estrita de responsabilidade (Chain of Responsibility) para manter o baixo acoplamento.

### **Exemplo: Reclassificação de um Vegetal (Transação Atômica)**

1. **View (painel\_vegetais\_auditoria\_view.py)**: O usuário interage com um ttk.Button.  
2. **Controller (painel\_vegetais\_auditoria\_controller.py)**: O evento command é disparado, chamando o método executar\_transacao\_reclassify.  
   * O Controller coleta os dados de entrada (nome\_vegetal, novo\_tipo) e o contexto (usuario\_logado).  
   * O Controller **NÃO** executa SQL, ele chama o Service Layer.  
3. **Service Layer (DataService)**: O método reclassificar\_vegetal\_e\_logar é invocado.  
   * Ele abre uma **transação de banco de dados**.  
   * **Passo 1 (Busca)**: Usa consultas SQL diretas (ou o Repository) para buscar ids e validar a existência do vegetal e do novo tipo.  
   * **Passo 2 (Update)**: Executa a atualização do id\_tipo na tabela vegetais.  
   * **Passo 3 (Auditoria)**: Executa a inserção do registro na tabela log\_alteracoes.  
   * Se todos os passos forem bem-sucedidos, a transação recebe um COMMIT. Se um passo falhar (ex: erro de banco, deadlock), ocorre um ROLLBACK, e o controle retorna ao Controller com uma mensagem de falha.  
4. **Controller (Resposta)**: Recebe o status da transação, exibe a mensagem apropriada (messagebox.showinfo ou messagebox.showerror) e chama carregar\_dados para atualizar a View.

## **🗂️ 4\. Estrutura de Diretórios e Módulos**

/  
├── run.py                     \# Ponto de entrada, inicializa logs, valida flags e carrega o DB.  
├── app.py                     \# Controller Principal / Root Window (Facade da Aplicação).  
├── config.py                  \# Configuração de Ambiente (Flags, Constantes).  
├── banco.ini                  \# Configuração da URL de Conexão (Protegido por criptografia).  
├── settings.json              \# Memento do estado da UI (Tema, Fontes).  
├── secret.key                 \# Chave mestra Fernet para criptografia de credenciais (NÃO COMPARTILHAR\!).  
│  
├── panels/                    \# Implementação do padrão MVC para cada tela principal.  
│   ├── base\_panel.py          \# Classe Base Abstrata (Abstração).  
│   ├── \*\_controller.py        \# Controller (Lógica da UI).  
│   ├── \*\_view.py              \# View (Renderização).  
│  
├── modals/                    \# Janelas modais (sub-aplicações com seu próprio ciclo MVC/MVP).  
│  
├── dialogs/                   \# Diálogos simples (ex: Login, About).  
│  
└── persistencia/              \# Camada de Persistência e Infraestrutura.  
    ├── database.py            \# Gerencia o Singleton da Engine (SQLAlchemy), lê \`banco.ini\`.  
    ├── repository.py          \# GenericRepository (Padrão Repository) para operações CRUD.  
    ├── data\_service.py        \# DataService (Service Layer) para transações atômicas/complexas.  
    ├── auth.py                \# Implementação da Estratégia de Hashing (bcrypt).  
    ├── security.py            \# Implementação da Estratégia de Criptografia (Fernet).  
    ├── logger.py              \# Configuração do Logging Rotativo.  
    ├── sql\_schema\_\*.sql       \# Scripts DDL/DML para inicialização de bancos.

## **⚙️ 5\. Configuração e Execução Técnica**

### **Pré-requisitos**

* **Python**: 3.9 ou superior  
* **Gerenciador de Pacotes**: pip  
* **SGBD** (Opcional, mas necessário para DATABASE\_ENABLED=True com PostgreSQL/MySQL/MariaDB/SQL Server).

### **1️⃣ Instalação de Dependências**

As dependências críticas para o funcionamento do framework incluem:

| Pacote | Versão | Função | Padrão |
| :---- | :---- | :---- | :---- |
| sqlalchemy | 2.0.43 | Framework de persistência de dados. | Data Mapper |
| pandas | 2.3.3 | Manipulação de DTOs e conjuntos de dados. | Value/Data Object |
| bcrypt | 5.0.0 | Algoritmo de hashing seguro de senhas. | Strategy (Hashing) |
| cryptography | 46.0.2 | Base para a criptografia Fernet (AES). | Strategy (Criptografia) |
| ttkbootstrap | 1.14.4 | Estilização avançada do Tkinter. | UI/View |

\# Crie e ative um ambiente virtual  
python3 \-m venv .venv  
source .venv/bin/activate

\# Instale as dependências  
pip install \-r requirements.txt

### **2️⃣ Configuração do Banco de Dados**

A conexão é gerenciada pelo banco.ini. Para bancos externos, as credenciais são criptografadas (ver persistencia/security.py).

1. Edite banco.ini e ative **apenas uma** seção (remova o \#).  
2. Para credenciais de usuário/senha, utilize o script GUI em instalacao/gerador\_credenciais\_gui.py para gerar os valores criptografados em formato Fernet (para banco.ini) ou hash Bcrypt (para sql\_schema\_\*.sql).

### **3️⃣ Execução**

O run.py atua como o **Bootstrapper**, verificando a integridade das flags em config.py (ex: USE\_LOGIN=True requer DATABASE\_ENABLED=True) antes de instanciar a AplicacaoPrincipal.

python run.py

## **✨ 6\. Extensibilidade e Convenções**

A estrutura do projeto foi desenhada para facilitar a expansão, utilizando a Herança e Injeção de Dependência (implícita via construtor do Controller).

### **6.1. Criação de Novo Módulo (Painel)**

Para adicionar uma nova funcionalidade, siga a convenção de Padrão **Factory Method (Implícito)**:

1. **Herança**: A View deve herdar de ttk.Frame. O Controller deve herdar de panels.base\_panel.BasePanel.  
2. **Contrato**: O método create\_widgets() no Controller é o contrato que inicia o carregamento da View.  
3. **Injeção de Dependência**: O app\_controller é injetado no construtor de BasePanel, permitindo que qualquer painel acesse serviços globais (como app.get\_current\_user()).

### **6.2. Convenção de Nomes e Padrão**

* **Minúsculas nas Colunas**: Para garantir a compatibilidade entre SGBDs (PostgreSQL é case-sensitive), todas as colunas e nomes de tabelas no Python e no SQL **são tratadas como minúsculas**. O GenericRepository garante essa normalização no mapeamento dos DataFrames.  
* **Trilha de Auditoria**: O Service Layer é o único ponto de entrada para operações que exigem rastreabilidade. A tabela log\_alteracoes deve ser o destino de toda Transação Atômica.