from __future__ import annotations

import json

import pytest

from agent_recovery.evidence_store import EvidenceStoreError, JsonlEvidenceStore
from agent_recovery.ledger import ActionLedger, EventType
from agent_recovery.persisted_operator_api import persisted_incident_detail, persisted_incident_list


def _persisted_incident(path):
    ledger = ActionLedger()
    action = ledger.record(
        EventType.ACTION_EXECUTED,
        "incident-1",
        {
            "action_type": "crm.update",
            "agent_id": "agent-a",
            "resource_keys": ("crm/customer-7",),
            "recovery_class": "reversible",
        },
    )
    hold = ledger.record(
        EventType.CONTAINMENT,
        "incident-1",
        {"scope": "crm/customer-7", "active": True},
        parent_event_ids=(action.event_id,),
    )
    store = JsonlEvidenceStore(path)
    store.append_from_ledger(ledger, action.event_id)
    store.append_from_ledger(ledger, hold.event_id)


def test_persisted_incident_api_reconstructs_read_only_state_after_restart(tmp_path):
    path = tmp_path / "evidence.jsonl"
    _persisted_incident(path)

    listing = persisted_incident_list(path)
    detail = persisted_incident_detail(path, incident_id="incident-1")

    assert listing["authority"] == "none"
    assert [item["incident_id"] for item in listing["incidents"]] == ["incident-1"]
    assert listing["incidents"][0]["status"]["containment_active"] is True
    assert listing["incidents"][0]["recovery_candidate_count"] == 1
    assert "detail" not in listing["incidents"][0]
    assert detail["authority"] == "none"
    assert detail["incident"]["incident_id"] == "incident-1"
    assert detail["incident"]["status"]["containment_active"] is True
    assert detail["incident"]["recovery_candidates"][0]["status"] == "requires_recovery_review"


def test_persisted_incident_api_fails_closed_on_missing_incident(tmp_path):
    path = tmp_path / "evidence.jsonl"
    _persisted_incident(path)

    with pytest.raises(KeyError):
        persisted_incident_detail(path, incident_id="missing")


def test_persisted_incident_api_rejects_tampered_store(tmp_path):
    path = tmp_path / "evidence.jsonl"
    _persisted_incident(path)
    rows = path.read_text(encoding="utf-8").splitlines()
    first = json.loads(rows[0])
    first["payload"]["action_type"] = "tampered.write"
    rows[0] = json.dumps(first)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")

    with pytest.raises(EvidenceStoreError, match="invalid or tampered evidence"):
        persisted_incident_list(path)
