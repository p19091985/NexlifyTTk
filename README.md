# 🧩 Painel de Controle Moderno com Python e Tkinter

Este projeto é um **framework robusto e completo** para a construção de **aplicações de desktop modernas e orientadas a dados**.  
Utilizando **Python**, a biblioteca gráfica nativa **Tkinter** (com o tema `'clam'` do ttk) e uma arquitetura limpa (**MVC**), ele fornece uma **base sólida, segura e altamente extensível** para desenvolvedores — juntamente com um poderoso conjunto de ferramentas que **acelera drasticamente o ciclo de desenvolvimento**.

---

## 🚀 Principais Funcionalidades

### 🧱 Arquitetura MVC (Model-View-Controller)
Código organizado com clara separação entre:
- **View:** Interface gráfica.
- **Controller:** Lógica de negócios.
- **Model:** Acesso e manipulação de dados.

➡️ Facilita manutenção, testes e escalabilidade do projeto.

---

### 🗄️ Suporte a Múltiplos Bancos de Dados
- Utiliza **SQLAlchemy** e um sistema de configuração flexível (`banco.ini`).
- Conecta-se a:
  - SQLite  
  - PostgreSQL  
  - MySQL  
  - SQL Server  
  - MariaDB  
  - Oracle  
  - Firebird  

---

### 🔐 Segurança Integrada

#### Autenticação Segura
- Senhas armazenadas com **hashing bcrypt** — padrão da indústria para proteção de credenciais.

#### Credenciais Criptografadas
- Credenciais do banco (`banco.ini`) criptografadas com **cryptography (Fernet)**.
- Protegidas por uma chave local (`secret.key`), evitando exposição em texto plano.

---

### 🎨 Interface Nativa e Personalizável
- Usa o tema **'clam' do ttk** para um visual limpo e profissional.
- Painel de **personalização de temas em tempo real**, permitindo:
  - Ajustar cores, fontes e estilos.  
  - Salvar preferências em `settings.json`.

---

### 💾 Camada de Persistência Abstrata
- `GenericRepository` padroniza operações CRUD.  
- Garante **insensibilidade a maiúsculas/minúsculas** em nomes de colunas.

---

## 🧰 Suíte de Ferramentas para Desenvolvedores

O projeto inclui diversas ferramentas gráficas para **acelerar o desenvolvimento, teste e manutenção** da aplicação.

---

### ⚙️ 1. Gerador de Código MVC
Ferramenta visual que:
- Inspeciona tabelas do banco de dados.
- Gera automaticamente todos os arquivos MVC necessários.

**Funcionalidades:**
- Gera Controller, View e Model via **templates Jinja2**.  
- Cria formulários e colunas automaticamente.  
- Configura controle de acesso.  

---

### 🛡️ 2. Gestor de Configuração e Segurança
Interface gráfica para gerenciar o arquivo `banco.ini` e outras configurações.

**Funcionalidades:**
- Ativa/desativa conexões com um clique.  
- Criptografa credenciais em texto plano.  
- Atualiza scripts `.sql` com **hashes bcrypt**.  
- Permite visualizar e decifrar credenciais.  

---

### 🧪 3. Dashboard de Testes Unitários
Interface gráfica para **descoberta e execução de testes `unittest`**.

**Funcionalidades:**
- Descobre automaticamente `test_*.py`.  
- Executa todos, selecionados ou apenas os que falharam.  
- Exibe resultados detalhados (status, duração, logs).  

---

### 🧠 4. Dashboard de Testes Supremo
Ferramenta para **testes de estresse, concorrência e resiliência** com métricas detalhadas.

**Funcionalidades:**
- Executa diferentes suítes (Clássica, Paralela, Estresse de BD, etc).  
- Simula múltiplos usuários.  
- Coleta métricas de performance.  
- Exporta resultados em **CSV**.  

---

### 🩺 5. Ferramenta de Diagnóstico (Health Check)
GUI simples para verificar a integridade do ambiente de desenvolvimento.

**Funcionalidades:**
- Verifica arquivos e diretórios essenciais.  
- Testa conexão com o banco configurado.  
- Checa bibliotecas opcionais (ex: `GPUtil`).  

---

## 🏗️ Arquitetura e Fluxo de Dados

