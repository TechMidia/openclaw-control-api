from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_ingest_token
from app.db.session import get_db
from app.schemas.ingest import IngestEnvelope, IngestResponse
from app.services.ingest_service import IngestService

router = APIRouter(prefix="/ingest", tags=["ingest"], dependencies=[Depends(require_ingest_token)])
logger = logging.getLogger("ingest")


def _normalize(payload: dict[str, Any]) -> IngestEnvelope:
    if "data" in payload:
        return IngestEnvelope.model_validate(payload)
    return IngestEnvelope(data=payload)


def _size_of(payload: dict[str, Any]) -> int:
    try:
        return len(json.dumps(payload))
    except Exception:
        return 0


@router.post("/operations", response_model=IngestResponse)
def ingest_operations(payload: dict[str, Any], db: Session = Depends(get_db)) -> IngestResponse:
    service = IngestService()
    envelope = _normalize(payload)
    try:
        snapshot = service.ingest_operations(db, envelope)
        service.log_ingest(
            db=db,
            block="operations",
            source=envelope.source,
            status="ok",
            detail=f"snapshot={snapshot.id}",
            payload_size=_size_of(payload),
        )
        return IngestResponse(
            accepted=True,
            block="operations",
            source=envelope.source,
            stored_at=datetime.now(tz=timezone.utc),
        )
    except Exception as exc:  # pragma: no cover
        logger.exception("operations ingest failed: %s", exc)
        service.log_ingest(
            db=db,
            block="operations",
            source=envelope.source,
            status="failed",
            detail=str(exc),
            payload_size=_size_of(payload),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/projects", response_model=IngestResponse)
def ingest_projects(payload: dict[str, Any], db: Session = Depends(get_db)) -> IngestResponse:
    service = IngestService()
    envelope = _normalize(payload)
    try:
        updated = service.ingest_projects(db, envelope)
        service.log_ingest(
            db=db,
            block="projects",
            source=envelope.source,
            status="ok",
            detail=f"updated={','.join(updated.keys()) or 'none'}",
            payload_size=_size_of(payload),
        )
        return IngestResponse(
            accepted=True,
            block="projects",
            source=envelope.source,
            stored_at=datetime.now(tz=timezone.utc),
        )
    except Exception as exc:  # pragma: no cover
        logger.exception("projects ingest failed: %s", exc)
        service.log_ingest(
            db=db,
            block="projects",
            source=envelope.source,
            status="failed",
            detail=str(exc),
            payload_size=_size_of(payload),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/financial", response_model=IngestResponse)
def ingest_financial(payload: dict[str, Any], db: Session = Depends(get_db)) -> IngestResponse:
    service = IngestService()
    envelope = _normalize(payload)
    try:
        snapshot = service.ingest_financial(db, envelope)
        service.log_ingest(
            db=db,
            block="financial",
            source=envelope.source,
            status="ok",
            detail=f"snapshot={snapshot.id}",
            payload_size=_size_of(payload),
        )
        return IngestResponse(
            accepted=True,
            block="financial",
            source=envelope.source,
            stored_at=datetime.now(tz=timezone.utc),
        )
    except Exception as exc:
        logger.exception("financial ingest failed: %s", exc)
        service.log_ingest(
            db=db,
            block="financial",
            source=envelope.source,
            status="failed",
            detail=str(exc),
            payload_size=_size_of(payload),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/governance", response_model=IngestResponse)
def ingest_governance(payload: dict[str, Any], db: Session = Depends(get_db)) -> IngestResponse:
    service = IngestService()
    envelope = _normalize(payload)
    try:
        snapshot = service.ingest_governance(db, envelope)
        service.log_ingest(
            db=db,
            block="governance",
            source=envelope.source,
            status="ok",
            detail=f"snapshot={snapshot.id}",
            payload_size=_size_of(payload),
        )
        return IngestResponse(
            accepted=True,
            block="governance",
            source=envelope.source,
            stored_at=datetime.now(tz=timezone.utc),
        )
    except Exception as exc:
        logger.exception("governance ingest failed: %s", exc)
        service.log_ingest(
            db=db,
            block="governance",
            source=envelope.source,
            status="failed",
            detail=str(exc),
            payload_size=_size_of(payload),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/consumption", response_model=IngestResponse)
def ingest_consumption(payload: dict[str, Any], db: Session = Depends(get_db)) -> IngestResponse:
    service = IngestService()
    envelope = _normalize(payload)
    try:
        snapshot = service.ingest_consumption(db, envelope)
        service.log_ingest(
            db=db,
            block="consumption",
            source=envelope.source,
            status="ok",
            detail=f"snapshot={snapshot.id}",
            payload_size=_size_of(payload),
        )
        return IngestResponse(
            accepted=True,
            block="consumption",
            source=envelope.source,
            stored_at=datetime.now(tz=timezone.utc),
        )
    except Exception as exc:
        logger.exception("consumption ingest failed: %s", exc)
        service.log_ingest(
            db=db,
            block="consumption",
            source=envelope.source,
            status="failed",
            detail=str(exc),
            payload_size=_size_of(payload),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/full", response_model=IngestResponse)
def ingest_full(payload: dict[str, Any], db: Session = Depends(get_db)) -> IngestResponse:
    service = IngestService()
    envelope = _normalize(payload)
    try:
        results = service.ingest_full(db, envelope)
        service.log_ingest(
            db=db,
            block="full",
            source=envelope.source,
            status="ok",
            detail=f"results={results}",
            payload_size=_size_of(payload),
        )
        return IngestResponse(
            accepted=True,
            block="full",
            source=envelope.source,
            stored_at=datetime.now(tz=timezone.utc),
        )
    except Exception as exc:
        logger.exception("full ingest failed: %s", exc)
        service.log_ingest(
            db=db,
            block="full",
            source=envelope.source,
            status="failed",
            detail=str(exc),
            payload_size=_size_of(payload),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

