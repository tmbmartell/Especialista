"""Prévia autenticada dos dois novos especialistas, sem LLM nem gravação."""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ValidationError

from auth import writable, require_sandbox
from culpa_engine import GuiltState, GuiltResult, turn as guilt_turn
from autovalor_engine import ValueState, ValueResult, turn as value_turn

router=APIRouter(prefix="/api/me/preview",tags=["preview"])

class PilotInput(BaseModel):
    message: str = Field(default="",max_length=1000)
    state: dict[str,Any] = Field(default_factory=dict)

@router.post("/{slug}/turn", response_model=GuiltResult|ValueResult)
def pilot_turn(slug:str, payload:PilotInput, user=Depends(writable)):
    require_sandbox()
    if slug not in ("solte-esse-peso","reconheca-seu-valor"):
        raise HTTPException(404,detail="Experiência não disponível.")
    try:
        if slug=="solte-esse-peso":
            state=GuiltState.model_validate(payload.state)
            return guilt_turn(payload.message,state)
        state=ValueState.model_validate(payload.state)
        return value_turn(payload.message,state)
    except ValidationError as exc:
        raise HTTPException(status_code=422,detail="Estado inválido do teste.") from exc
