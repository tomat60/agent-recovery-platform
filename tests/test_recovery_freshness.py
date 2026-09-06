from __future__ import annotations

from agent_recovery.catalog import synthetic_contracts
from agent_recovery.engine import RecoveryEngine
from agent_recovery.ledger import EventType
from agent_recovery.replay import ReplayActionSpec, ReplayLab
from agent_recovery.restoration import (
    RestorationDecision,
    RestorationGate,
    record_replay_verification,
)
from agent_recovery.simulator import SyntheticEnterprise


def make_engine() -> RecoveryEngine:
    engine = RecoveryEngine(SyntheticEnterprise())
    for contract in synthetic_contracts():
        engine.register(contract)
    return engine


def replay_for(engine: RecoveryEngine, incident_id: str, trigger_event_id: str):
    return ReplayLab(make_engine).run(
        source_ledger=engine.ledger,
        source_incident_id=incident_id,
        source_trigger_event_id=trigger_event_id,
        replay_id=f"replay-{incident_id}",
        action=ReplayActionSpec(
            agent_id="support-agent",
            tool_id="memory.write",
            params={"key": "instruction", "value": "poisoned"},
            containment_scopes=("agent:support-agent",),
        ),
    )


def test_recovery_evidence_change_invalidates_verified_replay() -> None:
    engine = make_engine()
    incident_id = "incident-recovery-freshness"
    trigger = engine.ledger.record(
        EventType.EXTERNAL_INPUT,
        incident_id,
        {"source": "poisoned_ticket", "digest": "attack"},
    )
    plan = engine.ledger.record(
        EventType.RECOVERY_PLANNED,
        incident_id,
        {"plan_id": "plan-1", "steps": ["restore-memory"]},
        parent_event_ids=(trigger.event_id,),
    )
    engine.ledger.record(
        EventType.RECOVERY_EXECUTED,
        incident_id,
        {"plan_id": "plan-1", "step": "restore-memory", "status": "verified"},
        parent_event_ids=(plan.event_id,),
    )
    replay = record_replay_verification(
        engine.ledger,
        incident_id=incident_id,
        evidence=replay_for(engine, incident_id, trigger.event_id),
    )
    assert replay.verified is True

    engine.ledger.record(
        EventType.RESIDUAL_EFFECT,
        incident_id,
        {"effect": "stale_token", "severity": "high"},
        parent_event_ids=(plan.event_id,),
    )
    result = RestorationGate(engine.ledger).authorize(
        incident_id=incident_id,
        authority_scope="agent:support-agent",
        replay_event_id=replay.event.event_id,
    )
    assert result.decision is RestorationDecision.BLOCKED
    assert result.reason == "stale_recovery_evidence"


def test_fresh_replay_after_recovery_change_can_restore_authority() -> None:
    engine = make_engine()
    incident_id = "incident-recovery-refresh"
    trigger = engine.ledger.record(
        EventType.EXTERNAL_INPUT,
        incident_id,
        {"source": "poisoned_ticket", "digest": "attack"},
    )
    engine.ledger.record(
        EventType.RESIDUAL_EFFECT,
        incident_id,
        {"effect": "irreversible_message", "reported": True},
        parent_event_ids=(trigger.event_id,),
    )
    replay = record_replay_verification(
        engine.ledger,
        incident_id=incident_id,
        evidence=replay_for(engine, incident_id, trigger.event_id),
    )
    result = RestorationGate(engine.ledger).authorize(
        incident_id=incident_id,
        authority_scope="agent:support-agent",
        replay_event_id=replay.event.event_id,
    )
    assert result.decision is RestorationDecision.RESTORED
    assert result.reason is None
