# Instalação e operação segura

Nos comandos, `python` representa o Python da **.venv**: `.venv\Scripts\python.exe` no Windows ou `.venv/bin/python` no Linux. Execute os módulos a partir da raiz. Os scripts de instalação/início também aceitam caminhos com espaços.

## Instalar cliente, servidor ou aplicação local

Windows:

```bat
instalacao\setup.bat --headless --profile core --mode client --api-url https://api.sua-empresa.example
```

Linux:

```sh
bash instalacao/setup.sh --headless --profile core --mode client --api-url https://api.sua-empresa.example
```

Substitua pela URL real. Para servidor, use `--mode server --database postgresql` ou outro banco suportado. Para operação local confiável: `--mode local --database sqlite`. A GUI permite selecionar os mesmos modos. Servidor pode ser instalado sem interface gráfica; desktop requer Tcl/Tk.

Não copie `banco.local.ini`, `.secrets`, `.venv` ou backups para clientes. Para CA privada, configure `NEXLIFY_API_CA`; não desative a verificação TLS. Use `iniciar.bat` ou `iniciar.sh` para o desktop.

## Provisionar banco e API

1. Crie banco/schema e conta de instalação pelo procedimento do fornecedor. Forneça segredos por cofre/ambiente ou configurador; evite histórico do terminal.
2. Com essa conta, execute `python -m instalacao.provision migrate`. Banco externo já provisionado exige `--backup-evidence caminho/ensaio.json`, contendo `backup_id`, `verified_at` e `restore_verified: true`. Essa declaração operacional não executa nem certifica backup remoto.
3. Gere privilégios: `python -m instalacao.db_permissions --database postgresql --user nexlify_app --schema public`. O DBA revisa/aplica a saída e retira concessões amplas anteriores. MySQL/MariaDB usam `--schema` como banco e `--host` como origem da conta. Oracle requer caixa correta do schema/usuário.
4. Configure conta de runtime limitada e `initialize_database_on_startup = False` em `config.local.ini`. A conta normal não precisa de DDL/administração. Logs, revisão, outbox e vínculos SSO possuem privilégios específicos no gerador.
5. Em banco vazio: `python -m instalacao.provision bootstrap-admin`. A senha é solicitada sem eco. Banco existente não é sobrescrito. Recuperação de admin pelo `reset_admin.bat`/`.sh` permanece exclusiva do ambiente/perfil DEV.
6. Configure TLS e auditoria externa; execute `python servidor.py --host 127.0.0.1 --port 8443 --cert caminho/cert.pem --key caminho/key.pem`. Exponha apenas a interface de rede necessária. Produção recusa HTTP, inclusive pelo módulo ASGI.

Use **um worker**: fluxos OIDC e limites por IP são mantidos em memória. Antes de balancear workers, adote coordenação compartilhada. Sessões e tentativas por conta ficam no banco. Cabeçalhos `X-Forwarded-*` não são confiados; se usar proxy, mantenha HTTPS também entre proxy e API.

## Contas, perfis e atualização do controle de páginas

O Administrador Global atribui o perfil em **Gestão de Usuários → Perfil de Acesso**. A [matriz de acesso](ACESSOS.md) é predefinida no código; a tela de contas não cria regras personalizadas. O [guia do usuário](GUIA_USUARIO.md) descreve criação, edição e redefinição de senha.

A navegação e os dados aplicam a mesma política. Operadores não recebem acesso administrativo ao instalar ferramentas de desenvolvimento. Auditor Externo pode consultar espécies e Vegetais e Auditoria, sem gravar. Informações do computador e diagnóstico exigem Administrador ou Gerente de TI; configuração SMTP exige Administrador na aplicação local/servidor.

Alterar o perfil revoga sessões existentes. Na próxima navegação ou verificação periódica, a aplicação fecha as janelas protegidas e pede novo login; requisições da API também revalidam a conta. Não é preciso reiniciar o servidor para uma alteração de perfil no banco.

