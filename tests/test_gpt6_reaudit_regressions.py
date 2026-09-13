from __future__ import annotations

from dataclasses import replace

import pytest

from agent_recovery.catalog import synthetic_contracts
from agent_recovery.engine import ActionDecision, RecoveryEngine, RecoveryStatus
from agent_recovery.judge_incident_evidence import (
    build_judge_incident_evidence,
    validate_judge_incident_evidence,
)
from agent_recovery.ledger import ActionLedger, EventType, LedgerIntegrityError
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


def execute_source_write(
    engine: RecoveryEngine,
    *,
    incident_id: str,
    trigger_event_id: str | None = None,
    agent_id: str = "support-agent",
    key: str = "instruction",
    value: str = "poison",
):
    parents = (trigger_event_id,) if trigger_event_id else ()
    return engine.execute(
        incident_id=incident_id,
        agent_id=agent_id,
        tool_id="memory.write",
        params={"key": key, "value": value},
        causal_parent_event_ids=parents,
    )


def prepared_recovery(
    incident_id: str = "i",
    *,
    release_scope: str = "agent:downstream",
):
    engine = make_engine()
    trigger = engine.ledger.record(
        EventType.EXTERNAL_INPUT,
        incident_id,
        {"source": "synthetic", "content": "poison"},
    )
    action = execute_source_write(
        engine,
        incident_id=incident_id,
        trigger_event_id=trigger.event_id,
    )
    engine.contain(incident_id, "agent:support-agent", reason="compromised source")
    engine.contain(incident_id, release_scope, reason="dependent authority held")
    recovery = engine.recover(incident_id=incident_id, action_event_id=action.action_event.event_id)
    assert recovery.status is RecoveryStatus.VERIFIED
    return engine, trigger, action


def replay_evidence(
    engine: RecoveryEngine,
    trigger_event_id: str,
    *,
    incident_id: str,
    release_scope: str,
    containment_scopes: tuple[str, ...],
    factory=make_engine,
):
    return ReplayLab(factory).run(
        source_ledger=engine.ledger,
        source_incident_id=incident_id,
        source_trigger_event_id=trigger_event_id,
        replay_id=f"replay-{incident_id}-{engine.ledger.head_hash[:8]}",
        action=ReplayActionSpec(
            agent_id="support-agent",
            tool_id="memory.write",
            params={"key": "instruction", "value": "poison"},
            containment_scopes=containment_scopes,
            release_scope=release_scope,
        ),
    )


def authorize_downstream(engine: RecoveryEngine, trigger_event_id: str, incident_id: str = "i"):
    evidence = replay_evidence(
        engine,
        trigger_event_id,
        incident_id=incident_id,
        release_scope="agent:downstream",
        containment_scopes=("agent:support-agent",),
    )
    replay = record_replay_verification(engine.ledger, incident_id=incident_id, evidence=evidence)
    assert replay.verified is True
    result = RestorationGate(engine.ledger).authorize(
        incident_id=incident_id,
        authority_scope="agent:downstream",
        replay_event_id=replay.event.event_id,
    )
    assert result.decision is RestorationDecision.RESTORED
    return result


def test_replay_only_tool_containment_cannot_justify_source_release() -> None:
    scope = "agent:support-agent"
    engine, trigger, _ = prepared_recovery("source-release", release_scope=scope)
    evidence = replay_evidence(
        engine,
        trigger.event_id,
        incident_id="source-release",
        release_scope=scope,
        containment_scopes=("tool:memory.write",),
    )
    with pytest.raises(ValueError, match="source agent"):
        record_replay_verification(
            engine.ledger,
            incident_id="source-release",
            evidence=evidence,
        )
    assert engine.is_contained(scope) is True


