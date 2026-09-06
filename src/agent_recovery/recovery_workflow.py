from __future__ import annotations

from dataclasses import dataclass

from .engine import RecoveryEngine, RecoveryStatus
from .ledger import EventType
from .plans import RecoveryPlan


@dataclass(frozen=True)
class RecoveryPlanExecution:
    verified_action_ids: tuple[str, ...]
    failed_action_ids: tuple[str, ...]
    blocked_action_ids: tuple[str, ...]
    residual_event_ids: tuple[str, ...]
    unsafe_recovery_executions: int = 0

    @property
    def complete(self) -> bool:
        return not self.failed_action_ids and not self.blocked_action_ids


def execute_recovery_plan(
    engine: RecoveryEngine,
    *,
    incident_id: str,
    plan: RecoveryPlan,
) -> RecoveryPlanExecution:
    """Execute a deterministic recovery plan without hiding partial compensation failure.

    A failed compensation is evidence, not an exception that may erase the remaining plan
    state. Downstream failure blocks any step that depends on it. Every failed or blocked
    action is left visible as an explicit residual effect so callers cannot mistake partial
    recovery for verified restoration.
    """

    verified: list[str] = []
    failed: list[str] = []
    blocked: list[str] = []
    residuals: list[str] = []
    unavailable: set[str] = set()

    for step in plan.execution_order():
        blocking_dependencies = tuple(
            dependency for dependency in step.depends_on if dependency in unavailable
        )
        if blocking_dependencies:
            failure = engine.ledger.record(
                EventType.RECOVERY_FAILED,
                incident_id,
                {
                    "action_event_id": step.action_event_id,
                    "reason": "recovery_dependency_not_verified",
                    "blocking_action_event_ids": blocking_dependencies,
                    "plan_id": plan.plan_id,
                },
                parent_event_ids=(step.action_event_id, *blocking_dependencies),
            )
            residual = engine.ledger.record(
                EventType.RESIDUAL_EFFECT,
                incident_id,
                {
                    "action_event_id": step.action_event_id,
                    "reason": "recovery_dependency_not_verified",
                    "recovery_failure_event_id": failure.event_id,
                    "plan_id": plan.plan_id,
                },
                parent_event_ids=(failure.event_id,),
            )
            blocked.append(step.action_event_id)
            unavailable.add(step.action_event_id)
            residuals.append(residual.event_id)
            continue

        try:
            result = engine.recover(
                incident_id=incident_id,
                action_event_id=step.action_event_id,
            )
        except (RuntimeError, TypeError, ValueError) as exc:
            failure = engine.ledger.record(
                EventType.RECOVERY_FAILED,
                incident_id,
                {
                    "action_event_id": step.action_event_id,
                    "reason": "recovery_executor_exception",
                    "error_type": type(exc).__name__,
                    "plan_id": plan.plan_id,
                },
                parent_event_ids=(step.action_event_id,),
            )
            residual = engine.ledger.record(
                EventType.RESIDUAL_EFFECT,
                incident_id,
                {
                    "action_event_id": step.action_event_id,
                    "reason": "recovery_executor_exception",
                    "recovery_failure_event_id": failure.event_id,
                    "plan_id": plan.plan_id,
                },
                parent_event_ids=(failure.event_id,),
            )
            failed.append(step.action_event_id)
            unavailable.add(step.action_event_id)
            residuals.append(residual.event_id)
            continue

        if result.status is RecoveryStatus.VERIFIED:
            verified.append(step.action_event_id)
            continue

        failure_event = result.recovery_event
        residual = engine.ledger.record(
            EventType.RESIDUAL_EFFECT,
            incident_id,
            {
                "action_event_id": step.action_event_id,
                "reason": "recovery_not_verified",
                "recovery_failure_event_id": failure_event.event_id,
                "plan_id": plan.plan_id,
            },
            parent_event_ids=(failure_event.event_id,),
        )
        failed.append(step.action_event_id)
        unavailable.add(step.action_event_id)
        residuals.append(residual.event_id)

    return RecoveryPlanExecution(
        verified_action_ids=tuple(verified),
        failed_action_ids=tuple(failed),
        blocked_action_ids=tuple(blocked),
        residual_event_ids=tuple(residuals),
    )
