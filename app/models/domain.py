from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    latest_status: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class OperationSnapshot(Base):
    __tablename__ = "operations_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_instance: Mapped[str | None] = mapped_column(String(120), index=True)
    operation_date: Mapped[str | None] = mapped_column(String(32), index=True)
    summary: Mapped[str | None] = mapped_column(Text)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    tasks: Mapped[list["Task"]] = relationship(back_populates="operation_snapshot")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    operation_snapshot_id: Mapped[int | None] = mapped_column(
        ForeignKey("operations_snapshots.id", ondelete="SET NULL"),
        index=True,
    )
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"), index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    priority: Mapped[str | None] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    operation_snapshot: Mapped[OperationSnapshot | None] = relationship(back_populates="tasks")


class FinancialSnapshot(Base):
    __tablename__ = "financial_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_instance: Mapped[str | None] = mapped_column(String(120), index=True)
    cash_position: Mapped[str | None] = mapped_column(String(120))
    receivables_summary: Mapped[str | None] = mapped_column(String(120))
    payables_summary: Mapped[str | None] = mapped_column(String(120))
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class Receivable(Base):
    __tablename__ = "receivables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    financial_snapshot_id: Mapped[int | None] = mapped_column(
        ForeignKey("financial_snapshots.id", ondelete="SET NULL"),
        index=True,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[float | None] = mapped_column(Numeric(14, 2))
    due_date: Mapped[str | None] = mapped_column(String(32))
    status: Mapped[str | None] = mapped_column(String(30))


class Payable(Base):
    __tablename__ = "payables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    financial_snapshot_id: Mapped[int | None] = mapped_column(
        ForeignKey("financial_snapshots.id", ondelete="SET NULL"),
        index=True,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[float | None] = mapped_column(Numeric(14, 2))
    due_date: Mapped[str | None] = mapped_column(String(32))
    status: Mapped[str | None] = mapped_column(String(30))


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    decision: Mapped[str] = mapped_column(Text, nullable=False)
    owner: Mapped[str | None] = mapped_column(String(120))
    status: Mapped[str | None] = mapped_column(String(30))
    payload: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    model: Mapped[str | None] = mapped_column(String(120))
    note: Mapped[str | None] = mapped_column(Text)
    last_heartbeat: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class Heartbeat(Base):
    __tablename__ = "heartbeats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    detail: Mapped[str | None] = mapped_column(Text)
    source_file: Mapped[str | None] = mapped_column(String(255))
    at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class GovernanceSnapshot(Base):
    __tablename__ = "governance_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_instance: Mapped[str | None] = mapped_column(String(120), index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class ConsumptionSnapshot(Base):
    __tablename__ = "consumption_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_instance: Mapped[str | None] = mapped_column(String(120), index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class IngestLog(Base):
    __tablename__ = "ingest_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    block: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    source_instance: Mapped[str | None] = mapped_column(String(120), index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    detail: Mapped[str | None] = mapped_column(Text)
    payload_size: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