def test_factory_cannot_hide_containment_of_released_scope() -> None:
    scope = "agent:support-agent"
    engine, trigger, _ = prepared_recovery("hidden", release_scope=scope)

    def hidden_factory() -> RecoveryEngine:
        replay_engine = make_engine()
        replay_engine.contain("replay-hidden", scope, reason="preconfigured")
        return replay_engine

    evidence = replay_evidence(
        engine,
        trigger.event_id,
        incident_id="hidden",
        release_scope=scope,
        containment_scopes=(),
        factory=hidden_factory,
    )
    with pytest.raises(ValueError, match="source agent"):
        record_replay_verification(
            engine.ledger,
            incident_id="hidden",
            evidence=evidence,
        )
    assert engine.is_contained(scope) is True


def test_stale_restoration_cannot_be_applied() -> None:
    engine, trigger, _ = prepared_recovery("stale")
    restoration = authorize_downstream(engine, trigger.event_id, "stale")
    execute_source_write(
        engine,
        incident_id="stale",
        agent_id="other-agent",
        key="other",
        value="new-poison",
    )
    with pytest.raises(ValueError):
        engine.release_containment(
            "stale",
            "agent:downstream",
            restoration_event_id=restoration.event.event_id,
        )
    assert engine.is_contained("agent:downstream") is True


def test_restoration_decision_is_single_use() -> None:
    engine, trigger, _ = prepared_recovery("single-use")
    restoration = authorize_downstream(engine, trigger.event_id, "single-use")
    engine.release_containment(
        "single-use",
        "agent:downstream",
        restoration_event_id=restoration.event.event_id,
    )
    engine.contain("single-use", "agent:downstream", reason="renewed hold")
    with pytest.raises(ValueError):
        engine.release_containment(
            "single-use",
            "agent:downstream",
            restoration_event_id=restoration.event.event_id,
        )
    assert engine.is_contained("agent:downstream") is True


def test_containment_reaches_preexisting_shared_ledger_controller() -> None:
    state = SyntheticEnterprise()
    ledger = ActionLedger()
    first = make_engine(state, ledger)
    second = make_engine(state, ledger)
    first.contain("i", "agent:support-agent", reason="compromised")
    result = execute_source_write(second, incident_id="i")
    assert result.decision is ActionDecision.BLOCKED
    assert "instruction" not in state.memory


def test_release_preserves_other_incident_hold() -> None:
    engine, trigger, _ = prepared_recovery("incident-i")
    engine.contain("incident-j", "agent:downstream", reason="independent hold")
    restoration = authorize_downstream(engine, trigger.event_id, "incident-i")
    engine.release_containment(
        "incident-i",
        "agent:downstream",
        restoration_event_id=restoration.event.event_id,
    )
    result = execute_source_write(
        engine,
        incident_id="incident-j",
        agent_id="downstream",
        key="other",
        value="poison",
    )
    assert result.decision is ActionDecision.BLOCKED
    assert engine.is_contained("agent:downstream") is True


def test_semantics_reject_999_recoveries_for_three_action_fixture() -> None:
    evidence = build_judge_incident_evidence()
    evidence["phases"]["recovery"]["verified_recoveries"] = 999
    evidence["measured_score"]["verified_recoveries"] = 999
    with pytest.raises(ValueError):
        validate_judge_incident_evidence(evidence)


def test_direct_recovery_exception_has_residual_evidence() -> None:
    engine = make_engine()
    contract = engine._contracts["memory.write"]

    def fail(state, params):
        raise ValueError("adapter unavailable")

    engine.register(replace(contract, recovery_executor=fail))
    action = execute_source_write(engine, incident_id="direct-failure")
    with pytest.raises(ValueError, match="adapter unavailable"):
        engine.recover(
            incident_id="direct-failure",
            action_event_id=action.action_event.event_id,
        )
    events = engine.ledger.events(incident_id="direct-failure")
    assert any(event.event_type is EventType.RECOVERY_FAILED for event in events)
    assert any(event.event_type is EventType.RESIDUAL_EFFECT for event in events)


