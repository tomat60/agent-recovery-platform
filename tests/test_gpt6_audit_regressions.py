from __future__ import annotations

from dataclasses import replace

import pytest

from agent_recovery.catalog import synthetic_contracts
from agent_recovery.contracts import ContractError, RecoveryContract, RiskLevel
from agent_recovery.engine import ActionDecision, Approval, RecoveryEngine, RecoveryStatus
from agent_recovery.graph import IncidentGraph
from agent_recovery.investigation import build_evidence_view
from agent_recovery.judge_incident_evidence import (
    build_judge_incident_evidence,
    validate_judge_incident_evidence,
)
from agent_recovery.ledger import ActionLedger, EventType
from agent_recovery.plans import RecoveryPlan, RecoveryPlanStep
from agent_recovery.recovery_workflow import execute_recovery_plan
from agent_recovery.replay import ReplayActionSpec, ReplayLab
from agent_recovery.restoration import (
    RestorationDecision,
    RestorationGate,
    record_replay_verification,
)
from agent_recovery.simulator import SyntheticEnterprise


def make_engine(
    state: SyntheticEnterprise | None = None,
    ledger: ActionLedger | None = None,
) -> RecoveryEngine:
    engine = RecoveryEngine(state if state is not None else SyntheticEnterprise(), ledger=ledger)
    for contract in synthetic_contracts():
        engine.register(contract)
    return engine


def prepared_recovery(incident_id: str = "audit"):
    engine = make_engine()
    scope = "agent:source"
    trigger = engine.ledger.record(
        EventType.EXTERNAL_INPUT,
        incident_id,
        {"source": "synthetic", "content": "poison"},
    )
    params = {"key": "instruction", "value": "poison"}
    action = engine.execute(
        incident_id=incident_id,
        agent_id="source",
        tool_id="memory.write",
        params=params,
        causal_parent_event_ids=(trigger.event_id,),
    )
    engine.contain(incident_id, scope, reason="compromised")
    recovery = engine.recover(
        incident_id=incident_id,
        action_event_id=action.action_event.event_id,
    )
    assert recovery.status is RecoveryStatus.VERIFIED
    return engine, trigger, action, params, scope


def replay_for(
    engine: RecoveryEngine,
    trigger_event_id: str,
    params: dict[str, object],
    scope: str,
    *,
    contained: bool = True,
    tool_id: str = "memory.write",
):
    return ReplayLab(make_engine).run(
        source_ledger=engine.ledger,
        source_incident_id=engine.ledger.get(trigger_event_id).incident_id,
        source_trigger_event_id=trigger_event_id,
        replay_id=f"replay-{engine.ledger.head_hash[:10]}",
        action=ReplayActionSpec(
            agent_id="source",
            tool_id=tool_id,
            params=params,
            containment_scopes=("agent:source",) if contained else (),
            release_scope=scope,
        ),
    )


def test_containment_survives_engine_reconstruction() -> None:
    state = SyntheticEnterprise()
    first = make_engine(state)
    first.contain("i", "agent:source", reason="compromised")
    blocked = first.execute(
        incident_id="i",
        agent_id="source",
        tool_id="memory.write",
        params={"key": "x", "value": "bad"},
    )
    assert blocked.decision is ActionDecision.BLOCKED

    recreated = make_engine(state, first.ledger)
    still_blocked = recreated.execute(
        incident_id="i",
        agent_id="source",
        tool_id="memory.write",
        params={"key": "x", "value": "bad"},
    )
    assert recreated.is_contained("agent:source") is True
    assert still_blocked.decision is ActionDecision.BLOCKED
    assert "x" not in state.memory


def test_preexisting_engines_consume_one_approval_at_most_once() -> None:
    state = SyntheticEnterprise()
    ledger = ActionLedger()
    first = make_engine(state, ledger)
    second = make_engine(state, ledger)
    params = {"channel": "customer", "body": "send once", "observed": True}
    approval = Approval.for_action("comms.send_message", params, "one-shot")

    a = first.execute(
        incident_id="i",
        agent_id="source",
        tool_id="comms.send_message",
        params=params,
        approval=approval,
    )
    b = second.execute(
        incident_id="i",
        agent_id="source",
        tool_id="comms.send_message",
        params=params,
        approval=approval,
    )
    assert [a.decision, b.decision] == [ActionDecision.EXECUTED, ActionDecision.BLOCKED]
    assert len(state.messages) == 1


def test_wrong_tool_replay_cannot_be_used_as_attack_proof() -> None:
    engine, trigger, _, params, scope = prepared_recovery("wrong-tool")
    with pytest.raises(ValueError, match="exactly one matching source action"):
        replay_for(engine, trigger.event_id, params, scope, tool_id="nonexistent.tool")


