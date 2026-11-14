import os
from pathlib import Path
os.environ["CATALOG_PATH"] = str(Path(__file__).resolve().parents[2] / "web" / "catalogo.json")

from fastapi.testclient import TestClient
from app import app, calculate_quote

client = TestClient(app)

def test_catalog_has_13_profiles():
    result = client.get("/api/catalog")
    assert result.status_code == 200
    assert result.json()["count"] == 13

def test_empty_quote():
    assert calculate_quote([])["monthlyCents"] == 0

def test_first_specialist():
    assert calculate_quote(["coragem-para-ir"])["monthlyCents"] == 990

def test_two_specialists():
    assert calculate_quote(["coragem-para-ir","solte-esse-peso"])["monthlyCents"] == 1489

def test_all_thirteen():
    items=client.get("/api/catalog").json()["items"]
    assert calculate_quote([item["slug"] for item in items])["monthlyCents"] == 6978

def test_reject_duplicate_products():
    res=client.post("/api/quote",json={"slugs":["coragem-para-ir","coragem-para-ir"]})
    assert res.status_code == 422

def test_reject_unknown_product():
    res=client.post("/api/quote",json={"slugs":["produto-inexistente"]})
    assert res.status_code == 422

def test_health_reports_disabled_integrations():
    res=client.get("/api/health")
    assert res.json()["billing"]=="disabled"
    assert res.json()["whatsapp"]=="disabled"
