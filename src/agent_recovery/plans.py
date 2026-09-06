from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field

from .graph import IncidentGraph


class RecoveryPlanError(ValueError):
    """Raised when a recovery plan is incomplete, cyclic, or unsafe."""


@dataclass(frozen=True)
class RecoveryPlanStep:
    action_event_id: str
    depends_on: tuple[str, ...] = ()
    idempotency_key: str | None = None


@dataclass(frozen=True)
class RecoveryPlan:
    steps: tuple[RecoveryPlanStep, ...]
    plan_id: str = "deterministic-plan"
    _by_action: dict[str, RecoveryPlanStep] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        by_action = {step.action_event_id: step for step in self.steps}
        if len(by_action) != len(self.steps):
            raise RecoveryPlanError("recovery plan contains duplicate action_event_id")
        object.__setattr__(self, "_by_action", by_action)
        self.validate()

    def validate(self) -> None:
        known = set(self._by_action)
        for step in self.steps:
            if not step.action_event_id:
                raise RecoveryPlanError("action_event_id is required")
            if not step.idempotency_key:
                raise RecoveryPlanError("every recovery step requires an idempotency key")
            missing = [dependency for dependency in step.depends_on if dependency not in known]
            if missing:
                raise RecoveryPlanError(
                    f"step {step.action_event_id} has unknown dependencies: {missing}"
                )
            if step.action_event_id in step.depends_on:
                raise RecoveryPlanError("recovery step cannot depend on itself")
        self.execution_order()

    def execution_order(self) -> tuple[RecoveryPlanStep, ...]:
        indegree = {action_id: 0 for action_id in self._by_action}
        children: dict[str, set[str]] = defaultdict(set)
        for step in self.steps:
            for dependency in step.depends_on:
                children[dependency].add(step.action_event_id)
                indegree[step.action_event_id] += 1

        queue: deque[str] = deque(sorted(key for key, value in indegree.items() if value == 0))
        ordered: list[RecoveryPlanStep] = []
        while queue:
            current = queue.popleft()
            ordered.append(self._by_action[current])
            for child in sorted(children[current]):
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)

        if len(ordered) != len(self.steps):
            raise RecoveryPlanError("recovery plan contains a dependency cycle")
        return tuple(ordered)


def build_reverse_causal_plan(
    graph: IncidentGraph,
    action_event_ids: tuple[str, ...],
    *,
    plan_id: str = "reverse-causal-plan",
) -> RecoveryPlan:
    """Build a plan where downstream actions are compensated before their causes."""

    selected = set(action_event_ids)
    if len(selected) != len(action_event_ids):
        raise RecoveryPlanError("action_event_ids must be unique")

    steps: list[RecoveryPlanStep] = []
    for action_id in sorted(selected):
        graph.event(action_id)
        downstream_actions = tuple(
            sorted(
                candidate
                for candidate in selected
                if candidate != action_id and graph.is_ancestor(action_id, candidate)
            )
        )
        steps.append(
            RecoveryPlanStep(
                action_event_id=action_id,
                # To recover an upstream action, every downstream action must have recovered first.
                depends_on=downstream_actions,
                idempotency_key=f"recover:{action_id}",
            )
        )
    return RecoveryPlan(steps=tuple(steps), plan_id=plan_id)


def build_shared_state_safe_plan(
    graph: IncidentGraph,
    action_event_ids: tuple[str, ...],
    *,
    plan_id: str = "shared-state-safe-plan",
) -> RecoveryPlan:
    """Build a reverse-causal plan only when shared-state recovery is unambiguous.

    A causally independent writer to the same resource makes before-image restoration
    unsafe: compensating one action can erase state produced by another agent. The safe
    default is escalation, not a guessed ordering. A future reconciler may resolve the
    conflict explicitly, but the deterministic auto-recovery boundary fails closed here.
    """

    selected = set(action_event_ids)
    if len(selected) != len(action_event_ids):
        raise RecoveryPlanError("action_event_ids must be unique")

    relevant_conflicts = tuple(
        conflict
        for conflict in graph.shared_state_conflicts()
        if conflict.left_event_id in selected or conflict.right_event_id in selected
    )
    if relevant_conflicts:
        descriptions = ", ".join(
            f"{conflict.resource_key}({conflict.left_event_id},{conflict.right_event_id})"
            for conflict in relevant_conflicts
        )
        raise RecoveryPlanError(
            "shared-state recovery requires explicit reconciliation for concurrent writers: "
            f"{descriptions}"
        )

    return build_reverse_causal_plan(graph, action_event_ids, plan_id=plan_id)
