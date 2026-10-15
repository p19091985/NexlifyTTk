                              
from tkinter import ttk

class ModeloView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        titulo = ttk.Label(main_frame, text="Estrutura de um Novo Painel (MVC)", font=("-size", 16, "-weight", "bold"))
        titulo.pack(pady=(0, 20))

        conteudo_frame = ttk.LabelFrame(main_frame, text=" Guia Rápido ", padding=15)
        conteudo_frame.pack(fill="both", expand=True, pady=10)

        instrucoes_texto = (
            "Este painel serve como um ponto de partida para novas telas no padrão MVC.\n\n"
            "Passos para criar um novo painel:\n"
            "1. Copie `painel_modelo_controller.py` e `painel_modelo_view.py` para novos arquivos.\n"
            "2. Renomeie as classes (Controller e View) nos dois arquivos.\n"
            "3. No Controller, altere `PANEL_NAME` e `PANEL_ICON`.\n"
            "4. Adicione seus widgets na classe View e a lógica no Controller.\n"
            "5. Registre a classe Controller no arquivo `panels/__init__.py`.\n"
            "6. Cadastre o PANEL_NAME e os perfis em `persistencia/access_policy.py`.\n"
            "7. Proteja as tabelas da página nessa política e teste acessos permitidos e negados.\n"
            "Páginas sem regra explícita ficam bloqueadas para todos os perfis."
        )
        instrucoes_label = ttk.Label(conteudo_frame, text=instrucoes_texto, justify="left")
        instrucoes_label.pack(pady=10)

        botao_exemplo = ttk.Button(conteudo_frame, text="Testar Interação", command=self.controller._on_botao_click, style="Success.TButton")
        botao_exemplo.pack(pady=20)
