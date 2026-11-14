"""Reconheça Seu Valor — questionário ORIGINAL 10x4, leitura não diagnóstica.

Duas dimensões: contribuições percebidas e retorno desejado.
A resposta não mede valor humano, mérito ou capacidade financeira.
"""
import re
from typing import Literal
from pydantic import BaseModel, Field
from conversation_adaptation import intervene
from coragem_engine import STOP, RESTART, BACK, SKIP, UNKNOWN, CRISIS, DANGER

# Os enunciados e alternativas abaixo foram escritos para este produto,
# não extraídos do material proprietário de terceiros.
QUESTIONS = [
 {"topic":"offering","prompt":"Num grupo, qual contribuição você costuma oferecer primeiro?","options":["Escutar até entender","Organizar as ideias","Dar o impulso inicial","Ajudar a executar"]},
 {"topic":"offering","prompt":"Quando alguém te pede ajuda, o que sai mais naturalmente?","options":["Fazer a pessoa se sentir ouvida","Criar um plano simples","Propor um caminho novo","Estar presente na tarefa"]},
 {"topic":"offering","prompt":"Quando surge um imprevisto, como você tende a colaborar?","options":["Acalmo a conversa","Organizo prioridades","Encontro outra possibilidade","Cuido do que precisa ser feito"]},
 {"topic":"offering","prompt":"O que você gostaria que notassem mais na sua contribuição?","options":["Minha sensibilidade","Minha clareza","Minha iniciativa","Minha constância"]},
 {"topic":"offering","prompt":"Em um projeto de que gosta, qual papel assume com prazer?","options":["Conectar pessoas","Planejar etapas","Começar algo novo","Garantir continuidade"]},
 {"topic":"return","prompt":"Depois de um esforço importante, qual retorno faz mais diferença?","options":["Tempo de atenção sincera","Condições justas e claras","Liberdade para decidir","Ajuda concreta quando preciso"]},
 {"topic":"return","prompt":"O que mais faz você sentir reciprocidade?","options":["Uma conversa presente","Acordos cumpridos","Confiarem nas minhas escolhas","Dividirem a responsabilidade"]},
 {"topic":"return","prompt":"Ao pedir reconhecimento, qual pedido combina mais com você?","options":["Quero ser escutado(a)","Quero uma troca justa","Quero espaço para agir","Quero apoio no cotidiano"]},
 {"topic":"return","prompt":"Quando uma relação está desequilibrada, o que costuma faltar?","options":["Presença de verdade","Combinados respeitados","Respeito à minha autonomia","Participação nas tarefas"]},
 {"topic":"return","prompt":"Que mudança de troca gostaria de experimentar primeiro?","options":["Mais atenção mútua","Mais clareza sobre expectativas","Mais voz nas escolhas","Mais divisão de cuidados"]},
]
OFFER = {"A":"escuta e conexão","B":"clareza e organização","C":"iniciativa e criação","D":"cooperação e constância"}
RETURN = {"A":"presença e atenção","B":"acordos e justiça nas trocas","C":"autonomia e confiança","D":"apoio prático"}
KEYS = ("A","B","C","D")
MAX_NOTES = 250

class ValueState(BaseModel):
    index: int = Field(default=0, ge=0, le=10)
    choices: list[str] = Field(default_factory=list, max_length=10)
    notes: dict[str,str] = Field(default_factory=dict)

    def filtered(self):
        safe=[c if c in KEYS else "-" for c in self.choices[:10]]
        safe=safe[:min(self.index,10)]
        return ValueState(index=min(self.index,10),choices=safe,
                          notes={str(k):str(v)[:MAX_NOTES] for k,v in self.notes.items() if str(k).isdigit()})

class ValueResult(BaseModel):
    reply: str
    state: ValueState
    done: bool = False
    safety: Literal["normal","crisis","danger"] = "normal"
    previewOnly: bool = True
    aiConnected: bool = False
    persisted: bool = False

def question(index:int)->str:
    q=QUESTIONS[index]
    options="  ".join(f"{letter}) {value}" for letter,value in zip(KEYS,q["options"]))
    return f"{index+1}/10 — {q['prompt']}\n{options}"

