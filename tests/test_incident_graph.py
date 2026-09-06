from __future__ import annotations

import pytest

from agent_recovery.catalog import synthetic_contracts
from agent_recovery.engine import RecoveryEngine, RecoveryStatus
from agent_recovery.graph import IncidentGraph
from agent_recovery.ledger import EventType
from agent_recovery.plans import (
    RecoveryPlan,
    RecoveryPlanError,
    RecoveryPlanStep,
    build_reverse_causal_plan,
)
from agent_recovery.simulator import SyntheticEnterprise


def make_engine() -> RecoveryEngine:
    engine = RecoveryEngine(SyntheticEnterprise())
    for contract in synthetic_contracts():
        engine.register(contract)
    return engine


def test_causal_graph_tracks_external_root_across_multiple_actions() -> None:
    engine = make_engine()
    root = engine.ledger.record(
        EventType.EXTERNAL_INPUT,
        "graph-1",
        {"source": "synthetic_external_ticket"},
    )
    first = engine.execute(
        incident_id="graph-1",
        agent_id="agent-1",
        tool_id="memory.write",
        params={"key": "task_hint", "value": "poisoned"},
        causal_parent_event_ids=(root.event_id,),
    )
    second = engine.execute(
        incident_id="graph-1",
        agent_id="agent-1",
        tool_id="crm.update_contact",
        params={"contact_id": "c-1", "field": "tier", "value": "vip"},
        causal_parent_event_ids=(first.action_event.event_id,),
    )

    graph = IncidentGraph.from_ledger(engine.ledger, incident_id="graph-1")
    radius = graph.blast_radius(root.event_id)

    assert first.action_event.event_id in radius.executed_action_event_ids
    assert second.action_event.event_id in radius.executed_action_event_ids
    assert graph.is_ancestor(first.action_event.event_id, second.action_event.event_id)


def test_reverse_causal_plan_recovers_downstream_before_upstream() -> None:
    engine = make_engine()
    first = engine.execute(
        incident_id="graph-2",
        agent_id="agent-1",
        tool_id="memory.write",
        params={"key": "task_hint", "value": "poisoned"},
    )
    second = engine.execute(
        incident_id="graph-2",
        agent_id="agent-1",
        tool_id="crm.update_contact",
        params={"contact_id": "c-1", "field": "tier", "value": "vip"},
        causal_parent_event_ids=(first.action_event.event_id,),
    )
    graph = IncidentGraph.from_ledger(engine.ledger, incident_id="graph-2")
    plan = build_reverse_causal_plan(
        graph,
        (first.action_event.event_id, second.action_event.event_id),
    )

    ordered = plan.execution_order()
    assert [step.action_event_id for step in ordered] == [
        second.action_event.event_id,
        first.action_event.event_id,
    ]

    results = [
        engine.recover(incident_id="graph-2", action_event_id=step.action_event_id)
        for step in ordered
    ]
    assert all(result.status is RecoveryStatus.VERIFIED for result in results)
    assert "task_hint" not in engine.state.memory
    assert engine.state.crm_contacts["c-1"]["tier"] == "standard"


def test_verified_recovery_is_idempotent() -> None:
    engine = make_engine()
    action = engine.execute(
        incident_id="graph-3",
        agent_id="agent-1",
        tool_id="crm.update_contact",
        params={"contact_id": "c-1", "field": "tier", "value": "vip"},
    )

    first = engine.recover(
        incident_id="graph-3",
        action_event_id=action.action_event.event_id,
    )
    event_count = len(engine.ledger.events(incident_id="graph-3"))
    second = engine.recover(
        incident_id="graph-3",
        action_event_id=action.action_event.event_id,
    )

    assert first is second
    assert len(engine.ledger.events(incident_id="graph-3")) == event_count
    assert engine.state.crm_contacts["c-1"]["tier"] == "standard"


def test_recovery_plan_rejects_cycles() -> None:
    with pytest.raises(RecoveryPlanError, match="dependency cycle"):
        RecoveryPlan(
            steps=(
                RecoveryPlanStep("a", depends_on=("b",), idempotency_key="recover:a"),
                RecoveryPlanStep("b", depends_on=("a",), idempotency_key="recover:b"),
            )
        )


def test_recovery_plan_requires_idempotency_key() -> None:
    with pytest.raises(RecoveryPlanError, match="idempotency key"):
        RecoveryPlan(steps=(RecoveryPlanStep("a"),))


def test_causal_parent_must_exist_in_ledger() -> None:
    engine = make_engine()
    with pytest.raises(ValueError, match="missing parent event"):
        engine.execute(
            incident_id="graph-4",
            agent_id="agent-1",
            tool_id="memory.write",
            params={"key": "x", "value": "y"},
            causal_parent_event_ids=("missing-event",),
        )