def test_replay_proof_cannot_be_restamped_after_source_state_changes() -> None:
    engine, trigger, _, params, scope = prepared_recovery("restamp")
    evidence = replay_for(engine, trigger.event_id, params, scope)
    engine.ledger.record(
        EventType.RECOVERY_PLANNED,
        "restamp",
        {"plan_id": "later-change"},
        parent_event_ids=(trigger.event_id,),
    )
    with pytest.raises(ValueError, match="stale or has already been consumed"):
        record_replay_verification(engine.ledger, incident_id="restamp", evidence=evidence)


def test_later_failed_replay_supersedes_earlier_success() -> None:
    engine, trigger, _, params, scope = prepared_recovery("supersede")
    good = record_replay_verification(
        engine.ledger,
        incident_id="supersede",
        evidence=replay_for(engine, trigger.event_id, params, scope),
    )
    bad = record_replay_verification(
        engine.ledger,
        incident_id="supersede",
        evidence=replay_for(engine, trigger.event_id, params, scope, contained=False),
    )
    assert good.verified is True
    assert bad.verified is False

    result = RestorationGate(engine.ledger).authorize(
        incident_id="supersede",
        authority_scope=scope,
        replay_event_id=good.event.event_id,
    )
    assert result.decision is RestorationDecision.BLOCKED
    assert result.reason == "replay_evidence_superseded"


def test_cross_incident_writer_is_not_clobbered_by_recovery() -> None:
    engine = make_engine()
    first = engine.execute(
        incident_id="incident-a",
        agent_id="source",
        tool_id="memory.write",
        params={"key": "shared", "value": "bad"},
    )
    engine.execute(
        incident_id="workflow-b",
        agent_id="benign",
        tool_id="memory.write",
        params={"key": "shared", "value": "legitimate"},
    )

    result = engine.recover(
        incident_id="incident-a",
        action_event_id=first.action_event.event_id,
    )
    assert result.status is RecoveryStatus.FAILED
    assert engine.state.memory["shared"] == "legitimate"


def test_upstream_recovery_blocks_until_causal_descendant_is_recovered() -> None:
    engine = make_engine()
    first = engine.execute(
        incident_id="deps",
        agent_id="a",
        tool_id="memory.write",
        params={"key": "instruction", "value": "poison-a"},
    )
    second = engine.execute(
        incident_id="deps",
        agent_id="b",
        tool_id="memory.write",
        params={"key": "instruction", "value": "poison-b"},
        causal_parent_event_ids=(first.action_event.event_id,),
    )

    blocked = engine.recover(incident_id="deps", action_event_id=first.action_event.event_id)
    assert blocked.status is RecoveryStatus.FAILED
    assert engine.state.memory["instruction"] == "poison-b"

    assert engine.recover(
        incident_id="deps",
        action_event_id=second.action_event.event_id,
    ).status is RecoveryStatus.VERIFIED
    assert engine.recover(
        incident_id="deps",
        action_event_id=first.action_event.event_id,
    ).status is RecoveryStatus.VERIFIED
    assert "instruction" not in engine.state.memory


def test_malformed_recovery_class_is_rejected_before_external_effect() -> None:
    state = SyntheticEnterprise()
    engine = RecoveryEngine(state)
    malformed = RecoveryContract(
        tool_id="bad.publish",
        action_type="publish",
        risk_level=RiskLevel.HIGH,
        recovery_class="irreversible",  # type: ignore[arg-type]
        executor=lambda s, p: s.send_message(p),
        verifier=lambda s, p: s.messages[-1],
        approval_before_action=False,
    )
    with pytest.raises(ContractError, match="recovery_class"):
        engine.register(malformed)
    assert state.messages == []


def test_recovery_preserves_permission_that_predated_noop_grant() -> None:
    engine = make_engine()
    before = sorted(engine.state.permissions["agent-1"])
    params = {"principal": "agent-1", "permission": "crm:read"}
    action = engine.execute(
        incident_id="permission",
        agent_id="source",
        tool_id="identity.grant_permission",
        params=params,
        approval=Approval.for_action("identity.grant_permission", params, "allow"),
    )
    result = engine.recover(
        incident_id="permission",
        action_event_id=action.action_event.event_id,
    )
    assert result.status is RecoveryStatus.VERIFIED
    assert sorted(engine.state.permissions["agent-1"]) == before


def test_original_action_approval_cannot_authorize_recovery() -> None:
    engine = make_engine()
    contract = next(c for c in synthetic_contracts() if c.tool_id == "memory.write")
    guarded = replace(contract, approval_before_action=True, approval_before_recovery=True)
    engine.register(guarded)
    params = {"key": "instruction", "value": "new"}
    action = engine.execute(
        incident_id="approval-purpose",
        agent_id="source",
        tool_id="memory.write",
        params=params,
        approval=Approval.for_action("memory.write", params, "action-approval"),
    )
    wrong = Approval.for_action("memory.write", params, "wrong-purpose")
    failed = engine.recover(
        incident_id="approval-purpose",
        action_event_id=action.action_event.event_id,
        approval=wrong,
    )
    assert failed.status is RecoveryStatus.FAILED
    assert failed.recovery_event.payload["reason"] == "missing_or_mismatched_recovery_approval"

    recovery_params = {"key": "instruction", "previous": None, "expected_state": None}
    exact = Approval.for_recovery(
        "memory.write",
        recovery_params,
        "recovery-approval",
        incident_id="approval-purpose",
        source_action_event_id=action.action_event.event_id,
        recovery_generation=0,
        contract_version=guarded.contract_version,
    )
    verified = engine.recover(
        incident_id="approval-purpose",
        action_event_id=action.action_event.event_id,
        approval=exact,
    )
    assert verified.status is RecoveryStatus.VERIFIED


