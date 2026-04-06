from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.dashboard import (
    CommandCenterResponse,
    DashboardSummary,
    FinanceSummaryResponse,
    InboxResponse,
    OperationTodayResponse,
    ProjectResponse,
)
from app.services.dashboard_service import DashboardService

router = APIRouter(tags=["dashboard"], dependencies=[Depends(get_current_user)])


@router.get("/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)) -> DashboardSummary:
    return DashboardService().summary(db)


@router.get("/dashboard/command-center", response_model=CommandCenterResponse)
def dashboard_command_center(db: Session = Depends(get_db)) -> CommandCenterResponse:
    return DashboardService().command_center(db)


@router.get("/dashboard/inbox", response_model=InboxResponse)
def dashboard_inbox(db: Session = Depends(get_db)) -> InboxResponse:
    return DashboardService().inbox(db)


@router.get("/dashboard/alerts")
def dashboard_alerts(db: Session = Depends(get_db)) -> list[dict]:
    return DashboardService().latest_alerts(db)


@router.get("/dashboard/decisions")
def dashboard_decisions(db: Session = Depends(get_db)) -> list[dict]:
    return DashboardService().latest_decisions(db)


@router.get("/operations/today", response_model=OperationTodayResponse)
def operations_today(db: Session = Depends(get_db)) -> OperationTodayResponse:
    return DashboardService().operation_today(db)


@router.get("/finance/summary", response_model=FinanceSummaryResponse)
def finance_summary(db: Session = Depends(get_db)) -> FinanceSummaryResponse:
    return DashboardService().finance_summary(db)


@router.get("/projects/techmidia", response_model=ProjectResponse)
def project_techmidia(db: Session = Depends(get_db)) -> ProjectResponse:
    return DashboardService().project_by_slug(db, "techmidia")


@router.get("/projects/doncarmo", response_model=ProjectResponse)
def project_doncarmo(db: Session = Depends(get_db)) -> ProjectResponse:
    return DashboardService().project_by_slug(db, "doncarmo")


@router.get("/projects/personal", response_model=ProjectResponse)
def project_personal(db: Session = Depends(get_db)) -> ProjectResponse:
    return DashboardService().project_by_slug(db, "personal")


@router.get("/governance/agents")
def governance_agents(db: Session = Depends(get_db)) -> list[dict]:
    return DashboardService().agents(db)


@router.get("/governance/heartbeats")
def governance_heartbeats(db: Session = Depends(get_db)) -> list[dict]:
    return DashboardService().heartbeats(db)


@router.get("/governance/consumption")
def governance_consumption(db: Session = Depends(get_db)) -> dict:
    return DashboardService().consumption(db)


@router.get("/history/events")
def history_events(db: Session = Depends(get_db)) -> list[dict]:
    return DashboardService().history_events(db)
