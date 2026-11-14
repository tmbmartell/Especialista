# Especialista — Nova Gente

Loja modular de especialistas de IA para experiências de autoconhecimento pelo WhatsApp.

**Status:** início de desenvolvimento (MVP). Ainda não é um serviço pronto para clientes reais.

## Experiência planejada
- Catálogo com 13 especialistas e linguagem comercial própria.
- Primeiro especialista a **R$ 9,90/mês**; cada adicional a **R$ 4,99/mês**.
- Um único login e um WhatsApp vinculado ao número verificado do assinante.
- Compra de adicionais sem criar outra conta; acesso liberado apenas após confirmação de pagamento.
- Troca de especialistas no mesmo chat, preservando o isolamento por cliente e a memória autorizada.

## Arquitetura
- **Loja e painel:** interface web.
- **API:** identidade, carrinho, assinatura, códigos temporários e permissões.
- **JEV:** classificação/roteamento (não autoriza pagamento nem acesso).
- **DeepSeek:** modelo conversacional a integrar.
- **WAHA:** transporte de mensagens a integrar.
- **Composio:** integrações externas opcionais, nunca substituto obrigatório do login.
- **Banco:** PostgreSQL na produção; persistência de demonstração pode ser local.

## Regras obrigatórias
1. Isolamento por usuário, cliente, especialista e versão de conteúdo.
2. Nenhum especialista liberado sem pagamento confirmado por backend.
3. Códigos de ativação de uso único, expiração e vínculo com o número de origem verificado.
4. Nenhuma API key, token, senha real, dado pessoal ou conteúdo protegido de terceiros no Git.
5. Os plugins são referências internas de capacidades; não estão conectados diretamente a este repositório.
6. Conteúdo emocional é educativo/reflexivo, não diagnóstico ou atendimento clínico.
7. Infraestrutura real só após homologação de segurança, custo, cobrança e LGPD.

## Fases
F0 Inventário e revisão de conteúdo → F1 Fundação → F2 Módulos → F3 IA/JEV → F4 WhatsApp → F5 Cobranças → F6 Interface final → F7 Segurança → F8 Publicação.

**Atenção:** não disponibilizar a versão de desenvolvimento como serviço comercial antes das integrações e testes.


## F1 — Sandbox de contas e carrinho (13/11/2026)

A aplicação de demonstração agora inclui cadastro/login, sessões com cookie HttpOnly,
proteção CSRF, limite de tentativas de login, carrinho persistente por usuário e pedidos
em estado `awaiting_payment`. **Nenhum pedido concede acesso, não há cobrança e
não há WhatsApp ou IA conectados.**

Executar localmente:

```sh
docker compose -f infra/docker-compose.demo.yml up --build
# Acesse http://127.0.0.1:8088
```

Testar:

```sh
python3 -m pip install -r apps/api/requirements.txt
python3 -m pip install pytest httpx
PYTHONPATH=apps/api pytest -q apps/api/tests/
```

A verificação isolada de 13 testes foi concluída com sucesso. Consulte
[contratos da API](docs/CONTRATOS_API.md) e
[pendências de identidade e isolamento](https://github.com/tmbmartell/Especialista/issues/1).

**Não disponibilize essa demonstração para clientes:** o login é somente para teste,
o e-mail não é verificado, há SQLite e não PostgreSQL, e o projeto permanece
em fases iniciais. Metodologias proprietárias e segredos não pertencem ao
repositório público.

## F2 — Identidades e jornadas (prévia em revisão)

A vitrine permite **conhecer as experiências** dos 13 especialistas: propósito,
pergunta inicial, voz e quatro etapas resumidas. Esses dados vêm de
`apps/web/experiencias.json`, que contém apenas descrições públicas.

A API expõe `GET /api/experiences` e `GET /api/experiences/{slug}/preview`.
As respostas sinalizam `previewOnly=true` e `availableForSale=false`.
Os prompts privados, textos de livros e documentos dos plugins não foram
publicados nem conectados. Veja [matriz de jornadas e segurança](docs/F2_METODOLOGIAS.md).
