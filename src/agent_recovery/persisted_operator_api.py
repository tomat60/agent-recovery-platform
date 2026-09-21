from __future__ import annotations

from pathlib import Path
from typing import Any

from .evidence_store import JsonlEvidenceStore
from .operator_api import incident_operator_detail


def _incident_summary(detail: dict[str, Any]) -> dict[str, Any]:
    """Return the minimum evidence-backed fields needed for an incident queue."""

    return {
        "incident_id": detail["incident_id"],
        "status": detail["status"],
        "recovery_candidate_count": len(detail["recovery_candidates"]),
    }


def persisted_incident_list(path: str | Path) -> dict[str, Any]:
    """List incidents reconstructed from integrity-checked persisted evidence.

    This is a read model only. Loading the evidence store verifies the complete hash chain
    before any incident identity or status is exposed. The queue stays compact; callers can
    fetch the full evidence-backed detail for a selected incident separately.
    """

    ledger = JsonlEvidenceStore(path).load_ledger()
    incident_ids = tuple(dict.fromkeys(event.incident_id for event in ledger.events()))
    incidents = tuple(
        _incident_summary(incident_operator_detail(ledger, incident_id=incident_id))
        for incident_id in incident_ids
    )
    return {"incidents": incidents, "authority": "none"}


def persisted_incident_detail(path: str | Path, *, incident_id: str) -> dict[str, Any]:
    """Fetch one incident from canonical persisted evidence after restart reconstruction."""

    ledger = JsonlEvidenceStore(path).load_ledger()
    detail = incident_operator_detail(ledger, incident_id=incident_id)
    return {"incident": detail, "authority": "none"}
