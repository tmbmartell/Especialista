"""Escuta adaptativa ORIGINAL para os três pilotos.
Não substitui a compreensão semântica de um modelo de IA.
Não armazena respostas, não chama serviços externos nem concede direitos.
"""
import re
import unicodedata
from dataclasses import dataclass

def normalize(message: str) -> str:
    text=unicodedata.normalize("NFKD",message.casefold())
    text="".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+"," ",text).strip(" \t\n.!?…")

@dataclass(frozen=True)
class Intervention:
    intent: str
    reply: str
    advances: bool = False

REPHRASES={
    "coragem-para-ir":{
        "goal":"Qual vontade você tem guardado por receio?",
        "impact":"O que tem ficado para depois por causa disso?",
        "prediction":"Qual é a consequência que mais te preocupa?",
        "evidence":"O que você realmente sabe sobre essa possibilidade?",
        "choice":"Qual passo seria pequeno o suficiente para ser seguro?",
        "timing":"Em que momento caberia esse passo?",
    },
    "solte-esse-peso":{
        "episode":"Qual lembrança ainda traz esse peso?",
        "emotion":"Que sentimento aparece quando você lembra?",
        "certainty":"Quais partes da história você sabe que aconteceram?",
        "control":"O que você podia escolher naquela ocasião?",
        "repair":"Há algo seguro que você queira conversar ou reparar?",
        "action":"Que atitude cuidadosa cabe na sua rotina agora?",
    },
    "reconheca-seu-valor":{},
}
EXAMPLES={
    "coragem-para-ir":{
        "goal":"Por exemplo, querer apresentar uma ideia e ficar adiando. O que você gostaria de tentar?",
        "impact":"Por exemplo, deixar de pedir uma oportunidade. O que ficou pendente para você?",
        "prediction":"Como quando alguém pensa que um 'não' prova incapacidade. O que você imagina que aconteceria?",
        "evidence":"Um medo pode soar como certeza sem ser prova. Que informação você já confirmou?",
        "choice":"Talvez apenas escrever uma mensagem, sem enviá-la ainda. Qual passo seguro ajudaria?",
        "timing":"Pode ser reservar cinco minutos na semana. Qual momento faria sentido?",
    },
    "solte-esse-peso":{
        "episode":"Pode ser uma conversa que terminou mal. Qual lembrança tem voltado para você?",
        "emotion":"Algumas pessoas sentem tristeza; outras, raiva. O que aparece em você?",
        "certainty":"É como separar uma fotografia das interpretações sobre ela. O que você sabe que ocorreu?",
        "control":"Você podia escolher suas palavras, mas não controlar a reação alheia. O que estava ao seu alcance?",
        "repair":"Pode ser um pedido de desculpas, se isso for seguro. Há algum gesto que faria sentido?",
        "action":"Às vezes escrever o que gostaria de dizer já ajuda a organizar. Qual pequeno gesto prefere?",
    },
    "reconheca-seu-valor":{},
}
def classify(message: str) -> str | None:
    text=normalize(message)
    if not text:return None
    commands=(
        ("disagree",("nao e bem isso","nao foi bem isso","nao faz sentido","nao concordo",
                     "discordo","isso nao combina","essa nao e a questao","nao e isso",
                     "voce entendeu errado","entendeu errado")),
        ("tried",("ja tentei","ja fiz","eu tentei isso","isso nao funcionou")),
        ("example",("pode dar um exemplo","me de um exemplo","da um exemplo","exemplo","por exemplo")),
        ("confused",("nao entendi","pode explicar de outro jeito","pode reformular","explica melhor",
                     "nao ficou claro","estou confuso","estou confusa")),
        ("free_space",("quero desabafar","quero so conversar","so queria conversar","posso falar um pouco")),
        ("other_topic",("quero falar de outra coisa","vamos mudar de assunto","prefiro outro assunto")),
    )
    for intent,words in commands:
        if any(text.startswith(word) for word in words):return intent
    return None

def intervene(message: str, specialist: str, step: str | int) -> Intervention | None:
    """Só responde a pedidos explícitos, preservando o passo atual.
    O chamador deve priorizar triagem de crise/perigo antes dessa função.
    """
    intent=classify(message)
    if not intent or specialist not in REPHRASES:return None
    common={
        "disagree":"Posso ter interpretado mal. O que não encaixou no que você viveu?",
        "tried":"Entendi. Não vou repetir a mesma sugestão. O que aconteceu quando você tentou?",
        "free_space":"Claro. Podemos deixar o roteiro de lado um instante. O que você precisa colocar para fora?",
        "other_topic":"Tudo bem mudar de assunto. Sobre o que você prefere conversar agora?",
    }
    if intent in common:return Intervention(intent,common[intent])
    if specialist=="reconheca-seu-valor":
        if intent=="example":
            return Intervention(intent,"Por exemplo, você pode gostar de organizar ideias e acolher pessoas. Escolha a opção mais próxima ou responda livremente.")
        if intent=="confused":
            return Intervention(intent,"Sem problema. Pense no que é mais parecido com você hoje. Se nenhuma opção servir, responda livremente.")
    if intent=="example":
        answer=EXAMPLES[specialist].get(str(step))
        if answer:return Intervention(intent,answer)
    if intent=="confused":
        question=REPHRASES[specialist].get(str(step))
        if question:return Intervention(intent,"Vou perguntar de outro jeito. "+question)
    return None
