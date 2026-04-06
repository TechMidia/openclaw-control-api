from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DashboardSummary(BaseModel):
    generated_at: datetime
    latest_operation_at: datetime | None = None
    latest_financial_at: datetime | None = None
    latest_governance_at: datetime | None = None
    latest_consumption_at: datetime | None = None
    alerts_total: int
    decisions_total: int
    agents_total: int
    open_ingest_errors: int
    projects: dict[str, Any] = Field(default_factory=dict)


class OperationTodayResponse(BaseModel):
    id: int | None = None
    date: str | None = None
    summary: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    tasks: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime | None = None


class FinanceSummaryResponse(BaseModel):
    id: int | None = None
    cash_position: str | None = None
    receivables_summary: str | None = None
    payables_summary: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None


class ProjectResponse(BaseModel):
    slug: str
    name: str
    latest_status: dict[str, Any] = Field(default_factory=dict)
    updated_at: datetime | None = None


class CommandCenterResponse(BaseModel):
    generated_at: datetime
    operations: OperationTodayResponse
    finance: FinanceSummaryResponse
    projects: list[ProjectResponse] = Field(default_factory=list)
    top_alerts: list[dict[str, Any]] = Field(default_factory=list)
    pending_decisions: list[dict[str, Any]] = Field(default_factory=list)


class InboxResponse(BaseModel):
    generated_at: datetime
    alerts: list[dict[str, Any]] = Field(default_factory=list)
    decisions: list[dict[str, Any]] = Field(default_factory=list)
    history: list[dict[str, Any]] = Field(default_factory=list)
