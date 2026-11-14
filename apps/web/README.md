# Vitrine demonstrativa

Prévia estática, sem login, pagamentos ou WhatsApp reais. Não armazena dados de clientes.

Para visualizar:

```bash
cd apps/web
python3 -m http.server 8088 --bind 127.0.0.1
# acesse http://127.0.0.1:8088
```

O catálogo é mantido em `catalogo.json`; cada item é uma proposta comercial em revisão. Não contém prompts, arquivos internos de plugins ou chaves. Próxima fase: conectar a vitrine ao backend com autenticação, autorização e pagamentos validados no servidor.
