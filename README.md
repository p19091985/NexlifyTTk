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
- **`panels/` (Módulos da UI):** Cada arquivo aqui representa uma tela ou funcionalidade principal da aplicação, como `painel_vegetais_auditoria_controller.py` e `painel_gestao_gatos_controller.py`, seguindo o padrão MVC.
- **`modals/` & `dialogs/` (Componentes de UI):** Contêm as janelas modais e diálogos, como a tela de login, a janela "Sobre" e os formulários de cadastro secundários (ex: `tipos_vegetais_controller.py`), também seguindo o padrão MVC.
- **Lógica de Modelo (Model):** A lógica de acesso aos dados para uma funcionalidade específica (Model) é encapsulada em arquivos como `tipos_vegetais_model.py`. Estes arquivos servem como a ponte entre o Controller e a camada de persistência e estão localizados junto aos seus componentes View e Controller correspondentes.
- **`persistencia/` (Camada de Acesso a Dados):** A camada mais baixa, responsável por toda a comunicação com o banco de dados.
  - `database.py`: Gerencia a criação da conexão (engine) do SQLAlchemy.
  - `repository.py`: Fornece métodos genéricos para CRUD (Create, Read, Update, Delete).
  - `data_service.py`: Orquestra operações complexas que envolvem múltiplos passos em uma única transação atômica, como `reclassificar_vegetal_e_logar`.
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