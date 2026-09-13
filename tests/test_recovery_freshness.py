from __future__ import annotations

from agent_recovery.catalog import synthetic_contracts
from agent_recovery.engine import RecoveryEngine, RecoveryStatus
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


def replay_for(
    engine: RecoveryEngine,
    incident_id: str,
    trigger_event_id: str,
    *,
    release_scope: str,
):
    return ReplayLab(make_engine).run(
        source_ledger=engine.ledger,
        source_incident_id=incident_id,
        source_trigger_event_id=trigger_event_id,
        replay_id=f"replay-{incident_id}-{release_scope}",
        action=ReplayActionSpec(
            agent_id="support-agent",
            tool_id="memory.write",
            params={"key": "instruction", "value": "poisoned"},
            containment_scopes=("agent:support-agent",),
            release_scope=release_scope,
        ),
    )


def prepared_incident(incident_id: str):
    engine = make_engine()
    root_scope = "agent:support-agent"
    release_scope = "agent:workflow-agent"
    trigger = engine.ledger.record(
        EventType.EXTERNAL_INPUT,
        incident_id,
        {"source": "poisoned_ticket", "digest": "attack"},
    )
    action = engine.execute(
        incident_id=incident_id,
        agent_id="support-agent",
        tool_id="memory.write",
        params={"key": "instruction", "value": "poisoned"},
        causal_parent_event_ids=(trigger.event_id,),
    )
    engine.contain(incident_id, root_scope, reason="source compromised")
    engine.contain(incident_id, release_scope, reason="dependent authority held during recovery")
    recovery = engine.recover(incident_id=incident_id, action_event_id=action.action_event.event_id)
    assert recovery.status is RecoveryStatus.VERIFIED
    return engine, release_scope, trigger


def test_recovery_evidence_change_invalidates_verified_replay() -> None:
    incident_id = "incident-recovery-freshness"
    engine, scope, trigger = prepared_incident(incident_id)
    replay = record_replay_verification(
        engine.ledger,
        incident_id=incident_id,
        evidence=replay_for(
            engine,
            incident_id,
            trigger.event_id,
            release_scope=scope,
        ),
    )
    assert replay.verified is True

    engine.ledger.record(
        EventType.RECOVERY_PLANNED,
        incident_id,
        {"plan_id": "new-plan", "steps": []},
        parent_event_ids=(trigger.event_id,),
    )
    result = RestorationGate(engine.ledger).authorize(
        incident_id=incident_id,
        authority_scope=scope,
        replay_event_id=replay.event.event_id,
    )
    assert result.decision is RestorationDecision.BLOCKED
    assert result.reason == "stale_recovery_evidence"


def test_fresh_replay_after_recovery_change_can_restore_downstream_authority() -> None:
    incident_id = "incident-recovery-refresh"
    engine, scope, trigger = prepared_incident(incident_id)
    engine.contain(incident_id, "agent:observer", reason="additional recovery evidence")

    replay = record_replay_verification(
        engine.ledger,
        incident_id=incident_id,
        evidence=replay_for(
            engine,
            incident_id,
            trigger.event_id,
            release_scope=scope,
        ),
    )
    result = RestorationGate(engine.ledger).authorize(
        incident_id=incident_id,
        authority_scope=scope,
        replay_event_id=replay.event.event_id,
    )
    assert result.decision is RestorationDecision.RESTORED
    assert result.reason is None
