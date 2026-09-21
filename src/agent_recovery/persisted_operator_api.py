from __future__ import annotations

from pathlib import Path
from typing import Any

from .evidence_store import JsonlEvidenceStore
from .operator_api import incident_operator_detail


def persisted_incident_list(path: str | Path) -> dict[str, Any]:
    """List incidents reconstructed from integrity-checked persisted evidence.

    This is a read model only. Loading the evidence store verifies the complete hash chain
    before any incident identity or status is exposed.
    """

    ledger = JsonlEvidenceStore(path).load_ledger()
    incident_ids = tuple(dict.fromkeys(event.incident_id for event in ledger.events()))
    incidents = tuple(
        {
            "incident_id": incident_id,
            "detail": incident_operator_detail(ledger, incident_id=incident_id),
        }
        for incident_id in incident_ids
    )
    return {"incidents": incidents, "authority": "none"}


def persisted_incident_detail(path: str | Path, *, incident_id: str) -> dict[str, Any]:
    """Fetch one incident from canonical persisted evidence after restart reconstruction."""

    ledger = JsonlEvidenceStore(path).load_ledger()
    detail = incident_operator_detail(ledger, incident_id=incident_id)
    return {"incident": detail, "authority": "none"}
