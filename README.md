# **✨ nexlifyttk ✨ — Template Desktop Python com Arquitetura de Painéis**

**nexlifyttk** é um *boilerplate* Python projetado para o desenvolvimento de aplicações desktop usando o *toolkit* nativo **Tkinter/ttk**. O projeto demonstra uma arquitetura limpa e extensível baseada em painéis, com foco em manutenibilidade e clareza de código.

Este documento detalha a arquitetura, a estrutura de diretórios e como estender o sistema.

## **🏛️ 1. Arquitetura do Sistema**

O nexlifyttk utiliza uma **Arquitetura de Painéis Unificados**, onde cada funcionalidade da aplicação é encapsulada em um painel independente que combina sua própria interface (View) e lógica (Controller).

| Camada | Módulos Principais | Responsabilidade |
| :--- | :--- | :--- |
| **Ponto de Entrada** | `run.py` | Inicialização da aplicação, setup de loggers. |
| **Controlador Principal** | `app.py` | Janela raiz, sidebar, navegação entre painéis, menus. |
| **Painéis** | `panels/*.py` | Cada painel implementa sua UI e lógica de forma unificada. |
| **Modais / Diálogos** | `modals/*.py`, `dialogs/*.py` | Janelas auxiliares (ex: diálogo "Sobre"). |
| **Configuração** | `config.py`, `config_settings.ini`, `settings.json` | Configuração de comportamento e estilo visual. |
| **Logging** | `persistencia/logger.py` | Sistema de log rotativo com separação por categorias. |

### **1.1. Padrão de Painéis Unificados**

Cada painel segue o padrão **Painel Unificado (View + Controller)**:

* **Herança**: Todo painel herda de `BasePanel` (que herda de `ttk.Frame`).
* **Contrato**: O método `create_widgets()` é o ponto de entrada obrigatório que constrói a interface.
* **Referência ao App**: Via `self.app`, cada painel pode acessar serviços do controlador principal.
* **Registro**: Painéis são registrados em `panels/__init__.py` na lista `ALL_PANELS`.

### **1.2. Controlador Principal (app.py)**

O `app.py` atua como **Facade** da aplicação:

* Gerencia a **sidebar** com botões de navegação para cada painel.
* Controla a **troca de painéis** (mostra/oculta painéis conforme seleção).
* Aplica o **tema visual** (fontes, cores) a partir do `settings.json`.
* Cria a **barra de menus** com acesso rápido a painéis, configurações e ajuda.

## **🗂️ 2. Estrutura de Diretórios**

```
/
├── run.py                     # Ponto de entrada — inicializa loggers e a aplicação.
├── app.py                     # Controlador principal / janela raiz (Facade).
├── config.py                  # Leitura de configurações do config_settings.ini.
├── config_settings.ini        # Configurações de comportamento (logging, tema).
├── settings.json              # Configurações de estilo visual (fontes, cores).
├── settings_manager.py        # Gerenciador de leitura/escrita do settings.json.
│
├── panels/                    # Painéis da aplicação.
│   ├── __init__.py            # Registro de painéis em ALL_PANELS.
│   ├── base_panel.py          # Classe base abstrata para todos os painéis.
│   ├── painel_modelo.py       # Painel template — referência para criar novos painéis.
│   └── painel_guia_config.py  # Guia interativo de configuração.
│
├── modals/                    # Janelas modais.
│   └── about_dialog.py        # Diálogo "Sobre" com informações do sistema.
│
├── dialogs/                   # Diálogos simples (atualmente vazio).
│
├── persistencia/              # Infraestrutura.
│   └── logger.py              # Configuração do sistema de logging rotativo.
│
└── logs/                      # Arquivos de log gerados automaticamente.
```

## **⚙️ 3. Configuração**

### **3.1. `config_settings.ini`**

| Configuração | Tipo | Padrão | Descrição |
| :--- | :--- | :--- | :--- |
| `redirect_console_to_log` | Boolean | `False` | Redireciona `stdout`/`stderr` para arquivos de log. |
| `enable_theme_menu` | Boolean | `True` | Exibe opções de personalização de tema no menu. |

### **3.2. `settings.json`**

Controla a aparência visual da aplicação:

* **`font_family`**: Família da fonte (ex: `Segoe UI`, `Arial`).
* **`font_size`**: Tamanho da fonte em pontos.
* **`custom_colors`**: Cores personalizadas para estilos de botão (`danger`, `success`, `warning`, `info`, `secondary`).

## **🚀 4. Instalação e Execução**

### **Pré-requisitos**

* **Python**: 3.9 ou superior
* **Sistema Operacional**: Windows, Linux ou macOS

### **Instalação**

```bash
# Crie e ative um ambiente virtual
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### **Execução**

```bash
python run.py
```

A aplicação abrirá diretamente na janela principal com a sidebar de navegação entre painéis.

## **✨ 5. Extensibilidade — Como Criar Novos Painéis**

Para adicionar novas funcionalidades, siga o template do **Painel Modelo** (`painel_modelo.py`):

1. **Copie** o arquivo `painel_modelo.py` para `painel_meu_painel.py`.
2. **Renomeie** a classe para `PainelMeuPainel`.
3. **Defina** `PANEL_NAME` (nome exibido na sidebar) e `PANEL_ICON` (emoji).
4. **Implemente** o método `create_widgets()` com sua interface.
5. **Registre** o novo painel em `panels/__init__.py`:

```python
from .painel_meu_painel import PainelMeuPainel

ALL_PANELS = [
    PainelModelo,
    PainelGuiaConfig,
    PainelMeuPainel,   # ← Novo painel
]
```

### **Convenções de Métodos**

| Prefixo | Propósito | Exemplo |
| :--- | :--- | :--- |
| `_build_*` | Criação de widgets e layout | `_build_form(frame)` |
| `_load_*` / `_get_*` | Busca ou coleta de dados | `_load_data_into_table()` |
| `_on_*` | Tratamento de eventos | `_on_save_button_click()` |

## **📦 6. Dependências**

| Pacote | Função |
| :--- | :--- |
| `pillow` | Manipulação de imagens. |
| `psutil` | Informações do sistema. |
| `ttkbootstrap` | Estilização avançada do Tkinter. |

## **📝 7. Licença**

Consulte o arquivo `LICENSE` para informações sobre a licença do projeto.
