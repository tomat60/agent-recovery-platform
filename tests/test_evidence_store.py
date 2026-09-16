import json

import pytest

from agent_recovery.evidence_store import EvidenceStoreError, JsonlEvidenceStore
from agent_recovery.ingestion import ActionObservation, ingest_action_observation
from agent_recovery.ledger import ActionLedger


def observation(*, observation_id: str, source_event_id: str) -> ActionObservation:
    return ActionObservation(
        incident_id="incident-1",
        tool_id="crm.update",
        action_type="update_customer",
        agent_id="agent-a",
        params={"customer_id": "customer-7", "status": "contacted"},
        source_system="otel",
        source_event_id=source_event_id,
        trace_id="trace-1",
        span_id=f"span-{source_event_id}",
        authority_scope="crm:customer-7",
        resource_keys=("crm/customer-7",),
        observation_id=observation_id,
        observed_at="2026-09-16T00:00:00.000+00:00",
    )


def test_store_survives_restart_with_stable_identity_and_causal_binding(tmp_path):
    ledger = ActionLedger()
    first = ingest_action_observation(ledger, observation(observation_id="obs-1", source_event_id="source-1"))
    second = ingest_action_observation(
        ledger,
        observation(observation_id="obs-2", source_event_id="source-2"),
        parent_event_ids=(first.event_id,),
    )

    store = JsonlEvidenceStore(tmp_path / "evidence.jsonl")
    store.append_from_ledger(ledger, first.event_id)
    store.append_from_ledger(ledger, second.event_id)

    restored = JsonlEvidenceStore(tmp_path / "evidence.jsonl").load_ledger()
    events = restored.events(incident_id="incident-1")

    assert [event.event_id for event in events] == [first.event_id, second.event_id]
    assert events[1].parent_event_ids == (first.event_id,)
    assert events[0].payload["observation_id"] == "obs-1"
    assert events[0].payload["authorization_effect"] == "none"
    assert restored.head_hash == ledger.head_hash
    assert restored.verify_integrity() is True


def test_store_rejects_tampered_persisted_payload(tmp_path):
    ledger = ActionLedger()
    event = ingest_action_observation(ledger, observation(observation_id="obs-1", source_event_id="source-1"))
    path = tmp_path / "evidence.jsonl"
    store = JsonlEvidenceStore(path)
    store.append_from_ledger(ledger, event.event_id)

    row = json.loads(path.read_text(encoding="utf-8"))
    row["payload"]["authorization_effect"] = "grant"
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")

    with pytest.raises(EvidenceStoreError, match="invalid or tampered evidence"):
        JsonlEvidenceStore(path).load_ledger()


def test_store_fails_closed_on_truncated_row(tmp_path):
    path = tmp_path / "evidence.jsonl"
    path.write_text('{"event_type":"action_intent"', encoding="utf-8")

    with pytest.raises(EvidenceStoreError, match="invalid or tampered evidence"):
        JsonlEvidenceStore(path).load_ledger()