### Estrutura em Camadas
- **Apresentação:** `run.py`, `app.py`
- **View:** `panels/`, `modals/`, `dialogs/`
- **Controller:** `*_controller.py`
- **Model/Persistência:** `persistencia/`

---

### Exemplo de Fluxo — Salvando um item

1. Usuário preenche formulário na **View**.  
2. **Controller** (`inserir_item`) coleta dados e valida.  
3. Chama **Model** (`GenericRepository.write_dataframe_to_table`).  
4. Banco confirma → Controller atualiza View (`carregar_dados`).  

---

## 🧱 Estrutura do Projeto

```
/
├── app.py
├── run.py
├── config.py
├── banco.ini
├── settings.json
├── secret.key
│
├── panels/
│   ├── __init__.py
│   ├── base_panel.py
│   ├── painel_gestao_gatos_controller.py
│   └── painel_gestao_gatos_view.py
│
├── modals/
│   ├── tipos_vegetais_controller.py
│   ├── tipos_vegetais_view.py
│   └── tipos_vegetais_model.py
│
├── dialogs/
│   ├── login_ui.py
│   └── about_dialog.py
│
├── persistencia/
│   ├── database.py
│   ├── repository.py
│   ├── data_service.py
│   ├── auth.py
│   ├── security.py
│   └── sql_schema_.sql
│
└── utilParaDesenvolvimento/
    ├── credenciais_manager_gui.py
    ├── toolsDev/
    │   ├── run_generator.py
    │   ├── generator_ui.py
    │   ├── generator_logic.py
    │   └── templates/
    ├── toolTest/
    │   ├── dashboard_supremo.py
    │   ├── health_check_gui.py
    │   └── suites/
    └── toolTestU/
        ├── run_all_tests_gui.py
        ├── mock_dependencies.py
        └── test_.py
```

---

## 🗃️ Banco de Dados

O framework é **agnóstico ao SGBD**, suportando:

- SQLite  
- PostgreSQL  
- MySQL  
- MariaDB  
- SQL Server  
- Oracle  
- Firebird  

📁 Scripts SQL disponíveis em `persistencia/sql_schema_*.sql`.

---

## 🧩 Pré-requisitos

- Python **3.9+**
- `pip` (gerenciador de pacotes)

---

## ⚙️ Instalação e Execução

### 1️⃣ Clone o Repositório

```bash
git clone <url-do-seu-repositorio>
cd <nome-do-repositorio>
```

### 2️⃣ Crie e Ative o Ambiente Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Instale as Dependências

**Aplicação principal:**
```bash
pip install pandas sqlalchemy cryptography bcrypt
```

**Ferramentas de desenvolvedor (opcional):**
```bash
pip install jinja2 psutil gputil
```

**Driver do banco de dados (exemplo PostgreSQL):**
```bash
pip install psycopg2-binary
```

> 💡 Consulte o `banco.ini` para ver os drivers recomendados para cada SGBD.

### 4️⃣ Configure o Banco de Dados

1. Abra o arquivo `banco.ini`.  
2. Descomente a seção do banco desejado.  
3. Certifique-se de ativar **apenas uma seção**.  
4. Para SQLite, o arquivo `NexlifyTTk.db` é criado automaticamente.

### 5️⃣ Execute a Aplicação

```bash
python run.py
```

---

## 🪄 Primeiros Passos: Adicionando um Novo Painel

### Método 1 — Manual (Painel Modelo)
1. Copie:
   - `panels/painel_modelo_controller.py`
   - `panels/painel_modelo_view.py`
2. Renomeie as classes `PainelModelo` e `ModeloView`.  
3. Defina:
   - `PANEL_NAME`
   - `PANEL_ICON`
   - `ALLOWED_ACCESS`
4. Adicione widgets e lógica.  
5. Registre no arquivo `panels/__init__.py`.

### Método 2 — Automatizado (Gerador de Código)

1. Execute:
   ```bash
   python utilParaDesenvolvimento/toolsDev/run_generator.py
   ```
2. Na interface:
   - Escolha o tipo de componente (Painel ou Modal).
   - Selecione “MVC CRUD”.
   - Escolha a tabela e clique em **Gerar Painel**.

O gerador criará automaticamente os arquivos `controller`, `view` e `model`, além de registrar o painel.