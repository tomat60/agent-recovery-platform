from __future__ import annotations

import pytest

from agent_recovery.ingestion import IngestionError, ingest_action_observation
from agent_recovery.ledger import ActionLedger
from agent_recovery.otel_adapter import normalize_otel_action_observation


def span(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "trace_id": "trace-abc",
        "span_id": "span-def",
        "start_time_unix_nano": 0,
        "attributes": {
            "agent.recovery.incident_id": "inc-88",
            "agent.recovery.tool_id": "crm.contacts",
            "agent.recovery.action_type": "contact.update",
            "agent.recovery.contract_version": "1",
            "agent.recovery.agent_id": "sales-agent",
            "agent.recovery.params": {
                "contact_id": "c-7",
                "status": "qualified",
            },
            "agent.recovery.authority_scope": "integration:crm",
            "agent.recovery.resource_keys": ["crm:contact:c-7"],
        },
    }
    value.update(overrides)
    return value


def test_otel_span_normalizes_to_contract_bound_non_authorizing_evidence() -> None:
    observation = normalize_otel_action_observation(span())

    assert observation.incident_id == "inc-88"
    assert observation.tool_id == "crm.contacts"
    assert observation.action_type == "contact.update"
    assert observation.contract_version == "1"
    assert observation.trace_id == "trace-abc"
    assert observation.span_id == "span-def"
    assert observation.source_system == "otel"
    assert observation.source_event_id == "span-def"
    assert observation.observation_id == "otel:trace-abc:span-def"
    assert observation.observed_at == "1970-01-01T00:00:00.000+00:00"

    ledger = ActionLedger()
    event = ingest_action_observation(ledger, observation)
    assert event.payload["contract_version"] == "1"
    assert event.payload["authorization_effect"] == "none"
    assert event.payload["authority_scope"] == "integration:crm"
    assert event.payload["resource_keys"] == ("crm:contact:c-7",)


def test_otel_explicit_observed_at_is_preserved() -> None:
    raw = span()
    attributes = dict(raw["attributes"])  # type: ignore[arg-type]
    attributes["agent.recovery.observed_at"] = "2026-09-18T15:20:00+00:00"
    raw["attributes"] = attributes

    observation = normalize_otel_action_observation(raw)

    assert observation.observed_at == "2026-09-18T15:20:00+00:00"


@pytest.mark.parametrize(
    "missing_key",
    [
        "agent.recovery.incident_id",
        "agent.recovery.tool_id",
        "agent.recovery.action_type",
        "agent.recovery.contract_version",
        "agent.recovery.agent_id",
    ],
)
def test_otel_adapter_fails_closed_on_missing_required_identity(missing_key: str) -> None:
    raw = span()
    attributes = dict(raw["attributes"])  # type: ignore[arg-type]
    del attributes[missing_key]
    raw["attributes"] = attributes

    with pytest.raises(IngestionError, match="required"):
        normalize_otel_action_observation(raw)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("attributes", [], "attributes"),
        ("trace_id", "", "trace_id"),
        ("span_id", "", "span_id"),
        ("start_time_unix_nano", -1, "start_time"),
    ],
)
def test_otel_adapter_rejects_malformed_span_fields(
    field: str,
    value: object,
    message: str,
) -> None:
    with pytest.raises(IngestionError, match=message):
        normalize_otel_action_observation(span(**{field: value}))


def test_otel_adapter_rejects_malformed_params_and_resource_keys() -> None:
    raw = span()
    attributes = dict(raw["attributes"])  # type: ignore[arg-type]
    attributes["agent.recovery.params"] = "not-a-mapping"
    raw["attributes"] = attributes
    with pytest.raises(IngestionError, match="params"):
        normalize_otel_action_observation(raw)

    raw = span()
    attributes = dict(raw["attributes"])  # type: ignore[arg-type]
    attributes["agent.recovery.resource_keys"] = "crm:contact:c-7"
    raw["attributes"] = attributes
    with pytest.raises(IngestionError, match="resource_keys"):
        normalize_otel_action_observation(raw)

    raw = span()
    attributes = dict(raw["attributes"])  # type: ignore[arg-type]
    attributes["agent.recovery.resource_keys"] = ["crm:contact:c-7", 7]
    raw["attributes"] = attributes
    with pytest.raises(IngestionError, match="strings"):
        normalize_otel_action_observation(raw)


def test_otel_adapter_requires_a_deterministic_observed_time() -> None:
    raw = span()
    del raw["start_time_unix_nano"]

    with pytest.raises(IngestionError, match="start_time_unix_nano"):
        normalize_otel_action_observation(raw)
