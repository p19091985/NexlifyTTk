import tkinter as tk
from tkinter import ttk, font
from tkinter import scrolledtext
import sys

class GuiaConfigView(ttk.Frame):
    """
    A View que exibe o Guia de Configuração: um guia detalhado e estilizado
    sobre as flags e modos de operação da aplicação.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        titulo = ttk.Label(main_frame, text="⚙️ Guia de Configuração e Modos de Operação", font=("-size", 18, "-weight", "bold"))
        titulo.pack(pady=(0, 20), anchor="w")

                                       
        text_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=20,
                                              font=("Segoe UI", 10), bd=0, relief=tk.FLAT,
                                              padx=15, pady=15, background="white")
        text_area.pack(fill="both", expand=True, pady=10)

                                         
        code_font = "Consolas" if "Consolas" in font.families() else "Courier New"
        header_font_family = "Segoe UI Semibold" if "Segoe UI Semibold" in font.families() else "Segoe UI"
        subheader_font_family = "Segoe UI Semibold" if "Segoe UI Semibold" in font.families() else "Segoe UI"

        text_area.tag_configure("h1", font=(header_font_family, 16, "bold"), spacing1=20, spacing3=10, foreground="#003366")
        text_area.tag_configure("h2", font=(subheader_font_family, 13, "bold"), spacing1=15, spacing3=8, foreground="#005a9e")
        text_area.tag_configure("h3", font=("Segoe UI", 11, "bold"), spacing1=10, spacing3=5, foreground="#333333")
        text_area.tag_configure("code", font=(code_font, 9), background="#f5f5f5", wrap=tk.NONE,
                                lmargin1=25, lmargin2=25, borderwidth=1, relief=tk.SOLID,
                                spacing1=8, spacing3=8, tabs=("1c", "2c", "3c"))
        text_area.tag_configure("bold", font=("Segoe UI", 10, "bold"))
        text_area.tag_configure("italic", font=("Segoe UI", 10, "italic"))
        text_area.tag_configure("body", lmargin1=10, lmargin2=10, spacing3=6)
        text_area.tag_configure("note", lmargin1=20, lmargin2=20, foreground="#555555", font=("Segoe UI", 9, "italic"), spacing3=8)
        text_area.tag_configure("flag", font=(code_font, 10, "bold"), foreground="#cc0000")                          
        text_area.tag_configure("success", foreground="#155724", font=("Segoe UI", 10, "bold"))
        text_area.tag_configure("danger", foreground="#721c24", font=("Segoe UI", 10, "bold"))
        text_area.tag_configure("warning", foreground="#856404", font=("Segoe UI", 10, "bold"))
        text_area.tag_configure("info", foreground="#004085")

                                  

                    
        text_area.insert(tk.END, "Guia de Configuração da Aplicação\n", "h1")
        text_area.insert(tk.END,
                         "Esta aplicação foi desenvolvida com flexibilidade. As flags de configuração, localizadas no arquivo ", "body")
        text_area.insert(tk.END, "config.py", "code")
        text_area.insert(tk.END,
                         ", permitem ajustar o comportamento do sistema para cenários de desenvolvimento, teste ou produção.\n\n", "body")
        text_area.insert(tk.END, "🛡️ Sistema de Validação Integrado:\n", ("h3", "info"))
        text_area.insert(tk.END,
                         "Ao iniciar (`run.py`), um validador verifica a coerência das flags. Combinações inválidas (como exigir autenticação sem um banco de dados) são interceptadas, exibindo um alerta claro sobre a correção necessária.\n", "body")

                                
        text_area.insert(tk.END, "1. Detalhamento das Flags (`config.py`)\n", "h2")
        text_area.insert(tk.END,
                         "Para alterar o modo de operação, edite os valores (`True` ou `False`) no arquivo ", "body")
        text_area.insert(tk.END, "config.py", "code")
        text_area.insert(tk.END, " e reinicie a aplicação.\n\n", "body")

                          
        text_area.insert(tk.END, "DATABASE_ENABLED\n", "flag")
        text_area.insert(tk.END, "   ↳ Controla a Conexão de Dados\n", "italic")
        text_area.insert(tk.END, "   ▪ ", "body")
        text_area.insert(tk.END, "True:", "bold")
        text_area.insert(tk.END, " (Produção / Dev Backend) Abre a conexão com o banco definido em ", "body")
        text_area.insert(tk.END, "banco.ini", "code")
        text_area.insert(tk.END, ". Funções que dependem de dados (CRUD, login) são ativadas.\n", "body")
        text_area.insert(tk.END, "   ▪ ", "body")
        text_area.insert(tk.END, "False:", "bold")
        text_area.insert(tk.END, " (Dev Frontend / Offline) Desativa a conexão. A aplicação opera sem banco, ideal para focar na interface. Funcionalidades de dados exibirão avisos.\n\n", "body")

                   
        text_area.insert(tk.END, "USE_LOGIN\n", "flag")
        text_area.insert(tk.END, "   ↳ Controla a Autenticação\n", "italic")
        text_area.insert(tk.END, "   ▪ ", "body")
        text_area.insert(tk.END, "True:", "bold")
        text_area.insert(tk.END, " (Produção) Exige que o usuário se autentique. Permissões de acesso são aplicadas. ", "body")
        text_area.insert(tk.END, "Requer DATABASE_ENABLED = True.\n", ("body", "warning"))
        text_area.insert(tk.END, "   ▪ ", "body")
        text_area.insert(tk.END, "False:", "bold")
        text_area.insert(tk.END, " (Dev Rápido) Pula a tela de login. O acesso é concedido automaticamente com um usuário mock de 'Administrador Global', acelerando testes internos.\n\n", "body")

                                        
        text_area.insert(tk.END, "INITIALIZE_DATABASE_ON_STARTUP\n", "flag")
        text_area.insert(tk.END, "   ↳ Criação Automática do Schema (Somente SQLite)\n", "italic")
        text_area.insert(tk.END, "   ▪ ", "body")
        text_area.insert(tk.END, "True:", "bold")
        text_area.insert(tk.END, " (Setup Inicial / Testes) Se o arquivo SQLite estiver ausente ou vazio, cria as tabelas e dados iniciais do script ", "body")
        text_area.insert(tk.END, "sql_schema_SQLLite.sql", "code")
        text_area.insert(tk.END, ". ", "body")
        text_area.insert(tk.END, "Requer DATABASE_ENABLED = True.\n", ("body", "warning"))
        text_area.insert(tk.END, "   ▪ ", "body")
        text_area.insert(tk.END, "False:", "bold")
        text_area.insert(tk.END, " (Padrão Seguro / Produção) Assume que o banco de dados já existe e está pronto. Essencial para bancos de dados externos ou SQLite já populados.\n", "body")
        text_area.insert(tk.END, "      ↳ ", "note")
        text_area.insert(tk.END, "Não use True em produção se o banco já contém dados valiosos!\n\n", "note")

                                 
        text_area.insert(tk.END, "REDIRECT_CONSOLE_TO_LOG\n", "flag")
        text_area.insert(tk.END, "   ↳ Direcionamento de Saída (Logs)\n", "italic")
        text_area.insert(tk.END, "   ▪ ", "body")
        text_area.insert(tk.END, "True:", "bold")
        text_area.insert(tk.END, " (Produção / Debug Centralizado) Saídas do console (`print`, erros) são redirecionadas para os arquivos de log rotativos em ", "body")
        text_area.insert(tk.END, "logs/", "code")
        text_area.insert(tk.END, ". Mantém o terminal limpo.\n", "body")
        text_area.insert(tk.END, "   ▪ ", "body")
        text_area.insert(tk.END, "False:", "bold")
        text_area.insert(tk.END, " (Debug Rápido) As saídas aparecem diretamente no terminal onde a aplicação foi iniciada. Útil para visibilidade imediata.\n\n", "body")

                         
        text_area.insert(tk.END, "2. Cenários de Configuração Comuns\n", "h2")

                           
        text_area.insert(tk.END, "✅ Modo Produção (Ambiente Real)\n", ("h3", "success"))
        text_area.insert(tk.END, "   ↳ Objetivo: Ambiente final, seguro, com dados reais e persistentes.\n", "body")
        text_area.insert(tk.END,
                         "DATABASE_ENABLED = True\n"
                         "USE_LOGIN = True\n"
                         "INITIALIZE_DATABASE_ON_STARTUP = False\n"
                         "REDIRECT_CONSOLE_TO_LOG = True", "code")
        text_area.insert(tk.END, "\n   ↳ Comportamento: Exige login, conecta ao banco real, aplica permissões, registra tudo em arquivos. Máxima segurança e funcionalidade.\n\n", "body")

                              
        text_area.insert(tk.END, "✅ Modo Desenvolvimento (Backend)\n", ("h3", "info"))
        text_area.insert(tk.END, "   ↳ Objetivo: Desenvolver/testar lógica de dados, serviços, regras de negócio com acesso rápido.\n", "body")
        text_area.insert(tk.END,
                         "DATABASE_ENABLED = True\n"
                         "USE_LOGIN = False\n"
                         "INITIALIZE_DATABASE_ON_STARTUP = True  # Opcional, ótimo com SQLite para reset\n"
                         "REDIRECT_CONSOLE_TO_LOG = False", "code")
        text_area.insert(tk.END, "\n   ↳ Comportamento: Conecta ao banco (podendo recriá-lo se SQLite+True), pula login (usuário Admin mock). Ideal para testar CRUD e transações sem barreiras.\n\n", "body")

                               
        text_area.insert(tk.END, "✅ Modo Desenvolvimento (Frontend/Offline)\n", ("h3", "info"))
        text_area.insert(tk.END, "   ↳ Objetivo: Focar no design visual e experiência do usuário (UI/UX) sem dependência do banco.\n", "body")
        text_area.insert(tk.END,
                         "DATABASE_ENABLED = False\n"
                         "USE_LOGIN = False\n"
                         "INITIALIZE_DATABASE_ON_STARTUP = False # Obrigatório!\n"
                         "REDIRECT_CONSOLE_TO_LOG = False", "code")
        text_area.insert(tk.END, "\n   ↳ Comportamento: Operação sem banco. Login pulado. Painéis que precisam de dados exibirão avisos, mas a navegação e a interface funcionarão.\n\n", "body")

                            
        text_area.insert(tk.END, "❌ Cenários Inválidos (Bloqueados Automaticamente)\n", ("h2", "danger"))
        text_area.insert(tk.END, "   ↳ O validador (`run.py`) impede o início se detectar estas combinações:\n\n", "body")

        text_area.insert(tk.END, "Inválido 1: Exigir Login Sem Banco de Dados\n", "h3")
        text_area.insert(tk.END,
                         "DATABASE_ENABLED = False\n"
                         "USE_LOGIN = True", "code")
        text_area.insert(tk.END, "\n   ↳ Motivo: Impossível validar um usuário sem acesso ao banco de dados que contém suas credenciais.\n\n", "body")

        text_area.insert(tk.END, "Inválido 2: Inicializar Banco de Dados Desativado\n", "h3")
        text_area.insert(tk.END,
                         "DATABASE_ENABLED = False\n"
                         "INITIALIZE_DATABASE_ON_STARTUP = True", "code")
        text_area.insert(tk.END, "\n   ↳ Motivo: Não se pode criar estruturas (`True`) se o acesso ao banco está desabilitado (`False`).\n\n", "body")

                     
        text_area.insert(tk.END, "--- Fim do Guia ---\n", ("italic", "body"))

                           
        text_area.config(state="disabled")