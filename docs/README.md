# Documentação do NexlifyTTk

O NexlifyTTk é um template desktop Python/Tkinter para Windows e Linux. Cada instalação escolhe um banco. Pode funcionar localmente ou como cliente de uma API HTTPS central. Consulte o [README principal](../README.md) para instalar e iniciar.

## Usuários e administradores

| Documento | Conteúdo |
| --- | --- |
| [Guia do usuário](GUIA_USUARIO.md) | Login, navegação, contas, perfis, preferências, MFA e solução de problemas comuns. |
| [Matriz de acesso](ACESSOS.md) | Permissões dos sete perfis, consulta do auditor, restrições DEV e testes de autorização. |

## Instalação e operação

| Documento | Conteúdo |
| --- | --- |
| [Windows e Linux](MULTIPLATAFORMA.md) | Pré-requisitos, `.venv`, scripts, ambientes validados e limites da homologação. |
| [Banco por instalação](BANCOS.md) | Sete opções, configuração, drivers, schema, privilégios e recuperação. |
| [E-mail e SMTP](EMAIL.md) | Dez presets, SMTP personalizado, OAuth2, teste de envio e proteção das credenciais. |
| [Operação segura](SEGURANCA_OPERACAO.md) | Local/cliente/servidor, provisionamento, MFA, SSO opcional, auditoria, backup e distribuição. |
| [Relatório de segurança](SEGURANCA.md) | Controles implementados, resultados, limitações e providências operacionais pendentes. |

## Desenvolvimento

| Documento | Conteúdo |
| --- | --- |
| [Guia de desenvolvimento](DESENVOLVIMENTO.md) | Arquitetura interna, autorização, novos painéis, migrações, testes e manutenção documental. |
| [Evoluções incorporadas](EVOLUCOES.md) | Adaptações estruturais das referências e funcionalidades adicionadas ao template. |

## Onde consultar cada informação

As regras executadas estão em `persistencia/access_policy.py`; sua descrição para usuários está em [ACESSOS.md](ACESSOS.md). O perfil de instalação `core`/`dev` não substitui o perfil do usuário. MFA por e-mail permanece desabilitado por padrão e configurar SMTP não o ativa.

Os resultados completos mais recentes do código estão no [relatório de segurança](SEGURANCA.md). Os números anteriores em [MULTIPLATAFORMA.md](MULTIPLATAFORMA.md) são registros históricos de etapas da implementação. Referências a `.runtime` descrevem evidências locais, não arquivos públicos distribuídos.

A ajuda **Guia de Configuração** dentro do aplicativo apresenta um resumo de uso. Os documentos desta pasta acompanham os novos pacotes gerados pelo projeto; arquivos ZIP já criados não são atualizados automaticamente. A revisão de documentação não publica conteúdo em serviços externos.
