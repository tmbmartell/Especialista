"""F1: isolamento entre duas contas e nenhuma liberação sem pagamento."""
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from app import app

PASSWORD = "SenhaForte#12345"

@pytest.fixture
def api(tmp_path, monkeypatch):
    monkeypatch.setenv("NG_DEMO_MODE", "true")
    monkeypatch.setenv("NG_COOKIE_SECURE", "false")
    monkeypatch.setenv("NG_DB_PATH", str(tmp_path / "sandbox.db"))
    with TestClient(app) as client:
        yield client

def register(c, email):
    resp = c.post("/api/auth/register", json={"email": email, "password": PASSWORD})
    assert resp.status_code == 201, resp.text
    return resp.json()["csrf_token"]

def headers(csrf):
    return {"X-CSRF-Token": csrf}

def test_session_cookie_and_csrf(api):
    token = register(api, "alice@example.test")
    assert api.cookies.get("ng_session")
    assert api.get("/api/auth/me").json()["email"] == "alice@example.test"
    assert api.put("/api/me/cart", json={"slugs":["coragem-para-ir"]}).status_code == 403
    response = api.put("/api/me/cart", json={"slugs":["coragem-para-ir"]},headers=headers(token))
    assert response.status_code == 200
    assert response.json()["monthlyCents"] == 990
    api.post("/api/auth/logout",headers=headers(token))
    assert api.get("/api/auth/me").status_code == 401

def test_isolation_and_pending_orders(api):
    a = register(api, "a@example.test")
    assert api.put("/api/me/cart",json={"slugs":["coragem-para-ir","solte-esse-peso"]},
                   headers=headers(a)).json()["monthlyCents"] == 1489
    res = api.post("/api/me/orders",headers=headers(a))
    assert res.status_code == 201
    order = res.json()
    assert order["state"] == "awaiting_payment" and order["entitlementsGranted"] is False
    api.cookies.clear()

    b = register(api, "b@example.test")
    assert api.get("/api/me/cart").json()["specialistCount"] == 0
    assert api.get("/api/me/orders").json()["orders"] == []
    assert api.get("/api/me/orders/"+order["order_id"]).status_code == 404
    assert api.put("/api/me/cart",json={"slugs":["o-que-seu-sonho-conta"]},
                   headers=headers(a)).status_code == 403
    assert api.put("/api/me/cart",json={"slugs":["o-que-seu-sonho-conta"]},
                   headers=headers(b)).json()["monthlyCents"] == 990

    login = api.post("/api/auth/login",json={"email":"a@example.test","password":PASSWORD})
    assert login.status_code == 200
    assert api.get("/api/me/cart").json()["specialistCount"] == 2
    assert len(api.get("/api/me/orders").json()["orders"]) == 1

def test_validation_and_no_free_access(api):
    assert api.get("/api/me/cart").status_code == 401
    token = register(api, "check@example.test")
    for slugs in [["coragem-para-ir","coragem-para-ir"],["unknown"]]:
        res=api.put("/api/me/cart",json={"slugs":slugs},headers=headers(token))
        assert res.status_code == 422
    assert api.get("/api/me/cart").json()["specialistCount"] == 0
    assert api.post("/api/me/orders",headers=headers(token)).status_code == 422

def test_wrong_password_and_rate_limit(api):
    register(api,"limit@example.test")
    api.cookies.clear()
    for _ in range(5):
        resp=api.post("/api/auth/login",json={"email":"limit@example.test","password":"SenhaErrada#12345"})
        assert resp.status_code == 401
    response=api.post("/api/auth/login",json={"email":"limit@example.test","password":PASSWORD})
    assert response.status_code == 429

def test_sandbox_disabled(monkeypatch):
    monkeypatch.setenv("NG_DEMO_MODE","false")
    with TestClient(app) as c:
        assert c.get("/api/auth/me").status_code in (401,503)
        assert c.post("/api/auth/register",json={"email":"a@example.test","password":PASSWORD}).status_code == 503
