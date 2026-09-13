from __future__ import annotations

from dataclasses import replace

import pytest

from agent_recovery.catalog import synthetic_contracts
from agent_recovery.engine import RecoveryEngine
from agent_recovery.ledger import EventType, LedgerIntegrityError
from agent_recovery.simulator import SyntheticEnterprise


def make_engine() -> RecoveryEngine:
    engine = RecoveryEngine(SyntheticEnterprise())
    for contract in synthetic_contracts():
        engine.register(contract)
    return engine


def test_corrupted_ledger_blocks_recovery_before_mutation() -> None:
    engine = make_engine()
    engine.state.memory["instruction"] = "trusted-before"
    action = engine.execute(
        incident_id="integrity-recovery",
        agent_id="source",
        tool_id="memory.write",
        params={"key": "instruction", "value": "poison"},
    )
    assert engine.state.memory["instruction"] == "poison"

    for index, event in enumerate(engine.ledger._events):  # type: ignore[attr-defined]
        if event.event_id != action.action_event.event_id:
            continue
        payload = dict(event.payload)
        execution_result = dict(payload["execution_result"])
        execution_result["before"] = "forged-before"
        payload["execution_result"] = execution_result
        engine.ledger._events[index] = replace(event, payload=payload)  # type: ignore[attr-defined]
        break
    else:
        raise AssertionError("executed action was not present in ledger")

    with pytest.raises(LedgerIntegrityError, match="event content"):
        engine.recover(
            incident_id="integrity-recovery",
            action_event_id=action.action_event.event_id,
        )

    assert engine.state.memory["instruction"] == "poison"
    assert not any(
        event.event_type is EventType.RECOVERY_EXECUTED
        for event in engine.ledger.events(incident_id="integrity-recovery")
    )
