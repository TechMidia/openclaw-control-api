from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.domain import (
    Agent,
    Alert,
    ConsumptionSnapshot,
    Decision,
    FinancialSnapshot,
    GovernanceSnapshot,
    Heartbeat,
    IngestLog,
    OperationSnapshot,
    Project,
    Task,
)
from app.schemas.dashboard import (
    CommandCenterResponse,
    DashboardSummary,
    FinanceSummaryResponse,
    InboxResponse,
    OperationTodayResponse,
    ProjectResponse,
)


class DashboardService:
    def summary(self, db: Session) -> DashboardSummary:
        latest_op = db.scalar(select(OperationSnapshot).order_by(desc(OperationSnapshot.created_at)).limit(1))
        latest_fin = db.scalar(select(FinancialSnapshot).order_by(desc(FinancialSnapshot.created_at)).limit(1))
        latest_gov = db.scalar(select(GovernanceSnapshot).order_by(desc(GovernanceSnapshot.created_at)).limit(1))
        latest_con = db.scalar(select(ConsumptionSnapshot).order_by(desc(ConsumptionSnapshot.created_at)).limit(1))

        alerts_total = db.scalar(select(func.count(Alert.id))) or 0
        decisions_total = db.scalar(select(func.count(Decision.id))) or 0
        agents_total = db.scalar(select(func.count(Agent.id))) or 0
        ingest_errors = db.scalar(select(func.count(IngestLog.id)).where(IngestLog.status == "failed")) or 0

        projects = {
            p.slug: p.latest_status or {}
            for p in db.scalars(select(Project).order_by(Project.slug)).all()
        }

        return DashboardSummary(
            generated_at=datetime.now(tz=timezone.utc),
            latest_operation_at=latest_op.created_at if latest_op else None,
            latest_financial_at=latest_fin.created_at if latest_fin else None,
            latest_governance_at=latest_gov.created_at if latest_gov else None,
            latest_consumption_at=latest_con.created_at if latest_con else None,
            alerts_total=int(alerts_total),
            decisions_total=int(decisions_total),
            agents_total=int(agents_total),
            open_ingest_errors=int(ingest_errors),
            projects=projects,
        )

    def latest_alerts(self, db: Session, limit: int = 100) -> list[dict[str, Any]]:
        items = db.scalars(select(Alert).order_by(desc(Alert.created_at)).limit(limit)).all()
        return [
            {
                "id": item.id,
                "source": item.source,
                "severity": item.severity,
                "message": item.message,
                "payload": item.payload or {},
                "created_at": item.created_at,
            }
            for item in items
        ]

    def latest_decisions(self, db: Session, limit: int = 100) -> list[dict[str, Any]]:
        items = db.scalars(select(Decision).order_by(desc(Decision.created_at)).limit(limit)).all()
        return [
            {
                "id": item.id,
                "source": item.source,
                "decision": item.decision,
                "owner": item.owner,
                "status": item.status,
                "payload": item.payload or {},
                "created_at": item.created_at,
            }
            for item in items
        ]

    def operation_today(self, db: Session) -> OperationTodayResponse:
        op = db.scalar(select(OperationSnapshot).order_by(desc(OperationSnapshot.created_at)).limit(1))
        if not op:
            return OperationTodayResponse()
        tasks = db.scalars(select(Task).where(Task.operation_snapshot_id == op.id).order_by(Task.id)).all()
        return OperationTodayResponse(
            id=op.id,
            date=op.operation_date,
            summary=op.summary,
            payload=op.payload or {},
            tasks=[
                {"id": task.id, "title": task.title, "status": task.status, "priority": task.priority}
                for task in tasks
            ],
            created_at=op.created_at,
        )

    def finance_summary(self, db: Session) -> FinanceSummaryResponse:
        fin = db.scalar(select(FinancialSnapshot).order_by(desc(FinancialSnapshot.created_at)).limit(1))
        if not fin:
            return FinanceSummaryResponse()
        return FinanceSummaryResponse(
            id=fin.id,
            cash_position=fin.cash_position,
            receivables_summary=fin.receivables_summary,
            payables_summary=fin.payables_summary,
            payload=fin.payload or {},
            created_at=fin.created_at,
        )

    def project_by_slug(self, db: Session, slug: str) -> ProjectResponse:
        project = db.scalar(select(Project).where(Project.slug == slug))
        if not project:
            return ProjectResponse(slug=slug, name=slug.title(), latest_status={}, updated_at=None)
        return ProjectResponse(
            slug=project.slug,
            name=project.name,
            latest_status=project.latest_status or {},
            updated_at=project.updated_at,
        )

    def agents(self, db: Session) -> list[dict[str, Any]]:
        rows = db.scalars(select(Agent).order_by(Agent.agent_id)).all()
        return [
            {
                "agent_id": row.agent_id,
                "status": row.status,
                "model": row.model,
                "note": row.note,
                "last_heartbeat": row.last_heartbeat,
                "updated_at": row.updated_at,
            }
            for row in rows
        ]

    def heartbeats(self, db: Session, limit: int = 200) -> list[dict[str, Any]]:
        rows = db.scalars(select(Heartbeat).order_by(desc(Heartbeat.created_at)).limit(limit)).all()
        return [
            {
                "agent_id": row.agent_id,
                "status": row.status,
                "detail": row.detail,
                "source_file": row.source_file,
                "at": row.at,
                "created_at": row.created_at,
            }
            for row in rows
        ]

    def consumption(self, db: Session) -> dict[str, Any]:
        snap = db.scalar(select(ConsumptionSnapshot).order_by(desc(ConsumptionSnapshot.created_at)).limit(1))
        if not snap:
            return {}
        return {"id": snap.id, "payload": snap.payload, "created_at": snap.created_at}

    def history_events(self, db: Session, limit: int = 200) -> list[dict[str, Any]]:
        rows = db.scalars(select(IngestLog).order_by(desc(IngestLog.created_at)).limit(limit)).all()
        return [
            {
                "id": row.id,
                "block": row.block,
                "source_instance": row.source_instance,
                "status": row.status,
                "detail": row.detail,
                "payload_size": row.payload_size,
                "created_at": row.created_at,
            }
            for row in rows
        ]

    def command_center(self, db: Session) -> CommandCenterResponse:
        projects = [
            self.project_by_slug(db, "techmidia"),
            self.project_by_slug(db, "doncarmo"),
            self.project_by_slug(db, "personal"),
        ]
        return CommandCenterResponse(
            generated_at=datetime.now(tz=timezone.utc),
            operations=self.operation_today(db),
            finance=self.finance_summary(db),
            projects=projects,
            top_alerts=self.latest_alerts(db, limit=20),
            pending_decisions=self.latest_decisions(db, limit=20),
        )

    def inbox(self, db: Session) -> InboxResponse:
        return InboxResponse(
            generated_at=datetime.now(tz=timezone.utc),
            alerts=self.latest_alerts(db, limit=50),
            decisions=self.latest_decisions(db, limit=50),
            history=self.history_events(db, limit=100),
        )
