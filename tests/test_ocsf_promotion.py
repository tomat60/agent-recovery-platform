from __future__ import annotations

from copy import deepcopy

import pytest

from agent_recovery.ingestion import IngestionError
from agent_recovery.ocsf_promotion import promote_ocsf_evidence_batch


def _event(uid: str, action: str = "Allowed") -> dict[str, object]:
    return {
        "class_uid": 4002,
        "activity_id": 1,
        "time": 1790751000000,
        "metadata": {
            "uid": uid,
            "version": "1.8.0",
            "product": {"name": "OpenShell Sandbox Supervisor"},
        },
        "container": {"uid": "sandbox-7"},
        "action": action,
        "disposition": action,
        "dst_endpoint": {"domain": "crm.example.test", "port": 443},
    }


def _mapping(incident_id: str, contact_id: str) -> dict[str, object]:
    return {
        "incident_id": incident_id,
        "tool_id": "crm.contacts",
        "action_type": "contact.update",
        "contract_version": "1",
        "agent_id": "support-agent",
        "params": {"contact_id": contact_id, "status": "vip"},
        "authority_scope": "integration:crm",
        "resource_keys": [f"crm:contact:{contact_id}"],
    }


def test_batch_promotion_binds_source_and_recovery_mapping_without_authority() -> None:
    events = [_event("event-1"), _event("event-2", action="Blocked")]
    mappings = {
        "event-1": _mapping("inc-1", "c-1"),
        "event-2": _mapping("inc-2", "c-2"),
    }

    promotions = promote_ocsf_evidence_batch(events, mappings)

    assert [item.source_event_id for item in promotions] == ["event-1", "event-2"]
    first = promotions[0].payload()
    second = promotions[1].payload()
    assert first["authorization_effect"] == "none"
    assert first["observation"]["authorization_effect"] == "none"
    assert first["observation"]["observation_id"] == "ocsf:event-1"
    assert len(first["source_provenance_digest"]) == 64
    assert len(first["recovery_mapping_digest"]) == 64
    assert second["observation"]["observation_id"] == "ocsf:event-2"
    assert second["authorization_effect"] == "none"


def test_source_and_mapping_digests_protect_independent_boundaries() -> None:
    event = _event("event-1")
    mapping = _mapping("inc-1", "c-1")
    baseline = promote_ocsf_evidence_batch([event], {"event-1": mapping})[0]

    changed_event = deepcopy(event)
    changed_event["dst_endpoint"] = {
        "domain": "billing.example.test",
        "port": 443,
    }
    source_changed = promote_ocsf_evidence_batch(
        [changed_event],
        {"event-1": mapping},
    )[0]

    changed_mapping = deepcopy(mapping)
    changed_mapping["params"] = {"contact_id": "c-9", "status": "vip"}
    mapping_changed = promote_ocsf_evidence_batch(
        [event],
        {"event-1": changed_mapping},
    )[0]

    assert source_changed.source_provenance_digest != (
        baseline.source_provenance_digest
    )
    assert source_changed.recovery_mapping_digest == (
        baseline.recovery_mapping_digest
    )
    assert mapping_changed.source_provenance_digest == (
        baseline.source_provenance_digest
    )
    assert mapping_changed.recovery_mapping_digest != (
        baseline.recovery_mapping_digest
    )


@pytest.mark.parametrize(
    ("mappings", "message"),
    [
        ({}, "missing OCSF recovery mappings for: event-1"),
        (
            {
                "event-1": _mapping("inc-1", "c-1"),
                "absent": _mapping("inc-2", "c-2"),
            },
            "unexpected OCSF recovery mappings for: absent",
        ),
    ],
)
def test_batch_promotion_requires_an_exact_mapping_manifest(
    mappings: dict[str, dict[str, object]],
    message: str,
) -> None:
    with pytest.raises(IngestionError, match=message):
        promote_ocsf_evidence_batch([_event("event-1")], mappings)


def test_batch_promotion_rejects_ambiguous_mapping_value() -> None:
    with pytest.raises(IngestionError, match="event-1 must be a mapping"):
        promote_ocsf_evidence_batch(
            [_event("event-1")],
            {"event-1": "not-a-mapping"},  # type: ignore[dict-item]
        )


def test_promotion_detaches_and_revalidates_nested_mapping_state() -> None:
    mapping = _mapping("inc-1", "c-1")
    promotion = promote_ocsf_evidence_batch(
        [_event("event-1")],
        {"event-1": mapping},
    )[0]

    mapping["params"]["contact_id"] = "external-mutation"
    assert promotion.payload()["observation"]["params"]["contact_id"] == "c-1"

    promotion.observation.params["contact_id"] = "internal-mutation"
    with pytest.raises(IngestionError, match="recovery_mapping_digest mismatch"):
        promotion.payload()
