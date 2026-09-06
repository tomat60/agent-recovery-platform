from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .catalog import synthetic_contracts
from .contracts import RecoveryClass, RecoveryContract, RiskLevel
from .engine import RecoveryEngine
from .graph import IncidentGraph
from .ledger import EventType
from .plans import build_reverse_causal_plan
from .recovery_workflow import execute_recovery_plan
from .simulator import SyntheticEnterprise


@dataclass(frozen=True)
class PartialFailureScore:
    scenario: str
    planned_steps: int
    verified_recoveries: int
    failed_recoveries: int
    dependency_blocked_recoveries: int
    explicit_residual_effects: int
    unsafe_recovery_executions: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_partial_compensation_failure_scenario() -> PartialFailureScore:
    incident_id = "bench-partial-compensation"
    engine = RecoveryEngine(SyntheticEnterprise())
    for contract in synthetic_contracts():
        engine.register(contract)
    engine.register(_flaky_memory_contract())

    root = engine.execute(
        incident_id=incident_id,
        agent_id="support-agent",
        tool_id="memory.write",
        params={"key": "root", "value": "poisoned"},
    )
    middle = engine.execute(
        incident_id=incident_id,
        agent_id="workflow-agent",
        tool_id="memory.write_flaky_recovery",
        params={"key": "middle", "value": "poisoned"},
        causal_parent_event_ids=(root.action_event.event_id,),
    )
    leaf = engine.execute(
        incident_id=incident_id,
        agent_id="crm-agent",
        tool_id="memory.write",
        params={"key": "leaf", "value": "poisoned"},
        causal_parent_event_ids=(middle.action_event.event_id,),
    )

    graph = IncidentGraph.from_ledger(engine.ledger, incident_id=incident_id)
    plan = build_reverse_causal_plan(
        graph,
        (
            root.action_event.event_id,
            middle.action_event.event_id,
            leaf.action_event.event_id,
        ),
        plan_id="bench-partial-compensation-plan",
    )
    execution = execute_recovery_plan(engine, incident_id=incident_id, plan=plan)

    residual_events = tuple(
        event
        for event in engine.ledger.events(incident_id=incident_id)
        if event.event_type is EventType.RESIDUAL_EFFECT
    )
    return PartialFailureScore(
        scenario="partial_compensating_workflow_failure",
        planned_steps=len(plan.steps),
        verified_recoveries=len(execution.verified_action_ids),
        failed_recoveries=len(execution.failed_action_ids),
        dependency_blocked_recoveries=len(execution.blocked_action_ids),
        explicit_residual_effects=len(residual_events),
        unsafe_recovery_executions=execution.unsafe_recovery_executions,
    )


def _flaky_memory_contract() -> RecoveryContract:
    return RecoveryContract(
        tool_id="memory.write_flaky_recovery",
        action_type="memory_write",
        risk_level=RiskLevel.MEDIUM,
        recovery_class=RecoveryClass.COMPENSATABLE,
        executor=lambda state, params: _enterprise(state).write_memory(params),
        verifier=lambda state, params: _enterprise(state).get_memory(params),
        recovery_executor=_fail_compensation,
        recovery_params_builder=lambda execution_result, observed_after, original_params: {
            "key": original_params["key"],
            "previous": execution_result.get("before") if isinstance(execution_result, dict) else None,
        },
        resource_key_builder=lambda params: (f"memory:key:{params['key']}",),
        containment_scopes=("tool", "agent", "memory"),
    )


def _fail_compensation(state: object, params: object) -> object:
    _enterprise(state)
    raise RuntimeError("synthetic compensation dependency unavailable")


def _enterprise(state: object) -> SyntheticEnterprise:
    if not isinstance(state, SyntheticEnterprise):
        raise TypeError("partial-failure benchmark requires SyntheticEnterprise")
    return state
