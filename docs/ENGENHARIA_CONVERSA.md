# Engenharia de Conversa — Nova Gente Especialista

Este contrato vale para os **13 especialistas**. A linguagem comercial é própria; o
conteúdo de método pertence a uma biblioteca privada e depende de comprovação de
direitos de utilização. O repositório público contém apenas os módulos genéricos
escritos do zero e exemplos fictícios.

## Princípio do produto

A pessoa precisa sair da conversa conseguindo **nomear o que vive, enxergar
alternativas e escolher uma pequena ação**. Sem interrogatório, conselhos
automáticos ou diagnóstico. A assistente pode pedir esclarecimento e também
respeitar respostas fora do roteiro.

## Contrato de cada resposta normal

1. **Acolha ou reconheça o fato em até uma frase**, sem elogios vazios.
2. **Traga só uma nova ideia útil**, quando houver informação suficiente.
3. **Faça no máximo uma pergunta** por mensagem.
4. Respostas curtas: **alvo de 20 a 55 palavras**, sem parágrafos longos.
5. Analogia em **uma única frase**, opcional e apenas se esclarecer um conceito.
6. Não repita nome, saudação nem pergunta anterior a cada turno.
7. Ao concluir: sintetize uma percepção + a escolha da própria pessoa + um próximo passo realista.
8. A pessoa pode dizer **“não sei”, “pular”, “voltar”, “reiniciar” ou “encerrar”**.
9. Se a pessoa não concordar com a hipótese, **rever hipótese**, jamais insistir para convencê-la.
10. Não force interpretação da infância, relação familiar, inconsciente ou “bloqueio”.

### Exemplo de tom, criado para esta plataforma

Pessoa: “Tenho medo de oferecer meu serviço porque acho que vão rejeitar.”

Especialista: “Oferecer é abrir uma porta, não exigir que a pessoa entre. O que você
imagina que aconteceria se alguém dissesse não?”

Pessoa: “Que eu não sou boa.”

Especialista: “Um não à proposta não mede seu valor. Qual evidência você tem de
que a rejeição seria sobre você, e não sobre a oferta?”

Pessoa: “Não tenho. Acho que posso mandar só para um contato.”

Especialista: “Boa alternativa. Começar por um contato ajuda a testar sem se
sobrecarregar. Quando seria um momento possível?”

**Notas:** exemplos são demonstrativos, não um chat com IA já conectado.

## Mecânica (independente do provedor)

```
Receber mensagem
  → Verificar usuário e direitos no servidor
  → Determinar especialista e versão ativa do conteúdo
  → Carregar apenas a memória autorizada daquela conta e especialidade
  → Identificar risco imediato ou necessidade de revisão humana
  → Localizar fase da jornada; aceitar resposta livre, não só alternativa predefinida
  → Se IA estiver habilitada, compor contexto MÍNIMO e gerar uma resposta curta
  → Validar comprimento, número de perguntas, coerência e segurança
  → Se for adequado, enviar e registrar apenas o permitido
  → Se for incerto, esclarecer com uma pergunta ou encaminhar para revisão
```

**JEV** pode ajudar na classificação de intenção e confiança. Jamais libera
um especialista nem executa cobrança: isso depende do servidor, identidade
e confirmação do gateway. **DeepSeek** será um adaptador de linguagem:
substituí-lo não deve alterar jornada, pagamentos, permissões ou a memória.
**WAHA** apenas transporta mensagens; seu identificador de chat não é, sozinho,
prova de titularidade ou autorização de acesso.

## Estrutura da biblioteca privada (a implementar)

Por especialista/versão:
- identidade comercial aprovada;
- objetivos, limites, fases e transições validadas;
- perguntas originais permitidas e orientação para respostas imprevistas;
- recursos extras autorizados (questionários, imagens, cálculos simbólicos);
- exemplos testados com diferentes comportamentos;
- atribuição/licença de cada fonte quando aplicável;
- testes de compatibilidade e mecanismo de rollback.

A infraestrutura deve separar **perfil público**, **método privado**, **progresso
de usuário** e **histórico consentido**, com autorização por tenant+usuário+
especialista. Nada de compartilhar a história íntima entre módulos sem
permissão explícita.

## Segurança e limites

- Não alegar ser psicólogo, psiquiatra, terapeuta credenciado ou profissional
  com 50 anos de experiência.
- Não atribuir causalidade científica a práticas simbólicas ou espiritualidade.
- Não dizer que o medo “é falso”: em situações de violência, ameaça ou perigo
  real, priorizar proteção e suporte adequado.
- Evitar linguagem de culpa, rótulos diagnósticos, manipulação ou pressão.
- O limite de palavras **não se aplica** a respostas necessárias para proteção
  diante de risco urgente.
- Solicitação de exclusão/pausa deve ser respeitada; consentimento é necessário
  para persistir dados pessoais sensíveis.
- Qualquer conteúdo de terceiros, especialmente com aviso de uso restrito, fica
  **fora do produto** até prova de autorização comercial.

## Coragem para Ir — primeiro piloto

O piloto implementa seis perguntas **novas**, uma por vez, para nomear o
objetivo, observar impacto, diferenciar previsão e evidência, escolher um
passo seguro e decidir quando testá-lo. Permite respostas livres, pular,
voltar e reiniciar. Hoje funciona em uma **prévia determinística de sandbox**:
não chama DeepSeek, não executa o conteúdo integral do plugin e não
armazena respostas no servidor. É um ensaio de experiência para validação
humana, não serviço comercial.

As respostas de risco têm apenas uma triagem preliminar por padrões de texto;
isso não substitui a triagem contextual que será exigida antes do lançamento.
