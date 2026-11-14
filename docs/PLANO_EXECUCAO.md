# Plano de execução — Especialista

## Etapas e critérios verificáveis
- **F0 — Catálogo:** confirmar 13 perfis, nomes comerciais, critérios de revisão e propriedade/licenciamento.
- **F1 — Identidade:** login e sessões; isolamento testado com duas contas reais de teste.
- **F2 — Metodologias:** converter e homologar funcionalidades próprias/autorizadas sem copiar textos de terceiros.
- **F3 — Motor:** Jev classifica intenções; política determinística controla direitos; LLM responde com contexto mínimo.
- **F4 — WhatsApp:** integrar WAHA em rede interna; verificar remetente; ativação por código de uso único; deduplicar eventos.
- **F5 — Assinaturas:** gateway com webhooks autenticados, recorrência, prorrata e compra de módulos adicionais.
- **F6 — Painéis:** cliente gerencia assinaturas; admin gerencia preços, capacidades, versões e liberação individual.
- **F7 — Segurança:** segregação por usuário, testes de acesso, LGPD, observabilidade, retenção, limites e backups.
- **F8 — Publicação:** domínio, TLS, homologação, piloto e expansão gradual.

## Níveis
N0 planejado → N1 especificado → N2 desenvolvido → N3 integrado → N4 homologado → N5 publicado.

## Entrega atual
A **vitrine demonstrativa e API de orçamento** estão no código. F1 implementou contas e carrinho em sandbox (não homologados para produção). F2 tem **13 identidades públicas e etapas resumidas de jornada**, API de prévias e interface de exploração; os conteúdos integrais dos plugins ainda NÃO foram migrados, autorizados, testados ou integrados ao modelo conversacional. Pagamento, JEV, WAHA e DeepSeek seguem desconectados. Consulte [F2 Metodologias](F2_METODOLOGIAS.md).
