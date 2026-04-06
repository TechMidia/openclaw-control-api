from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
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
    Payable,
    Project,
    Receivable,
    Task,
)
from app.schemas.ingest import FullIngestData, IngestEnvelope

logger = logging.getLogger("ingest")

PROJECT_LABELS = {
    "techmidia": "TechMidia",
    "doncarmo": "DonCarmo",
    "personal": "Vida Pessoal",
}


def _utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = f"{candidate[:-1]}+00:00"
    try:
        return datetime.fromisoformat(candidate)
    except Exception:
        return None


def _stringify(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return str(value)


class IngestService:
    def _payload(self, envelope: IngestEnvelope) -> dict[str, Any] | list[Any]:
        data = envelope.data
        if data is None:
            return {}
        return data

    def ingest_operations(self, db: Session, envelope: IngestEnvelope) -> OperationSnapshot:
        raw = self._payload(envelope)
        payload = raw if isinstance(raw, dict) else {"items": raw}
        snapshot = OperationSnapshot(
            source_instance=envelope.source,
            operation_date=str(payload.get("date") or payload.get("operation_date") or ""),
            summary=payload.get("summary"),
            payload=payload,
            created_at=_utc_now(),
        )
        db.add(snapshot)
        db.flush()

        tasks = payload.get("tasks") or []
        if isinstance(tasks, list):
            for item in tasks:
                text = item if isinstance(item, str) else item.get("title", "")
                if not text:
                    continue
                db.add(
                    Task(
                        operation_snapshot_id=snapshot.id,
                        title=text,
                        status=(item.get("status") if isinstance(item, dict) else "pending") or "pending",
                        priority=(item.get("priority") if isinstance(item, dict) else None),
                    )
                )
        db.commit()
        db.refresh(snapshot)
        return snapshot

    def ingest_projects(self, db: Session, envelope: IngestEnvelope) -> dict[str, Any]:
        raw = self._payload(envelope)
        payload = raw if isinstance(raw, dict) else {}

        updated: dict[str, Any] = {}
        for slug in ("techmidia", "doncarmo", "personal"):
            project_payload = payload.get(slug) or payload.get(f"project_{slug}")
            if not project_payload:
                continue
            project = db.scalar(select(Project).where(Project.slug == slug))
            if not project:
                project = Project(slug=slug, name=PROJECT_LABELS[slug], latest_status={})
                db.add(project)
                db.flush()
            project.latest_status = project_payload if isinstance(project_payload, dict) else {"value": project_payload}
            project.updated_at = _utc_now()
            updated[slug] = project.latest_status

        db.commit()
        return updated

    def ingest_financial(self, db: Session, envelope: IngestEnvelope) -> FinancialSnapshot:
        raw = self._payload(envelope)
        payload = raw if isinstance(raw, dict) else {"items": raw}
        snapshot = FinancialSnapshot(
            source_instance=envelope.source,
            cash_position=_stringify(payload.get("cash_position")),
            receivables_summary=_stringify(payload.get("receivables")),
            payables_summary=_stringify(payload.get("payables")),
            payload=payload,
            created_at=_utc_now(),
        )
        db.add(snapshot)
        db.flush()

        receivables = payload.get("receivables_items") or payload.get("receivables_list")
        if receivables is None and isinstance(payload.get("receivables"), list):
            receivables = payload.get("receivables")
        if isinstance(receivables, list):
            for item in receivables:
                if not isinstance(item, dict):
                    continue
                description = _stringify(item.get("description")) or _stringify(item.get("title"))
                if not description:
                    continue
                db.add(
                    Receivable(
                        financial_snapshot_id=snapshot.id,
                        description=description,
                        amount=item.get("amount"),
                        due_date=_stringify(item.get("due_date")),
                        status=_stringify(item.get("status")),
                    )
                )

        payables = payload.get("payables_items") or payload.get("payables_list")
        if payables is None and isinstance(payload.get("payables"), list):
            payables = payload.get("payables")
        if isinstance(payables, list):
            for item in payables:
                if not isinstance(item, dict):
                    continue
                description = _stringify(item.get("description")) or _stringify(item.get("title"))
                if not description:
                    continue
                db.add(
                    Payable(
                        financial_snapshot_id=snapshot.id,
                        description=description,
                        amount=item.get("amount"),
                        due_date=_stringify(item.get("due_date")),
                        status=_stringify(item.get("status")),
                    )
                )

        db.commit()
        db.refresh(snapshot)
        return snapshot

    def ingest_governance(self, db: Session, envelope: IngestEnvelope) -> GovernanceSnapshot:
        raw = self._payload(envelope)
        payload = raw if isinstance(raw, dict) else {"items": raw}
        snapshot = GovernanceSnapshot(
            source_instance=envelope.source,
            payload=payload,
            created_at=_utc_now(),
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return snapshot

    def ingest_consumption(self, db: Session, envelope: IngestEnvelope) -> ConsumptionSnapshot:
        raw = self._payload(envelope)
        payload = raw if isinstance(raw, dict) else {"items": raw}
        snapshot = ConsumptionSnapshot(
            source_instance=envelope.source,
            payload=payload,
            created_at=_utc_now(),
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return snapshot

    def ingest_full(self, db: Session, envelope: IngestEnvelope) -> dict[str, Any]:
        raw = self._payload(envelope)
        full_data = FullIngestData.model_validate(raw if isinstance(raw, dict) else {})

        results: dict[str, Any] = {}
        if full_data.operations_day:
            op_envelope = IngestEnvelope(source=envelope.source, data=full_data.operations_day)
            operation = self.ingest_operations(db, op_envelope)
            results["operations_snapshot_id"] = operation.id

        if full_data.projects_status:
            projects = full_data.projects_status
            projects_payload = {
                "techmidia": projects.get("techmidia", {}),
                "doncarmo": projects.get("doncarmo", {}),
                "personal": projects.get("personal", {}),
            }
            updated = self.ingest_projects(db, IngestEnvelope(source=envelope.source, data=projects_payload))
            results["projects_updated"] = list(updated.keys())

        if full_data.financial_summary:
            fin = self.ingest_financial(db, IngestEnvelope(source=envelope.source, data=full_data.financial_summary))
            results["financial_snapshot_id"] = fin.id

        if full_data.governance_state:
            gov = self.ingest_governance(db, IngestEnvelope(source=envelope.source, data=full_data.governance_state))
            results["governance_snapshot_id"] = gov.id

        if full_data.consumption_metrics:
            con = self.ingest_consumption(db, IngestEnvelope(source=envelope.source, data=full_data.consumption_metrics))
            results["consumption_snapshot_id"] = con.id

        self._ingest_alerts(db, full_data.alerts)
        self._ingest_decisions(db, full_data.decisions)
        self._ingest_agents(db, full_data.agents)
        self._ingest_heartbeats(db, full_data.heartbeats)

        return results

    def _ingest_alerts(self, db: Session, alerts: list[dict[str, Any]]) -> None:
        for item in alerts:
            message = item.get("message")
            if not message:
                continue
            db.add(
                Alert(
                    source=item.get("source", "unknown"),
                    severity=item.get("severity", "medium"),
                    message=message,
                    payload=item,
                    created_at=_utc_now(),
                )
            )
        db.commit()

    def _ingest_decisions(self, db: Session, decisions: list[dict[str, Any]]) -> None:
        for item in decisions:
            decision = item.get("decision")
            if not decision:
                continue
            db.add(
                Decision(
                    source=item.get("source", "unknown"),
                    decision=decision,
                    owner=item.get("owner"),
                    status=item.get("status"),
                    payload=item,
                    created_at=_utc_now(),
                )
            )
        db.commit()

    def _ingest_agents(self, db: Session, agents: list[dict[str, Any]]) -> None:
        for item in agents:
            agent_id = item.get("agent_id")
            if not agent_id:
                continue
            agent = db.scalar(select(Agent).where(Agent.agent_id == agent_id))
            if not agent:
                agent = Agent(agent_id=agent_id, status=item.get("status", "unknown"))
                db.add(agent)
                db.flush()
            agent.status = item.get("status", agent.status)
            agent.model = item.get("model")
            agent.note = item.get("note")
            parsed_last_heartbeat = _parse_datetime(item.get("last_heartbeat"))
            if parsed_last_heartbeat:
                agent.last_heartbeat = parsed_last_heartbeat
            agent.updated_at = _utc_now()
        db.commit()

    def _ingest_heartbeats(self, db: Session, heartbeats: list[dict[str, Any]]) -> None:
        for item in heartbeats:
            db.add(
                Heartbeat(
                    agent_id=item.get("agent_id", "unknown"),
                    status=item.get("status", "unknown"),
                    detail=item.get("detail"),
                    source_file=item.get("source_file"),
                    at=_parse_datetime(item.get("at")),
                    created_at=_utc_now(),
                )
            )
        db.commit()

    def log_ingest(
        self,
        db: Session,
        block: str,
        source: str | None,
        status: str,
        detail: str | None,
        payload_size: int | None,
    ) -> None:
        db.add(
            IngestLog(
                block=block,
                source_instance=source,
                status=status,
                detail=detail,
                payload_size=payload_size,
                created_at=_utc_now(),
            )
        )
        db.commit()
        logger.info("Ingest log block=%s status=%s source=%s", block, status, source)
