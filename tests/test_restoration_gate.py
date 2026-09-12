from __future__ import annotations

from agent_recovery.catalog import synthetic_contracts
from agent_recovery.engine import ActionDecision, Approval, RecoveryEngine, RecoveryStatus
from agent_recovery.ledger import EventType
from agent_recovery.replay import ReplayActionSpec, ReplayLab
from agent_recovery.restoration import (
    RestorationDecision,
    RestorationGate,
    record_replay_verification,
)
from agent_recovery.simulator import SyntheticEnterprise


def make_engine(state: SyntheticEnterprise | None = None, ledger=None) -> RecoveryEngine:
    engine = RecoveryEngine(state or SyntheticEnterprise(), ledger=ledger)
    for contract in synthetic_contracts():
        engine.register(contract)
    return engine


def run_memory_replay(
    engine: RecoveryEngine,
    trigger_event_id: str,
    *,
    contained: bool,
    release_scope: str,
):
    return ReplayLab(make_engine).run(
        source_ledger=engine.ledger,
        source_incident_id=engine.ledger.get(trigger_event_id).incident_id,
        source_trigger_event_id=trigger_event_id,
        replay_id=f"replay-{trigger_event_id}-{release_scope}",
        action=ReplayActionSpec(
            agent_id="support-agent",
            tool_id="memory.write",
            params={"key": "instruction", "value": "poisoned"},
            containment_scopes=("agent:support-agent",) if contained else (),
            release_scope=release_scope,
        ),
    )


def test_verified_recovery_and_scope_bound_replay_allow_authority_restoration() -> None:
    engine = make_engine()
    incident_id = "restore-1"
    scope = "agent:support-agent"
    trigger = engine.ledger.record(
        EventType.EXTERNAL_INPUT,
        incident_id,
        {"source": "poisoned_ticket", "content_digest": "attack-a"},
    )
    action = engine.execute(
        incident_id=incident_id,
        agent_id="support-agent",
        tool_id="memory.write",
        params={"key": "instruction", "value": "poisoned"},
        causal_parent_event_ids=(trigger.event_id,),
    )
    engine.contain(incident_id, scope, reason="source compromised")
    recovery = engine.recover(
        incident_id=incident_id,
        action_event_id=action.action_event.event_id,
    )
    assert recovery.status is RecoveryStatus.VERIFIED

    replay = record_replay_verification(
        engine.ledger,
        incident_id=incident_id,
        evidence=run_memory_replay(
            engine,
            trigger.event_id,
            contained=True,
            release_scope=scope,
        ),
    )
    assert replay.verified is True
    assert replay.event.payload["evidence_source"] == "isolated_replay_lab"
    assert replay.event.payload["authority_scope"] == scope

    result = RestorationGate(engine.ledger).authorize(
        incident_id=incident_id,
        authority_scope=scope,
        replay_event_id=replay.event.event_id,
    )
    assert result.decision is RestorationDecision.RESTORED
    engine.release_containment(
        incident_id,
        scope,
        restoration_event_id=result.event.event_id,
    )
    assert engine.is_contained(scope) is False


def test_restoration_blocks_unrecovered_or_unrelated_authority() -> None:
    engine = make_engine()
    incident_id = "restore-unrecovered"
    scope = "agent:support-agent"
    trigger = engine.ledger.record(
        EventType.EXTERNAL_INPUT,
        incident_id,
        {"source": "poisoned_ticket", "content_digest": "attack"},
    )
    engine.execute(
        incident_id=incident_id,
        agent_id="support-agent",
        tool_id="memory.write",
        params={"key": "instruction", "value": "poisoned"},
        causal_parent_event_ids=(trigger.event_id,),
    )
    engine.contain(incident_id, scope, reason="source compromised")
    evidence = run_memory_replay(
        engine,
        trigger.event_id,
        contained=True,
        release_scope=scope,
    )
    replay = record_replay_verification(engine.ledger, incident_id=incident_id, evidence=evidence)

    unrecovered = RestorationGate(engine.ledger).authorize(
        incident_id=incident_id,
        authority_scope=scope,
        replay_event_id=replay.event.event_id,
    )
    unrelated = RestorationGate(engine.ledger).authorize(
        incident_id=incident_id,
        authority_scope="identity:unrelated-admin",
        replay_event_id=replay.event.event_id,
    )
    assert unrecovered.decision is RestorationDecision.BLOCKED
    assert unrecovered.reason == "recovery_obligations_incomplete"
    assert unrelated.decision is RestorationDecision.BLOCKED
    assert unrelated.reason == "replay_scope_mismatch"


