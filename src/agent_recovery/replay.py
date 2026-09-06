from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from .engine import ActionDecision, RecoveryEngine
from .ledger import ActionLedger, EventType


@dataclass(frozen=True)
class ReplayActionSpec:
    agent_id: str
    tool_id: str
    params: Mapping[str, Any]
    containment_scopes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReplayEvidence:
    replay_id: str
    source_trigger_event_id: str
    replay_ledger: ActionLedger
    replay_trigger_event_id: str
    replay_action_event_id: str

    def derive(self, *, source_ledger: ActionLedger, source_incident_id: str) -> ReplayObservation:
        """Derive replay facts from the two tamper-evident ledgers at verification time."""

        source_ledger.verify_integrity()
        self.replay_ledger.verify_integrity()

        source_trigger = source_ledger.get(self.source_trigger_event_id)
        if source_trigger.incident_id != source_incident_id:
            raise ValueError("replay source trigger must belong to the source incident")
        if source_trigger.event_type is not EventType.EXTERNAL_INPUT:
            raise ValueError("replay source trigger must be an external input")

        replay_trigger = self.replay_ledger.get(self.replay_trigger_event_id)
        replay_action = self.replay_ledger.get(self.replay_action_event_id)
        if replay_trigger.incident_id != self.replay_id or replay_action.incident_id != self.replay_id:
            raise ValueError("replay evidence must belong to the isolated replay incident")
        if replay_trigger.event_type is not EventType.EXTERNAL_INPUT:
            raise ValueError("isolated replay must begin from an external input")
        if replay_action.event_type not in {EventType.ACTION_BLOCKED, EventType.ACTION_EXECUTED}:
            raise ValueError("replay action evidence must be an action outcome")

        executed = tuple(
            event.event_id
            for event in self.replay_ledger.events(incident_id=self.replay_id)
            if event.event_type is EventType.ACTION_EXECUTED
        )
        return ReplayObservation(
            replay_id=self.replay_id,
            source_trigger_event_id=self.source_trigger_event_id,
            source_payload_matches=replay_trigger.payload == source_trigger.payload,
            entry_action_blocked=replay_action.event_type is EventType.ACTION_BLOCKED,
            executed_side_effect_event_ids=executed,
            replay_ledger_head=self.replay_ledger.head_hash,
        )


@dataclass(frozen=True)
class ReplayObservation:
    replay_id: str
    source_trigger_event_id: str
    source_payload_matches: bool
    entry_action_blocked: bool
    executed_side_effect_event_ids: tuple[str, ...]
    replay_ledger_head: str

    @property
    def evidence_complete(self) -> bool:
        return self.source_payload_matches and bool(self.replay_ledger_head)

    @property
    def verified(self) -> bool:
        return (
            self.evidence_complete
            and self.entry_action_blocked
            and not self.executed_side_effect_event_ids
        )


class ReplayLab:
    """Execute a bounded attack-path replay in a fresh isolated synthetic runtime."""

    def __init__(self, engine_factory: Callable[[], RecoveryEngine]) -> None:
        self._engine_factory = engine_factory

    def run(
        self,
        *,
        source_ledger: ActionLedger,
        source_incident_id: str,
        source_trigger_event_id: str,
        replay_id: str,
        action: ReplayActionSpec,
    ) -> ReplayEvidence:
        source_ledger.verify_integrity()
        source_trigger = source_ledger.get(source_trigger_event_id)
        if source_trigger.incident_id != source_incident_id:
            raise ValueError("replay source trigger must belong to the source incident")
        if source_trigger.event_type is not EventType.EXTERNAL_INPUT:
            raise ValueError("replay source trigger must be an external input")

        replay_engine = self._engine_factory()
        for scope in action.containment_scopes:
            replay_engine.contain(
                replay_id,
                scope,
                reason="containment preserved during isolated replay",
            )

        replay_trigger = replay_engine.ledger.record(
            EventType.EXTERNAL_INPUT,
            replay_id,
            dict(source_trigger.payload),
        )
        replay_result = replay_engine.execute(
            incident_id=replay_id,
            agent_id=action.agent_id,
            tool_id=action.tool_id,
            params=dict(action.params),
            causal_parent_event_ids=(replay_trigger.event_id,),
        )
        replay_engine.ledger.verify_integrity()

        return ReplayEvidence(
            replay_id=replay_id,
            source_trigger_event_id=source_trigger_event_id,
            replay_ledger=replay_engine.ledger,
            replay_trigger_event_id=replay_trigger.event_id,
            replay_action_event_id=replay_result.action_event.event_id,
        )
