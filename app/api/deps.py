from __future__ import annotations

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.models.auth import User
from app.services.auth_service import AuthError, AuthService

bearer_scheme = HTTPBearer(auto_error=False)


def settings_dep() -> Settings:
    return get_settings()


def require_ingest_token(
    authorization: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    x_ingest_token: str | None = Header(default=None, alias="X-Ingest-Token"),
    settings: Settings = Depends(settings_dep),
) -> None:
    expected = settings.ingest_api_token
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="INGEST_API_TOKEN não configurado no servidor.",
        )

    provided = x_ingest_token
    if not provided and authorization:
        provided = authorization.credentials

    if provided != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de ingestão inválido.")


def get_auth_service(settings: Settings = Depends(settings_dep)) -> AuthService:
    return AuthService(settings)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token JWT ausente.")
    try:
        user = auth_service.get_user_from_token(db=db, token=credentials.credentials)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    auth_service.audit(
        db=db,
        user_id=user.id,
        action="access_api",
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return user
