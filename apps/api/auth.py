"""Autenticação e carrinhos POR USUÁRIO, apenas para sandbox local.

Não ativar publicamente antes de e-mail verificado, antifraude, banco de produção
e gateway de pagamentos. Nenhuma rota concede acesso aos especialistas.
"""
import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api")
SESSION_AGE = 7 * 86400
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", re.ASCII)
SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL,
  created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
  token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  csrf TEXT NOT NULL, expires_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS carts (
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, slug TEXT NOT NULL,
  PRIMARY KEY(user_id,slug)
);
CREATE TABLE IF NOT EXISTS orders (
  id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  slugs_json TEXT NOT NULL, monthly_cents INTEGER NOT NULL,
  state TEXT NOT NULL DEFAULT 'awaiting_payment', created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS login_limits (
  email TEXT PRIMARY KEY, attempts INTEGER NOT NULL, since INTEGER NOT NULL
);
"""

def sandbox():
    return os.getenv("NG_DEMO_MODE", "false").lower() == "true"

def require_sandbox():
    if not sandbox():
        raise HTTPException(status_code=503, detail="Autenticação ainda não disponível fora do sandbox.")

def db_path():
    return Path(os.getenv("NG_DB_PATH", "/tmp/especialista-sandbox.sqlite3"))

@contextmanager
def db():
    require_sandbox()
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=10, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    try:
        conn.executescript(SCHEMA)
        yield conn
    finally:
        conn.close()

def hash_password(password):
    salt = secrets.token_bytes(16)
    value = hashlib.scrypt(password.encode("utf8"), salt=salt, n=2**14, r=8, p=1)
    return "scrypt:" + salt.hex() + ":" + value.hex()

def matches_password(password, encoded):
    try:
        scheme, salt, digest = encoded.split(":")
        if scheme != "scrypt":
            return False
        got = hashlib.scrypt(password.encode("utf8"), salt=bytes.fromhex(salt), n=2**14, r=8, p=1)
        return hmac.compare_digest(got, bytes.fromhex(digest))
    except (ValueError, TypeError):
        return False

def start_session(conn, user_id, response):
    now = int(time.time())
    token = secrets.token_urlsafe(32)
    csrf = secrets.token_urlsafe(24)
    conn.execute("DELETE FROM sessions WHERE expires_at<=?", (now,))
    conn.execute("INSERT INTO sessions(token_hash,user_id,csrf,expires_at) VALUES(?,?,?,?)",
                 (hashlib.sha256(token.encode()).hexdigest(), user_id, csrf, now + SESSION_AGE))
    response.set_cookie("ng_session", token, httponly=True,
                        secure=os.getenv("NG_COOKIE_SECURE", "true").lower() == "true",
                        samesite="strict", max_age=SESSION_AGE, path="/api")
    return csrf

class Credentials(BaseModel):
    email: str = Field(min_length=5, max_length=160)
    password: str = Field(min_length=12, max_length=256)

class Selection(BaseModel):
    slugs: list[str] = Field(default_factory=list, max_length=13)

def current_user(request: Request):
    token = request.cookies.get("ng_session", "")
    if not token:
        raise HTTPException(401, detail="Entre na sua conta.")
    digest = hashlib.sha256(token.encode()).hexdigest()
    with db() as conn:
        row = conn.execute("""
          SELECT u.id, u.email, s.csrf
          FROM sessions s JOIN users u ON s.user_id=u.id
          WHERE s.token_hash=? AND s.expires_at>?""", (digest, int(time.time()))).fetchone()
    if row is None:
        raise HTTPException(401, detail="Sessão expirada.")
    return dict(row)

def writable(user=Depends(current_user), x_csrf_token: str | None = Header(None)):
    if not x_csrf_token or not hmac.compare_digest(user["csrf"], x_csrf_token):
        raise HTTPException(403, detail="Proteção de sessão inválida.")
    return user

def normalized_email(email):
    email = email.strip().lower()
    if not EMAIL_RE.fullmatch(email):
        raise HTTPException(422, detail="Informe um e-mail válido.")
    return email

@router.post("/auth/register", status_code=201)
def register(body: Credentials, response: Response):
    require_sandbox()
    email = normalized_email(body.email)
    uid = str(uuid.uuid4())
    pwd = hash_password(body.password)
    try:
        with db() as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("INSERT INTO users(id,email,password_hash,created_at) VALUES(?,?,?,?)",
                         (uid, email, pwd, int(time.time())))
            csrf = start_session(conn, uid, response)
            conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(409, detail="E-mail já cadastrado.")
    return {"email": email, "csrf_token": csrf, "email_verified": False, "sandbox_only": True}

@router.post("/auth/login")
def login(body: Credentials, response: Response):
    require_sandbox()
    email = normalized_email(body.email)
    now = int(time.time())
    with db() as conn:
        conn.execute("BEGIN IMMEDIATE")
        rate = conn.execute("SELECT attempts,since FROM login_limits WHERE email=?", (email,)).fetchone()
        if rate and rate["attempts"] >= 5 and now-rate["since"] < 900:
            raise HTTPException(429, detail="Muitas tentativas. Tente novamente mais tarde.")
        row = conn.execute("SELECT id,password_hash FROM users WHERE email=?", (email,)).fetchone()
        good = row is not None and matches_password(body.password, row["password_hash"])
        if not good:
            attempts = rate["attempts"]+1 if rate and now-rate["since"] < 900 else 1
            since = rate["since"] if rate and now-rate["since"] < 900 else now
            conn.execute("INSERT INTO login_limits VALUES(?,?,?) ON CONFLICT(email) DO UPDATE SET attempts=excluded.attempts,since=excluded.since",
                         (email, attempts, since))
            conn.commit()
            raise HTTPException(401, detail="E-mail ou senha incorretos.")
        conn.execute("DELETE FROM login_limits WHERE email=?", (email,))
        csrf = start_session(conn, row["id"], response)
        conn.commit()
    return {"email": email, "csrf_token": csrf, "email_verified": False, "sandbox_only": True}

@router.get("/auth/me")
def me(user=Depends(current_user)):
    return {"email": user["email"], "csrf_token": user["csrf"],
            "email_verified": False, "phone_verified": False, "sandbox_only": True}

@router.post("/auth/logout")
def logout(response: Response, request: Request, user=Depends(writable)):
    token = request.cookies.get("ng_session", "")
    with db() as conn:
        conn.execute("DELETE FROM sessions WHERE token_hash=? AND user_id=?",
                     (hashlib.sha256(token.encode()).hexdigest(), user["id"]))
    response.delete_cookie("ng_session", path="/api")
    return {"ok": True}

def selection_for(conn, user_id):
    return [row["slug"] for row in conn.execute(
        "SELECT slug FROM carts WHERE user_id=? ORDER BY slug", (user_id,)).fetchall()]

@router.get("/me/cart")
def get_cart(user=Depends(current_user)):
    from app import calculate_quote
    with db() as conn:
        chosen = selection_for(conn, user["id"])
    return calculate_quote(chosen)

@router.put("/me/cart")
def save_cart(body: Selection, user=Depends(writable)):
    from app import calculate_quote
    try:
        quote = calculate_quote(body.slugs)
    except ValueError as exc:
        raise HTTPException(422, detail=str(exc)) from exc
    with db() as conn:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("DELETE FROM carts WHERE user_id=?", (user["id"],))
        conn.executemany("INSERT INTO carts(user_id,slug) VALUES(?,?)",
                         [(user["id"], slug) for slug in body.slugs])
        conn.commit()
    return quote

@router.post("/me/orders", status_code=201)
def create_pending_order(user=Depends(writable)):
    from app import calculate_quote
    with db() as conn:
        conn.execute("BEGIN IMMEDIATE")
        chosen = selection_for(conn, user["id"])
        if not chosen:
            raise HTTPException(422, detail="Escolha pelo menos um especialista.")
        quoted = calculate_quote(chosen)
        oid = str(uuid.uuid4())
        conn.execute("INSERT INTO orders(id,user_id,slugs_json,monthly_cents,state,created_at) VALUES(?,?,?,?,?,?)",
                     (oid, user["id"], json.dumps(chosen), quoted["monthlyCents"],
                      "awaiting_payment", int(time.time())))
        conn.commit()
    return {"order_id": oid, "state": "awaiting_payment", "monthlyCents": quoted["monthlyCents"],
            "paymentAvailable": False, "entitlementsGranted": False,
            "notice": "Pedido demonstrativo; não há cobrança ou acesso liberado."}

@router.get("/me/orders")
def list_own_orders(user=Depends(current_user)):
    with db() as conn:
        rows = conn.execute("SELECT id,monthly_cents,state FROM orders WHERE user_id=? ORDER BY created_at DESC LIMIT 20",
                            (user["id"],)).fetchall()
    return {"orders": [{"order_id": row["id"], "monthlyCents": row["monthly_cents"],
                       "state": row["state"]} for row in rows]}

@router.get("/me/orders/{order_id}")
def read_own_order(order_id: str, user=Depends(current_user)):
    with db() as conn:
        row = conn.execute("SELECT id,monthly_cents,state FROM orders WHERE id=? AND user_id=?",
                           (order_id, user["id"])).fetchone()
    if row is None:
        raise HTTPException(404, detail="Pedido não encontrado.")
    return {"order_id": row["id"], "monthlyCents": row["monthly_cents"], "state": row["state"]}
