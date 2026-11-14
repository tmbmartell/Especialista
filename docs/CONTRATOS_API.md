# API do Especialista — sandbox F1

Esta versão tem **cadastro/login e carrinho por usuário**, mas não tem pagamentos, e-mail verificado, reset de senha nem ativação real de especialistas. Nunca publique a demonstração como serviço para clientes.

## Catálogo (sem login)
- `GET /api/health`: estados das integrações desabilitadas.
- `GET /api/catalog`: catálogo comercial com 13 perfis.
- `POST /api/quote`: orçamento sem cobrança. Exemplo `{"slugs":["coragem-para-ir","solte-esse-peso"]}` → R$ 14,89/mês.

## Conta e sessão (somente se NG_DEMO_MODE=true)
- `POST /api/auth/register`: cadastro de teste (e-mail e senha com no mínimo 12 caracteres).
- `POST /api/auth/login`: início de sessão; tentativas incorretas limitadas.
- `GET /api/auth/me`: dados mínimos da conta, `csrf_token` e indicação explícita de não verificação.
- `POST /api/auth/logout`: encerra a sessão.
- `GET /api/me/cart`: leitura do carrinho do usuário autenticado.
- `PUT /api/me/cart`: substitui seleção (`{"slugs":[...]}`) sem afetar outras contas.
- `POST /api/me/orders`: cria apenas um pedido `awaiting_payment`, sem pagamento nem direitos concedidos.
- `GET /api/me/orders` e `GET /api/me/orders/{id}`: somente pedidos da própria conta.

As rotas que alteram estado, depois do login, exigem o cabeçalho `X-CSRF-Token` recebido na resposta de login ou `/api/auth/me`. A sessão fica em cookie `HttpOnly`, `SameSite=Strict`; em HTTPS, habilitar `NG_COOKIE_SECURE=true`. O modo de demonstração exige `NG_DEMO_MODE=true` e deve ficar acessível **apenas no localhost**.

## Como executar localmente, com a mesma origem de API e site

Na raiz do repositório:
```sh
docker compose -f infra/docker-compose.demo.yml up --build
```
Acesse **http://127.0.0.1:8088**. O proxy do Nginx encaminha `/api/` para o container da API. Não há porta pública para a API. Dados fictícios de sandbox ficam em volume Docker local.

Não use senhas pessoais ou contas reais nesse teste. Para apagar o banco de demonstração, o operador pode parar o compose e remover explicitamente o volume **após confirmar** que não precisa preservar os dados.

## Testes automatizados
```sh
python3 -m pip install -r apps/api/requirements.txt
python3 -m pip install pytest httpx
PYTHONPATH=apps/api pytest -q apps/api/tests/
```

## Limitações atuais e próximos passos
- E-mails ainda não são verificados e não existe recuperação de senha.
- Persistência SQLite é exclusiva da demo; produção exigirá PostgreSQL, migrações e verificação adicional de isolamento.
- Não há sessão ou API real do WhatsApp, nem código de ativação funcional.
- Não há gateway, webhook validado, assinatura recorrente ou liberação de direitos.
- JEV e DeepSeek não estão conectados; metodologias privadas não estão neste repositório público.
- É necessário revisar LGPD e conteúdo de terceiros antes da publicação comercial.
