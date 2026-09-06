from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from itertools import combinations

from .ledger import ActionLedger, EventType, LedgerEvent


@dataclass(frozen=True)
class BlastRadius:
    root_event_id: str
    event_ids: tuple[str, ...]
    executed_action_event_ids: tuple[str, ...]


@dataclass(frozen=True)
class SharedStateConflict:
    """Two causally independent actions that mutate the same declared resource."""

    resource_key: str
    left_event_id: str
    right_event_id: str
    left_agent_id: str | None
    right_agent_id: str | None
    cross_agent: bool


class IncidentGraph:
    """Deterministic causal graph reconstructed from ledger parent references."""

    def __init__(self, events: tuple[LedgerEvent, ...]) -> None:
        self._events = {event.event_id: event for event in events}
        self._parents: dict[str, set[str]] = defaultdict(set)
        self._children: dict[str, set[str]] = defaultdict(set)
        for event in events:
            for parent in event.parent_event_ids:
                if parent not in self._events:
                    raise ValueError(f"graph contains missing parent event: {parent}")
                self._parents[event.event_id].add(parent)
                self._children[parent].add(event.event_id)

    @classmethod
    def from_ledger(cls, ledger: ActionLedger, *, incident_id: str) -> IncidentGraph:
        return cls(ledger.events(incident_id=incident_id))

    def event(self, event_id: str) -> LedgerEvent:
        try:
            return self._events[event_id]
        except KeyError as exc:
            raise KeyError(f"unknown event: {event_id}") from exc

    def parents(self, event_id: str) -> tuple[str, ...]:
        self.event(event_id)
        return tuple(sorted(self._parents[event_id]))

    def children(self, event_id: str) -> tuple[str, ...]:
        self.event(event_id)
        return tuple(sorted(self._children[event_id]))

    def ancestors(self, event_id: str) -> tuple[str, ...]:
        return self._walk(event_id, self._parents)

    def descendants(self, event_id: str) -> tuple[str, ...]:
        return self._walk(event_id, self._children)

    def blast_radius(self, root_event_id: str) -> BlastRadius:
        descendant_ids = self.descendants(root_event_id)
        all_ids = (root_event_id, *descendant_ids)
        action_ids = tuple(
            event_id
            for event_id in all_ids
            if self.event(event_id).event_type is EventType.ACTION_EXECUTED
        )
        return BlastRadius(
            root_event_id=root_event_id,
            event_ids=all_ids,
            executed_action_event_ids=action_ids,
        )

    def is_ancestor(self, candidate_ancestor: str, event_id: str) -> bool:
        return candidate_ancestor in self.ancestors(event_id)

    def resource_keys(self, action_event_id: str) -> tuple[str, ...]:
        event = self.event(action_event_id)
        if event.event_type is not EventType.ACTION_EXECUTED:
            raise ValueError(f"event is not an executed action: {action_event_id}")
        raw = event.payload.get("resource_keys", ())
        if isinstance(raw, str):
            raw = (raw,)
        try:
            keys = tuple(sorted(str(key) for key in raw))
        except TypeError as exc:
            raise ValueError(f"invalid resource_keys on action: {action_event_id}") from exc
        return keys

    def shared_state_conflicts(
        self,
        action_event_ids: tuple[str, ...] | None = None,
    ) -> tuple[SharedStateConflict, ...]:
        """Find concurrent-writer hazards that causal ordering alone cannot safely undo.

        Two actions conflict when they declare at least one identical mutable resource and
        neither action is causally downstream of the other. A recovery system must not
        silently choose an undo order for this case because restoring one action's before
        image can erase an independent writer's legitimate state.
        """

        if action_event_ids is None:
            selected = tuple(
                event.event_id
                for event in self._events.values()
                if event.event_type is EventType.ACTION_EXECUTED
            )
        else:
            if len(set(action_event_ids)) != len(action_event_ids):
                raise ValueError("action_event_ids must be unique")
            for event_id in action_event_ids:
                event = self.event(event_id)
                if event.event_type is not EventType.ACTION_EXECUTED:
                    raise ValueError(f"event is not an executed action: {event_id}")
            selected = action_event_ids

        by_resource: dict[str, list[str]] = defaultdict(list)
        for event_id in selected:
            for resource_key in self.resource_keys(event_id):
                by_resource[resource_key].append(event_id)

        conflicts: list[SharedStateConflict] = []
        for resource_key, event_ids in sorted(by_resource.items()):
            for left, right in combinations(sorted(event_ids), 2):
                if self.is_ancestor(left, right) or self.is_ancestor(right, left):
                    continue
                left_agent = self._agent_id(left)
                right_agent = self._agent_id(right)
                conflicts.append(
                    SharedStateConflict(
                        resource_key=resource_key,
                        left_event_id=left,
                        right_event_id=right,
                        left_agent_id=left_agent,
                        right_agent_id=right_agent,
                        cross_agent=(
                            left_agent is not None
                            and right_agent is not None
                            and left_agent != right_agent
                        ),
                    )
                )
        return tuple(conflicts)

    def conflicts_for(self, action_event_id: str) -> tuple[SharedStateConflict, ...]:
        self.resource_keys(action_event_id)
        return tuple(
            conflict
            for conflict in self.shared_state_conflicts()
            if action_event_id in {conflict.left_event_id, conflict.right_event_id}
        )

    def _agent_id(self, action_event_id: str) -> str | None:
        value = self.event(action_event_id).payload.get("agent_id")
        return None if value is None else str(value)

    def _walk(self, event_id: str, adjacency: dict[str, set[str]]) -> tuple[str, ...]:
        self.event(event_id)
        visited: set[str] = set()
        queue: deque[str] = deque(sorted(adjacency[event_id]))
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            queue.extend(sorted(adjacency[current]))
        return tuple(sorted(visited))
