# Configuração e envio de e-mail

O template oferece **dez provedores populares com SMTP e a opção SMTP personalizado**, tanto no Windows quanto no Linux. A seleção preenche parâmetros iniciais; a conta precisa autorizar o acesso e atender ao plano e método de autenticação do provedor. O catálogo não representa uma classificação por quantidade de usuários.

O envio é configurado **na máquina do servidor ou da aplicação local**. Clientes da API não leem credenciais SMTP nem executam envios diretamente. Configurar e-mail não ativa o MFA; ele permanece desligado por padrão.

## Provedores disponíveis

Parâmetros conferidos na documentação dos provedores em 15/10/2026. Os links de cada linha são as referências da configuração.

| Provedor | Servidor inicial | Porta / segurança | Autenticação e condições |
| --- | --- | --- | --- |
| [Gmail / Google Workspace](https://support.google.com/mail/answer/7104828) | `smtp.gmail.com` | 587 / STARTTLS | Senha de aplicativo, quando permitida. Exige verificação em duas etapas para gerar essa senha; consulte [senhas de aplicativo Google](https://support.google.com/accounts/answer/185833). |
| [Outlook / Hotmail / Live](https://support.microsoft.com/en-au/outlook/pop-imap-and-smtp-settings-for-outlook-com) | `smtp-mail.outlook.com` | 587 / STARTTLS | OAuth2 obrigatório. Assistente de conexão Microsoft disponível. |
| [Yahoo Mail](https://help.yahoo.com/kb/SLN3217.html) | `smtp.mail.yahoo.com` | 465 / TLS direto | Senha de aplicativo Yahoo. |
| [iCloud Mail](https://support.apple.com/102525) | `smtp.mail.me.com` | 587 / STARTTLS | Endereço completo e senha específica de aplicativo Apple. |
| [Zoho Mail](https://www.zoho.com/mail/help/zoho-smtp.html) | `smtp.zoho.com` | 465 / TLS direto | Preset pessoal do datacenter US. Domínios empresariais podem usar `smtppro.zoho.com`; confirme plano, região e servidor no painel da conta. |
| [AOL Mail](https://help.aol.com/articles/how-do-i-use-other-email-applications-to-send-and-receive-my-aol-mail) | `smtp.aol.com` | 465 / TLS direto | Senha de aplicativo AOL. |
| [GMX](https://support.gmx.com/pop-imap/imap/server.html) | `mail.gmx.com` | 587 / STARTTLS | Preset internacional. Confira a liberação de clientes externos e senha de aplicativo quando exigida. |
| [mail.com](https://support.mail.com/premium/imap/server.html) | `smtp.mail.com` | 587 / STARTTLS | Acesso por clientes externos depende do plano Premium. |
| [Fastmail](https://www.fastmail.help/hc/en-us/articles/1500000278342-Server-names-and-ports) | `smtp.fastmail.com` | 465 / TLS direto | Senha de aplicativo e plano com acesso SMTP; Basic não inclui esse acesso. |
| [Yandex Mail](https://yandex.com/support/yandex-360/customers/mail/en/mail-clients/others) | `smtp.yandex.com` | 465 / TLS direto | Libere clientes externos e gere senha de aplicativo Mail no Yandex ID. |
| SMTP personalizado | Informado pelo administrador | Porta configurável / STARTTLS ou TLS direto | Senha ou OAuth2 com refresh token. Aceita servidor próprio e arquivo de CA privada para SMTP. |

O campo `ssl` da configuração representa conexão TLS direta, normalmente na porta 465. `starttls` inicia a sessão SMTP e exige a negociação TLS antes de enviar credenciais ou mensagens. Certificado e hostname são sempre verificados. Não há opção de conexão aberta sem TLS.

## Configuração pela interface

Na aplicação local, entre como Administrador Global e abra **Configurações → Envio de e-mail / SMTP**. A tela revalida a identidade e pede reautenticação quando necessário.

A restrição vale também para a abertura direta da tela: perfil de instalação DEV não concede acesso SMTP a outros usuários. No cliente HTTPS, a configuração é feita na máquina do servidor pelo responsável, não por esse menu. Consulte a [matriz de permissões](ACESSOS.md) e o [guia do usuário](GUIA_USUARIO.md) para distinguir a conta remetente SMTP do endereço que recebe códigos MFA.

1. Selecione o provedor ou **SMTP personalizado**.
2. Confira host, porta e segurança. Preencha o remetente autorizado pelo provedor e o usuário SMTP.
3. Na aba **Autenticação**, informe a senha de aplicativo ou conecte a conta OAuth2.
4. Marque **Habilitar envio por esta conta** e salve.
5. Informe o destinatário e clique em **Enviar e-mail de teste**. Essa ação envia uma única mensagem de teste; confira também a pasta de spam.

O teste usa os valores atuais da tela e pode ser feito antes de salvar. A mensagem de sucesso significa que o servidor SMTP aceitou a mensagem; não confirma a entrega na caixa de entrada.

Senhas e tokens salvos não são exibidos. Campos secretos em branco preservam a credencial somente se conta, destino e parâmetros de autenticação permanecerem iguais. Mudar o servidor ou a conta exige informar novamente a credencial. Os próximos envios usam a configuração salva, sem reiniciar o aplicativo. O estado do MFA continua independente.

## Configuração diretamente no servidor

Execute na raiz, usando o Python da `.venv`:

```text
python -m instalacao.config_email
python -m instalacao.config_email --headless
python -m instalacao.config_email --list
python -m instalacao.config_email --test-to destinatario@seu-dominio.example
```

O primeiro comando abre a tela. `--headless` oferece um assistente interativo sem Tk; senhas e tokens são solicitados sem eco e não entram nos argumentos do processo. `--list` mostra apenas o catálogo público. `--test-to` envia uma mensagem real com a configuração efetiva.

No Windows, substitua `python` por `.venv\Scripts\python.exe`. No Linux, use `.venv/bin/python`. Os pacotes local e servidor incluem esse utilitário. O pacote cliente não inclui o configurador de servidor.

O utilitário independente é uma ferramenta de administração da máquina, assim como o provisionamento do banco: o acesso é autorizado pela conta do sistema operacional que controla a instalação. Não é exposto por RPC e não exige um usuário do aplicativo, permitindo configurar o SMTP antes do primeiro login/MFA.

## Conectar Outlook / Hotmail

O preset usa OAuth2 delegado para contas pessoais Microsoft. O procedimento requer registrar o aplicativo da sua instalação; não existe um client ID compartilhado embutido no template.

1. Registre o aplicativo no Microsoft Entra com suporte a contas pessoais Microsoft e habilite o fluxo de cliente público.
2. Configure a permissão delegada **SMTP.Send** do serviço Exchange Online e o consentimento necessário.
3. Cole o **Application (client) ID** na aba Autenticação e clique em **Conectar conta Outlook à Microsoft**.
4. Abra o endereço Microsoft exibido no navegador do computador, informe o código temporário e autorize a conta que enviará as mensagens. O código não é um MFA por celular.
5. Aguarde a confirmação na tela, salve e envie um teste.

O fluxo usa os escopos `https://outlook.office.com/SMTP.Send offline_access`. O refresh token fica criptografado no servidor; tokens de acesso ficam apenas em memória e são renovados automaticamente. Um novo refresh token fornecido durante a renovação é salvo sem sobrescrever alterações concorrentes do administrador. Uma autorização recusada ou expirada não salva credenciais.

Para Microsoft 365 empresarial, use SMTP personalizado com o host e OAuth2 autorizados pelo tenant, ou adapte o cadastro conforme as políticas da organização. A opção Outlook do catálogo é para contas pessoais. A referência explica os requisitos de aplicativo e de consentimento: [OAuth para SMTP Microsoft](https://learn.microsoft.com/en-us/exchange/client-developer/legacy-protocols/how-to-authenticate-an-imap-pop-smtp-application-by-using-oauth/). O fluxo interativo segue a [autorização por código de dispositivo](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-device-code).

SMTP personalizado também aceita OAuth2: informe client ID, endpoint HTTPS de token, escopos, refresh token e client secret quando exigido. Obtenha esses dados pelo fluxo autorizado do provedor. A configuração não contorna políticas, planos ou limites de envio.

## Variáveis de ambiente e proteção

As variáveis `NEXLIFY_SMTP_*` existentes continuam aceitas. Havendo qualquer variável SMTP, a configuração vem **integralmente do ambiente**, sem herdar segredos do arquivo. Isso evita combinar uma senha salva com um host alterado por variável. A tela informa essa precedência e bloqueia a gravação até a retirada das variáveis.

| Variável | Uso |
| --- | --- |
| `NEXLIFY_SMTP_PROVIDER` | ID de preset: `gmail`, `outlook`, `yahoo`, `icloud`, `zoho`, `aol`, `gmx`, `mailcom`, `fastmail`, `yandex` ou `custom`. Padrão `custom`. |
| `NEXLIFY_SMTP_HOST`, `NEXLIFY_SMTP_PORT`, `NEXLIFY_SMTP_SECURITY` | Host, porta e `starttls`/`ssl`; o preset fornece valores iniciais. |
| `NEXLIFY_SMTP_FROM`, `NEXLIFY_SMTP_USER` | Remetente e usuário da conta. |
| `NEXLIFY_SMTP_AUTH` | `password` ou `oauth2`. |
| `NEXLIFY_SMTP_PASSWORD` | Senha de aplicativo/SMTP no método password. |
| `NEXLIFY_SMTP_CLIENT_ID`, `NEXLIFY_SMTP_CLIENT_SECRET` | Credenciais do aplicativo OAuth2; secret é opcional conforme o fluxo. |
| `NEXLIFY_SMTP_TOKEN_URL`, `NEXLIFY_SMTP_SCOPE`, `NEXLIFY_SMTP_REFRESH_TOKEN` | Endpoint HTTPS, escopos e refresh token OAuth2. |
| `NEXLIFY_SMTP_CA` | CA privada opcional para o certificado SMTP. |

Credenciais gerenciadas pelo ambiente não são regravadas no arquivo. Para provedores que invalidam refresh tokens antigos após renovação, prefira o armazenamento local gerenciado ou mantenha a rotação no cofre externo. O assistente Microsoft salva pelo armazenamento local.

A configuração inteira é criptografada em `.secrets/email.json`, usando o chaveiro da instalação, com DACL privada no Windows e permissões 0600/0700 no Linux. O arquivo fica fora do Git e dos pacotes de distribuição. `instalacao.harden` protege a pasta e `instalacao.rotate_key` recriptografa a configuração SMTP junto das outras credenciais. Proteja e faça backup do arquivo e do chaveiro. Quem controla ambos na máquina controla o envio.

## Uso pelos módulos do sistema

```python
from services.email_delivery import send_email

# Executar somente no servidor/aplicação local, após autorização da operação.
send_email(destinatario, assunto, mensagem)
```

`send_code` usa esse mesmo serviço para MFA e `send_test` envia a mensagem de teste. A função genérica aceita um destinatário, texto simples e corpo de até 1 MiB. A configuração restringe a conta remetente. Dados, códigos e credenciais não entram nos logs.

O serviço não expõe um disparador público na API nem faz reenvios automáticos após falhas de SMTP: uma desconexão após a aceitação pode causar duplicidade se a mensagem for reenviada cegamente. O MFA conserva seus limites de tentativas, expiração e reenvio. Outros módulos devem aplicar sua própria autorização e frequência antes de chamar o serviço.

## Validação

Presets, criptografia, isolamento cliente/servidor, precedência do ambiente, rejeição de configurações inseguras, renovação OAuth2 e telas são exercitados por testes locais com SMTP/Microsoft simulados. Não foram fornecidas contas reais dos dez provedores e nenhuma mensagem real foi enviada durante a implementação. Use o teste da instalação para homologar a conta escolhida.


Resultado em 15/10/2026: **234 testes aprovados no Windows e 233 no Ubuntu/WSL2**, incluindo GUI e exclusão mútua da configuração entre processos reais nos dois sistemas. Foram pulados dois testes no Windows (banco externo e symlink sem privilégio) e um no Linux (banco externo). Há um aviso de depreciação do adaptador HTTP da biblioteca de testes. `pip check` passou e Bandit não encontrou achados médios/altos nos módulos verificados. Relatórios: `.runtime/smtp-providers-windows.xml`, `.runtime/smtp-providers-linux.xml` e `.runtime/smtp-providers-bandit.json`.
