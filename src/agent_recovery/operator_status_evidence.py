from __future__ import annotations

from typing import Any

from .ledger import ActionLedger
from .operator_api import incident_evidence_response, incident_status_summary


def incident_status_evidence_response(
    ledger: ActionLedger, *, incident_id: str
) -> dict[str, Any]:
    """Return compact operator status with the exact ledger evidence supporting it.

    Evidence references are identifiers only. This read model never exposes approvals,
    runtime bindings, callables, or executable authority.
    """

    evidence = incident_evidence_response(ledger, incident_id=incident_id)
    summary = incident_status_summary(ledger, incident_id=incident_id)

    executed_recovery = [
        event
        for event in evidence["recovery_events"]
        if event["event_type"] in {"recovery_executed", "reconciliation_executed"}
    ]
    recovered_action_ids = {
        event["source_action_event_id"]
        for event in executed_recovery
        if event["source_action_event_id"] is not None
    }
    local_verification = [
        event
        for event in evidence["verification_events"]
        if event["verification_kind"] != "adversarial_replay"
        and event["source_action_event_id"] in recovered_action_ids
    ]

    return {
        "incident_id": incident_id,
        "status": summary,
        "evidence_refs": {
            "recovery_event_id": executed_recovery[-1]["event_id"] if executed_recovery else None,
            "verification_event_id": (
                local_verification[-1]["event_id"] if local_verification else None
            ),
            "restoration_event_id": (
                evidence["restoration_events"][-1]["event_id"]
                if evidence["restoration_events"]
                else None
            ),
        },
        "authority": "none",
    }
