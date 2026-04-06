from __future__ import annotations

from datetime import datetime, timezone

from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import create_access_token, verify_password
from app.models.auth import SessionAudit, User


class AuthError(Exception):
    pass


class AuthService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def authenticate(self, db: Session, username: str, password: str) -> str:
        user = db.scalar(select(User).where(User.username == username))
        if not user or not user.is_active:
            raise AuthError("Usuário inválido")
        if not verify_password(password, user.password_hash):
            raise AuthError("Credenciais inválidas")
        return create_access_token(
            subject=str(user.id),
            settings=self.settings,
            extra_claims={"username": user.username},
        )

    def get_user_from_token(self, db: Session, token: str) -> User:
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret_key,
                algorithms=[self.settings.jwt_algorithm],
            )
        except JWTError as exc:  # pragma: no cover
            raise AuthError("Token inválido") from exc
        sub = payload.get("sub")
        if not sub:
            raise AuthError("Token sem sujeito")

        user = db.scalar(select(User).where(User.id == int(sub)))
        if not user or not user.is_active:
            raise AuthError("Usuário não autorizado")
        return user

    def audit(self, db: Session, user_id: int | None, action: str, ip: str | None, user_agent: str | None) -> None:
        db.add(
            SessionAudit(
                user_id=user_id,
                action=action,
                ip_address=ip,
                user_agent=user_agent,
                created_at=datetime.now(tz=timezone.utc),
            )
        )
        db.commit()

