from __future__ import annotations

import pytest

from agent_recovery.catalog import synthetic_contracts
from agent_recovery.engine import RecoveryEngine, RecoveryStatus
from agent_recovery.graph import IncidentGraph
from agent_recovery.ledger import EventType
from agent_recovery.plans import RecoveryPlanError, build_shared_state_safe_plan
from agent_recovery.simulator import SyntheticEnterprise


def make_engine() -> RecoveryEngine:
    engine = RecoveryEngine(SyntheticEnterprise())
    for contract in synthetic_contracts():
        engine.register(contract)
    return engine


def test_independent_agents_can_recover_different_fields_without_clobbering_peer_state() -> None:
    engine = make_engine()
    root = engine.ledger.record(
        EventType.EXTERNAL_INPUT,
        "shared-1",
        {"source": "poisoned_ticket"},
    )
    compromised = engine.execute(
        incident_id="shared-1",
        agent_id="support-agent",
        tool_id="crm.update_contact",
        params={"contact_id": "c-1", "field": "tier", "value": "vip"},
        causal_parent_event_ids=(root.event_id,),
    )
    legitimate = engine.execute(
        incident_id="shared-1",
        agent_id="billing-agent",
        tool_id="crm.update_contact",
        params={"contact_id": "c-1", "field": "owner", "value": "billing"},
        causal_parent_event_ids=(root.event_id,),
    )

    graph = IncidentGraph.from_ledger(engine.ledger, incident_id="shared-1")
    assert graph.shared_state_conflicts() == ()
    assert compromised.action_event.payload["resource_keys"] == (
        "crm:contact:c-1:field:tier",
    )
    assert legitimate.action_event.payload["resource_keys"] == (
        "crm:contact:c-1:field:owner",
    )

    result = engine.recover(
        incident_id="shared-1",
        action_event_id=compromised.action_event.event_id,
    )
    assert result.status is RecoveryStatus.VERIFIED
    assert engine.state.crm_contacts["c-1"] == {
        "name": "Alex Rivera",
        "tier": "standard",
        "owner": "billing",
    }


def test_cross_agent_same_field_conflict_still_fails_closed() -> None:
    engine = make_engine()
    root = engine.ledger.record(
        EventType.EXTERNAL_INPUT,
        "shared-same-field",
        {"source": "shared_work_item"},
    )
    first = engine.execute(
        incident_id="shared-same-field",
        agent_id="support-agent",
        tool_id="crm.update_contact",
        params={"contact_id": "c-1", "field": "tier", "value": "vip"},
        causal_parent_event_ids=(root.event_id,),
    )
    second = engine.execute(
        incident_id="shared-same-field",
        agent_id="billing-agent",
        tool_id="crm.update_contact",
        params={"contact_id": "c-1", "field": "tier", "value": "blocked"},
        causal_parent_event_ids=(root.event_id,),
    )

    graph = IncidentGraph.from_ledger(engine.ledger, incident_id="shared-same-field")
    conflicts = graph.shared_state_conflicts()
    assert len(conflicts) == 1
    assert conflicts[0].resource_key == "crm:contact:c-1:field:tier"
    assert conflicts[0].cross_agent is True

    with pytest.raises(RecoveryPlanError, match="explicit reconciliation"):
        build_shared_state_safe_plan(
            graph,
            (first.action_event.event_id, second.action_event.event_id),
        )

    result = engine.recover(
        incident_id="shared-same-field",
        action_event_id=first.action_event.event_id,
    )
    assert result.status is RecoveryStatus.FAILED
    assert result.residual_reason == "later_resource_writer_requires_recovery_or_reconciliation"
    assert engine.state.crm_contacts["c-1"]["tier"] == "blocked"


def test_causally_ordered_writes_to_same_field_are_recovered_in_reverse_order() -> None:
    engine = make_engine()
    first = engine.execute(
        incident_id="shared-2",
        agent_id="support-agent",
        tool_id="crm.update_contact",
        params={"contact_id": "c-1", "field": "tier", "value": "vip"},
    )
    second = engine.execute(
        incident_id="shared-2",
        agent_id="billing-agent",
        tool_id="crm.update_contact",
        params={"contact_id": "c-1", "field": "tier", "value": "blocked"},
        causal_parent_event_ids=(first.action_event.event_id,),
    )

    graph = IncidentGraph.from_ledger(engine.ledger, incident_id="shared-2")
    assert graph.shared_state_conflicts() == ()

    plan = build_shared_state_safe_plan(
        graph,
        (first.action_event.event_id, second.action_event.event_id),
    )
    assert [step.action_event_id for step in plan.execution_order()] == [
        second.action_event.event_id,
        first.action_event.event_id,
    ]

    for step in plan.execution_order():
        result = engine.recover(
            incident_id="shared-2",
            action_event_id=step.action_event_id,
        )
        assert result.status is RecoveryStatus.VERIFIED

    assert engine.state.crm_contacts["c-1"] == {
        "name": "Alex Rivera",
        "tier": "standard",
        "owner": "team-a",
    }


def test_independent_agents_can_write_different_resources_without_false_conflict() -> None:
    engine = make_engine()
    root = engine.ledger.record(
        EventType.EXTERNAL_INPUT,
        "shared-3",
        {"source": "shared_work_item"},
    )
    first = engine.execute(
        incident_id="shared-3",
        agent_id="agent-a",
        tool_id="memory.write",
        params={"key": "customer", "value": "c-1"},
        causal_parent_event_ids=(root.event_id,),
    )
    second = engine.execute(
        incident_id="shared-3",
        agent_id="agent-b",
        tool_id="memory.write",
        params={"key": "invoice", "value": "i-9"},
        causal_parent_event_ids=(root.event_id,),
    )

    graph = IncidentGraph.from_ledger(engine.ledger, incident_id="shared-3")
    assert graph.shared_state_conflicts() == ()

    plan = build_shared_state_safe_plan(
        graph,
        (first.action_event.event_id, second.action_event.event_id),
    )
    assert {step.action_event_id for step in plan.steps} == {
        first.action_event.event_id,
        second.action_event.event_id,
    }
