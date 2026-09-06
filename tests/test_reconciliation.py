from __future__ import annotations

from agent_recovery.catalog import synthetic_contracts
from agent_recovery.engine import RecoveryEngine, RecoveryStatus
from agent_recovery.graph import IncidentGraph
from agent_recovery.ledger import EventType
from agent_recovery.reconciliation import ReconciliationApproval, ReconciliationStatus
from agent_recovery.restoration import recovery_fingerprint
from agent_recovery.simulator import SyntheticEnterprise


def make_engine() -> RecoveryEngine:
    engine = RecoveryEngine(SyntheticEnterprise())
    for contract in synthetic_contracts():
        engine.register(contract)
    return engine


def same_field_conflict(engine: RecoveryEngine, incident_id: str = "reconcile-1"):
    poisoned_root = engine.ledger.record(
        EventType.EXTERNAL_INPUT,
        incident_id,
        {"source": "poisoned_ticket"},
    )
    trusted_root = engine.ledger.record(
        EventType.EXTERNAL_INPUT,
        incident_id,
        {"source": "trusted_operator_change"},
    )
    trusted = engine.execute(
        incident_id=incident_id,
        agent_id="billing-agent",
        tool_id="crm.update_contact",
        params={"contact_id": "c-1", "field": "tier", "value": "gold"},
        causal_parent_event_ids=(trusted_root.event_id,),
    )
    compromised = engine.execute(
        incident_id=incident_id,
        agent_id="support-agent",
        tool_id="crm.update_contact",
        params={"contact_id": "c-1", "field": "tier", "value": "vip"},
        causal_parent_event_ids=(poisoned_root.event_id,),
    )
    graph = IncidentGraph.from_ledger(engine.ledger, incident_id=incident_id)
    conflicts = graph.shared_state_conflicts(
        (compromised.action_event.event_id, trusted.action_event.event_id)
    )
    assert len(conflicts) == 1
    return trusted, compromised, conflicts[0]


def approval_for(
    engine: RecoveryEngine,
    *,
    incident_id: str,
    resource_key: str,
    compromised_action_event_id: str,
    trusted_action_event_id: str,
    approval_id: str,
) -> ReconciliationApproval:
    return ReconciliationApproval.for_conflict(
        incident_id=incident_id,
        resource_key=resource_key,
        compromised_action_event_id=compromised_action_event_id,
        trusted_action_event_id=trusted_action_event_id,
        evidence_head_hash=engine.ledger.head_hash,
        approval_id=approval_id,
    )


def test_same_field_conflict_can_reconcile_to_fresh_approved_trusted_evidence() -> None:
    engine = make_engine()
    incident_id = "reconcile-safe"
    trusted, compromised, conflict = same_field_conflict(engine, incident_id)

    failed_recovery = engine.recover(
        incident_id=incident_id,
        action_event_id=compromised.action_event.event_id,
    )
    assert failed_recovery.status is RecoveryStatus.FAILED
    assert engine.state.crm_contacts["c-1"]["tier"] == "vip"

    before_fingerprint = recovery_fingerprint(engine.ledger, incident_id=incident_id)
    approval = approval_for(
        engine,
        incident_id=incident_id,
        resource_key=conflict.resource_key,
        compromised_action_event_id=compromised.action_event.event_id,
        trusted_action_event_id=trusted.action_event.event_id,
        approval_id="reconcile-safe-approval",
    )
    result = engine.reconcile_conflict(
        incident_id=incident_id,
        compromised_action_event_id=compromised.action_event.event_id,
        trusted_action_event_id=trusted.action_event.event_id,
        approval=approval,
    )

    assert result.status is ReconciliationStatus.VERIFIED
    assert result.verification_event is not None
    assert result.verification_event.payload["verification_kind"] == "shared_state_reconciliation"
    assert result.verification_event.payload["verified"] is True
    assert engine.state.crm_contacts["c-1"]["tier"] == "gold"
    assert recovery_fingerprint(engine.ledger, incident_id=incident_id) != before_fingerprint
    authority_events = [
        event
        for event in engine.ledger.events(incident_id=incident_id)
        if event.event_type is EventType.AUTHORITY_CONSUMED
        and event.payload.get("purpose") == "reconciliation"
    ]
    assert len(authority_events) == 1
    assert authority_events[0].payload["resource_key"] == conflict.resource_key


