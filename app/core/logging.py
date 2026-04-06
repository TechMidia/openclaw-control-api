from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def _handler(path: Path, level: int) -> RotatingFileHandler:
    h = RotatingFileHandler(path, maxBytes=10_000_000, backupCount=5, encoding="utf-8")
    h.setLevel(level)
    h.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    return h


def configure_logging(level_name: str = "INFO", logs_dir: Path | None = None) -> None:
    level = getattr(logging, level_name.upper(), logging.INFO)
    logs_root = logs_dir or Path("logs")
    logs_root.mkdir(parents=True, exist_ok=True)

    api_log = logs_root / "api.log"
    ingest_log = logs_root / "ingest.log"
    errors_log = logs_root / "errors.log"

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
    root.addHandler(console)
    root.addHandler(_handler(api_log, level))

    ingest_logger = logging.getLogger("ingest")
    ingest_logger.setLevel(level)
    ingest_logger.propagate = True
    ingest_logger.addHandler(_handler(ingest_log, level))

    err_logger = logging.getLogger("control.errors")
    err_logger.setLevel(logging.ERROR)
    err_logger.propagate = True
    err_logger.addHandler(_handler(errors_log, logging.ERROR))

