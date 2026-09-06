from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass

from .ledger import ActionLedger, EventType, LedgerEvent


@dataclass(frozen=True)
class BlastRadius:
    root_event_id: str
    event_ids: tuple[str, ...]
    executed_action_event_ids: tuple[str, ...]


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
