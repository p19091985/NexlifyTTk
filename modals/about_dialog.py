import tkinter as tk
from tkinter import ttk
import webbrowser

class AboutDialog(tk.Toplevel):
    """
    Exibe informações detalhadas sobre a arquitetura e propósito do sistema.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Sobre o Sistema (v1.0.0)")

        self.transient(parent)
        self.grab_set()

                                      
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        self_width = 550
        self_height = 480

        pos_x = parent_x + (parent_width // 2) - (self_width // 2)
        pos_y = parent_y + (parent_height // 2) - (self_height // 2)

        self.geometry(f"{self_width}x{self_height}+{pos_x}+{pos_y}")
        self.resizable(False, False)

                                      
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=1)

                   
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(pady=(0, 15))
                                   
        ttk.Label(header_frame, text="🚀", font=("-size", 36)).pack(side="left", padx=(0, 10))
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side="left")
        ttk.Label(title_frame, text="Sistema de Demonstração Tkinter/ttk", font=("-size", 16, "-weight", "bold")).pack(anchor="w")
        ttk.Label(title_frame, text="Versão 1.0.0 - Arquitetura MVC/Camadas", font=("-size", 9)).pack(anchor="w")

        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=(0, 15))

                                     
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 15))

                        
        purpose_tab = ttk.Frame(notebook, padding=10)
        notebook.add(purpose_tab, text=" Propósito ")
        ttk.Label(purpose_tab, text=(
            "Esta aplicação é um boilerplate de referência, construído com Tkinter e o estilo ttk.\n"
            "Seu objetivo principal é demonstrar uma arquitetura de software desacoplada, baseada em "
            "padrões como MVC (Model-View-Controller), aplicada a um ambiente desktop Python.\n\n"
            "O foco do projeto é a clareza da separação de camadas, a manutenibilidade e a extensibilidade "
            "que essa estrutura proporciona."
            ), wraplength=self_width-60, justify="left").pack(anchor="w")

                          
        arch_tab = ttk.Frame(notebook, padding=10)
        notebook.add(arch_tab, text=" Arquitetura ")
        ttk.Label(arch_tab, text=(
            "O sistema é estruturado em camadas bem definidas:\n\n"
            "■ UI (Interface): Tkinter/ttk (Views, Dialogs, Modals)\n"
            "   ↳ Responsável pela apresentação visual e interação primária.\n\n"
            "■ Controle (Lógica de Apresentação) (`panels`):\n"
            "   ↳ Cada 'Painel' atua como um Controller, gerenciando o estado da UI,\n"
            "      respondendo a eventos e comunicando-se com a camada de persistência.\n\n"
            "■ Persistência (`persistencia`):\n"
            "   ↳ Abstrai o acesso aos dados, garantindo independência do banco.\n"
            "   ↳ `Repository`: CRUD genérico via SQLAlchemy Core.\n"
            "   ↳ `DataService`: Transações atômicas e lógica de negócio complexa.\n"
            "   ↳ `Database`: Gerencia a conexão (lê `banco.ini`).\n"
            "   ↳ `Auth/Security`: Cuida da autenticação (bcrypt) e criptografia (Fernet).\n\n"
            "■ Configuração (`config.py`, `banco.ini`, `settings.json`):\n"
            "   ↳ Permite flexibilidade em tempo de execução e deployment."
            ), wraplength=self_width-60, justify="left").pack(anchor="w")

                        
        features_tab = ttk.Frame(notebook, padding=10)
        notebook.add(features_tab, text=" Destaques ")
        ttk.Label(features_tab, text=(
            "Pontos Notáveis:\n\n"
            "▶ **Multi-Banco:** Suporte nativo a SQLite, PostgreSQL, MySQL/MariaDB\n"
            "   e SQL Server, configurável via `banco.ini`.\n"
            "▶ **Segurança:** Senhas de usuário hasheadas (bcrypt) e credenciais\n"
            "   de banco criptografadas (Fernet).\n"
            "▶ **Desacoplamento:** Clara separação entre UI, lógica e dados.\n"
            "▶ **Configurabilidade:** Flags em `config.py` para modos de operação\n"
            "   (Produção, Dev Backend, Dev Frontend Offline).\n"
            "▶ **Estilo Personalizável:** Configuração de fontes e cores via\n"
            "   `settings.json` e diálogo de tema avançado.\n"
            "▶ **Validação:** Verificação automática de configurações lógicas ao iniciar."
            ), wraplength=self_width-60, justify="left").pack(anchor="w")


                  
        ok_button = ttk.Button(main_frame, text="OK", command=self.destroy, style="Success.TButton")
        ok_button.pack(pady=(10, 0))
        ok_button.focus_set()

        self.wait_window(self)