def test_replay_evidence_becomes_stale_if_incident_changes_after_verification() -> None:
    engine = make_engine()
    incident_id = "restore-2"
    scope = "agent:support-agent"
    trigger = engine.ledger.record(
        EventType.EXTERNAL_INPUT,
        incident_id,
        {"source": "external_content", "content_digest": "attack-b"},
    )
    first = engine.execute(
        incident_id=incident_id,
        agent_id="support-agent",
        tool_id="memory.write",
        params={"key": "instruction", "value": "poisoned"},
        causal_parent_event_ids=(trigger.event_id,),
    )
    engine.contain(incident_id, scope, reason="source compromised")
    engine.recover(incident_id=incident_id, action_event_id=first.action_event.event_id)
    replay = record_replay_verification(
        engine.ledger,
        incident_id=incident_id,
        evidence=run_memory_replay(
            engine,
            trigger.event_id,
            contained=True,
            release_scope=scope,
        ),
    )
    engine.ledger.record(
        EventType.TOOL_OUTPUT,
        incident_id,
        {"tool_id": "detector", "result": "new evidence"},
        parent_event_ids=(trigger.event_id,),
    )
    result = RestorationGate(engine.ledger).authorize(
        incident_id=incident_id,
        authority_scope=scope,
        replay_event_id=replay.event.event_id,
    )
    assert result.decision is RestorationDecision.BLOCKED
    assert result.reason == "stale_replay_evidence"


def test_replay_with_observed_side_effects_cannot_restore_authority() -> None:
    engine = make_engine()
    incident_id = "restore-3"
    scope = "agent:support-agent"
    trigger = engine.ledger.record(
        EventType.EXTERNAL_INPUT,
        incident_id,
        {"source": "malicious_tool_output"},
    )
    action = engine.execute(
        incident_id=incident_id,
        agent_id="support-agent",
        tool_id="memory.write",
        params={"key": "instruction", "value": "poisoned"},
        causal_parent_event_ids=(trigger.event_id,),
    )
    engine.contain(incident_id, scope, reason="source compromised")
    engine.recover(incident_id=incident_id, action_event_id=action.action_event.event_id)
    evidence = run_memory_replay(
        engine,
        trigger.event_id,
        contained=False,
        release_scope=scope,
    )
    observation = evidence.derive(source_ledger=engine.ledger, source_incident_id=incident_id)
    assert observation.entry_action_blocked_by_containment is False
    assert observation.executed_side_effect_event_ids

    replay = record_replay_verification(engine.ledger, incident_id=incident_id, evidence=evidence)
    assert replay.verified is False
    result = RestorationGate(engine.ledger).authorize(
        incident_id=incident_id,
        authority_scope=scope,
        replay_event_id=replay.event.event_id,
    )
    assert result.decision is RestorationDecision.BLOCKED
    assert result.reason == "replay_not_verified"


def test_forged_verification_without_replay_lab_provenance_is_rejected() -> None:
    engine = make_engine()
    trigger = engine.ledger.record(EventType.EXTERNAL_INPUT, "restore-forged", {"source": "x"})
    forged = engine.ledger.record(
        EventType.VERIFICATION,
        "restore-forged",
        {
            "verification_kind": "adversarial_replay",
            "source_incident_id": "restore-forged",
            "source_fingerprint": "forged",
            "recovery_fingerprint": "forged",
            "verified": True,
        },
        parent_event_ids=(trigger.event_id,),
    )
    result = RestorationGate(engine.ledger).authorize(
        incident_id="restore-forged",
        authority_scope="agent:support-agent",
        replay_event_id=forged.event_id,
    )
    assert result.decision is RestorationDecision.BLOCKED
    assert result.reason == "untrusted_replay_evidence_source"


def test_consumed_approval_cannot_resurrect_after_engine_recreation() -> None:
    state = SyntheticEnterprise()
    engine = make_engine(state)
    params = {"channel": "customer", "body": "Approved once", "observed": True}
    approval = Approval.for_action("comms.send_message", params, "approval-once")
    first = engine.execute(
        incident_id="restore-4",
        agent_id="comms-agent",
        tool_id="comms.send_message",
        params=params,
        approval=approval,
    )
    assert first.decision is ActionDecision.EXECUTED
    restored_local_runtime = make_engine(state, ledger=engine.ledger)
    replayed = restored_local_runtime.execute(
        incident_id="restore-4",
        agent_id="comms-agent",
        tool_id="comms.send_message",
        params=params,
        approval=approval,
    )
    assert replayed.decision is ActionDecision.BLOCKED
    assert replayed.action_event.payload["reason"] == "approval_already_consumed"
    assert len(state.messages) == 1
