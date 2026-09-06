from __future__ import annotations

import pytest

from agent_recovery.catalog import synthetic_contracts
from agent_recovery.engine import RecoveryEngine, RecoveryStatus
from agent_recovery.ledger import EventType
from agent_recovery.lineage import (
    RecoveryGenerationError,
    current_generation,
    record_recovery_fork,
    uncovered_residual_effect_event_ids,
)
from agent_recovery.restoration import recovery_fingerprint
from agent_recovery.simulator import SyntheticEnterprise


def make_engine() -> RecoveryEngine:
    engine = RecoveryEngine(SyntheticEnterprise())
    for contract in synthetic_contracts():
        engine.register(contract)
    return engine


def verified_local_recovery(engine: RecoveryEngine, incident_id: str):
    trigger = engine.ledger.record(
        EventType.EXTERNAL_INPUT,
        incident_id,
        {"source": "support_ticket", "digest": "poisoned"},
    )
    action = engine.execute(
        incident_id=incident_id,
        agent_id="support-agent",
        tool_id="memory.write",
        params={"key": "instruction", "value": "poisoned"},
        causal_parent_event_ids=(trigger.event_id,),
    )
    recovery = engine.recover(
        incident_id=incident_id,
        action_event_id=action.action_event.event_id,
    )
    assert recovery.status is RecoveryStatus.VERIFIED
    assert recovery.verification_event is not None
    return trigger, action, recovery


def test_recovery_fork_preserves_external_history_and_advances_generation() -> None:
    engine = make_engine()
    incident_id = "incident-fork-1"
    _, action, recovery = verified_local_recovery(engine, incident_id)
    residual = engine.ledger.record(
        EventType.RESIDUAL_EFFECT,
        incident_id,
        {"effect": "delivered_message", "observed": True},
        parent_event_ids=(action.action_event.event_id,),
    )

    fork = record_recovery_fork(
        engine.ledger,
        incident_id=incident_id,
        verified_recovery_event_id=recovery.verification_event.event_id,
    )

    assert fork.generation == 1
    assert fork.parent_generation == 0
    assert fork.residual_effect_event_ids == (residual.event_id,)
    assert fork.event.payload["external_history_rewritten"] is False
    assert current_generation(engine.ledger, incident_id=incident_id) == 1
    assert uncovered_residual_effect_event_ids(engine.ledger, incident_id=incident_id) == ()
    assert engine.ledger.get(residual.event_id).payload["observed"] is True


def test_new_external_effect_after_fork_remains_uncovered() -> None:
    engine = make_engine()
    incident_id = "incident-fork-2"
    _, action, recovery = verified_local_recovery(engine, incident_id)
    first = engine.ledger.record(
        EventType.RESIDUAL_EFFECT,
        incident_id,
        {"effect": "message-1"},
        parent_event_ids=(action.action_event.event_id,),
    )
    record_recovery_fork(
        engine.ledger,
        incident_id=incident_id,
        verified_recovery_event_id=recovery.verification_event.event_id,
        residual_event_ids=(first.event_id,),
    )
    second = engine.ledger.record(
        EventType.RESIDUAL_EFFECT,
        incident_id,
        {"effect": "message-2"},
        parent_event_ids=(action.action_event.event_id,),
    )

    assert uncovered_residual_effect_event_ids(engine.ledger, incident_id=incident_id) == (
        second.event_id,
    )


def test_recovery_fork_rejects_forged_verification_without_recovery_parent() -> None:
    engine = make_engine()
    incident_id = "incident-fork-forged"
    trigger = engine.ledger.record(
        EventType.EXTERNAL_INPUT,
        incident_id,
        {"source": "synthetic"},
    )
    forged = engine.ledger.record(
        EventType.VERIFICATION,
        incident_id,
        {"verified": True, "action_event_id": "invented-action"},
        parent_event_ids=(trigger.event_id,),
    )
    residual = engine.ledger.record(
        EventType.RESIDUAL_EFFECT,
        incident_id,
        {"effect": "externalized"},
        parent_event_ids=(trigger.event_id,),
    )

    with pytest.raises(RecoveryGenerationError, match="causally bound"):
        record_recovery_fork(
            engine.ledger,
            incident_id=incident_id,
            verified_recovery_event_id=forged.event_id,
            residual_event_ids=(residual.event_id,),
        )


def test_recovery_fork_changes_replay_freshness_fingerprint() -> None:
    engine = make_engine()
    incident_id = "incident-fork-fingerprint"
    _, action, recovery = verified_local_recovery(engine, incident_id)
    residual = engine.ledger.record(
        EventType.RESIDUAL_EFFECT,
        incident_id,
        {"effect": "externalized"},
        parent_event_ids=(action.action_event.event_id,),
    )
    before = recovery_fingerprint(engine.ledger, incident_id=incident_id)

    record_recovery_fork(
        engine.ledger,
        incident_id=incident_id,
        verified_recovery_event_id=recovery.verification_event.event_id,
        residual_event_ids=(residual.event_id,),
    )

    after = recovery_fingerprint(engine.ledger, incident_id=incident_id)
    assert after != before
