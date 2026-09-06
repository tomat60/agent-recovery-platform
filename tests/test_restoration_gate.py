from __future__ import annotations

from agent_recovery.catalog import synthetic_contracts
from agent_recovery.engine import ActionDecision, Approval, RecoveryEngine
from agent_recovery.ledger import EventType
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


def test_verified_adversarial_replay_allows_authority_restoration() -> None:
    engine = make_engine()
    trigger = engine.ledger.record(
        EventType.EXTERNAL_INPUT,
        "restore-1",
        {"source": "poisoned_ticket", "content_digest": "attack-a"},
    )
    engine.execute(
        incident_id="restore-1",
        agent_id="support-agent",
        tool_id="memory.write",
        params={"key": "instruction", "value": "poisoned"},
        causal_parent_event_ids=(trigger.event_id,),
    )

    replay = record_replay_verification(
        engine.ledger,
        incident_id="restore-1",
        trigger_event_id=trigger.event_id,
        replay_id="replay-001",
        attack_blocked=True,
        evidence_complete=True,
    )
    assert replay.verified is True

    result = RestorationGate(engine.ledger).authorize(
        incident_id="restore-1",
        authority_scope="agent:support-agent",
        replay_event_id=replay.event.event_id,
    )
    assert result.decision is RestorationDecision.RESTORED
    assert result.event.payload["authorized"] is True


def test_replay_evidence_becomes_stale_if_incident_changes_after_verification() -> None:
    engine = make_engine()
    trigger = engine.ledger.record(
        EventType.EXTERNAL_INPUT,
        "restore-2",
        {"source": "external_content", "content_digest": "attack-b"},
    )
    first = engine.execute(
        incident_id="restore-2",
        agent_id="agent-a",
        tool_id="memory.write",
        params={"key": "instruction", "value": "poisoned"},
        causal_parent_event_ids=(trigger.event_id,),
    )
    replay = record_replay_verification(
        engine.ledger,
        incident_id="restore-2",
        trigger_event_id=trigger.event_id,
        replay_id="replay-002",
        attack_blocked=True,
        evidence_complete=True,
    )

    engine.execute(
        incident_id="restore-2",
        agent_id="agent-b",
        tool_id="memory.write",
        params={"key": "downstream", "value": "new-effect"},
        causal_parent_event_ids=(first.action_event.event_id,),
    )

    result = RestorationGate(engine.ledger).authorize(
        incident_id="restore-2",
        authority_scope="agent:agent-a",
        replay_event_id=replay.event.event_id,
    )
    assert result.decision is RestorationDecision.BLOCKED
    assert result.reason == "stale_replay_evidence"


def test_replay_with_unsafe_side_effects_cannot_restore_authority() -> None:
    engine = make_engine()
    trigger = engine.ledger.record(
        EventType.EXTERNAL_INPUT,
        "restore-3",
        {"source": "malicious_tool_output"},
    )
    replay = record_replay_verification(
        engine.ledger,
        incident_id="restore-3",
        trigger_event_id=trigger.event_id,
        replay_id="replay-003",
        attack_blocked=False,
        evidence_complete=True,
        unsafe_side_effects=("external_message_sent",),
    )
    assert replay.verified is False

    result = RestorationGate(engine.ledger).authorize(
        incident_id="restore-3",
        authority_scope="agent:agent-a",
        replay_event_id=replay.event.event_id,
    )
    assert result.decision is RestorationDecision.BLOCKED
    assert result.reason == "replay_not_verified"


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
    assert len(state.messages) == 1

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
    consumed = [
        event
        for event in engine.ledger.events(incident_id="restore-4")
        if event.event_type is EventType.AUTHORITY_CONSUMED
    ]
    assert len(consumed) == 1