def test_prompt_evidence_mutation_does_not_alias_ledger_or_recovery_inputs() -> None:
    engine = make_engine()
    engine.state.memory["instruction"] = "trusted-before"
    action = engine.execute(
        incident_id="evidence-copy",
        agent_id="source",
        tool_id="memory.write",
        params={"key": "instruction", "value": "poison"},
    )
    view = build_evidence_view(engine.ledger, incident_id="evidence-copy")
    payload = view.as_prompt_payload()
    exported = next(
        event for event in payload["events"] if event["event_type"] == "action_executed"
    )
    exported["payload"]["execution_result"]["before"] = "forged-before"

    assert engine.ledger.verify_integrity() is True
    preserved = engine.ledger.get(action.action_event.event_id)
    assert preserved.payload["execution_result"]["before"] == "trusted-before"
    result = engine.recover(
        incident_id="evidence-copy",
        action_event_id=action.action_event.event_id,
    )
    assert result.status is RecoveryStatus.VERIFIED
    assert engine.state.memory["instruction"] == "trusted-before"


def test_verifier_failure_after_effect_is_visible_as_uncertain_residual() -> None:
    engine = make_engine()

    def unavailable(state, params):
        raise RuntimeError("synthetic verifier unavailable")

    contract = next(c for c in synthetic_contracts() if c.tool_id == "memory.write")
    engine.register(replace(contract, verifier=unavailable))
    trigger = engine.ledger.record(EventType.EXTERNAL_INPUT, "observe-failure", {"source": "x"})
    with pytest.raises(RuntimeError, match="verifier unavailable"):
        engine.execute(
            incident_id="observe-failure",
            agent_id="source",
            tool_id="memory.write",
            params={"key": "instruction", "value": "poison"},
            causal_parent_event_ids=(trigger.event_id,),
        )

    graph = IncidentGraph.from_ledger(engine.ledger, incident_id="observe-failure")
    assert engine.state.memory["instruction"] == "poison"
    assert len(graph.blast_radius(trigger.event_id).executed_action_event_ids) == 1
    residuals = [
        event
        for event in engine.ledger.events(incident_id="observe-failure")
        if event.event_type is EventType.RESIDUAL_EFFECT
    ]
    assert len(residuals) == 1


def test_non_runtime_compensation_failure_records_residual() -> None:
    engine = make_engine()

    def unavailable(state, params):
        raise ValueError("synthetic adapter failure")

    contract = next(c for c in synthetic_contracts() if c.tool_id == "memory.write")
    engine.register(replace(contract, recovery_executor=unavailable))
    action = engine.execute(
        incident_id="compensation-failure",
        agent_id="source",
        tool_id="memory.write",
        params={"key": "instruction", "value": "poison"},
    )
    plan = RecoveryPlan(
        (RecoveryPlanStep(action.action_event.event_id, idempotency_key="recover:test"),)
    )
    execution = execute_recovery_plan(engine, incident_id="compensation-failure", plan=plan)
    assert execution.failed_action_ids == (action.action_event.event_id,)
    assert len(execution.residual_event_ids) == 1
    assert engine.state.memory["instruction"] == "poison"


def test_cached_success_cannot_be_rebound_to_another_incident() -> None:
    engine = make_engine()
    action = engine.execute(
        incident_id="cache-a",
        agent_id="source",
        tool_id="memory.write",
        params={"key": "x", "value": "bad"},
    )
    assert engine.recover(
        incident_id="cache-a",
        action_event_id=action.action_event.event_id,
    ).status is RecoveryStatus.VERIFIED
    foreign = engine.recover(
        incident_id="cache-b",
        action_event_id=action.action_event.event_id,
    )
    assert foreign.status is RecoveryStatus.FAILED
    assert foreign.recovery_event.payload["reason"] == "incident_mismatch"


def test_judge_validator_rejects_impossible_semantic_claims() -> None:
    data = build_judge_incident_evidence()
    data["phases"]["restoration"]["root_authority_restored"] = True  # type: ignore[index]
    with pytest.raises(ValueError, match="root authority"):
        validate_judge_incident_evidence(data)

    data = build_judge_incident_evidence()
    data["phases"]["recovery"]["verified_recoveries"] = -999  # type: ignore[index]
    with pytest.raises(ValueError, match="non-negative"):
        validate_judge_incident_evidence(data)
