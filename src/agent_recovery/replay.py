from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from .engine import RecoveryEngine, digest_params
from .graph import IncidentGraph
from .ledger import ActionLedger, EventType
from .lineage import current_generation


@dataclass(frozen=True)
class ReplayActionSpec:
    agent_id: str
    tool_id: str
    params: Mapping[str, Any]
    containment_scopes: tuple[str, ...] = ()
    release_scope: str | None = None


@dataclass(frozen=True)
class ReplayEvidence:
    replay_id: str
    source_incident_id: str
    source_trigger_event_id: str
    source_action_event_id: str
    source_ledger_head_at_run: str
    recovery_generation_at_run: int
    release_scope: str
    action_agent_id: str
    action_tool_id: str
    action_params_digest: str
    action_contract_version: str
    source_contract_manifest: tuple[tuple[str, str], ...]
    replay_contract_manifest: tuple[tuple[str, str], ...]
    replay_ledger: ActionLedger
    replay_trigger_event_id: str
    replay_action_event_id: str

    def derive(self, *, source_ledger: ActionLedger, source_incident_id: str) -> ReplayObservation:
        """Derive replay facts from immutable execution-time bindings and both ledgers."""

        source_ledger.verify_integrity()
        self.replay_ledger.verify_integrity()
        if source_incident_id != self.source_incident_id:
            raise ValueError("replay evidence source incident mismatch")

        source_trigger = source_ledger.get(self.source_trigger_event_id)
        if source_trigger.incident_id != source_incident_id:
            raise ValueError("replay source trigger must belong to the source incident")
        if source_trigger.event_type is not EventType.EXTERNAL_INPUT:
            raise ValueError("replay source trigger must be an external input")

        source_action = source_ledger.get(self.source_action_event_id)
        if source_action.incident_id != source_incident_id:
            raise ValueError("replay source action must belong to the source incident")
        if source_action.event_type is not EventType.ACTION_EXECUTED:
            raise ValueError("replay source action must be an executed action")

        replay_trigger = self.replay_ledger.get(self.replay_trigger_event_id)
        replay_action = self.replay_ledger.get(self.replay_action_event_id)
        if replay_trigger.incident_id != self.replay_id or replay_action.incident_id != self.replay_id:
            raise ValueError("replay evidence must belong to the isolated replay incident")
        if replay_trigger.event_type is not EventType.EXTERNAL_INPUT:
            raise ValueError("isolated replay must begin from an external input")
        if replay_action.event_type not in {EventType.ACTION_BLOCKED, EventType.ACTION_EXECUTED}:
            raise ValueError("replay action evidence must be an action outcome")

        source_digest = source_action.payload.get("params_digest")
        if not isinstance(source_digest, str):
            source_params = source_action.payload.get("params")
            source_digest = digest_params(source_params) if isinstance(source_params, Mapping) else ""

        source_action_matches = (
            source_action.payload.get("agent_id") == self.action_agent_id
            and source_action.payload.get("tool_id") == self.action_tool_id
            and source_digest == self.action_params_digest
            and source_action.payload.get("contract_version") == self.action_contract_version
        )
        replay_action_matches = (
            replay_action.payload.get("agent_id") == self.action_agent_id
            and replay_action.payload.get("tool_id") == self.action_tool_id
            and replay_action.payload.get("params_digest") == self.action_params_digest
            and replay_action.payload.get("contract_version") == self.action_contract_version
        )
        containment_blocked = (
            replay_action.event_type is EventType.ACTION_BLOCKED
            and replay_action.payload.get("reason") == "contained"
        )
        graph = IncidentGraph.from_ledger(source_ledger, incident_id=source_incident_id)
        source_action_is_on_trigger_path = graph.is_ancestor(
            self.source_trigger_event_id,
            self.source_action_event_id,
        )
        environment_matches = all(
            (tool_id, version) in self.replay_contract_manifest
            for tool_id, version in self.source_contract_manifest
        )

        executed = tuple(
            event.event_id
            for event in self.replay_ledger.events(incident_id=self.replay_id)
            if event.event_type is EventType.ACTION_EXECUTED
        )
        return ReplayObservation(
            replay_id=self.replay_id,
            source_trigger_event_id=self.source_trigger_event_id,
            source_action_event_id=self.source_action_event_id,
            release_scope=self.release_scope,
            source_payload_matches=replay_trigger.payload == source_trigger.payload,
            source_action_matches=source_action_matches and source_action_is_on_trigger_path,
            replay_action_matches=replay_action_matches,
            environment_matches=environment_matches,
            entry_action_blocked_by_containment=containment_blocked,
            executed_side_effect_event_ids=executed,
            replay_ledger_head=self.replay_ledger.head_hash,
        )


