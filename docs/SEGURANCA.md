# Segurança — implementação do relatório

Atualizado em 15/10/2026. Os controles abaixo foram implementados no código, instalação e ferramentas. A ativação em serviços externos exige a infraestrutura da instalação. Esta revisão não é um pentest nem certificação.

## Recomendações implementadas

| Item | Implementação |
| --- | --- |
| Credenciais antigas | Hashes publicados continuam bloqueados. Não há senha padrão. Criação inicial e recuperação DEV exigem senha escolhida pelo responsável; contas redefinidas por outro administrador precisam trocar a senha. |
| Chave comprometida | Segredos fora do Git. `instalacao.rotate_key` publica um chaveiro de recuperação antes de recriptografar credenciais locais e sementes MFA legadas. Uma interrupção não abandona tokens antigos sem chave. Chave externa exige rotação no cofre. Trocar a chave do arquivo não troca a senha real do banco. |
| Permissões existentes | `instalacao.harden` restringe chaves, configurações, SQLite, logs e backups existentes. Windows: DACL protegida para conta executora, SYSTEM e Administrators. Linux: diretórios 0700 e arquivos 0600. Links/junctions recusados. |
| Conta de banco limitada | Runtime de produção recusa nomes administrativos conhecidos. `instalacao.db_permissions` gera GRANTs específicos por dialeto, sem DDL ou senha. Logs permitem SELECT/INSERT; revisão e vínculos SSO são somente leitura. O DBA deve retirar concessões amplas e verificar os privilégios efetivos. |
| Transporte do banco | PostgreSQL verifica TLS/hostname; MySQL/MariaDB usam SSLContext verificado; SQL Server exige criptografia/certificado; Oracle exige TCPS em produção. Firebird exige `WireCrypt = Required` e `Srp256` no cliente. Servidores externos ainda precisam de homologação real. |
| Distribuição de operação | Pacotes por lista permitida e manifesto SHA-256. Excluem ambientes virtuais, bancos, backups, chaves, configurações privadas, testes e reset DEV. Cliente não inclui provisionamento nem servidor. |
| Clientes não confiáveis | API HTTPS central em `servidor.py`, com autenticação, autorização e CRUD no servidor. Desktop em `api_mode=client` recebe somente token opaco em memória, sem credenciais de banco; sua camada de banco recusa conexão direta. |
| Sessões | Apenas SHA-256 do token da API é persistido. Expiração por inatividade/tempo absoluto; senha, perfil e versão MFA revalidados. Consultas de status não renovam atividade. Logout, alteração de senha/MFA revogam acesso. |
| Argon2id | 64 MiB, três iterações, paralelismo quatro. Bcrypt custo 12 é convertido após login válido. Hashes publicados não migram: são bloqueados. Novas senhas: mínimo 15 caracteres, máximo 1024 bytes UTF-8. Custo de hashes armazenados também é limitado antes da verificação. |
| Senhas comprometidas | Lista básica local, arquivo opcional de SHA-256 e HIBP por prefixo SHA-1 de cinco caracteres, com padding. Produção usa HIBP por padrão e falha se a consulta não puder concluir. Senha em texto puro não é enviada ao HIBP. |
| MFA | **Por e-mail e desabilitado por padrão**, inclusive em produção. Código aleatório de seis dígitos, cinco minutos, uso único, finalidade vinculada e HMAC-SHA-256 com nonce no banco. SMTP com TLS/certificado verificado, sem fallback aberto. Reenvio limitado a 60 segundos. Oito códigos de recuperação armazenados como hashes. Erros participam do bloqueio persistente. Quando a instalação ativa MFA, administradores de produção precisam cadastrá-lo. |
| Envio de e-mail | Dez presets e SMTP personalizado, TLS obrigatório, senhas de aplicativo ou OAuth2, credenciais criptografadas em `.secrets/email.json`. Configuração no servidor; clientes/RPC não recebem credenciais SMTP. Campos secretos não são exibidos e não são reutilizados ao mudar conta/servidor. Variáveis de ambiente não herdam segredos locais. OAuth2 Microsoft com fluxo de autorização, expiração e renovação de tokens. |
| Reautenticação | Escritas em usuários e alterações de MFA exigem autenticação nos últimos cinco minutos. Interface solicita senha e código por e-mail quando MFA estiver habilitado; servidor verifica independentemente. |
| SSO | OIDC Authorization Code com PKCE S256, state, nonce, assinatura RS256/ES256, issuer, audience, expiração e autenticação recente. Tokens do provedor ficam no servidor. Vínculo issuer/subject explícito; claims não atribuem perfil administrativo. MFA local continua aplicável. |
| Auditoria externa | Evento e outbox na mesma transação. Entrega HTTPS/HMAC, recibo de conteúdo e retry persistente. Coletor separado permite criação/repetição idêntica, mas recusa sobrescrita. API em produção exige destino de auditoria configurado. |
| Dependências/artefatos | Locks universais de versões transitivas e SHA-256; instalador usa `--require-hashes`. CI Windows/Linux com actions fixadas por SHA, testes, pip-audit e Bandit. Pacotes possuem manifesto e checksum externo. |
| Segredos no histórico | Gitleaks 8.30.1 com checksum da distribuição fixado; examina todos os refs e árvore atual, ocultando valores. CI busca histórico completo e falha em achados. Sem exceções para esconder exposições antigas. |
| Migrações/restauração | Revisões explícitas 1, 2 e 3 (MFA por e-mail); recusa de revisão futura/schema incompleto. Backup SQLite antes da migração; restauração valida checksum e só cria destino novo. Migração externa em produção exige provisionamento explícito e, em banco já provisionado, evidência de restauração. |

