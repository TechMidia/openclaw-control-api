from __future__ import annotations

from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.auth import Role, User
from app.models.domain import Project


def run() -> None:
    settings = get_settings()
    db = SessionLocal()
    try:
        admin_role = db.scalar(select(Role).where(Role.name == "admin"))
        if not admin_role:
            admin_role = Role(name="admin", description="Administrator")
            db.add(admin_role)
            db.flush()

        viewer_role = db.scalar(select(Role).where(Role.name == "viewer"))
        if not viewer_role:
            viewer_role = Role(name="viewer", description="Read-only user")
            db.add(viewer_role)
            db.flush()

        admin_user = db.scalar(select(User).where(User.username == settings.admin_default_username))
        if not admin_user:
            db.add(
                User(
                    username=settings.admin_default_username,
                    password_hash=hash_password(settings.admin_default_password),
                    role_id=admin_role.id,
                    is_active=True,
                )
            )

        for slug, name in (("techmidia", "TechMidia"), ("doncarmo", "DonCarmo"), ("personal", "Vida Pessoal")):
            existing = db.scalar(select(Project).where(Project.slug == slug))
            if not existing:
                db.add(Project(slug=slug, name=name, latest_status={}))

        db.commit()
        print("seed completed")
    finally:
        db.close()


if __name__ == "__main__":
    run()

