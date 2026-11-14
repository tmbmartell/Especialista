# Coragem para Ir — Jornada V1 (sandbox)

## Entrega

Primeiro roteiro interativo criado **do zero**, inspirado somente nos
objetivos gerais de reflexão sobre o medo. A fonte histórica da proposta
contém restrição explícita de reprodução; portanto, **não copiamos**
suas perguntas, tabelas, marcações, termos exclusivos nem textos do PDF.

Este roteiro de demonstração não é terapia e não pretende reproduzir
integralmente o plugin original. Uma incorporação posterior de conteúdo
protegido depende de autorização comercial documentada.

## Como experimentar no sandbox local

1. Na raiz, rode `docker compose -f infra/docker-compose.demo.yml up --build`.
2. Abra `http://127.0.0.1:8088`.
3. Crie uma conta **fictícia** de demonstração (não reutilize senhas reais).
4. No catálogo, clique em **Coragem para Ir → Conhecer experiência**.
5. Clique em **Experimentar conversa curta**.
6. Responda com textos de teste. O roteiro faz uma pergunta por turno e
   mostra um resumo com o passo escolhido pela própria pessoa.

Não há IA conectada nem armazenamento de respostas no servidor;
as respostas ficam em memória do navegador durante a prévia e são
descartadas ao fechar. **Não use dados sensíveis nesse ambiente.**

## Seis passos (perguntas originais)

1. **Objetivo:** escolher uma situação ou iniciativa concreta.
2. **Impacto:** observar o que está ficando pendente.
3. **Receio:** nomear o resultado indesejado imaginado.
4. **Evidência:** distinguir sinais verificáveis de suposições.
5. **Alternativa:** desenhar um passo pequeno, escolhido pela pessoa e seguro.
6. **Momento:** escolher um momento realista; encerrar com uma síntese breve.

### Respostas fora do roteiro

- `não sei` → exemplo e pergunta alternativa curta, sem avançar.
- `pular` → pula aquela etapa, sem julgamento.
- `voltar` → permite corrigir a resposta anterior.
- `reiniciar`, `novo protocolo` → limpa o contexto e começa uma jornada.
- `encerrar`, `parar` → finaliza sem pressionar.
- Resposta longa → limitada pelo contrato de entrada; não interpreta
  automaticamente crenças ou causas não comprovadas.

## Diretrizes de resposta de todos os especialistas

- Tom humano, doce e objetivo, jamais condescendente.
- Alvo de **20–55 palavras** nas respostas habituais.
- **Até uma pergunta por mensagem**, inclusive quando não compreende a resposta.
- Uma analogia breve apenas quando esclarece uma decisão.
- Nada de diagnósticos, certezas sobre o inconsciente ou promessas de cura.
- Síntese da jornada com ação concreta, sem impor a decisão.
- Se houver relato de risco urgente, priorizar proteção; a regra de
  tamanho não pode eliminar instruções de segurança importantes.

## Segurança atual

O endpoint `POST /api/me/preview/coragem-para-ir/turn` exige
sessão autenticada, token CSRF e `NG_DEMO_MODE=true`. Qualquer
resposta enviada de volta inclui `previewOnly=true`,
`aiConnected=false`, `persisted=false`.

A classificação de risco implementada nesta versão é **apenas lexical**.
Não deve ser usada isoladamente em produção: exige triagem contextual,
avaliação humana e testes de robustez. A camada de qualidade
`response_quality.py` contém verificações objetivas de concisão, mas
não substitui validação semântica.

## Próxima etapa

Uma biblioteca privada de metodologias autorizadas, com versionamento,
conversa baseada em contexto mínimo, memória por pessoa e especialista,
limites de consumo e integração de JEV/DeepSeek por adaptadores.
Sem isso, o sistema continua um roteiro conversacional determinístico,
não um assistente de IA completo.

## Testes

```sh
PYTHONPATH=apps/api pytest -q apps/api/tests/
```

Em 13/11/2026: **35 testes passaram** no sandbox temporário. Nenhuma alteração
foi implantada na VPS em produção.
