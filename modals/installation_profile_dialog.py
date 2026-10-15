import tkinter as tk
from tkinter import ttk
from utils.installation_profile import load_installation_profile


class InstallationProfileDialog(tk.Toplevel):
    def __init__(self, parent, project_root):
        super().__init__(parent)
        self.title('Instalação ativa')
        self.transient(parent)
        info = load_installation_profile(project_root)
        from persistencia.database import read_database_config
        import config
        text = (f"Perfil: {info['title']}\nAmbiente: {config.ENVIRONMENT}\n"
                f"Banco configurado: {read_database_config().get('type', 'sqlite')}\n\n"
                'Operação: aplicação, temas e diagnóstico.\n'
                'Desenvolvimento: testes, monitor e configuração.\n'
                'O perfil de instalação não substitui as permissões do usuário.')
        ttk.Label(self, text=text, padding=24, justify='left').pack()
        ttk.Button(self, text='Fechar', command=self.destroy).pack(pady=12)
        self.grab_set()
