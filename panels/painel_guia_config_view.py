import tkinter as tk
from tkinter import ttk, scrolledtext
from theme import C


class GuiaConfigView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text='Guia do template', font=('Segoe UI',18,'bold')).pack(anchor='w', padx=24, pady=20)
        text = scrolledtext.ScrolledText(self, wrap='word', font=('Segoe UI',11), relief='flat',
                                        bg=C['bg_darkest'], fg=C['fg_primary'], padx=20, pady=20)
        text.pack(fill='both', expand=True, padx=24, pady=(0,24))
        text.insert('end', '''INSTALAÇÃO
Use instalacao/setup.bat no Windows ou bash instalacao/setup.sh no Linux.
Escolha Operação ou Desenvolvimento e o modo local, cliente ou servidor. Na instalação local/servidor, escolha um banco; o instalador prepara a .venv e o driver necessário. No cliente, informe a URL HTTPS da API.
Depois, use iniciar.bat no Windows ou bash iniciar.sh no Linux. Cada sistema precisa da própria .venv.

BANCOS
SQLite dispensa servidor. PostgreSQL, MySQL, MariaDB, SQL Server, Oracle e Firebird usam servidores preparados separadamente. As tabelas são geradas pelo mesmo schema e a inicialização preserva os dados existentes.
A configuração local fica em banco.local.ini. Senhas são criptografadas ou lidas de uma variável de ambiente. Consulte docs/BANCOS.md para certificados e dependências nativas.

CONTA INICIAL E SENHAS
Uma instalação local com banco vazio pede a criação de admin no primeiro início. Na API, o responsável provisiona a conta no servidor. Não há senha padrão.
Use Aplicação → Trocar senha para alterar a própria senha. Somente o Administrador Global pode gerenciar outras contas.
Contas antigas com a senha compartilhada do template foram bloqueadas. No desenvolvimento, recupere admin pelo reset_admin.bat/reset_admin.sh na raiz e redefina as demais contas pela gestão de usuários.

ACESSO ÀS PÁGINAS
A barra lateral e o menu Painéis mostram apenas as páginas permitidas. O sistema também verifica a abertura direta e o acesso aos dados.
Administrador Global gerencia contas e perfis em Gestão de Usuários → Perfil de Acesso.
Administrador, Diretor de Operações, Gerente de TI e Analista de Dados acessam o cadastro de vegetais e a página de auditoria.
Supervisor e Operador acessam Gestão de Espécies e este guia.
Auditor Externo consulta espécies e Vegetais e Auditoria, sem gravar ou excluir dados.
Alterações de perfil ou senha exigem novo login. Uma sessão expirada ou revogada fecha as janelas protegidas.
Consulte docs/ACESSOS.md para a matriz completa.

PERFIL DE INSTALAÇÃO
Operação e Desenvolvimento são perfis da instalação, diferentes do perfil da conta. Instalar ferramentas DEV não concede privilégios ao usuário.
Painel Modelo e menu Desenvolvimento exigem Administrador Global, instalação dev, ambiente development e execução fora do modo cliente.

INTERFACE
Os painéis são carregados no primeiro acesso. Configurações → Seleção de tema permite escolher o visual. A posição da janela pode ser salva no menu Aplicação.
Informações do computador e Diagnóstico estão disponíveis ao Administrador e ao Gerente de TI.

E-MAIL E MFA
O MFA por e-mail vem desligado por padrão. Quando habilitado e cadastrado, o login envia um código temporário de seis dígitos para o endereço confirmado; não exige aplicativo no celular.
O Administrador configura o envio em Configurações → Envio de e-mail / SMTP na instalação local/servidor. Há dez presets e SMTP personalizado. Clientes HTTPS não configuram credenciais SMTP.
Configurar o envio não ativa o MFA. Com a função habilitada na instalação, use Aplicação → Ativar MFA por e-mail e guarde os códigos de recuperação. Consulte docs/EMAIL.md e docs/SEGURANCA_OPERACAO.md.

MANUTENÇÃO
Logs são rotacionados em logs/. Eventos de autenticação e alterações de dados são registrados. Faça backup do banco e guarde as chaves separadamente.
O reset do banco de desenvolvimento exige confirmação e gera backup verificado; não deve ser usado em produção.
Após uma atualização, feche e reabra a aplicação. No modo HTTPS, cliente e servidor precisam de versões compatíveis.

DOCUMENTAÇÃO
docs/README.md: índice completo.
docs/GUIA_USUARIO.md: uso diário, contas e problemas comuns.
docs/ACESSOS.md: permissões por perfil.
docs/MULTIPLATAFORMA.md e docs/BANCOS.md: instalação e banco.
docs/DESENVOLVIMENTO.md: arquitetura, novos painéis e testes.
docs/SEGURANCA.md: validações e limitações.
''')
        text.configure(state='disabled')
