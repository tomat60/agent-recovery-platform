from __future__ import annotations

import pytest

from agent_recovery.ingestion import ActionObservation, IngestionError, ingest_action_observation
from agent_recovery.ledger import ActionLedger, EventType


def observation(**overrides: object) -> ActionObservation:
    values: dict[str, object] = {
        "incident_id": "inc-1",
        "tool_id": "crm.contacts",
        "action_type": "update_contact",
        "contract_version": "1",
        "agent_id": "sales-agent",
        "params": {"contact_id": "c-7", "status": "qualified"},
        "source_system": "otel",
        "source_event_id": "span-event-42",
        "trace_id": "trace-1",
        "span_id": "span-2",
        "authority_scope": "integration:crm",
        "resource_keys": ("crm:contact:c-7",),
        "observation_id": "obs-1",
        "observed_at": "2026-09-15T16:30:00+00:00",
    }
    values.update(overrides)
    return ActionObservation(**values)  # type: ignore[arg-type]


def test_ingestion_records_detached_non_authorizing_action_intent() -> None:
    ledger = ActionLedger()
    params = {"contact_id": "c-7", "status": "qualified"}
    event = ingest_action_observation(ledger, observation(params=params))

    assert event.event_type is EventType.ACTION_INTENT
    assert event.incident_id == "inc-1"
    assert event.payload["authorization_effect"] == "none"
    assert event.payload["source_system"] == "otel"
    assert event.payload["contract_version"] == "1"
    assert event.payload["trace_id"] == "trace-1"
    assert event.payload["resource_keys"] == ("crm:contact:c-7",)

    params["status"] = "mutated-after-ingest"
    assert ledger.get(event.event_id).payload["params"]["status"] == "qualified"


def test_ingestion_can_bind_existing_causal_evidence() -> None:
    ledger = ActionLedger()
    source = ledger.record(EventType.EXTERNAL_INPUT, "inc-1", {"kind": "ticket"})
    event = ingest_action_observation(
        ledger,
        observation(observation_id="obs-2", source_event_id="span-event-43"),
        parent_event_ids=(source.event_id,),
    )
    assert event.parent_event_ids == (source.event_id,)
    assert ledger.verify_integrity() is True


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("incident_id", ""),
        ("tool_id", " "),
        ("action_type", ""),
        ("contract_version", ""),
        ("agent_id", ""),
        ("source_system", ""),
        ("source_event_id", ""),
        ("observation_id", ""),
    ],
)
def test_ingestion_fails_closed_on_missing_identity(field: str, value: object) -> None:
    with pytest.raises(IngestionError):
        observation(**{field: value}).validate()


def test_ingestion_rejects_ambiguous_resource_identity() -> None:
    with pytest.raises(IngestionError, match="unique"):
        observation(resource_keys=("crm:contact:c-7", "crm:contact:c-7")).validate()

    with pytest.raises(IngestionError, match="strings"):
        observation(resource_keys=("crm:contact:c-7", 7)).validate()