def test_restoration_requires_an_actual_active_hold() -> None:
    incident_id = "never-contained"
    engine = make_engine()
    trigger = engine.ledger.record(EventType.EXTERNAL_INPUT, incident_id, {"source": "synthetic"})
    action = execute_source_write(
        engine,
        incident_id=incident_id,
        trigger_event_id=trigger.event_id,
    )
    engine.contain(incident_id, "agent:support-agent", reason="compromised source")
    assert engine.recover(
        incident_id=incident_id,
        action_event_id=action.action_event.event_id,
    ).status is RecoveryStatus.VERIFIED
    evidence = replay_evidence(
        engine,
        trigger.event_id,
        incident_id=incident_id,
        release_scope="agent:downstream",
        containment_scopes=("agent:support-agent",),
    )
    replay = record_replay_verification(engine.ledger, incident_id=incident_id, evidence=evidence)
    result = RestorationGate(engine.ledger).authorize(
        incident_id=incident_id,
        authority_scope="agent:downstream",
        replay_event_id=replay.event.event_id,
    )
    assert result.decision is RestorationDecision.BLOCKED
    assert result.reason == "scope_not_actively_contained"


def test_non_restoring_compensator_cannot_define_its_own_success_target() -> None:
    engine = make_engine()
    contract = engine._contracts["memory.write"]
    engine.register(
        replace(
            contract,
            recovery_executor=lambda state, params: {
                "after": state.memory.get(params["key"]),
            },
        )
    )
    action = execute_source_write(engine, incident_id="independent-target")
    result = engine.recover(
        incident_id="independent-target",
        action_event_id=action.action_event.event_id,
    )
    assert result.status is RecoveryStatus.FAILED
    assert engine.state.memory["instruction"] == "poison"


def test_malicious_builder_and_noop_executor_cannot_forge_restoration() -> None:
    engine = make_engine()
    contract = engine._contracts["memory.write"]
    engine.register(
        replace(
            contract,
            recovery_params_builder=lambda execution_result, observed_after, original_params: {
                "key": original_params["key"],
                "previous": observed_after,
                "expected_state": observed_after,
            },
            recovery_executor=lambda state, params: {"after": params["expected_state"]},
        )
    )
    action = execute_source_write(engine, incident_id="forged-recovery-target")
    result = engine.recover(
        incident_id="forged-recovery-target",
        action_event_id=action.action_event.event_id,
    )
    assert result.status is RecoveryStatus.FAILED
    assert engine.state.memory["instruction"] == "poison"
    assert result.verification_event is not None
    assert result.verification_event.payload["verified"] is False
    assert result.verification_event.payload["expected"] is None
    assert result.verification_event.payload["observed"] == "poison"
    assert result.residual_reason == "recovery_verification_mismatch"
    events = engine.ledger.events(incident_id="forged-recovery-target")
    assert any(
        event.event_type is EventType.RECOVERY_FAILED
        and event.payload["reason"] == "recovery_verification_mismatch"
        for event in events
    )
    assert any(
        event.event_type is EventType.RESIDUAL_EFFECT
        and event.payload["reason"] == "recovery_verification_mismatch"
        for event in events
    )
    assert not any(
        event.event_type is EventType.VERIFICATION and event.payload["verified"] is True
        for event in events
    )


def test_cached_recovery_still_checks_ledger_integrity() -> None:
    engine = make_engine()
    action = execute_source_write(engine, incident_id="cached-integrity")
    first = engine.recover(
        incident_id="cached-integrity",
        action_event_id=action.action_event.event_id,
    )
    assert first.status is RecoveryStatus.VERIFIED

    for index, event in enumerate(engine.ledger._events):
        if event.event_id == action.action_event.event_id:
            engine.ledger._events[index] = replace(
                event,
                payload={**event.payload, "corrupt": True},
            )
            break

    with pytest.raises(LedgerIntegrityError):
        engine.recover(
            incident_id="cached-integrity",
            action_event_id=action.action_event.event_id,
        )
