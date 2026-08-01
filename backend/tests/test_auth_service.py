from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models.user import User
from app.services.auth_service import (
    AuthService, create_session_token, session_user_id,
)


def test_register_authenticate_and_signed_session(monkeypatch) -> None:
    monkeypatch.setenv("AUTH_SECRET", "test-secret-that-is-long-and-private")
    engine = create_engine("sqlite:///:memory:")
    User.__table__.create(engine)
    with Session(engine) as session:
        service = AuthService(session)
        user = service.register("FRIEND@example.com", "safe-pass-123", "Amigo")

        assert user.email == "friend@example.com"
        assert user.password_hash != "safe-pass-123"
        assert service.authenticate("friend@example.com", "safe-pass-123") == user
        assert service.authenticate("friend@example.com", "wrong-pass") is None
        assert session_user_id(create_session_token(user.id)) == user.id
        assert session_user_id(create_session_token(user.id) + "invalid") is None


def test_registration_rejects_duplicate_email() -> None:
    engine = create_engine("sqlite:///:memory:")
    User.__table__.create(engine)
    with Session(engine) as session:
        service = AuthService(session)
        service.register("friend@example.com", "safe-pass-123", "Amigo")
        try:
            service.register("FRIEND@example.com", "another-pass", "Outro")
        except ValueError as error:
            assert "já está cadastrado" in str(error)
        else:
            raise AssertionError("duplicate email was accepted")
