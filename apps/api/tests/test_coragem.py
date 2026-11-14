"""Roteiro original curto: progressão, flexibilidade, privacidade e segurança."""
from fastapi.testclient import TestClient
import os
import pytest

from coragem_engine import JourneyState, QUESTIONS, talk
from app import app

PASSWORD = "SenhaForte#12345"


def test_one_question_per_turn_and_concise():
    state = JourneyState()
    start = talk("", state)
    assert start.state.step == "goal"
    assert start.reply.count("?") == 1
    data = [
        "Quero conversar com meu gestor.",
        "Tenho adiado pedir feedback.",
        "Acho que ele vai me julgar.",
        "Não tenho certeza; nunca perguntei.",
        "Posso mandar uma mensagem curta.",
        "Na terça-feira de manhã."
    ]
    for message in data:
        result = talk(message, state)
        assert len(result.reply) <= 380
        assert result.reply.count("?") <= 1
        state = result.state
    assert result.done is True
    assert state.step == "done"
    assert "mandar uma mensagem curta" in result.reply
    assert result.persisted is False
    assert result.aiConnected is False


@pytest.mark.parametrize("message,expected", [
    ("não sei", "goal"), ("sei lá", "goal"),
    (" ", "goal"), ("a", "goal"),
])
def test_unclear_messages_do_not_advance(message, expected):
    result = talk(message, JourneyState())
    assert result.state.step == expected
    assert result.reply.count("?") == 1


def test_skip_back_restart_stop():
    first = talk("Quero começar um projeto.", JourneyState())
    skipped = talk("pular", first.state)
    assert skipped.state.step == "prediction"
    back = talk("voltar", skipped.state)
    assert back.state.step == "impact"
    restart = talk("novo protocolo", skipped.state)
    assert restart.state.step == "goal"
    assert restart.state.answers == {}
    stop = talk("encerrar", first.state)
    assert stop.done and stop.state.step == "done"


@pytest.mark.parametrize("message,flag", [
    ("Eu quero me matar.", "crisis"),
    ("Ele me ameaçou ontem.", "danger"),
    ("Estou em perigo imediato.", "danger"),
])
def test_protection_overrides_progress(message,flag):
    state = talk("Quero mudar de cidade.").state
    result = talk(message, state)
    assert result.safety == flag
    assert result.state.step == state.step
    assert result.reply.count("?") == 1
    assert "segurança" in result.reply.lower() or "seguro" in result.reply.lower()


def test_empty_messages_and_long_answers():
    result = talk("A"*900, JourneyState())
    assert len(result.state.answers["goal"]) <= 450
    assert "A"*451 not in str(result.state.answers)


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("NG_DEMO_MODE", "true")
    monkeypatch.setenv("NG_COOKIE_SECURE", "false")
    monkeypatch.setenv("NG_DB_PATH", str(tmp_path/"sandbox.sqlite3"))
    with TestClient(app) as c:
        yield c


def test_preview_requires_login_and_csrf(client):
    endpoint="/api/me/preview/coragem-para-ir/turn"
    assert client.post(endpoint,json={"message":""}).status_code==401
    user=client.post("/api/auth/register",json={"email":"teste@example.test","password":PASSWORD})
    assert user.status_code==201
    assert client.post(endpoint,json={"message":""}).status_code==403
    ok=client.post(endpoint,json={"message":""},
                   headers={"X-CSRF-Token":user.json()["csrf_token"]})
    assert ok.status_code==200
    assert ok.json()["state"]["step"]=="goal"
    assert ok.json()["persisted"] is False


def test_preview_disabled_outside_sandbox(monkeypatch):
    monkeypatch.setenv("NG_DEMO_MODE","false")
    with TestClient(app) as client:
        result=client.post("/api/me/preview/coragem-para-ir/turn",json={"message":""})
    assert result.status_code in (401,403,503)