Instruções de ativação e recuperação: [SEGURANCA_OPERACAO.md](SEGURANCA_OPERACAO.md).

### Autorização de páginas por perfil

Política central em `persistencia/access_policy.py`, com negação por padrão para páginas e perfis desconhecidos. Menus, abertura direta, construção dos painéis e reabertura de páginas já carregadas validam o acesso; repositório e API aplicam as permissões de dados independentemente da interface. Ferramentas DEV exigem administrador, instalação DEV e ambiente de desenvolvimento. Auditor externo tem consulta sem gravações. A API valida o token e não aceita o perfil informado pelo cliente. Matriz completa, comportamento de revogação e testes: [ACESSOS.md](ACESSOS.md).

## Proteções anteriores mantidas

- Repositório não aceita SQL textual; valida árvore de expressões, tabelas, colunas e funções. Hashes não são expostos em leitura ou filtro. API não aceita SQL nem hashes enviados por clientes.
- Escritas revalidam autorização dentro da transação e protegem o último administrador. Valores são parametrizados. Tabelas internas não são acessíveis pelo CRUD remoto.
- Cinco falhas bloqueiam a conta por cinco minutos, persistentemente. Login, reautenticação, senha atual e confirmação MFA aplicam limites. SQLite serializa o contador.
- Sessões: 15 minutos de inatividade e oito horas de duração por padrão; interface verifica validade periodicamente. Mudanças de senha/perfil/MFA e da política global de MFA revogam sessões.
- Descriptografia falha sem retornar texto original nem gerar chave substituta. Configurações usam escrita atômica, temporários exclusivos e arquivos privados.
- Produção exige login/logs e interrompe inicialização se o log não puder abrir. Logs têm rotação e escapam valores de usuário.
- API limita corpo real, requisições e autenticações simultâneas. Erros não expõem corpo, SQL, senhas ou hashes. TLS não tem fallback inseguro.

## Aplicado nesta instalação

Banco local migrado para revisão **3**, com 12 tabelas. A revisão 3 acrescenta `email_mfa` sem alterar registros anteriores. O MFA está efetivamente desabilitado nesta instalação. Comparação integral preservou **16 usuários, 5 tipos, 30 vegetais, 4 espécies e 0 eventos antigos**. Backup e restauração em outro arquivo passaram na verificação; o banco original não foi substituído. As permissões existentes foram restringidas, incluindo `.venv/backup-before-evolution`.

Nenhuma senha de usuário foi escolhida ou redefinida automaticamente. As contas antigas permanecem bloqueadas até recuperação explícita pelo responsável.

## Evidências e limites

Validação após o controle de acesso às páginas: **273 testes aprovados no Windows e 272 no Ubuntu Linux**, incluindo **39 novos testes** de autorização, API e interface. Foram pulados o teste de servidor externo nos dois ambientes e o teste de symlink no Windows por falta de privilégio. Há um aviso de depreciação do adaptador HTTP da biblioteca de testes, sem falha funcional. Bandit reexecutado nos módulos de autorização, aplicativo, painéis, API e controlador de tipos: nenhum achado médio/alto. Relatórios locais: `.runtime/page-access-windows.xml`, `.runtime/page-access-linux.xml` e `.runtime/page-access-bandit.json`. Na validação anterior das dependências, `pip check` passou e `pip-audit` não encontrou vulnerabilidades conhecidas; esta alteração não acrescentou dependências. Instalação limpa do pacote de operação e provisionamento passaram nos dois sistemas. O cliente foi testado contra servidor HTTPS real, incluindo recusa de certificado não confiável.

