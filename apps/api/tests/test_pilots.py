"""Testes de empatia curta, respeito às respostas e separação das experiências."""
from pathlib import Path
import os
import pytest
from fastapi.testclient import TestClient

os.environ["CATALOG_PATH"] = str(Path(__file__).resolve().parents[2]/"web"/"catalogo.json")
os.environ["EXPERIENCES_PATH"] = str(Path(__file__).resolve().parents[2]/"web"/"experiencias.json")

from app import app
from culpa_engine import GuiltState,turn as guilt_turn
from autovalor_engine import ValueState,turn as value_turn,QUESTIONS
from response_quality import response_issues

def test_culpa_six_steps_and_concise_summary():
    current=GuiltState()
    for text in ["Briguei com meu amigo.","Tristeza.","Nós discutimos e ele saiu.","Poderia ter ouvido melhor.","Posso pedir desculpas sem exigir resposta.","Vou mandar uma mensagem curta."]:
        out=guilt_turn(text,current)
        assert response_issues(out.reply,emergency=out.safety!="normal")==[],out.reply
        assert out.persisted is False and out.aiConnected is False
        current=out.state
    assert out.done is True and current.step=="done"
    assert "mensagem curta" in out.reply
    assert len(current.answers)==6

@pytest.mark.parametrize("cmd",["não sei","sei lá"," ","a"])
def test_culpa_uncertainty_does_not_force_advance(cmd):
    r=guilt_turn(cmd,GuiltState())
    assert r.state.step=="episode"
    assert r.reply.count("?")==1

def test_culpa_controls():
    r=guilt_turn("Uma lembrança antiga.")
    assert r.state.step=="emotion"
    assert guilt_turn("voltar",r.state).state.step=="episode"
    assert guilt_turn("pular",r.state).state.step=="certainty"
    assert guilt_turn("reiniciar",r.state).state.answers=={}
    assert guilt_turn("encerrar",r.state).done

def test_culpa_does_not_minimize_violence():
    for text in ["Ele me ameaçou.","Estou em perigo imediato.","Quero me matar."]:
        r=guilt_turn(text,GuiltState())
        assert r.safety!="normal"
        assert r.state.step=="episode"
        assert "segurança" in r.reply.lower() or "seguro" in r.reply.lower()

def test_value_exactly_ten_original_questions():
    assert len(QUESTIONS)==10
    state=ValueState()
    for index in range(10):
        res=value_turn("",state)
        assert res.state.index==index
        assert res.reply.count("?")==1
        assert len(res.reply.split())<=65,res.reply
        nxt=value_turn("A",state)
        assert response_issues(nxt.reply)==[],nxt.reply
        assert not nxt.aiConnected and not nxt.persisted
        state=nxt.state
    assert nxt.done is True and state.index==10
    assert "escuta" in nxt.reply.lower()
    assert "presença" in nxt.reply.lower()
    assert "não mede seu valor" in nxt.reply.lower()

def test_value_tie_and_non_diagnostic():
    state=ValueState(index=9,choices=["A","B","A","B","-","C","D","C","D"])
    r=value_turn("D",state)
    assert r.done
    assert " e " in r.reply
    assert "preferências" in r.reply or "valor" in r.reply

def test_value_freetext_skip_and_back():
    state=ValueState()
    invalid=value_turn("Eu costumo ajudar de várias formas.",state)
    assert invalid.state.index==0
    r=value_turn("minha resposta: ouvi e organizei, depende da situação",state)
    assert r.state.index==1 and r.state.choices==["-"]
    assert "0" in r.state.notes
    r=value_turn("pular",r.state)
    assert r.state.index==2 and r.state.choices==["-","-"]
    r=value_turn("voltar",r.state)
    assert r.state.index==1 and len(r.state.choices)==1
    assert value_turn("novo protocolo",r.state).state.index==0

@pytest.mark.parametrize("message",["Vou me matar.","Estou em perigo imediato."])
def test_value_risk_pause(message):
    r=value_turn(message,ValueState())
    assert r.safety!="normal"
    assert r.state.index==0

@pytest.fixture()
def api(tmp_path,monkeypatch):
    monkeypatch.setenv("NG_DEMO_MODE","true")
    monkeypatch.setenv("NG_COOKIE_SECURE","false")
    monkeypatch.setenv("NG_DB_PATH",str(tmp_path/"sandbox.sqlite3"))
    with TestClient(app) as client:
        yield client

def test_preview_endpoints_require_login_csrf(api):
    url="/api/me/preview/solte-esse-peso/turn"
    assert api.post(url,json={"message":""}).status_code==401
    user=api.post("/api/auth/register",json={"email":"teste-piloto@example.test","password":"SenhaForte#123456"})
    assert user.status_code==201
    assert api.post(url,json={"message":""}).status_code==403
    headers={"X-CSRF-Token":user.json()["csrf_token"]}
    a=api.post(url,json={"message":"","state":{}},headers=headers)
    assert a.status_code==200 and a.json()["state"]["step"]=="episode"
    b=api.post("/api/me/preview/reconheca-seu-valor/turn",json={"message":"","state":{}},headers=headers)
    assert b.status_code==200 and b.json()["state"]["index"]==0
    assert b.json()["aiConnected"] is False and b.json()["persisted"] is False
    unknown=api.post("/api/me/preview/nao-existe/turn",json={"message":""},headers=headers)
    assert unknown.status_code==404

def test_invalid_state_rejected(api):
    r=api.post("/api/auth/register",json={"email":"outro@example.test","password":"SenhaForte#123456"})
    h={"X-CSRF-Token":r.json()["csrf_token"]}
    res=api.post("/api/me/preview/reconheca-seu-valor/turn",json={"message":"A","state":{"index":9999}},headers=h)
    assert res.status_code==422
    res=api.post("/api/me/preview/solte-esse-peso/turn",json={"message":"oi","state":{"step":"nao-existe"}},headers=h)
    assert res.status_code==422
