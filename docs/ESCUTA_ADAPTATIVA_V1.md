# Especialista — Escuta adaptativa V1

## O que foi implementado

Os três motores piloto preservam sua estrutura independente:
- **Coragem para Ir:** seis passos para identificar medo e avaliar um próximo passo seguro.
- **Solte Esse Peso:** seis passos para reconhecer uma situação, distinguir o que é conhecido do que foi interpretado e escolher uma atitude possível sem negar responsabilidades.
- **Reconheça Seu Valor:** dez perguntas originais, com respostas A/B/C/D, texto livre e resultados que não medem valor humano.

Foi adicionada a camada `conversation_adaptation.py`, que intercepta **pedidos explícitos de conversa**, sem mudar o estado e sem exigir uma nova resposta de formulário:

| Pedido | Resposta desejada |
|---|---|
| “Não entendi” | reformular com uma pergunta simples |
| “Pode dar um exemplo?” | dar exemplo/analogia breve, só quando pertinente |
| “Não foi bem isso” | reconhecer interpretação equivocada e abrir espaço para correção |
| “Já tentei” | perguntar o resultado da tentativa, sem repetir conselho |
| “Quero desabafar” | abrir espaço para falar, sem pressionar |
| “Mudar de assunto” | acolher a mudança e perguntar o novo tema |

No questionário **Reconheça Seu Valor**, respostas livres são salvas como `notes`, **sem pontuação fabricada**. Não é necessário escrever a expressão artificial `minha resposta:`. Se as respostas pontuadas forem insuficientes, não se afirma um perfil predominante.

## Engenharia geral

1. A sessão/identidade é verificada no servidor antes de abrir a prévia.
2. A checagem de risco urgente precede a camada de adaptação.
3. Uma intenção de esclarecimento **não avança a etapa**.
4. Em respostas normais, alvo de até 55 palavras e uma pergunta por vez.
5. Analogias são opcionais e nunca devem virar longas histórias.
6. Comandos de parar, voltar, reiniciar e pular permanecem disponíveis.
7. Nenhuma conversa real é gravada neste sandbox. O estado é temporário e devolvido ao navegador.
8. Os plugins originais são referências de capacidades; **não** foram copiados nem incorporados automaticamente.

## Limitações explícitas

- Este é um **classificador de frases explícitas**, não um modelo generativo.
- Não substitui a futura integração DeepSeek/JEV, interpretação de respostas ambíguas nem avaliação contextual de risco.
- Não libera produtos, não verifica pagamentos, não conecta WhatsApp e não utiliza materiais restritos.
- Sem licença comercial confirmada, nenhuma pergunta/texto protegido de terceiro deve ser publicada.
- Não é adequado para conduzir casos de saúde mental como terapia; a triagem de risco é preliminar e precisa de validação humana.

## Testes desta versão

Executados em sandbox temporário, sem alterar produção:
- Python: **50 testes passaram** (fluxos de Coragem, Culpa, Autovalor, orçamento, interpretação e segurança).
- Verificação de sintaxe Python: aprovada.
- Um aviso de depreciação da biblioteca de testes, não impeditivo.

Além disso, foi corrigido o bloco `run` da etapa de validação JSON no GitHub Actions.

## Próxima etapa

Testes de comportamento com casos reais **fictícios** e um adaptador opcional de IA que:
- só rode com credencial de servidor configurada;
- jamais envie contexto de outra conta ou especialista;
- mantenha limites curtos e uma pergunta por turno;
- possua resposta segura de fallback quando o modelo falhar;
- não exponha métodos privados no Git público.