Para atualizar uma instalação para esta versão:

1. Prepare uma cópia de homologação e backup conforme o procedimento do banco. A mudança de acesso às páginas não exige nova revisão além da 3 já usada pelo template.
2. Distribua o código compatível ao servidor e aos clientes; o cliente usa o RPC `pages/authorize`. Não misture cliente novo e servidor antigo sem esse método.
3. Reinicie os processos atualizados para carregar o código. As permissões dependem da conta validada pelo servidor, não de um perfil enviado pelo cliente.
4. Confira os acessos com contas de homologação: administrador, operador e auditor. Verifique menus, abertura negada, consulta sem gravação e revogação após alteração do perfil.

Não há fallback que libere páginas quando a validação da sessão falha ou o servidor fica indisponível. Ferramentas independentes executadas pela conta do sistema operacional, como provisionamento e configuração SMTP, exigem proteção dessa conta e dos arquivos; não são endpoints administrativos para operadores.

## MFA, senhas e reautenticação

**O MFA por e-mail vem desabilitado por padrão**, inclusive em produção (`mfa_enabled = False`). Sem ativação, o login pede apenas usuário e senha; não há envio de e-mail nem exigência de cadastro MFA. Não utiliza aplicativo autenticador ou celular.

Para habilitar, configure primeiro o SMTP na máquina que valida o login (servidor da API ou aplicação local). Use a tela **Configurações → Envio de e-mail / SMTP** ou `python -m instalacao.config_email --headless`; ambos oferecem dez presets e SMTP personalizado, com credenciais criptografadas. Consulte [configuração de e-mail e OAuth2](EMAIL.md). Também é possível usar variáveis de ambiente fornecidas pelo gerenciador de serviços/cofre, sem gravar senhas no Git:

| Variável | Conteúdo |
| --- | --- |
| `NEXLIFY_SMTP_HOST` | Host do servidor SMTP. |
| `NEXLIFY_SMTP_PORT` | Porta: 587 por padrão com STARTTLS, 465 com SSL/TLS. |
| `NEXLIFY_SMTP_SECURITY` | `starttls` (padrão) ou `ssl`; conexões sem TLS são recusadas. |
| `NEXLIFY_SMTP_FROM` | Endereço de e-mail remetente, sem nome de exibição. |
| `NEXLIFY_SMTP_USER` | Usuário de autenticação SMTP. |
| `NEXLIFY_SMTP_PASSWORD` | Senha SMTP ou senha de aplicativo do provedor, fornecida pelo cofre. |
| `NEXLIFY_SMTP_CA` | Arquivo de CA privada, opcional. Certificado e hostname sempre são verificados. |

Edite a seção existente de `config.local.ini` (não duplique `[Settings]`):

```ini
[Settings]
mfa_enabled = True
```

A variável `NEXLIFY_MFA_ENABLED=true` também habilita a função e tem precedência sobre o arquivo. Para desabilitar, use `False`/`false` no local efetivo e reinicie a aplicação/servidor. Alterar a política invalida as sessões anteriores. Clientes da API seguem a configuração do servidor, independentemente da configuração local. O instalador e os pacotes novos mantêm o padrão desligado.

Com a função ativa, use **Aplicação → Ativar MFA por e-mail**, informe seu endereço, clique em **Enviar código por e-mail** e confirme o código recebido. Administradores de produção precisam concluir esse cadastro antes de acessar dados; a exigência só existe quando o responsável habilita a função na instalação. Outros perfis podem aderir pelo menu.

No login, informe usuário e senha. Se sua conta tiver MFA ativo, o sistema enviará **um código temporário de seis dígitos para o e-mail cadastrado** e exibirá o campo de confirmação. O código vale cinco minutos, tem uso único e finalidade específica. O reenvio respeita intervalo de 60 segundos; dentro desse intervalo, continua válido o código já enviado. Um novo envio substitui o anterior. A sessão só é liberada depois da confirmação. Falha no SMTP não libera acesso. A confirmação inicial do cadastro permite receber imediatamente o primeiro código de login.

