"""Solte Esse Peso — percurso ORIGINAL, educativo e sem LLM.

Diferencia fato, impacto e responsabilidade sem afirmar culpas ou patologias.
Não reproduz questionários nem marcas do material restrito de terceiros.
"""
import re
from typing import Literal
from pydantic import BaseModel, Field
from coragem_engine import STOP, RESTART, BACK, SKIP, UNKNOWN, CRISIS, DANGER

Stage = Literal["episode","emotion","certainty","control","repair","action","done"]
ORDER = ("episode","emotion","certainty","control","repair","action")
QUESTIONS = {
 "episode":"Qual situação ainda pesa quando você se lembra dela?",
 "emotion":"Quando pensa nisso, o que sente com mais força?",
 "certainty":"O que você sabe que aconteceu, sem completar a história com suposições?",
 "control":"O que realmente estava ao seu alcance naquele momento?",
 "repair":"Há algo que você gostaria de reparar ou conversar, se for seguro?",
 "action":"Qual gesto pequeno, possível e respeitoso você poderia fazer agora?",
}
LEADS = {
 "emotion":"Imagino que isso mexa com você.",
 "certainty":"Podemos olhar com calma, sem tirar conclusões rápidas.",
 "control":"Uma lembrança tem várias partes. Vamos olhar só a sua.",
 "repair":"Reconhecer limites não apaga os efeitos do que aconteceu.",
 "action":"Reparar e se cuidar podem coexistir.",
}
HINTS = {
 "episode":"Pode ser um episódio pequeno ou antigo. Qual lembrança veio primeiro?",
 "emotion":"Uma palavra já serve: tristeza, vergonha, raiva ou outra. Qual é a sua?",
 "certainty":"Pense no que uma câmera teria registrado, sem adivinhar pensamentos. O que aconteceu?",
 "control":"Nem tudo dependia de você. O que podia decidir naquele momento?",
 "repair":"Às vezes não cabe contato. Existe algo seguro que faça sentido para você?",
 "action":"Não precisa resolver tudo hoje. Qual atitude cabe na sua semana?",
}
MAX_ANSWER = 360

class GuiltState(BaseModel):
    step: Stage = "episode"
    answers: dict[str,str] = Field(default_factory=dict)

    def compact(self):
        return GuiltState(step=self.step, answers={
            k: re.sub(r"\s+"," ",v).strip()[:MAX_ANSWER]
            for k,v in self.answers.items() if k in ORDER and isinstance(v,str)
        })

class GuiltResult(BaseModel):
    reply: str
    state: GuiltState
    done: bool = False
    safety: Literal["normal","crisis","danger"] = "normal"
    previewOnly: bool = True
    aiConnected: bool = False
    persisted: bool = False

def short(text: str, limit=65):
    text = re.sub(r"\s+"," ",text).strip().strip(".")
    return text if len(text) <= limit else text[:limit].rsplit(" ",1)[0] + "…"

def turn(message: str, state: GuiltState | None = None) -> GuiltResult:
    state=(state or GuiltState()).compact()
    content=re.sub(r"\s+"," ",message).strip()
    cmd=content.casefold().strip(" .!?")

    if CRISIS.search(content):
        return GuiltResult(reply="Sinto muito que isso esteja tão difícil. Sua segurança vem primeiro. Procure ajuda de emergência se houver risco imediato e avise alguém de confiança. Você está em segurança agora?",state=state,safety="crisis")
    if DANGER.search(content):
        return GuiltResult(reply="Se existe ameaça ou violência, sua segurança vem antes de qualquer conversa ou reparação. Procure um local seguro e apoio de confiança. Você está em segurança agora?",state=state,safety="danger")
    if cmd in STOP:
        return GuiltResult(reply="Tudo bem encerrar. Você pode retomar quando quiser, sem cobrança.",state=GuiltState(step="done"),done=True)
    if cmd in RESTART:
        return GuiltResult(reply="Vamos recomeçar com calma. "+QUESTIONS["episode"],state=GuiltState())
    if cmd in BACK:
        idx=ORDER.index(state.step) if state.step in ORDER else len(ORDER)
        target=ORDER[max(0,idx-1)]
        kept={k:v for k,v in state.answers.items() if ORDER.index(k)<ORDER.index(target)}
        return GuiltResult(reply="Claro, podemos rever. "+QUESTIONS[target],state=GuiltState(step=target,answers=kept))
    if state.step=="done":
        return GuiltResult(reply="Por hoje, encerramos. Para outra conversa, escreva «reiniciar».",state=state,done=True)
    if not content:
        return GuiltResult(reply="Estou aqui para olhar isso com você, sem julgamentos. "+QUESTIONS[state.step],state=state)
    if cmd in UNKNOWN:
        return GuiltResult(reply=HINTS[state.step],state=state)
    if len(content)<2 and cmd not in SKIP:
        return GuiltResult(reply="Pode contar um pouco mais. "+QUESTIONS[state.step],state=state)
    responses=dict(state.answers)
    responses[state.step]="Prefiro não responder" if cmd in SKIP else content[:MAX_ANSWER]
    idx=ORDER.index(state.step)
    if idx==len(ORDER)-1:
        final=GuiltState(step="done",answers=responses)
        action=responses.get("action","revisar o que é possível")
        if action=="Prefiro não responder":
            return GuiltResult(reply="Você olhou para um assunto difícil sem precisar resolver tudo agora. Se quiser, podemos retomar e escolher uma ação depois.",state=final,done=True)
        return GuiltResult(reply=f"Você encontrou um possível próximo gesto: {short(action)}. Faça no seu ritmo, sem apagar responsabilidades reais. O importante é agir com cuidado, não se punir indefinidamente.",state=final,done=True)
    next_step=ORDER[idx+1]
    return GuiltResult(reply=LEADS[next_step]+" "+QUESTIONS[next_step],state=GuiltState(step=next_step,answers=responses))
