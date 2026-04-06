from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class IngestEnvelope(BaseModel):
    bridge: str | None = None
    block: str | None = None
    source: str | None = None
    sent_at: datetime | None = None
    data: dict[str, Any] | list[Any] | None = None


class IngestResponse(BaseModel):
    accepted: bool
    block: str
    source: str | None = None
    stored_at: datetime
    detail: str = "ok"


class FullIngestData(BaseModel):
    system_status: dict[str, Any] | None = None
    projects_status: dict[str, Any] | None = None
    operations_day: dict[str, Any] | None = None
    financial_summary: dict[str, Any] | None = None
    governance_state: dict[str, Any] | None = None
    consumption_metrics: dict[str, Any] | None = None
    alerts: list[dict[str, Any]] = Field(default_factory=list)
    decisions: list[dict[str, Any]] = Field(default_factory=list)
    agents: list[dict[str, Any]] = Field(default_factory=list)
    heartbeats: list[dict[str, Any]] = Field(default_factory=list)

