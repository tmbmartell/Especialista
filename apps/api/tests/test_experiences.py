"""F2: perfis públicos distintos, sem vazamento de materiais internos."""
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

os.environ["CATALOG_PATH"]=str(Path(__file__).resolve().parents[2] / "web" / "catalogo.json")
os.environ["EXPERIENCES_PATH"]=str(Path(__file__).resolve().parents[2] / "web" / "experiencias.json")
from app import app

client=TestClient(app)

def test_all_thirteen_profiles_match_catalog():
    catalog=client.get("/api/catalog").json()["items"]
    profiles=client.get("/api/experiences")
    assert profiles.status_code==200
    assert profiles.json()["previewOnly"] is True
    assert profiles.json()["count"]==13
    assert {x["slug"] for x in profiles.json()["items"]}=={x["slug"] for x in catalog}

def test_distinct_opening_questions_and_stages():
    slugs=[x["slug"] for x in client.get("/api/experiences").json()["items"]]
    previews=[client.get("/api/experiences/"+slug+"/preview").json() for slug in slugs]
    assert len({x["firstQuestion"] for x in previews})==13
    for item in previews:
        assert len(item["stages"])==4
        assert item["previewOnly"] is True
        assert item["availableForSale"] is False
        assert item["aiConnected"] is False
        assert item["privateMethodologyLoaded"] is False
        assert item["disclaimer"]
        assert not any(k in item for k in ("prompt", "systemPrompt", "sourceText", "apiKey"))

def test_unknown_profile_never_leaks():
    res=client.get("/api/experiences/nao-existe/preview")
    assert res.status_code==404

@pytest.mark.parametrize("slug,expected",[
    ("coragem-para-ir","receio"),
    ("solte-esse-peso","cobrar"),
    ("reconheca-seu-valor","entrega")
])
def test_pilot_openings_are_unique(slug,expected):
    res=client.get("/api/experiences/"+slug+"/preview")
    assert res.status_code==200
    assert expected.lower() in res.json()["firstQuestion"].lower()

def test_public_profiles_are_not_chat():
    for path in ["/api/experiences/coragem-para-ir/chat", "/api/experiences/reconheca-seu-valor/answer"]:
        assert client.post(path,json={"message":"oi"}).status_code==404
