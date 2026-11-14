"""Testes da escuta adaptativa e integração aos três motores de demonstração."""
import pytest
from conversation_adaptation import intervene, classify, normalize
from coragem_engine import JourneyState, talk
from culpa_engine import GuiltState, turn as guilt_turn
from autovalor_engine import ValueState, turn as value_turn

@pytest.mark.parametrize("message,expected",[
    ("Não entendi", "confused"),("Pode dar um exemplo?", "example"),
    ("Não foi bem isso", "disagree"),("Já tentei e não deu certo", "tried"),
    ("Quero desabafar", "free_space"),("Vamos mudar de assunto", "other_topic")
])
def test_recognizes_explicit_intent(message,expected):
    assert classify(message)==expected

@pytest.mark.parametrize("message",[
    "Tenho medo de perder o emprego",
    "Não quero sair de casa ainda",
    "Eu me senti triste por isso"
])
def test_does_not_intercept_normal_personal_answer(message):
    assert classify(message) is None

@pytest.mark.parametrize("specialist,step",[
    ("coragem-para-ir","evidence"),
    ("solte-esse-peso","control"),
    ("reconheca-seu-valor",3)
])
def test_intervention_short_and_only_one_question(specialist,step):
    for message in ("Não foi bem isso", "Já tentei", "Me dê um exemplo"):
        result=intervene(message,specialist,step)
        assert result and not result.advances
        assert result.reply.count("?")<=1
        assert len(result.reply.split())<=55

def test_correcting_interpretation_preserves_stage():
    courage=JourneyState(step="evidence", answers={"goal":"Fazer uma apresentação"})
    result=talk("Você entendeu errado",courage)
    assert result.state.step=="evidence"
    assert result.state.answers==courage.answers
    assert "interpretado mal" in result.reply

    guilt=GuiltState(step="control",answers={"episode":"Uma conversa difícil"})
    result=guilt_turn("Pode dar um exemplo?",guilt)
    assert result.state.step=="control"
    assert "alcance" in result.reply

    value=ValueState(index=3,choices=["A","B","C"])
    result=value_turn("Já tentei isso",value)
    assert result.state.index==3 and result.state.choices==value.choices
    assert "O que aconteceu" in result.reply

def test_unprefixed_free_text_is_accepted_without_invented_scoring():
    result=value_turn("Eu escuto as pessoas e organizo as ideias",ValueState())
    assert result.state.index==1
    assert result.state.choices==["-"]
    assert "escuto" in result.state.notes["0"]
    result2=value_turn("A",ValueState())
    assert result2.state.choices==["A"]

def test_safety_takes_priority():
    for fn,state in ((talk,JourneyState()),(guilt_turn,GuiltState()),(value_turn,ValueState())):
        result=fn("Quero me matar",state)
        assert result.safety=="crisis"
        assert result.state==state

def test_normalize_accents():
    assert normalize("  NÃO ENTENDI!!!  ")=="nao entendi"