Guarde os oito códigos de recuperação em cofre; cada um funciona uma vez, inclusive quando o e-mail estiver indisponível. Eles podem ser usados no campo do código. Contas da versão anterior com autenticador precisam de um código de recuperação antigo para entrar e cadastrar o e-mail; os códigos TOTP não são mais aceitos. Não remova o segundo fator diretamente no banco para contornar a confirmação de identidade.

Ações administrativas após cinco minutos pedem a senha novamente e, se o MFA estiver ativo na conta e instalação, enviam outro código por e-mail. Troca de senha/MFA encerra a sessão. Alterar senha não remove MFA. Desabilitar a função global preserva os cadastros para futura reativação. Proteja também a conta de e-mail: quem controla essa caixa recebe os códigos.

Argon2id usa 64 MiB, três iterações e quatro vias; afira a latência no hardware antes de mudar a política. Bcrypt antigo não publicado é convertido no login.

Produção consulta HIBP por prefixo de cinco caracteres SHA-1, com padding. Indisponibilidade impede criar/trocar senha, mas não consulta logins existentes. Em rede isolada, configure `NEXLIFY_PASSWORD_BREACH_MODE=local` e `NEXLIFY_PASSWORD_BLOCKLIST` apontando para uma base mantida de SHA-256, um hash por linha. A lista básica embutida é pequena e não substitui uma base atualizada.

## SSO opcional

Registre cliente OIDC Authorization Code com PKCE S256 e configure no servidor:

| Variável | Conteúdo |
| --- | --- |
| `NEXLIFY_OIDC_ISSUER` | Issuer exato, incluindo tenant/realm. |
| `NEXLIFY_OIDC_CLIENT_ID` | ID do aplicativo registrado. |
| `NEXLIFY_OIDC_REDIRECT_URI` | URL HTTPS da API terminada em `/sso/callback`, idêntica à registrada. |
| `NEXLIFY_OIDC_CLIENT_SECRET` | Segredo de cliente confidencial, se exigido; fornecido pelo cofre. |
| `NEXLIFY_OIDC_CA` | CA privada opcional. |

O provedor deve anunciar PKCE S256 e emitir ID token RS256/ES256 com nonce e `auth_time` solicitados. A integração do tenant precisa de homologação.

Vincule conta existente: `python -m instalacao.provision bind-sso --login usuario --issuer https://id.sua-empresa.example/realm --subject ID-ESTAVEL`. Use issuer + subject, não email mutável. Perfil continua local; claims não criam administradores automaticamente.

No cliente, clique **Entrar com SSO**, conclua no navegador e confirme o código enviado por e-mail quando MFA estiver habilitado. ID/access tokens ficam no servidor. O fluxo expira, só pode ser usado uma vez e é cancelado ao reiniciar. Reautenticação administrativa nesta versão usa senha local e MFA; mantenha essa credencial no cofre do titular.

## Auditoria fora do host

Configure `NEXLIFY_AUDIT_URL` com URL HTTPS do coletor e `NEXLIFY_AUDIT_KEY` com pelo menos 32 bytes aleatórios, fornecidos pelo cofre. CA privada: `NEXLIFY_AUDIT_CA`. API de produção exige essa configuração e tenta entregar a cada 30 segundos. Falhas mantêm o evento na fila e aplicam retry; monitore os pendentes.

Coletor opcional em **outro host/conta**: instale dependências do servidor, configure a mesma chave e `NEXLIFY_AUDIT_STORAGE` com diretório protegido. Execute:

```text
python -m uvicorn services.audit_receiver:app --host 127.0.0.1 --port 9443 --ssl-certfile caminho/cert.pem --ssl-keyfile caminho/key.pem --no-access-log
```

Endpoint `/events`: HMAC, escrita atômica sem sobrescrita e recibo SHA-256. Repetição idêntica é aceita; conteúdo divergente para o mesmo evento é recusado. Não há alteração/exclusão pela API. Configure retenção WORM/imutável e backup externos: administradores do host ainda podem alterar arquivos comuns. Não compartilhe conta/disco do coletor com desktop.

