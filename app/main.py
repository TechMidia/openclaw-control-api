from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.api.routers.auth import router as auth_router
from app.api.routers.dashboard import router as dashboard_router
from app.api.routers.health import router as health_router
from app.api.routers.ingest import router as ingest_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.auth import Role, User


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level, logs_dir=Path("logs"))
    logger = logging.getLogger(__name__)

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="API receptora de ingestão OpenClaw no servidor VPS.",
    )
    app.state.settings = settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(ingest_router)
    app.include_router(dashboard_router)

    @app.on_event("startup")
    async def startup_event() -> None:
        logger.info("Starting %s", settings.app_name)
        _ensure_default_admin(settings, logger)

    return app


def _ensure_default_admin(settings: Settings, logger: logging.Logger) -> None:
    try:
        db = SessionLocal()
        role = db.scalar(select(Role).where(Role.name == "admin"))
        if not role:
            role = Role(name="admin", description="Administrator")
            db.add(role)
            db.flush()

        user = db.scalar(select(User).where(User.username == settings.admin_default_username))
        if not user:
            user = User(
                username=settings.admin_default_username,
                password_hash=hash_password(settings.admin_default_password),
                role_id=role.id if role else None,
                is_active=True,
            )
            db.add(user)
            db.commit()
            logger.info("Default admin user created: %s", settings.admin_default_username)
        else:
            db.commit()
    except Exception as exc:
        logger.warning("Default admin bootstrap skipped (tables may not exist yet): %s", exc)
    finally:
        try:
            db.close()
        except Exception:
            pass


app = create_app()