def test_reconciliation_approval_becomes_stale_when_evidence_changes() -> None:
    engine = make_engine()
    incident_id = "reconcile-stale"
    trusted, compromised, conflict = same_field_conflict(engine, incident_id)
    approval = approval_for(
        engine,
        incident_id=incident_id,
        resource_key=conflict.resource_key,
        compromised_action_event_id=compromised.action_event.event_id,
        trusted_action_event_id=trusted.action_event.event_id,
        approval_id="stale-approval",
    )
    engine.ledger.record(
        EventType.CONTAINMENT,
        incident_id,
        {"scope": "agent:support-agent", "reason": "new-evidence", "active": True},
    )

    result = engine.reconcile_conflict(
        incident_id=incident_id,
        compromised_action_event_id=compromised.action_event.event_id,
        trusted_action_event_id=trusted.action_event.event_id,
        approval=approval,
    )

    assert result.status is ReconciliationStatus.BLOCKED
    assert result.reason == "stale_reconciliation_approval"
    assert engine.state.crm_contacts["c-1"]["tier"] == "vip"


def test_reconciliation_approval_is_bound_to_exact_resource_and_action_roles() -> None:
    engine = make_engine()
    incident_id = "reconcile-binding"
    trusted, compromised, conflict = same_field_conflict(engine, incident_id)
    approval = approval_for(
        engine,
        incident_id=incident_id,
        resource_key=f"{conflict.resource_key}:wrong",
        compromised_action_event_id=compromised.action_event.event_id,
        trusted_action_event_id=trusted.action_event.event_id,
        approval_id="wrong-resource",
    )

    result = engine.reconcile_conflict(
        incident_id=incident_id,
        compromised_action_event_id=compromised.action_event.event_id,
        trusted_action_event_id=trusted.action_event.event_id,
        approval=approval,
    )

    assert result.status is ReconciliationStatus.BLOCKED
    assert result.reason == "reconciliation_approval_resource_mismatch"
    assert engine.state.crm_contacts["c-1"]["tier"] == "vip"


def test_reconciliation_approval_is_single_use_even_if_rebound_to_fresh_head() -> None:
    engine = make_engine()
    incident_id = "reconcile-single-use"
    trusted, compromised, conflict = same_field_conflict(engine, incident_id)
    first = approval_for(
        engine,
        incident_id=incident_id,
        resource_key=conflict.resource_key,
        compromised_action_event_id=compromised.action_event.event_id,
        trusted_action_event_id=trusted.action_event.event_id,
        approval_id="one-shot-reconciliation",
    )
    verified = engine.reconcile_conflict(
        incident_id=incident_id,
        compromised_action_event_id=compromised.action_event.event_id,
        trusted_action_event_id=trusted.action_event.event_id,
        approval=first,
    )
    assert verified.status is ReconciliationStatus.VERIFIED

    reused = approval_for(
        engine,
        incident_id=incident_id,
        resource_key=conflict.resource_key,
        compromised_action_event_id=compromised.action_event.event_id,
        trusted_action_event_id=trusted.action_event.event_id,
        approval_id="one-shot-reconciliation",
    )
    blocked = engine.reconcile_conflict(
        incident_id=incident_id,
        compromised_action_event_id=compromised.action_event.event_id,
        trusted_action_event_id=trusted.action_event.event_id,
        approval=reused,
    )

    assert blocked.status is ReconciliationStatus.BLOCKED
    assert blocked.reason == "reconciliation_approval_already_consumed"
    assert engine.state.crm_contacts["c-1"]["tier"] == "gold"


def test_contract_without_reconciliation_path_keeps_same_resource_conflict_fail_closed() -> None:
    engine = make_engine()
    incident_id = "reconcile-unsupported"
    left_root = engine.ledger.record(EventType.EXTERNAL_INPUT, incident_id, {"source": "a"})
    right_root = engine.ledger.record(EventType.EXTERNAL_INPUT, incident_id, {"source": "b"})
    left = engine.execute(
        incident_id=incident_id,
        agent_id="agent-a",
        tool_id="memory.write",
        params={"key": "shared", "value": "a"},
        causal_parent_event_ids=(left_root.event_id,),
    )
    right = engine.execute(
        incident_id=incident_id,
        agent_id="agent-b",
        tool_id="memory.write",
        params={"key": "shared", "value": "b"},
        causal_parent_event_ids=(right_root.event_id,),
    )

    result = engine.reconcile_conflict(
        incident_id=incident_id,
        compromised_action_event_id=right.action_event.event_id,
        trusted_action_event_id=left.action_event.event_id,
        approval=None,
    )

    assert result.status is ReconciliationStatus.BLOCKED
    assert result.reason == "contract_has_no_reconciliation_path"
    assert engine.state.memory["shared"] == "b"
