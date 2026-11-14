# F2 — Identidades, jornadas e biblioteca de metodologias

**Situação:** especificação funcional e prévias públicas desenvolvidas. Não é a implementação integral dos plugins e não autoriza vendas.

## Regra de produto

O visitante escolhe pelo **resultado desejado**, nunca pelo nome original do GPT, autor ou obra de referência. A plataforma contém 13 produtos contratuais e uma única infraestrutura.

Cada especialista terá:
1. identidade comercial própria (nome, proposta, abertura, voz e experiência);
2. uma jornada de perguntas que aceita respostas livres e escolhas fora do roteiro;
3. capacidades específicas (texto, cartas, imagens ou cálculos, quando implementadas);
4. memória **por cliente + especialista**, controlada por autorização explícita;
5. um núcleo de conteúdo **privado e versionado**, não incluído neste repositório.

O arquivo `apps/web/experiencias.json` contém **somente informações públicas**: missão do produto, tom comercial, uma pergunta de abertura e títulos resumidos das etapas. Não contém perguntas proprietárias, livros, prompts de sistema, PDFs, textos originais ou documentos de terceiros.

## Matriz de diferenciação

| Especialista | Função percebida | Mecânica futura a preservar |
|---|---|---|
| A Virada de Chave | Examinar interpretações e decisões | Situação concreta → interpretação → alternativas → decisão prática |
| Quebre o Ciclo | Perceber padrões repetidos | Episódio → repetição → resposta alternativa → revisão |
| Cartas e Caminhos | Tarô como reflexão simbólica | Seleção de cartas, posições, leitura e pergunta final |
| Raízes e Laços | Vínculos familiares e narrativas | Fato conhecido → perspectivas possíveis → limites presentes |
| O Que Seu Sonho Conta? | Registro e análise reflexiva dos sonhos | Relato → imagens → associações pessoais → reflexão |
| Reconheça Seu Valor | Autovalorização e trocas | Questionário de 10 perguntas → síntese explicativa → opção de aprofundar |
| Nas Linhas da Sua Mão | Quiromancia recreativa | Imagens ou descrição → símbolos → reflexão sem previsões factuais |
| Conexões que Fazem Sentido | Relações e numerologia simbólica | Relacionamento → leitura opcional → ações práticas |
| Seu Mapa em Números | Numerologia recreativa | Dados opcionais → cálculo verificável → interpretação simbólica |
| Mude por Dentro | Hábitos e mudanças pessoais | Intenção → contexto → plano pequeno → revisão |
| Amar Sem Se Perder | Limites em relacionamentos | Contextos internos/externos → necessidades → limites → escolhas |
| Solte Esse Peso | Culpa e autocobrança | Fato → responsabilidade → reparação ou aceitação → ação |
| Coragem para Ir | Medo e decisões | Situação → receio → riscos reais → passo seguro |

Essas sequências são um **mapa de capacidades**. A lógica detalhada e validada de cada plugin deverá ser reconstituída de conteúdo original ou devidamente autorizado, sem transferir redação protegida ou replicar a identidade de terceiros.

## Primeiro lote de homologação

### Coragem para Ir
- Resultado: compreender um receio concreto e planejar o primeiro passo de baixo risco.
- Conversa: próxima, objetiva e sem forçar decisão.
- Testes futuros: caso cotidiano, caso de risco físico real (não encorajar exposição), resposta livre e pausa voluntária.

### Solte Esse Peso
- Resultado: distinguir responsabilidade possível de autocobrança desnecessária.
- Conversa: cuidadosa, sem culpabilizar ou diagnosticar.
- Testes futuros: reparar algo quando cabível, aceitar limites, acolher ambiguidade e acompanhar progresso.

### Reconheça Seu Valor
- Resultado: explorar padrões de reciprocidade e limites.
- Mecânica específica a preservar: **10 perguntas de escolha**, pontuação coerente e explicação não diagnóstica; versão reconstruída e auditada.
- Testes futuros: todas as alternativas, empates, interrupção, retomada e respostas inesperadas.

## Camadas de conteúdo e segurança

**Camada pública (GitHub atual):** vitrine, preço, descrições, nomes comerciais, roteiro resumido e uma pergunta demonstrativa. Nada confidencial.

**Camada privada (a provisionar):** arquivos de método, textos de perguntas, regras de transição, pesos, prompts completos, licenças, revisões e exemplos de resposta. Acesso só pelo backend e administrador autorizado. Não copiar esses dados para o frontend.

**Camada de conversas (produção futura):** respostas do cliente, progresso, consentimento, exclusão, retenção e exportação de dados. Isolamento por conta e especialista; acesso entre módulos apenas com permissão explícita.

**Camada de decisões (JEV futuro):** classifica intenção e incerteza, sem conceder direitos nem extrair dados de outras contas. A política de autorização permanece determinística no servidor.

**Camada do modelo conversacional (DeepSeek futuro):** contexto mínimo e métodos autorizados, sempre com versão identificável. A conversa não deve afirmar credenciais terapêuticas, diagnósticos ou resultados garantidos.

## Regra administrativa para inserir novas metodologias

Estados: `rascunho → em_revisao → aprovado_para_teste → homologado → publicado`.

Cada alteração deve guardar: identificador do especialista, versão, editor, justificativa, fontes e direitos de uso, data de publicação, conjunto de testes e possibilidade de rollback. Adicionar novo método **não deve sobrescrever silenciosamente** as sessões em andamento: cada conversa registra a versão utilizada.

## Bloqueios antes do lançamento

- Revisão jurídica/autoral; retirar nomes comerciais não é licença para republicar conteúdo de terceiro.
- Validar e ajustar cada percurso com testes humanos; evitar rótulos como “narcisista” aplicados a pessoas sem avaliação.
- Medidas de privacidade para informações emocionais, familiares e dados de nascimento.
- Conteúdo simbólico explícito como recreativo e não comprovado cientificamente.
- Recursos de saúde mental: foco educativo, redirecionamento responsável quando necessário, sem alegar atendimento clínico.
- Cobranças, vínculo seguro de WhatsApp e verificação de direitos ainda não integrados.

**A prévia não envia mensagens nem gera uma conversa real.** O próximo incremento funcional é o armazenamento seguro de conteúdos e testes isolados do motor, sem expor metodologias no frontend.