Testes cobrem os dez presets SMTP, configuração personalizada, isolamento de credenciais, TLS, OAuth2 Microsoft/renovação, bloqueio de arquivo entre processos Windows/Linux, telas de configuração, o padrão MFA desligado em produção, cadastro e login por e-mail, indisponibilidade SMTP com recuperação, expiração, finalidade dos códigos, reenvio, confirmação TLS, migração de cadastros antigos, importação dos três pacotes, Argon2id/bcrypt, HIBP, MFA/replay/recuperação, bloqueio, reautenticação, API/perfis/revogação/expiração, cliente com HTTPS real e certificado, OIDC/PKCE, auditoria/coletor/retry, rotação, ACL nativa, migração/restauração e pacote sem segredos. Permanecem os testes de interface, CRUD, SQL inseguro, TLS e scripts multiplataforma.

Relatórios locais, não versionados:

- `.runtime/smtp-providers-windows.xml` e `.runtime/smtp-providers-linux.xml`: suíte atual. Os relatórios `email-mfa-*.xml` e `security-implementation-*.xml` registram revisões anteriores.
- `.runtime/email-mfa-dependencies.json`: dependências, sem vulnerabilidades conhecidas nesta execução.
- `.runtime/smtp-providers-bandit.json`: serviços SMTP/OAuth2, tela, configurador e rotação, sem achados médios/altos. `email-mfa-bandit.json` e `bandit-implementation.json` registram análises anteriores.
- `.runtime/email-mfa-local-validation.json`: revisão 2 → 3, preservação integral, backup/restauração e MFA desligado. `implementation-local-validation.json` registra também a revisão anterior e as permissões.
- `.runtime/secrets-history.json` e `.runtime/secrets-working.json`: segredos, com valores ocultados.

**Histórico Git:** 68 ocorrências: 64 hashes nos quatro scripts SQL antigos, uma chave Fernet e três detecções adicionais em configuração/código antigo. A árvore atual passou sem achados. O scanner continuará retornando falha enquanto os achados históricos permanecerem. Isso não comprova que todas as credenciais ainda sejam válidas; exige tratá-las como expostas. A remoção atual não apaga commits, clones ou backups. Não houve reescrita do histórico.

O SMTP foi validado com testes simulados, inclusive falha de certificado, sem enviar mensagens reais. Nenhuma credencial SMTP real foi solicitada ou configurada. A tela e o assistente de configuração estão documentados em [EMAIL.md](EMAIL.md). A ativação é opcional e requer as variáveis descritas no guia operacional; o padrão permanece desligado.

Ainda dependem da instalação:

1. Escolher novas senhas para admin/contas mantidas; revogar no serviço de origem qualquer credencial real associada à chave antiga.
2. Fornecer certificados, destino externo de auditoria e chave de entrega. Para SSO: issuer, client ID, redirect URI, segredo quando aplicável e vínculos de identidade.
3. Homologar banco externo, firewall, permissões efetivas e restauração nativa. Não houve conexão real com PostgreSQL, MySQL, MariaDB, SQL Server, Oracle ou Firebird nesta instalação.
4. Configurar retenção imutável/WORM e backup no coletor externo. Sua API impede sobrescrita, mas administradores do host ainda controlam arquivos comuns. Cópia no mesmo host não é isolamento externo.
5. Executar workflow no GitHub após publicar as alterações e tratar o histórico exposto. Testes locais não equivalem à execução remota.

Código hostil dentro do processo que possui a credencial do banco pode contornar proteções Python. Para máquinas não confiáveis, distribua o **cliente da API** e mantenha servidor, banco e coletor sob contas separadas e rede restrita.

## Referências

[OWASP autenticação](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html), [senhas](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html), [segredos](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html); [Argon2-cffi](https://argon2-cffi.readthedocs.io/en/stable/api.html); [HIBP](https://haveibeenpwned.com/API/v3#PwnedPasswords); [joserfc](https://jose.authlib.org/en/guide/jwt/); [Firebird](https://www.firebirdsql.org/docs/html/en/refdocs/fbconf/firebird-configuration-reference.html); [Gitleaks](https://github.com/gitleaks/gitleaks).