@dataclass(frozen=True)
class ReplayObservation:
    replay_id: str
    source_trigger_event_id: str
    source_action_event_id: str
    release_scope: str
    source_payload_matches: bool
    source_action_matches: bool
    replay_action_matches: bool
    environment_matches: bool
    entry_action_blocked_by_containment: bool
    executed_side_effect_event_ids: tuple[str, ...]
    replay_ledger_head: str

    @property
    def evidence_complete(self) -> bool:
        return (
            self.source_payload_matches
            and self.source_action_matches
            and self.replay_action_matches
            and self.environment_matches
            and bool(self.release_scope)
            and bool(self.replay_ledger_head)
        )

    @property
    def verified(self) -> bool:
        return (
            self.evidence_complete
            and self.entry_action_blocked_by_containment
            and not self.executed_side_effect_event_ids
        )


class ReplayLab:
    """Execute a bounded attack-path replay in an isolated tamper-evident runtime."""

    def __init__(self, engine_factory: Callable[[], RecoveryEngine]) -> None:
        self._engine_factory = engine_factory

    @staticmethod
    def _source_contract_manifest(
        source_ledger: ActionLedger,
        *,
        source_incident_id: str,
    ) -> tuple[tuple[str, str], ...]:
        contracts: set[tuple[str, str]] = set()
        for event in source_ledger.events(incident_id=source_incident_id):
            if event.event_type is not EventType.ACTION_EXECUTED:
                continue
            tool_id = event.payload.get("tool_id")
            version = event.payload.get("contract_version")
            if not isinstance(tool_id, str) or not tool_id:
                raise ValueError("executed source action lacks tool identity")
            if not isinstance(version, str) or not version:
                raise ValueError("executed source action lacks contract identity")
            contracts.add((tool_id, version))
        return tuple(sorted(contracts))

    @staticmethod
    def _replay_contract_manifest(engine: RecoveryEngine) -> tuple[tuple[str, str], ...]:
        registry = getattr(engine, "_contracts", None)
        if not isinstance(registry, dict):
            raise ValueError("replay runtime does not expose deterministic contract identity")
        manifest: list[tuple[str, str]] = []
        for tool_id, contract in registry.items():
            version = getattr(contract, "contract_version", None)
            if not isinstance(tool_id, str) or not isinstance(version, str) or not version:
                raise ValueError("replay runtime has unusable contract identity")
            manifest.append((tool_id, version))
        return tuple(sorted(manifest))

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
        if not action.release_scope:
            raise ValueError("replay must be bound to one proposed release scope")
        if action.release_scope in action.containment_scopes:
            raise ValueError("replay cannot keep the proposed release scope contained")

        params_digest = digest_params(action.params)
        graph = IncidentGraph.from_ledger(source_ledger, incident_id=source_incident_id)
        matching_actions = []
        for event in source_ledger.events(incident_id=source_incident_id):
            if event.event_type is not EventType.ACTION_EXECUTED:
                continue
            if not graph.is_ancestor(source_trigger_event_id, event.event_id):
                continue
            event_digest = event.payload.get("params_digest")
            if not isinstance(event_digest, str):
                event_params = event.payload.get("params")
                event_digest = digest_params(event_params) if isinstance(event_params, Mapping) else ""
            if (
                event.payload.get("agent_id") == action.agent_id
                and event.payload.get("tool_id") == action.tool_id
                and event_digest == params_digest
            ):
                matching_actions.append(event)
        if len(matching_actions) != 1:
            raise ValueError("replay must bind to exactly one matching source action")
        source_action = matching_actions[0]
        contract_version = source_action.payload.get("contract_version")
        if not isinstance(contract_version, str) or not contract_version:
            raise ValueError("source action lacks contract identity")

        source_contract_manifest = self._source_contract_manifest(
            source_ledger,
            source_incident_id=source_incident_id,
        )
        source_head = source_ledger.head_hash
        generation = current_generation(source_ledger, incident_id=source_incident_id)
        replay_engine = self._engine_factory()
        replay_contract_manifest = self._replay_contract_manifest(replay_engine)
        missing_or_changed = tuple(
            item for item in source_contract_manifest if item not in replay_contract_manifest
        )
        if missing_or_changed:
            raise ValueError(
                f"replay environment contract mismatch: {missing_or_changed}"
            )

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
            source_incident_id=source_incident_id,
            source_trigger_event_id=source_trigger_event_id,
            source_action_event_id=source_action.event_id,
            source_ledger_head_at_run=source_head,
            recovery_generation_at_run=generation,
            release_scope=action.release_scope,
            action_agent_id=action.agent_id,
            action_tool_id=action.tool_id,
            action_params_digest=params_digest,
            action_contract_version=contract_version,
            source_contract_manifest=source_contract_manifest,
            replay_contract_manifest=replay_contract_manifest,
            replay_ledger=replay_engine.ledger,
            replay_trigger_event_id=replay_trigger.event_id,
            replay_action_event_id=replay_result.action_event.event_id,
        )