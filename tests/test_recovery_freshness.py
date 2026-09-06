from __future__ import annotations

from agent_recovery.ledger import ActionLedger, EventType
from agent_recovery.restoration import RestorationDecision, RestorationGate, record_replay_verification


def test_recovery_evidence_change_invalidates_verified_replay() -> None:
    ledger = ActionLedger()
    trigger = ledger.record(
        EventType.EXTERNAL_INPUT,
        "incident-recovery-freshness",
        {"source": "poisoned_ticket", "digest": "attack"},
    )
    plan = ledger.record(
        EventType.RECOVERY_PLANNED,
        "incident-recovery-freshness",
        {"plan_id": "plan-1", "steps": ["restore-memory"]},
        parent_event_ids=(trigger.event_id,),
    )
    ledger.record(
        EventType.RECOVERY_EXECUTED,
        "incident-recovery-freshness",
        {"plan_id": "plan-1", "step": "restore-memory", "status": "verified"},
        parent_event_ids=(plan.event_id,),
    )

    replay = record_replay_verification(
        ledger,
        incident_id="incident-recovery-freshness",
        trigger_event_id=trigger.event_id,
        replay_id="replay-before-recovery-change",
        attack_blocked=True,
        evidence_complete=True,
    )
    assert replay.verified is True

    ledger.record(
        EventType.RESIDUAL_EFFECT,
        "incident-recovery-freshness",
        {"effect": "stale_token", "severity": "high"},
        parent_event_ids=(plan.event_id,),
    )

    result = RestorationGate(ledger).authorize(
        incident_id="incident-recovery-freshness",
        authority_scope="agent:support-agent",
        replay_event_id=replay.event.event_id,
    )

    assert result.decision is RestorationDecision.BLOCKED
    assert result.reason == "stale_recovery_evidence"


def test_fresh_replay_after_recovery_change_can_restore_authority() -> None:
    ledger = ActionLedger()
    trigger = ledger.record(
        EventType.EXTERNAL_INPUT,
        "incident-recovery-refresh",
        {"source": "poisoned_ticket", "digest": "attack"},
    )
    ledger.record(
        EventType.RESIDUAL_EFFECT,
        "incident-recovery-refresh",
        {"effect": "irreversible_message", "reported": True},
        parent_event_ids=(trigger.event_id,),
    )

    replay = record_replay_verification(
        ledger,
        incident_id="incident-recovery-refresh",
        trigger_event_id=trigger.event_id,
        replay_id="replay-after-recovery-state",
        attack_blocked=True,
        evidence_complete=True,
    )

    result = RestorationGate(ledger).authorize(
        incident_id="incident-recovery-refresh",
        authority_scope="agent:support-agent",
        replay_event_id=replay.event.event_id,
    )

    assert result.decision is RestorationDecision.RESTORED
    assert result.reason is None
