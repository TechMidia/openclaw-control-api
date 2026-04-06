from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_auth_service, get_current_user
from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthError, AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        token = auth_service.authenticate(db=db, username=payload.username, password=payload.password)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    user = auth_service.get_user_from_token(db=db, token=token)
    auth_service.audit(
        db=db,
        user_id=user.id,
        action="login",
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return TokenResponse(access_token=token, expires_in_minutes=auth_service.settings.jwt_expire_minutes)


@router.get("/me", response_model=UserResponse)
def me(current_user=Depends(get_current_user)) -> UserResponse:
    role_name = current_user.role.name if current_user.role else None
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        role=role_name,
        is_active=current_user.is_active,
    )

