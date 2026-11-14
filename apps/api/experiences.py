"""Metadados públicos de experiências. Nenhum prompt ou material interno é servido."""
import json
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api")
DEFAULT = Path(__file__).resolve().parents[1] / "web" / "experiencias.json"

def experiences():
    path = Path(os.environ.get("EXPERIENCES_PATH", str(DEFAULT)))
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not data.get("publicDataOnly") or not isinstance(data.get("items"), list):
        raise RuntimeError("Manifesto público de experiências inválido.")
    return data

@router.get("/experiences")
def list_public_experiences():
    data = experiences()
    return {
        "previewOnly": True,
        "count": len(data["items"]),
        "items": [
            {"slug": item["slug"], "purpose": item["purpose"],
             "inputMode": item["inputMode"], "contentReview": item["contentReview"],
             "availableForSale": False}
            for item in data["items"]
        ],
    }

@router.get("/experiences/{slug}/preview")
def preview_public_experience(slug: str):
    item = next((x for x in experiences()["items"] if x["slug"] == slug), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Especialista não encontrado.")
    return {
        "slug": item["slug"], "purpose": item["purpose"], "voice": item["voice"],
        "firstQuestion": item["firstQuestion"],
        "stages": item["stages"], "disclaimer": item["disclaimer"],
        "previewOnly": True, "availableForSale": False,
        "aiConnected": False, "privateMethodologyLoaded": False,
    }
