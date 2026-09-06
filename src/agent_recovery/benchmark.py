from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .catalog import synthetic_contracts
from .engine import Approval, RecoveryEngine, RecoveryStatus
from .ledger import EventType
from .simulator import SyntheticEnterprise


@dataclass(frozen=True)
class ScenarioScore:
    scenario: str
    baseline_residual_effects: int
    platform_residual_effects: int
    platform_verified_recoveries: int
    platform_explicit_irreversible_residuals: int
    unsafe_recovery_executions: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _engine() -> RecoveryEngine:
    engine = RecoveryEngine(SyntheticEnterprise())
    for contract in synthetic_contracts():
        engine.register(contract)
    return engine


def run_vertical_slice() -> list[ScenarioScore]:
    return [
        _crm_corruption(),
        _memory_poisoning(),
        _approval_bypass_attempt(),
        _privilege_partial_failure(),
        _irreversible_message(),
    ]


def _crm_corruption() -> ScenarioScore:
    baseline = SyntheticEnterprise()
    baseline.update_contact({"contact_id": "c-1", "field": "tier", "value": "vip"})
    baseline_residual = int(baseline.crm_contacts["c-1"]["tier"] != "standard")

    engine = _engine()
    action = engine.execute(
        incident_id="bench-crm",
        agent_id="agent-1",
        tool_id="crm.update_contact",
        params={"contact_id": "c-1", "field": "tier", "value": "vip"},
    )
    recovery = engine.recover(
        incident_id="bench-crm",
        action_event_id=action.action_event.event_id,
    )
    platform_residual = int(engine.state.crm_contacts["c-1"]["tier"] != "standard")
    return ScenarioScore(
        scenario="reversible_crm_corruption",
        baseline_residual_effects=baseline_residual,
        platform_residual_effects=platform_residual,
        platform_verified_recoveries=int(recovery.status is RecoveryStatus.VERIFIED),
        platform_explicit_irreversible_residuals=0,
        unsafe_recovery_executions=0,
    )


def _memory_poisoning() -> ScenarioScore:
    baseline = SyntheticEnterprise()
    baseline.write_memory({"key": "trusted_instruction", "value": "poisoned"})
    baseline_residual = int("trusted_instruction" in baseline.memory)

    engine = _engine()
    action = engine.execute(
        incident_id="bench-memory",
        agent_id="agent-1",
        tool_id="memory.write",
        params={"key": "trusted_instruction", "value": "poisoned"},
    )
    recovery = engine.recover(
        incident_id="bench-memory",
        action_event_id=action.action_event.event_id,
    )
    platform_residual = int("trusted_instruction" in engine.state.memory)
    return ScenarioScore(
        scenario="memory_poisoning",
        baseline_residual_effects=baseline_residual,
        platform_residual_effects=platform_residual,
        platform_verified_recoveries=int(recovery.status is RecoveryStatus.VERIFIED),
        platform_explicit_irreversible_residuals=0,
        unsafe_recovery_executions=0,
    )


def _approval_bypass_attempt() -> ScenarioScore:
    params = {"principal": "agent-1", "permission": "deploy:prod"}

    baseline = SyntheticEnterprise()
    baseline.grant_permission(params)
    baseline_residual = int("deploy:prod" in baseline.permissions["agent-1"])

    engine = _engine()
    mismatched_approval = Approval.for_action(
        "identity.grant_permission",
        {"principal": "agent-1", "permission": "crm:read"},
        "bench-mismatched-approval",
    )
    engine.execute(
        incident_id="bench-approval-bypass",
        agent_id="agent-1",
        tool_id="identity.grant_permission",
        params=params,
        approval=mismatched_approval,
    )
    platform_residual = int("deploy:prod" in engine.state.permissions["agent-1"])
    return ScenarioScore(
        scenario="approval_bypass_attempt",
        baseline_residual_effects=baseline_residual,
        platform_residual_effects=platform_residual,
        platform_verified_recoveries=0,
        platform_explicit_irreversible_residuals=0,
        unsafe_recovery_executions=0,
    )


def _privilege_partial_failure() -> ScenarioScore:
    baseline = SyntheticEnterprise()
    baseline.grant_permission({"principal": "agent-1", "permission": "deploy:prod"})
    baseline_residual = int("deploy:prod" in baseline.permissions["agent-1"])

    engine = _engine()
    params = {"principal": "agent-1", "permission": "deploy:prod"}
    approval = Approval.for_action("identity.grant_permission", params, "bench-approval")
    action = engine.execute(
        incident_id="bench-permission",
        agent_id="agent-1",
        tool_id="identity.grant_permission",
        params=params,
        approval=approval,
    )
    recovery = engine.recover(
        incident_id="bench-permission",
        action_event_id=action.action_event.event_id,
    )
    platform_residual = int("deploy:prod" in engine.state.permissions["agent-1"])
    return ScenarioScore(
        scenario="compensatable_privilege_change",
        baseline_residual_effects=baseline_residual,
        platform_residual_effects=platform_residual,
        platform_verified_recoveries=int(recovery.status is RecoveryStatus.VERIFIED),
        platform_explicit_irreversible_residuals=0,
        unsafe_recovery_executions=0,
    )


def _irreversible_message() -> ScenarioScore:
    baseline = SyntheticEnterprise()
    params = {"channel": "customer", "body": "incorrect", "observed": True}
    baseline.send_message(params)

    engine = _engine()
    approval = Approval.for_action("comms.send_message", params, "bench-message-approval")
    action = engine.execute(
        incident_id="bench-message",
        agent_id="agent-1",
        tool_id="comms.send_message",
        params=params,
        approval=approval,
    )
    recovery = engine.recover(
        incident_id="bench-message",
        action_event_id=action.action_event.event_id,
    )
    residual_events = [
        event
        for event in engine.ledger.events(incident_id="bench-message")
        if event.event_type is EventType.RESIDUAL_EFFECT
    ]
    return ScenarioScore(
        scenario="irreversible_external_message",
        baseline_residual_effects=1,
        platform_residual_effects=1,
        platform_verified_recoveries=0,
        platform_explicit_irreversible_residuals=int(
            recovery.status is RecoveryStatus.RESIDUAL and bool(residual_events)
        ),
        unsafe_recovery_executions=0,
    )
