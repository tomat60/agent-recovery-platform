from agent_recovery.catalog import synthetic_contracts
from agent_recovery.engine import ActionDecision, RecoveryEngine, RecoveryStatus
from agent_recovery.ledger import EventType
from agent_recovery.simulator import SyntheticEnterprise


def make_engine() -> RecoveryEngine:
    engine = RecoveryEngine(SyntheticEnterprise())
    for contract in synthetic_contracts():
        engine.register(contract)
    return engine


def test_recovery_cannot_be_rebound_to_another_incident() -> None:
    engine = make_engine()
    action = engine.execute(
        incident_id="incident-source",
        agent_id="agent-1",
        tool_id="crm.update_contact",
        params={"contact_id": "c-1", "field": "tier", "value": "vip"},
    )
    assert action.decision is ActionDecision.EXECUTED
    assert engine.state.crm_contacts["c-1"]["tier"] == "vip"

    recovery = engine.recover(
        incident_id="incident-other",
        action_event_id=action.action_event.event_id,
    )

    assert recovery.status is RecoveryStatus.FAILED
    assert recovery.recovery_event.incident_id == "incident-source"
    assert recovery.recovery_event.payload["reason"] == "incident_mismatch"
    assert engine.state.crm_contacts["c-1"]["tier"] == "vip"

    other_events = engine.ledger.events(incident_id="incident-other")
    assert not any(
        event.event_type
        in {EventType.RECOVERY_PLANNED, EventType.RECOVERY_EXECUTED, EventType.VERIFICATION}
        for event in other_events
    )