def _best(choices: list[str], labels:dict[str,str])->str:
    counts={key:choices.count(key) for key in KEYS}
    max_count=max(counts.values()) if counts else 0
    if max_count==0:return "não foi possível identificar uma preferência"
    leaders=[labels[k] for k,v in counts.items() if v==max_count]
    return " e ".join(leaders[:2])+(f" (e outras {len(leaders)-2} opções)" if len(leaders)>2 else "")

def _final(state:ValueState)->str:
    offers=[c for c in state.choices[:5] if c in KEYS]
    receives=[c for c in state.choices[5:10] if c in KEYS]
    if len(offers)<2 or len(receives)<2:
        return "Você fez uma reflexão inicial. Como houve poucas escolhas em uma das partes, prefiro não tirar conclusões. Experimente notar o que oferece e o que gostaria de receber."
    return (f"Você destacou { _best(offers,OFFER) } no que oferece; e { _best(receives,RETURN) } no retorno que deseja. "
            "Isso mostra preferências, não mede seu valor. Experimento: faça um pedido claro sobre o retorno de que precisa.")

def turn(message:str,state:ValueState|None=None)->ValueResult:
    state=(state or ValueState()).filtered()
    content=re.sub(r"\s+"," ",message).strip()
    cmd=content.casefold().strip(" .!?")
    if CRISIS.search(content):
        return ValueResult(reply="Sinto muito que esteja tão difícil. Sua segurança vale mais que qualquer questionário. Em risco imediato, procure ajuda de emergência e alguém de confiança. Você está em segurança agora?",state=state,safety="crisis")
    if DANGER.search(content):
        return ValueResult(reply="Se existe ameaça ou violência, priorize proteção, não um teste de valor pessoal. Busque apoio de confiança e um lugar seguro. Você está em segurança agora?",state=state,safety="danger")
    # Não avançar a jornada quando a pessoa pede esclarecimento ou corrige a leitura.
    intervention = intervene(content, "reconheca-seu-valor", state.index)
    if intervention is not None:
        return ValueResult(reply=intervention.reply, state=state)
    if cmd in STOP:
        return ValueResult(reply="Tudo bem parar aqui. Seu valor não depende de completar um questionário.",state=ValueState(index=10),done=True)
    if cmd in RESTART:
        return ValueResult(reply="Vamos recomeçar sem pressa. "+question(0),state=ValueState())
    if cmd in BACK:
        target=max(0,state.index-1)
        return ValueResult(reply="Claro, vamos rever. "+question(target),
                           state=ValueState(index=target,choices=state.choices[:target],notes={k:v for k,v in state.notes.items() if int(k)<target}))
    if state.index==10:
        return ValueResult(reply="Essa reflexão terminou. Escreva «reiniciar» para fazer outra.",state=state,done=True)
    if not content:
        return ValueResult(reply=("Vamos observar como você contribui e como prefere receber. " if state.index==0 else "")+question(state.index),state=state)
    if cmd in UNKNOWN:
        return ValueResult(reply="Não precisa se encaixar perfeitamente. Escolha a opção que mais se aproxima hoje, ou escreva «pular».\n"+question(state.index),state=state)
    answer=content.upper()
    notes=dict(state.notes)
    if answer in KEYS or cmd in SKIP:
        chosen=answer if answer in KEYS else "-"
    elif len(content) >= 2:
        chosen="-"  # Texto livre não vira pontuação fictícia.
        notes[str(state.index)]=(content.split(":",1)[1].strip() if cmd.startswith("minha resposta:") else content)[:MAX_NOTES]
    else:
        return ValueResult(reply="Você pode escolher A, B, C ou D ou responder com suas palavras.",state=state)
    next_state=ValueState(index=state.index+1,choices=[*state.choices,chosen],notes=notes)
    if next_state.index==10:
        return ValueResult(reply=_final(next_state),state=next_state,done=True)
    lead="Entendi. " if state.index in (0,5) else ""
    return ValueResult(reply=lead+question(next_state.index),state=next_state)
