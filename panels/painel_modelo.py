import tkinter as tk
from tkinter import ttk, messagebox
from panels.base_panel import BasePanel


# Não precisamos mais importar a View, pois ela está nesta classe.


class PainelModelo(BasePanel):
    """
    Controller e View unificados.
    Este é o painel 'modelo' que serve como template para novos painéis.
    """
    PANEL_NAME = "Painel Modelo"
    PANEL_ICON = "📋"
    ALLOWED_ACCESS = []  # Deixe vazio para permitir acesso a todos

    def __init__(self, parent, app_controller, **kwargs):
        super().__init__(parent, app_controller, **kwargs)

    def create_widgets(self):
        """
        Método principal que constrói a UI do painel.
        """
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        titulo = ttk.Label(main_frame, text="Estrutura de um Novo Painel (Unificado)",
                           font=("-size", 16, "-weight", "bold"))
        titulo.pack(pady=(0, 20))

        conteudo_frame = ttk.LabelFrame(main_frame, text=" Guia Rápido (Padrão Simplificado) ", padding=15)
        conteudo_frame.pack(fill="both", expand=True, pady=10)

        # --- TEXTO DE INSTRUÇÃO ATUALIZADO ---
        # Agora ele reflete o nosso novo padrão de arquivo único.
        instrucoes_texto = (
            "Este painel serve como um ponto de partida para novas telas.\n\n"
            "Passos para criar um novo painel:\n"
            "1. Copie este arquivo (`painel_modelo.py`) para um novo nome.\n"
            "   (Ex: `painel_meu_painel_controller.py`)\n\n"
            "2. Renomeie a classe (Ex: `PainelMeuPainel`).\n\n"
            "3. Altere as constantes de classe `PANEL_NAME`, `PANEL_ICON` e `ALLOWED_ACCESS`.\n\n"
            "4. Adicione seus widgets no método `create_widgets()` e sua lógica\n"
            "   em novos métodos (como `_on_botao_click`).\n\n"
            "5. Registre sua nova classe no arquivo `panels/__init__.py`."
        )
        instrucoes_label = ttk.Label(conteudo_frame, text=instrucoes_texto, justify="left")
        instrucoes_label.pack(pady=10)

        # Comando direto: self._on_botao_click (não self.controller._on_botao_click)
        botao_exemplo = ttk.Button(conteudo_frame, text="Testar Interação",
                                   command=self._on_botao_click, style="Success.TButton")
        botao_exemplo.pack(pady=20)

    def _on_botao_click(self):
        """Lógica de evento chamada diretamente pelo botão."""
        # self.app é herdado de BasePanel
        usuario_atual = self.app.get_current_user()

        # --- MENSAGEM ATUALIZADA ---
        messagebox.showinfo(
            "Interação Funcionou!",
            f"Olá, {usuario_atual['name']}!\n\nO painel modelo no padrão UNIFICADO está funcionando corretamente.",
            parent=self
        )