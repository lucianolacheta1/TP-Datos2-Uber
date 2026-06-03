"""Tests del outbox (cola simple en archivo para proyecciones fallidas)."""
import pytest
from pathlib import Path


@pytest.fixture
def outbox_clean(tmp_path, monkeypatch):
    """Redirige el outbox a un archivo temporal y lo vacía."""
    from src.utils import outbox
    temp_file = tmp_path / "outbox.log"
    monkeypatch.setattr(outbox, "_OUTBOX_FILE", temp_file)
    yield temp_file


def test_enqueue_y_pending(outbox_clean):
    from src.utils import outbox
    outbox.enqueue("test_op", {"viaje_id": "ABC"})
    pendings = outbox.pending()
    assert len(pendings) == 1
    assert pendings[0]["operation"] == "test_op"
    assert pendings[0]["payload"]["viaje_id"] == "ABC"


def test_pending_vacio(outbox_clean):
    from src.utils import outbox
    assert outbox.pending() == []


def test_enqueue_multiple(outbox_clean):
    from src.utils import outbox
    outbox.enqueue("op1")
    outbox.enqueue("op2", {"x": 1})
    outbox.enqueue("op3")
    pendings = outbox.pending()
    assert len(pendings) == 3
    assert [p["operation"] for p in pendings] == ["op1", "op2", "op3"]


def test_clear_vacia_el_outbox(outbox_clean):
    from src.utils import outbox
    outbox.enqueue("op")
    outbox.clear()
    assert outbox.pending() == []
