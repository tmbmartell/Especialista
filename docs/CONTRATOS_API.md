# Contratos iniciais da API de demonstração

- `GET /api/health`: estados das integrações (todas desabilitadas).
- `GET /api/catalog`: 13 produtos e seus nomes comerciais.
- `POST /api/quote` com `{"slugs":["coragem-para-ir","solte-esse-peso"]}`: retorna **R$ 14,89/mês**. A API rejeita itens inexistentes e duplicados.

Esta API **não cria usuários, cobranças, tokens, ativações ou acessos**. É um serviço sem dados pessoais e sem segredos. Preços são orçamento simulado e não fornecem direitos de uso.

## Rodar local
```sh
python3 -m pip install -r apps/api/requirements.txt
CATALOG_PATH=apps/web/catalogo.json uvicorn app:app --app-dir apps/api --host 127.0.0.1 --port 8090
# Em outro terminal:
cd apps/web && python3 -m http.server 8088 --bind 127.0.0.1
```

## Testes
```sh
python3 -m pip install pytest httpx
pytest -q apps/api/tests/test_api.py
```

## Docker
```sh
docker compose -f infra/docker-compose.demo.yml up --build
```
Ambiente local: vitrine em 127.0.0.1:8088 e API em 127.0.0.1:8090.

## Próxima fase
Login e permissões no backend, depois confirmação de pagamento. A ativação pelo WAHA nunca deverá usar um número fornecido pelo cliente sem verificação da origem da mensagem.
