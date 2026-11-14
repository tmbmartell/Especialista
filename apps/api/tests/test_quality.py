from response_quality import response_issues
from coragem_engine import JourneyState, talk


def test_response_style_in_all_conversation_turns():
    state=JourneyState()
    sequence=[
        "Quero apresentar um projeto novo.",
        "Estou adiando falar da ideia.",
        "Talvez eu escute um não.",
        "Não tenho como provar isso.",
        "Vou perguntar a opinião de uma pessoa.",
        "Na semana que vem.",
    ]
    for user_input in sequence:
        reply=talk(user_input,state)
        assert response_issues(reply.reply,emergency=reply.safety!="normal")==[],reply.reply
        state=reply.state


def test_detects_multiple_questions_and_long_reply():
    assert "multiple_questions" in response_issues("Tudo bem? E você?")
    assert "long" in response_issues("palavra " * 66)


def test_safety_emergency_is_not_forced_into_short_format():
    assert response_issues("palavra " * 100, emergency=True)==[]