Modo local: `python -m services.audit_delivery --watch`, ou execução periódica sem `--watch`. Saída informa entregues/pendentes sem conteúdo. Eventos não são apagados automaticamente.

## Proteger, rotacionar e restaurar

- `python -m instalacao.harden`: restringe arquivos existentes. Execute pela conta autorizada do serviço. Arquivos fora da raiz/cofres devem receber proteção no respectivo local; runtime não deve usar conta administrativa.
- `python -m instalacao.rotate_key`: execute em manutenção, sem escritores concorrentes. Recriptografa tokens de `banco.local.ini`, a configuração SMTP em `.secrets/email.json` e sementes MFA legadas, preservadas para compatibilidade. Publica primeiro o chaveiro novo + anteriores; após interrupção é possível repetir sem perder leitura de tokens antigos. Guarde o chaveiro protegido para recuperar backups; não distribua a clientes. Chave externa `NEXLIFY_SECRET_KEY` requer rotação coordenada no cofre. Isso não altera a credencial real no serviço externo.
- `python -m instalacao.backup backup NexlifyTTk.db .runtime/backups`: snapshot SQLite com integridade e manifesto SHA-256.
- `python -m instalacao.backup restore caminho/backup.db caminho/novo.db`: ensaio em destino novo, nunca sobrescreve banco existente. Compare dados; para rollback, pare o serviço e aponte configuração para cópia validada com a versão de código compatível.

Banco com MFA exige também o chaveiro correto, guardado separadamente com proteção equivalente. Para migrar entre Windows/Linux, use snapshot e configure caminhos nativos; crie uma `.venv` no destino. Banco externo exige ferramentas nativas e restauração em instância isolada; o template não executa comandos arbitrários de backup.

## Distribuição e CI

```text
python -m instalacao.package_release dist/NexlifyTTk-servidor.zip --mode server
python -m instalacao.package_release dist/NexlifyTTk-local.zip --mode local
python -m instalacao.package_release dist/NexlifyTTk-cliente.zip --mode client --api-url https://api.sua-empresa.example
python -m instalacao.package_release dist/NexlifyTTk-cliente.zip --verify
```

O gerador não sobrescreve pacote existente. Registre o SHA-256 retornado em canal confiável; manifesto interno sozinho pode ser substituído por quem adulterar todo o pacote. Servidor inclui provisionamento; cliente não. Ambos excluem segredos, bancos, backups e ferramentas DEV.

Os novos pacotes incluem o [índice documental](README.md), o [guia do usuário](GUIA_USUARIO.md), a [matriz de acesso](ACESSOS.md), os guias de operação e o [guia de desenvolvimento](DESENVOLVIMENTO.md). Atualizar os arquivos do projeto não modifica ZIPs já gerados: produza um novo artefato e confira o manifesto antes de distribuí-lo. Referências a evidências locais em `.runtime` não significam que esses relatórios privados acompanhem o pacote.

Locks de runtime, servidor, desenvolvimento e drivers fixam transitivas/hashes. Atualizações devem regenerar locks, passar `pip check`, testes e `pip-audit` antes de nova distribuição. Comandos principais estão nos cabeçalhos; foi usado uv 0.13.1. O instalador não precisa de uv.

`python -m instalacao.secret_scan` examina todos os refs/árvore atual sem imprimir valores. Não suprima o código de saída para aprovar entrega. As 68 ocorrências históricas precisam de tratamento de credenciais e eventual limpeza coordenada de histórico/clones pelo responsável. Reescrever Git não revoga credencial exposta.

Workflow Windows/Linux preparado com checkout completo/scanner, ainda não acionado remotamente. Homologação de bancos externos: [BANCOS.md](BANCOS.md). Resultado e limites desta implementação: [SEGURANCA.md](SEGURANCA.md).
