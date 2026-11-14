"""Rotas de roteiro interativo: SANDBOX SOMENTE, sem armazenamento nem IA."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from auth import require_sandbox, writable
from coragem_engine import JourneyState, TurnResult, talk

router = APIRouter(prefix="/api/me/preview", tags=["preview"])


class MessageInput(BaseModel):
    message: str = Field(default="", max_length=1000)
    state: JourneyState = Field(default_factory=JourneyState)


@router.post("/coragem-para-ir/turn", response_model=TurnResult)
def coragem_turn(payload: MessageInput, user=Depends(writable)):
    # A autorização vem da sessão/CSRF, nunca da etapa do roteiro.
    # Estado e respostas retornam ao navegador; não persistimos dados sensíveis.
    require_sandbox()
    return talk(payload.message, payload.state)
