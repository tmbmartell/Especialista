"""API de demonstração: catálogo e orçamento. Sem login, pagamento ou autorização de WhatsApp."""
import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DEFAULT_CATALOG = Path(__file__).resolve().parents[1] / "web" / "catalogo.json"
CATALOG_PATH = Path(os.environ.get("CATALOG_PATH", str(DEFAULT_CATALOG)))

app = FastAPI(title="Especialista — Nova Gente (sandbox)", version="0.2.0")

from auth import router as identity_router
from experiences import router as experiences_router
from coragem_routes import router as coragem_router
app.include_router(identity_router)
app.include_router(experiences_router)
app.include_router(coragem_router)

class QuoteRequest(BaseModel):
    slugs: list[str] = Field(default_factory=list, max_length=13)

def catalog():
    with CATALOG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)

def cents_to_brl(cents: int) -> str:
    return "R$ " + f"{cents / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calculate_quote(slugs: list[str]) -> dict:
    data = catalog()
    available = {item["slug"]: item for item in data["items"]}
    if len(slugs) != len(set(slugs)):
        raise ValueError("Não repita especialistas no mesmo carrinho.")
    missing = set(slugs) - set(available)
    if missing:
        raise ValueError("Especialista desconhecido.")
    total = 0 if not slugs else data["firstPriceCents"] + (len(slugs)-1) * data["extraPriceCents"]
    return {"specialistCount": len(slugs),
            "selected": [{"slug":s,"name":available[s]["name"]} for s in slugs],
            "monthlyCents": total, "monthlyBRL": cents_to_brl(total),
            "currency": "BRL", "isSimulation": True, "paymentAvailable": False}

@app.get("/api/health")
def health():
    return {"status": "ok", "stage": "development", "billing": "disabled",
            "whatsapp": "disabled", "jev": "disabled", "deepseek": "disabled"}

@app.get("/api/catalog")
def list_catalog():
    data = catalog()
    return {"count": len(data["items"]), "items": data["items"],
            "notice": "Cadastro comercial em revisão; sem compra ativa."}

@app.post("/api/quote")
def quote(request: QuoteRequest):
    try:
        return calculate_quote(request.slugs)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
