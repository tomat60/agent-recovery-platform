from __future__ import annotations

from dataclasses import replace

import pytest

from agent_recovery.ledger import ActionLedger, EventType, LedgerIntegrityError
from agent_recovery.restoration import RestorationDecision, RestorationGate


def test_ledger_hash_chain_verifies_after_normal_appends() -> None:
    ledger = ActionLedger()
    root = ledger.record(EventType.EXTERNAL_INPUT, "incident-1", {"digest": "a"})
    child = ledger.record(
        EventType.ACTION_INTENT,
        "incident-1",
        {"tool": "memory.write"},
        parent_event_ids=(root.event_id,),
    )
    assert root.event_hash
    assert child.previous_hash == root.event_hash
    assert ledger.head_hash == child.event_hash
    assert ledger.verify_integrity() is True


def test_ledger_detects_payload_tampering() -> None:
    ledger = ActionLedger()
    event = ledger.record(EventType.EXTERNAL_INPUT, "incident-2", {"digest": "a"})
    ledger._events[0] = replace(event, payload={"digest": "tampered"})  # type: ignore[attr-defined]
    with pytest.raises(LedgerIntegrityError, match="event content"):
        ledger.verify_integrity()


def test_ledger_detects_event_deletion_or_reordering() -> None:
    ledger = ActionLedger()
    first = ledger.record(EventType.EXTERNAL_INPUT, "incident-3", {"digest": "a"})
    second = ledger.record(
        EventType.ACTION_INTENT,
        "incident-3",
        {"tool": "crm.update"},
        parent_event_ids=(first.event_id,),
    )
    third = ledger.record(
        EventType.ACTION_EXECUTED,
        "incident-3",
        {"tool": "crm.update"},
        parent_event_ids=(second.event_id,),
    )
    ledger._events[:] = [first, third, second]  # type: ignore[attr-defined]
    with pytest.raises(LedgerIntegrityError):
        ledger.verify_integrity()


def test_restoration_fails_closed_when_ledger_integrity_is_broken() -> None:
    ledger = ActionLedger()
    trigger = ledger.record(EventType.EXTERNAL_INPUT, "incident-4", {"digest": "attack"})
    replay = ledger.record(
        EventType.VERIFICATION,
        "incident-4",
        {"verification_kind": "adversarial_replay", "verified": True},
        parent_event_ids=(trigger.event_id,),
    )
    ledger._events[0] = replace(trigger, payload={"digest": "forged"})  # type: ignore[attr-defined]
    result = RestorationGate(ledger).authorize(
        incident_id="incident-4",
        authority_scope="agent:support",
        replay_event_id=replay.event_id,
    )
    assert result.decision is RestorationDecision.BLOCKED
    assert result.reason == "ledger_integrity_failure"
    assert result.event.payload["persisted"] is False
