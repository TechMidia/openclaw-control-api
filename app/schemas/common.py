from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ApiMessage(BaseModel):
    message: str


class PaginatedResponse(BaseModel):
    items: list[dict[str, Any]] = Field(default_factory=list)
    total: int


class HealthResponse(BaseModel):
    status: str
    service: str
    at: datetime

