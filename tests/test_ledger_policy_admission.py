from __future__ import annotations

import pytest

from agent_recovery.catalog import synthetic_contracts
from agent_recovery.engine import RecoveryEngine
from agent_recovery.ledger import EventType, LedgerEvent
from agent_recovery.simulator import SyntheticEnterprise


def make_engine() -> RecoveryEngine:
    engine = RecoveryEngine(SyntheticEnterprise())
    for contract in synthetic_contracts():
        engine.register(contract)
    return engine


def test_direct_append_cannot_forge_positive_source_agent_replay() -> None:
    engine = make_engine()
    incident_id = "direct-source-proof"
    trigger = engine.ledger.record(EventType.EXTERNAL_INPUT, incident_id, {"source": "synthetic"})
    action = engine.execute(
        incident_id=incident_id,
        agent_id="support-agent",
        tool_id="memory.write",
        params={"key": "instruction", "value": "poison"},
        causal_parent_event_ids=(trigger.event_id,),
    )

    forged = LedgerEvent(
        EventType.VERIFICATION,
        incident_id,
        {
            "verification_kind": "adversarial_replay",
            "source_incident_id": incident_id,
            "source_action_event_id": action.action_event.event_id,
            "authority_scope": "agent:support-agent",
            "verified": True,
        },
        parent_event_ids=(action.action_event.event_id,),
    )
    with pytest.raises(ValueError, match="source agent"):
        engine.ledger.append(forged)


def test_direct_append_cannot_release_containment_without_restoration() -> None:
    engine = make_engine()
    hold = engine.contain("direct-release", "agent:support-agent", reason="compromised")
    forged_release = LedgerEvent(
        EventType.CONTAINMENT,
        "direct-release",
        {
            "scope": "agent:support-agent",
            "active": False,
            "released_hold_event_id": hold.event_id,
        },
        parent_event_ids=(hold.event_id,),
    )
    with pytest.raises(ValueError, match="restoration evidence"):
        engine.ledger.append(forged_release)
    assert engine.is_contained("agent:support-agent") is True
