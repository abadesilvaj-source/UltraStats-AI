import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


COOKIE_NAME = "ultrastats_session"
SESSION_TTL = 60 * 60 * 24 * 14


def _secret() -> bytes:
    return os.getenv("AUTH_SECRET", "development-only-change-me").encode()


def hash_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("A senha deve ter pelo menos 8 caracteres.")
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, salt, digest = stored.split("$", 2)
        if algorithm != "scrypt":
            return False
        candidate = hashlib.scrypt(
            password.encode(), salt=base64.urlsafe_b64decode(salt),
            n=2**14, r=8, p=1,
        )
        return hmac.compare_digest(candidate, base64.urlsafe_b64decode(digest))
    except (ValueError, TypeError):
        return False


def create_session_token(user_id: str) -> str:
    payload = base64.urlsafe_b64encode(json.dumps({
        "sub": user_id, "exp": int(time.time()) + SESSION_TTL,
    }, separators=(",", ":")).encode()).decode().rstrip("=")
    signature = hmac.new(_secret(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def session_user_id(token: str | None) -> str | None:
    try:
        payload, signature = (token or "").split(".", 1)
        expected = hmac.new(_secret(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        decoded = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        return str(decoded["sub"]) if int(decoded["exp"]) >= int(time.time()) else None
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def register(self, email: str, password: str, display_name: str) -> User:
        normalized = email.strip().casefold()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", normalized):
            raise ValueError("Informe um e-mail válido.")
        name = display_name.strip()
        if len(name) < 2:
            raise ValueError("Informe seu nome.")
        if self.session.scalar(select(User).where(User.email == normalized)):
            raise ValueError("Este e-mail já está cadastrado.")
        user = User(email=normalized, display_name=name, password_hash=hash_password(password))
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> User | None:
        user = self.session.scalar(select(User).where(User.email == email.strip().casefold()))
        return user if user and user.active and verify_password(password, user.password_hash) else None
