# panels/painel_06.py
import tkinter as tk
from tkinter import ttk
from panels.base_panel import BasePanel


# Para usar componentes do ttkbootstrap, descomente a linha abaixo
# import ttkbootstrap as bstrap


class PainelEsqueleto(BasePanel):
    """
    Este é um painel de modelo (esqueleto) para a criação de novas telas.
    Copie este arquivo para criar um novo painel.
    """
    # 1. Defina o nome que aparecerá na barra lateral e no menu
    PANEL_NAME = "Painel Esqueleto"

    # 2. Escolha um ícone para o painel
    PANEL_ICON = "📋"

    # 3. Defina os perfis de utilizador que podem aceder a este painel.
    #    Deixe a lista vazia `[]` para permitir o acesso a todos.
    ALLOWED_ACCESS = []

    def __init__(self, parent, app_controller, **kwargs):
        """
        O construtor do painel. A chamada super().__init__ é essencial.
        """
        # Não se esqueça de chamar o __init__ da classe pai (BasePanel)
        super().__init__(parent, app_controller, **kwargs)

        # Aqui você pode inicializar variáveis de estado específicas deste painel, se necessário
        # Ex: self.dados_do_grafico = None

    def create_widgets(self):
        """
        Este é o método principal onde a interface do seu painel é construída.
        """
        # --- Início da Área de Criação de Widgets ---

        # É uma boa prática criar um frame principal com padding
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Exemplo de um título para o seu painel
        titulo = ttk.Label(
            main_frame,
            text="Este é o seu Novo Painel",
            font=("-size", 16, "-weight", "bold")
        )
        titulo.pack(pady=(0, 20))

        # Exemplo de um frame para organizar o conteúdo
        conteudo_frame = ttk.LabelFrame(main_frame, text=" Área de Conteúdo ", padding=15)
        conteudo_frame.pack(fill="both", expand=True)

        instrucoes = ttk.Label(
            conteudo_frame,
            text="Adicione aqui os seus widgets, como botões, campos de entrada, tabelas, etc.",
            wraplength=400  # Faz com que o texto quebre a linha automaticamente
        )
        instrucoes.pack(pady=10)

        # Exemplo de um botão que chama um método deste painel
        botao_exemplo = ttk.Button(
            conteudo_frame,
            text="Clique-me",
            command=self._on_botao_exemplo_click,
            style="success.TButton"
        )
        botao_exemplo.pack(pady=10)

        # --- Fim da Área de Criação de Widgets ---

    # É uma boa prática usar métodos privados (com _ no início) para os handlers de eventos
    def _on_botao_exemplo_click(self):
        """
        Este método é chamado quando o 'botao_exemplo' é clicado.
        """
        # Use o messagebox do tkinter para feedback ao utilizador
        from tkinter import messagebox
        messagebox.showinfo("Aviso", "O botão de exemplo foi clicado!", parent=self)

        # Exemplo de como aceder a métodos da aplicação principal (app_controller)
        # usuario_atual = self.app.get_current_user()
        # print(f"Botão clicado pelo utilizador: {usuario_atual['name']}")