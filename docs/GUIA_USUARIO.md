# Guia do usuário

## Abrir e entrar

No Windows, execute `iniciar.bat`. No Linux, execute `bash iniciar.sh`. Os scripts usam a `.venv` da instalação. Se o ambiente ainda não estiver preparado, siga o [guia de instalação](MULTIPLATAFORMA.md).

Uma instalação local com banco vazio solicita a criação de `admin`. Não existe senha padrão. Em uma instalação cliente/servidor, o responsável provisiona a conta no servidor. Use a conta recebida do administrador; senhas temporárias precisam ser trocadas no primeiro acesso.

O MFA usa código por e-mail e vem desligado por padrão. Quando habilitado na instalação e cadastrado na conta, o login envia um código de seis dígitos para o endereço confirmado. Não é necessário aplicativo autenticador no celular. Consulte [MFA e recuperação](SEGURANCA_OPERACAO.md#mfa-senhas-e-reautenticação).

## Navegar pelas páginas

A barra lateral e o menu **Painéis** mostram as páginas permitidas para sua conta. Clique no nome para abrir. As telas são carregadas no primeiro acesso e verificadas novamente ao reabrir.

| Página | Uso |
| --- | --- |
| Cadastro de Vegetais | Cadastrar, consultar, editar e excluir vegetais nos perfis autorizados. |
| Gestão de Espécies (Gatos) | Exemplo de cadastro de espécies, edição e transação de renomeação. |
| Gestão de Usuários | Administrar contas, nomes, perfis e senhas; somente Administrador Global. |
| Guia de Configuração | Ajuda interna de instalação e utilização. |
| Vegetais e Auditoria | Consultar vegetais e eventos; executar operações permitidas ao perfil. |
| Painel Modelo | Referência para desenvolvimento, restrita ao administrador em instalação DEV. |

Consulte a [matriz completa de permissões](ACESSOS.md) para comparar os sete perfis. O Auditor Externo vê tabelas e atualização de consulta; não pode gravar dados nem modificar eventos. Uma página ausente pode ser uma restrição correta do perfil, não uma falha de instalação.

## Administrar contas e perfis

Entre como **Administrador Global** e abra **Gestão de Usuários**.

1. Para editar uma conta, selecione a linha na lista. Para criar uma conta, use **Limpar** e preencha login, nome, perfil e senha.
2. Escolha o **Perfil de Acesso** de acordo com as atividades da pessoa. A matriz é predefinida no template; a tela atribui perfis, não edita suas permissões.
3. Clique em **Salvar**. Ao editar uma conta, deixe a senha vazia se não quiser redefini-la.
4. Confirme sua identidade quando o sistema pedir reautenticação.

O login de uma conta existente não pode ser renomeado. O sistema protege o último administrador contra exclusão ou perda do perfil administrativo. Redefinir uma senha exige troca pelo titular; alterações de senha e perfil invalidam sessões anteriores. O usuário afetado precisa entrar novamente para receber os novos acessos.

Para excluir uma conta, selecione-a, clique em **Excluir** e confirme. Não use a exclusão como procedimento de recuperação de senha.

## Preferências e ferramentas

- **Aplicação → Salvar posição da janela** guarda a geometria.
- **Aplicação → Trocar senha** altera a senha da própria conta.
- **Aplicação → Trocar usuário** encerra a sessão e retorna ao fluxo de login.
- **Configurações → Seleção de tema / Fontes e preferências** personaliza a interface quando esse menu estiver habilitado.
- **Configurações → Informações do computador / Diagnóstico da instalação** está disponível ao Administrador e ao Gerente de TI.
- **Configurações → Envio de e-mail / SMTP** está disponível ao Administrador na instalação local/servidor. O cliente HTTPS não configura segredos SMTP.

Instalar o perfil `dev` não concede acesso administrativo. As ferramentas do menu **Desenvolvimento** exigem Administrador Global, instalação `dev`, ambiente `development` e execução fora do modo cliente.

## E-mail e MFA

A conta SMTP envia as mensagens do sistema; o e-mail cadastrado no MFA recebe os códigos do usuário. São configurações diferentes. O servidor oferece dez presets de provedores e SMTP personalizado; consulte [EMAIL.md](EMAIL.md).

Quando a instalação habilitar MFA, use **Aplicação → Ativar MFA por e-mail**, informe seu endereço e confirme o código. Guarde os códigos de recuperação em local protegido. Cada código recebido por e-mail vale cinco minutos e só pode ser usado uma vez. Configurar o SMTP sozinho não ativa o MFA.

## Problemas comuns

| Situação | Como proceder |
| --- | --- |
| Página ou menu ausente | Peça ao administrador que confira seu perfil na matriz. Ferramentas DEV também dependem da instalação e do ambiente. |
| Sessão encerrada ao mudar de página | Entre novamente. A sessão pode ter expirado, sido revogada por alteração da conta ou não ter sido validada pelo servidor. |
| Cliente não conecta | Confira com o responsável a disponibilidade da API e o certificado. Não desative a verificação TLS. |
| Código não chegou | Confira o endereço e o spam. Aguarde o intervalo de reenvio; use um código de recuperação guardado se necessário. O responsável pode testar o SMTP no servidor. |
| Conta bloqueada após erros | Aguarde cinco minutos antes de tentar de novo; confira as credenciais. |
| Esqueci a senha | Solicite redefinição ao administrador. O reset de `admin` na raiz é exclusivo de desenvolvimento; produção exige recuperação controlada. |
| `.venv` ausente ou incompatível | Execute o instalador correspondente ao sistema. Não copie ambientes virtuais entre Windows e Linux. |

Após atualização do projeto, feche e reabra o aplicativo para carregar o código novo. No modo HTTPS, o responsável deve manter cliente e servidor compatíveis. Documentos adicionais: [índice](README.md) e [operação segura](SEGURANCA_OPERACAO.md).
