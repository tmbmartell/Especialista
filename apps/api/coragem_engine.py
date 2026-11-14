"""Coragem para Ir — roteiro conversacional ORIGINAL, determinístico e sem LLM.

Os passos foram escritos do zero a partir do objetivo geral de reconhecer receios,
distinguir riscos e escolher ações. Não reproduzem o questionário restrito da fonte.
Sem persistência, diagnóstico, previsão ou liberação de acesso a especialista.
"""
import re
from typing import Literal

from pydantic import BaseModel, Field

Step = Literal["goal", "impact", "prediction", "evidence", "choice", "timing", "done"]
ORDER = ("goal", "impact", "prediction", "evidence", "choice", "timing")
QUESTIONS = {
    "goal": "Me conta: o que você gostaria de fazer, mas o medo está segurando?",
    "impact": "O que você tem deixado de fazer por causa desse receio?",
    "prediction": "O que você imagina que poderia dar errado?",
    "evidence": "O que você sabe de fato sobre esse risco hoje?",
    "choice": "Qual seria um primeiro passo pequeno e seguro?",
    "timing": "Quando você poderia experimentar esse passo, sem se pressionar?",
}
LEADS = {
    "impact": "Entendi. Vamos olhar para o efeito disso.",
    "prediction": "É bom reconhecer o que isso tem custado.",
    "evidence": "O medo às vezes parece certeza. Vamos separar as coisas.",
    "choice": "Você já olhou para o risco. Agora pense nas opções.",
    "timing": "Pequenos passos costumam ser mais viáveis.",
}
HINTS = {
    "goal": "Não precisa explicar tudo. Pense numa situação recente. O que você queria fazer?",
    "impact": "Pode ser algo simples, como uma conversa adiada. O que ficou pendente?",
    "prediction": "Se esse receio tivesse uma frase, qual seria?",
    "evidence": "Medo é como um alarme: avisa, mas não prova o perigo. O que você conseguiu confirmar?",
    "choice": "Pode ser um passo de cinco minutos. Qual seria seguro para você?",
    "timing": "Sem prazo rígido. Qual momento da semana parece possível?",
}
RESTART = {"reiniciar", "começar de novo", "novo protocolo", "recomeçar"}
STOP = {"encerrar", "parar", "encerro esse protocolo", "sair"}
BACK = {"voltar", "voltar uma pergunta", "anterior"}
SKIP = {"pular", "passar", "prefiro não responder"}
UNKNOWN = {"não sei", "nao sei", "sei lá", "sei la", "não faço ideia", "nao faco ideia"}
# Esses sinais são apenas proteção preliminar; uma implantação real exige
# triagem contextual revisada e rota humana, sem depender só de palavras-chave.
CRISIS = re.compile(r"\b(?:quero morrer|vou me matar|me matar|tirar minha vida|tirar a minha vida|acabar com minha vida|pensando em suic[ií]dio)\b", re.I)
DANGER = re.compile(r"\b(?:me ameaçou|me ameacou|estou sendo ameaçad[ao]|estou sendo ameacad[ao]|me agrediu|violência doméstica|violencia domestica|me persegue|estou em perigo imediato)\b", re.I)


class JourneyState(BaseModel):
    step: Step = "goal"
    answers: dict[str, str] = Field(default_factory=dict)

    @staticmethod
    def clean(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()[:450]

    def filtered(self) -> "JourneyState":
        clean = {key: self.clean(value) for key, value in self.answers.items()
                 if key in ORDER and isinstance(value, str)}
        return JourneyState(step=self.step, answers=clean)


class TurnResult(BaseModel):
    reply: str
    state: JourneyState
    done: bool = False
    safety: Literal["normal", "crisis", "danger"] = "normal"
    previewOnly: bool = True
    aiConnected: bool = False
    persisted: bool = False


def _text(value: str, limit: int = 75) -> str:
    value = re.sub(r"\s+", " ", value).strip().strip(".")
    return value if len(value) <= limit else value[:limit].rsplit(" ", 1)[0] + "…"


def _finish(state: JourneyState) -> str:
    answers = state.answers
    goal = _text(answers.get("goal", "dar um passo importante"))
    choice = _text(answers.get("choice", "definir um passo seguro"))
    when = _text(answers.get("timing", "quando for possível"), 45)
    return (
        f"Você quer: {goal}. Seu próximo passo: {choice}. "
        f"Momento escolhido: {when}. É um começo, não uma cobrança. "
        "Se precisar, podemos revisar o plano."
    )


def talk(message: str, supplied: JourneyState | None = None) -> TurnResult:
    state = (supplied or JourneyState()).filtered()
    content = re.sub(r"\s+", " ", message).strip()
    command = content.casefold().strip(".! ")

    if CRISIS.search(content):
        return TurnResult(
            reply=("Sinto muito que esteja tão difícil. Sua segurança vem primeiro. "
                   "Se houver risco imediato, procure a emergência local e alguém de confiança. "
                   "Você está em segurança agora?"),
            state=state, safety="crisis")
    if DANGER.search(content):
        return TurnResult(
            reply=("Se alguém está te ameaçando, não precisa enfrentar essa situação para provar coragem. "
                   "Priorize um lugar seguro e apoio de alguém de confiança. "
                   "Você está em segurança agora?"),
            state=state, safety="danger")
    if command in RESTART:
        return TurnResult(reply="Vamos começar de novo, no seu ritmo. " + QUESTIONS["goal"],
                          state=JourneyState())
    if command in STOP:
        return TurnResult(reply="Tudo bem encerrar por aqui. Você pode voltar quando quiser.",
                          state=JourneyState(step="done"), done=True)
    if command in BACK:
        index = ORDER.index(state.step) if state.step in ORDER else len(ORDER)
        previous = ORDER[max(0, index - 1)]
        answers = {key: val for key, val in state.answers.items()
                   if ORDER.index(key) < ORDER.index(previous)}
        return TurnResult(reply="Claro, vamos voltar. " + QUESTIONS[previous],
                          state=JourneyState(step=previous, answers=answers))
    if state.step == "done":
        return TurnResult(reply="Essa jornada foi encerrada. Escreva «reiniciar» para começar outra.",
                          state=state, done=True)
    if not content:
        return TurnResult(reply="Oi, que bom ter você aqui. Vamos com calma. " + QUESTIONS[state.step],
                          state=state)
    if command in UNKNOWN:
        return TurnResult(reply=HINTS[state.step], state=state)
    if len(content) < 2 and command not in SKIP:
        return TurnResult(reply="Pode me contar um pouquinho mais. " + QUESTIONS[state.step], state=state)

    answers = dict(state.answers)
    answers[state.step] = "Prefiro não responder" if command in SKIP else JourneyState.clean(content)
    index = ORDER.index(state.step)
    if index == len(ORDER) - 1:
        finished = JourneyState(step="done", answers=answers)
        return TurnResult(reply=_finish(finished), state=finished, done=True)

    following = ORDER[index+1]
    next_state = JourneyState(step=following, answers=answers)
    return TurnResult(reply=LEADS[following] + " " + QUESTIONS[following],
                      state=next_state)
