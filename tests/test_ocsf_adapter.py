from __future__ import annotations

from copy import deepcopy

import pytest

from agent_recovery.ingestion import IngestionError
from agent_recovery.ocsf_adapter import (
    normalize_ocsf_evidence_event,
    normalize_ocsf_json_events,
    promote_ocsf_action_observation,
)


def ocsf_event(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "class_uid": 4002,
        "class_name": "HTTP Activity",
        "activity_id": 1,
        "activity_name": "Request",
        "time": 1790751000000,
        "metadata": {
            "uid": "openshell-event-42",
            "version": "1.8.0",
            "product": {
                "name": "OpenShell Sandbox Supervisor",
                "vendor_name": "NVIDIA",
                "version": "0.3.0",
            },
        },
        "container": {"uid": "sandbox-7"},
        "action": "Allowed",
        "disposition": "Allowed",
        "http_request": {"http_method": "POST"},
        "dst_endpoint": {"domain": "crm.example.test", "port": 443},
    }
    value.update(overrides)
    return value


def recovery_mapping(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "incident_id": "inc-ocsf-1",
        "tool_id": "crm.contacts",
        "action_type": "contact.update",
        "contract_version": "1",
        "agent_id": "support-agent",
        "params": {"contact_id": "c-7", "status": "vip"},
        "authority_scope": "integration:crm",
        "resource_keys": ["crm:contact:c-7"],
        "trace_id": "trace-ocsf-1",
    }
    value.update(overrides)
    return value


def test_ocsf_event_preserves_source_identity_and_zero_authority() -> None:
    envelope = normalize_ocsf_evidence_event(ocsf_event())

    assert envelope.event_uid == "openshell-event-42"
    assert envelope.class_uid == 4002
    assert envelope.sandbox_uid == "sandbox-7"
    assert envelope.product_name == "OpenShell Sandbox Supervisor"
    assert envelope.schema_version == "1.8.0"
    assert envelope.action == "Allowed"
    assert envelope.disposition == "Allowed"
    assert envelope.evidence_payload()["authorization_effect"] == "none"


def test_ocsf_provenance_digest_is_deterministic_and_tamper_sensitive() -> None:
    first = normalize_ocsf_evidence_event(ocsf_event())
    repeated = normalize_ocsf_evidence_event(deepcopy(ocsf_event()))
    changed = normalize_ocsf_evidence_event(
        ocsf_event(dst_endpoint={"domain": "billing.example.test", "port": 443})
    )

    assert first.provenance_digest() == repeated.provenance_digest()
    assert first.provenance_digest() != changed.provenance_digest()


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ({"metadata": {"version": "1.8.0", "product": {"name": "OpenShell"}}}, "uid"),
        ({"metadata": {"uid": "event-1", "product": {"name": "OpenShell"}}}, "version"),
        ({"class_uid": -1}, "class_uid"),
        ({"activity_id": "1"}, "activity_id"),
        ({"time": -1}, "time"),
        ({"container": {"uid": ""}}, "container.uid"),
    ],
)
def test_ocsf_adapter_fails_closed_on_malformed_identity(
    mutation: dict[str, object],
    message: str,
) -> None:
    raw = ocsf_event(**mutation)

    with pytest.raises(IngestionError, match=message):
        normalize_ocsf_evidence_event(raw)


def test_ocsf_batch_rejects_duplicate_source_event_identity() -> None:
    event = ocsf_event()

    with pytest.raises(IngestionError, match="duplicate OCSF source event"):
        normalize_ocsf_json_events([event, deepcopy(event)])


def test_ocsf_policy_outcome_does_not_create_recovery_identity() -> None:
    envelope = normalize_ocsf_evidence_event(ocsf_event())

    with pytest.raises(IngestionError, match="incident_id"):
        promote_ocsf_action_observation(envelope, {"params": {}})


def test_ocsf_promotion_requires_explicit_recovery_mapping() -> None:
    envelope = normalize_ocsf_evidence_event(ocsf_event())
    observation = promote_ocsf_action_observation(envelope, recovery_mapping())

    assert observation.incident_id == "inc-ocsf-1"
    assert observation.source_system == "ocsf"
    assert observation.source_event_id == "openshell-event-42"
    assert observation.observation_id == "ocsf:openshell-event-42"
    assert observation.authority_scope == "integration:crm"
    assert observation.resource_keys == ("crm:contact:c-7",)
    assert observation.payload()["authorization_effect"] == "none"


def test_ocsf_promotion_uses_event_time_when_observed_at_is_not_mapped() -> None:
    envelope = normalize_ocsf_evidence_event(ocsf_event(time=0))
    observation = promote_ocsf_action_observation(envelope, recovery_mapping())

    assert observation.observed_at == "1970-01-01T00:00:00.000+00:00"


def test_ocsf_promotion_rejects_ambiguous_resource_keys() -> None:
    envelope = normalize_ocsf_evidence_event(ocsf_event())

    with pytest.raises(IngestionError, match="resource_keys"):
        promote_ocsf_action_observation(
            envelope,
            recovery_mapping(resource_keys="crm:contact:c-7"),
        )
