"""Cola simple en archivo para registrar proyecciones fallidas.

Las funciones de los services llaman a enqueue() cuando una proyección
a una base derivada falla. El job de reconciliación (Plan 03 §7) procesa
estas entradas periódicamente.
"""
import json
from pathlib import Path
from datetime import datetime, UTC

from src.utils.logger import logger

_OUTBOX_FILE = Path("outbox.log")


def enqueue(operation: str, payload: dict | None = None) -> None:
    """Registra una proyección fallida."""
    entry = {
        "ts": datetime.now(UTC).isoformat(),
        "operation": operation,
        "payload": payload or {},
    }
    with _OUTBOX_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    logger.warning(f"Outbox enqueued: {operation}")


def pending() -> list[dict]:
    """Devuelve todas las entradas pendientes en el outbox."""
    if not _OUTBOX_FILE.exists():
        return []
    with _OUTBOX_FILE.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def clear() -> None:
    """Vacía el outbox. Llamar después de reconciliar exitosamente."""
    if _OUTBOX_FILE.exists():
        _OUTBOX_FILE.unlink()
