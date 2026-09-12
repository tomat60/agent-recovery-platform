from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum

from .contracts import RecoveryClass, RecoveryContract
from .graph import IncidentGraph
from .ledger import ActionLedger, EventType, LedgerEvent
from .lineage import current_generation
from .reconciliation import (
    ReconciliationApproval,
    ReconciliationResult,
    ReconciliationStatus,
)


class ActionDecision(str, Enum):
    EXECUTED = "executed"
    BLOCKED = "blocked"


class RecoveryStatus(str, Enum):
    VERIFIED = "verified"
    RESIDUAL = "residual"
    FAILED = "failed"


@dataclass(frozen=True)
class Approval:
    tool_id: str
    params_digest: str
    approval_id: str
    purpose: str = "action"
    incident_id: str | None = None
    source_action_event_id: str | None = None
    recovery_generation: int | None = None
    contract_version: str | None = None

    @classmethod
    def for_action(
        cls,
        tool_id: str,
        params: Mapping[str, object],
        approval_id: str,
        *,
        incident_id: str | None = None,
        contract_version: str | None = None,
    ) -> Approval:
        return cls(
            tool_id=tool_id,
            params_digest=digest_params(params),
            approval_id=approval_id,
            purpose="action",
            incident_id=incident_id,
            contract_version=contract_version,
        )

    @classmethod
    def for_recovery(
        cls,
        tool_id: str,
        recovery_params: Mapping[str, object],
        approval_id: str,
        *,
        incident_id: str,
        source_action_event_id: str,
        recovery_generation: int,
        contract_version: str,
    ) -> Approval:
        return cls(
            tool_id=tool_id,
            params_digest=digest_params(recovery_params),
            approval_id=approval_id,
            purpose="recovery",
            incident_id=incident_id,
            source_action_event_id=source_action_event_id,
            recovery_generation=recovery_generation,
            contract_version=contract_version,
        )


@dataclass(frozen=True)
class ActionResult:
    decision: ActionDecision
    intent_event: LedgerEvent
    action_event: LedgerEvent
    observed_state: object | None = None


@dataclass(frozen=True)
class RecoveryResult:
    status: RecoveryStatus
    recovery_event: LedgerEvent
    verification_event: LedgerEvent | None
    residual_reason: str | None = None


def digest_params(params: Mapping[str, object]) -> str:
    normalized = json.dumps(params, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class RecoveryEngine:
    """Deterministic execution boundary around model-proposed actions."""

    def __init__(self, state: object, ledger: ActionLedger | None = None) -> None:
        self.state = state
        self.ledger = ledger or ActionLedger()
        self.ledger.verify_integrity()
        self._contracts: dict[str, RecoveryContract] = {}
        self._executed: dict[
            str,
            tuple[str, RecoveryContract, dict[str, object], object, object],
        ] = {}
        self._recovery_results: dict[str, RecoveryResult] = {}
        self._contained_scopes = self._reconstruct_containment()

    def register(self, contract: RecoveryContract) -> None:
        contract.validate()
        self._contracts[contract.tool_id] = contract

    def contain(self, incident_id: str, scope: str, *, reason: str) -> LedgerEvent:
        event = self.ledger.record(
            EventType.CONTAINMENT,
            incident_id,
            {"scope": scope, "reason": reason, "active": True},
        )
        self._contained_scopes.add(scope)
        return event

    def release_containment(
        self,
        incident_id: str,
        scope: str,
        *,
        restoration_event_id: str,
    ) -> LedgerEvent:
        """Apply one exact authorized restoration decision to runtime containment."""

        self.ledger.verify_integrity()
        restoration = self.ledger.get(restoration_event_id)
        if restoration.incident_id != incident_id:
            raise ValueError("restoration incident mismatch")
        if restoration.event_type is not EventType.RESTORATION:
            raise ValueError("release requires a restoration event")
        if restoration.payload.get("authorized") is not True:
            raise ValueError("release requires authorized restoration")
        if restoration.payload.get("authority_scope") != scope:
            raise ValueError("restoration scope mismatch")
        if scope not in self._contained_scopes:
            raise ValueError("scope is not currently contained")

        event = self.ledger.record(
            EventType.CONTAINMENT,
            incident_id,
            {
                "scope": scope,
                "reason": "authorized_restoration_applied",
                "active": False,
                "restoration_event_id": restoration.event_id,
            },
            parent_event_ids=(restoration.event_id,),
        )
        self._contained_scopes.discard(scope)
        return event

    def is_contained(self, scope: str) -> bool:
        return scope in self._contained_scopes

    def execute(
        self,
        *,
        incident_id: str,
        agent_id: str,
        tool_id: str,
        params: Mapping[str, object],
        approval: Approval | None = None,
        causal_parent_event_ids: Iterable[str] = (),
    ) -> ActionResult:
        contract = self._contracts.get(tool_id)
        if contract is not None:
            contract.validate()
            resource_keys = contract.resource_keys(params)
        else:
            resource_keys = ()

        intent = self.ledger.record(
            EventType.ACTION_INTENT,
            incident_id,
            {
                "agent_id": agent_id,
                "tool_id": tool_id,
                "params_digest": digest_params(params),
                "resource_keys": resource_keys,
            },
            parent_event_ids=tuple(causal_parent_event_ids),
        )

        if contract is None:
            blocked = self.ledger.record(
                EventType.ACTION_BLOCKED,
                incident_id,
                {
                    "agent_id": agent_id,
                    "tool_id": tool_id,
                    "params_digest": digest_params(params),
                    "reason": "missing_recovery_contract",
                },
                parent_event_ids=(intent.event_id,),
            )
            return ActionResult(ActionDecision.BLOCKED, intent, blocked)

        if self.is_contained(f"tool:{tool_id}") or self.is_contained(f"agent:{agent_id}"):
            blocked = self.ledger.record(
                EventType.ACTION_BLOCKED,
                incident_id,
                {
                    "agent_id": agent_id,
                    "tool_id": tool_id,
                    "params_digest": digest_params(params),
                    "contract_version": contract.contract_version,
                    "recovery_class": contract.recovery_class.value,
                    "reason": "contained",
                },
                parent_event_ids=(intent.event_id,),
            )
            return ActionResult(ActionDecision.BLOCKED, intent, blocked)

        authority_event: LedgerEvent | None = None
        if contract.approval_before_action:
            if not self._approval_matches(
                contract,
                params,
                approval,
                incident_id=incident_id,
            ):
                blocked = self.ledger.record(
                    EventType.ACTION_BLOCKED,
                    incident_id,
                    {"tool_id": tool_id, "reason": "missing_or_mismatched_approval"},
                    parent_event_ids=(intent.event_id,),
                )
                return ActionResult(ActionDecision.BLOCKED, intent, blocked)
            assert approval is not None
            authority_event = self._consume_approval(
                incident_id=incident_id,
                approval=approval,
                purpose="action",
                parent_event_id=intent.event_id,
            )
            if authority_event is None:
                blocked = self.ledger.record(
                    EventType.ACTION_BLOCKED,
                    incident_id,
                    {
                        "tool_id": tool_id,
                        "reason": "approval_already_consumed",
                        "approval_id": approval.approval_id,
                    },
                    parent_event_ids=(intent.event_id,),
                )
                return ActionResult(ActionDecision.BLOCKED, intent, blocked)

        execution_parent_id = authority_event.event_id if authority_event else intent.event_id
        try:
            execution_result = contract.executor(self.state, params)
        except Exception as exc:
            uncertain = self._record_uncertain_action(
                incident_id=incident_id,
                agent_id=agent_id,
                contract=contract,
                params=params,
                resource_keys=resource_keys,
                execution_result=None,
                observed_state=None,
                parent_event_id=execution_parent_id,
                error_stage="executor",
                error_type=type(exc).__name__,
                approval=approval,
            )
            self.ledger.record(
                EventType.RESIDUAL_EFFECT,
                incident_id,
                {
                    "action_event_id": uncertain.event_id,
                    "tool_id": tool_id,
                    "reason": "action_outcome_uncertain_after_executor_exception",
                    "error_type": type(exc).__name__,
                },
                parent_event_ids=(uncertain.event_id,),
            )
            raise

        try:
            observed_state = contract.verifier(self.state, params)
        except Exception as exc:
            uncertain = self._record_uncertain_action(
                incident_id=incident_id,
                agent_id=agent_id,
                contract=contract,
                params=params,
                resource_keys=resource_keys,
                execution_result=execution_result,
                observed_state=None,
                parent_event_id=execution_parent_id,
                error_stage="verifier",
                error_type=type(exc).__name__,
                approval=approval,
            )
            self.ledger.record(
                EventType.RESIDUAL_EFFECT,
                incident_id,
                {
                    "action_event_id": uncertain.event_id,
                    "tool_id": tool_id,
                    "reason": "action_effect_unverified_after_observation_failure",
                    "error_type": type(exc).__name__,
                },
                parent_event_ids=(uncertain.event_id,),
            )
            raise

        executed = self.ledger.record(
            EventType.ACTION_EXECUTED,
            incident_id,
            {
                "agent_id": agent_id,
                "tool_id": tool_id,
                "contract_version": contract.contract_version,
                "recovery_class": contract.recovery_class.value,
                "resource_keys": resource_keys,
                "params": dict(params),
                "params_digest": digest_params(params),
                "execution_result": execution_result,
                "observed_state": observed_state,
                "outcome_uncertain": False,
                "approval_id": approval.approval_id if approval else None,
            },
            parent_event_ids=(execution_parent_id,),
        )
        self._executed[executed.event_id] = (
            incident_id,
            contract,
            dict(params),
            execution_result,
            observed_state,
        )
        return ActionResult(ActionDecision.EXECUTED, intent, executed, observed_state)

    def recover(
        self,
        *,
        incident_id: str,
        action_event_id: str,
        approval: Approval | None = None,
    ) -> RecoveryResult:
        self.ledger.verify_integrity()

        try:
            (
                source_incident_id,
                contract,
                original_params,
                execution_result,
                observed_after,
            ) = self._executed[action_event_id]
        except KeyError as exc:
            raise KeyError(f"unknown executed action: {action_event_id}") from exc

        if incident_id != source_incident_id:
            failed = self.ledger.record(
                EventType.RECOVERY_FAILED,
                source_incident_id,
                {
                    "action_event_id": action_event_id,
                    "tool_id": contract.tool_id,
                    "reason": "incident_mismatch",
                    "requested_incident_id": incident_id,
                },
                parent_event_ids=(action_event_id,),
            )
            return RecoveryResult(RecoveryStatus.FAILED, failed, None)

        cached = self._recovery_results.get(action_event_id)
        if cached is not None:
            return cached

        later_writers = self._unresolved_later_resource_writers(action_event_id)
        if later_writers:
            failed = self.ledger.record(
                EventType.RECOVERY_FAILED,
                source_incident_id,
                {
                    "action_event_id": action_event_id,
                    "tool_id": contract.tool_id,
                    "reason": "later_resource_writer_requires_recovery_or_reconciliation",
                    "conflicting_action_event_ids": later_writers,
                },
                parent_event_ids=(action_event_id, *later_writers),
            )
            return RecoveryResult(
                RecoveryStatus.FAILED,
                failed,
                None,
                residual_reason="later_resource_writer_requires_recovery_or_reconciliation",
            )

        graph = IncidentGraph.from_ledger(self.ledger, incident_id=source_incident_id)
        conflicts = graph.conflicts_for(action_event_id)
        if conflicts:
            conflicting_ids = tuple(
                sorted(
                    {
                        conflict.right_event_id
                        if conflict.left_event_id == action_event_id
                        else conflict.left_event_id
                        for conflict in conflicts
                    }
                )
            )
            failed = self.ledger.record(
                EventType.RECOVERY_FAILED,
                source_incident_id,
                {
                    "action_event_id": action_event_id,
                    "tool_id": contract.tool_id,
                    "reason": "shared_state_conflict_requires_reconciliation",
                    "resource_keys": tuple(sorted({c.resource_key for c in conflicts})),
                    "conflicting_action_event_ids": conflicting_ids,
                },
                parent_event_ids=(action_event_id, *conflicting_ids),
            )
            return RecoveryResult(
                RecoveryStatus.FAILED,
                failed,
                None,
                residual_reason="shared_state_conflict_requires_reconciliation",
            )

        if contract.recovery_class is RecoveryClass.IRREVERSIBLE:
            residual = self.ledger.record(
                EventType.RESIDUAL_EFFECT,
                incident_id,
                {
                    "action_event_id": action_event_id,
                    "tool_id": contract.tool_id,
                    "reason": "action_is_irreversible",
                },
                parent_event_ids=(action_event_id,),
            )
            result = RecoveryResult(
                status=RecoveryStatus.RESIDUAL,
                recovery_event=residual,
                verification_event=None,
                residual_reason="action_is_irreversible",
            )
            self._recovery_results[action_event_id] = result
            return result

        assert contract.recovery_params_builder is not None
        assert contract.recovery_executor is not None
        recovery_params = dict(
            contract.recovery_params_builder(execution_result, observed_after, original_params)
        )
        expected = self._expected_recovered_state(execution_result, recovery_params)
        generation = current_generation(self.ledger, incident_id=incident_id)

        recovery_parent_event_id = action_event_id
        if contract.approval_before_recovery:
            if not self._recovery_approval_matches(
                contract,
                recovery_params,
                approval,
                incident_id=incident_id,
                action_event_id=action_event_id,
                recovery_generation=generation,
            ):
                failed = self.ledger.record(
                    EventType.RECOVERY_FAILED,
                    incident_id,
                    {
                        "action_event_id": action_event_id,
                        "tool_id": contract.tool_id,
                        "reason": "missing_or_mismatched_recovery_approval",
                    },
                    parent_event_ids=(action_event_id,),
                )
                return RecoveryResult(RecoveryStatus.FAILED, failed, None)
            assert approval is not None
            recovery_authority = self._consume_approval(
                incident_id=incident_id,
                approval=approval,
                purpose="recovery",
                parent_event_id=action_event_id,
                extra_payload={
                    "source_action_event_id": action_event_id,
                    "recovery_generation": generation,
                    "contract_version": contract.contract_version,
                },
            )
            if recovery_authority is None:
                failed = self.ledger.record(
                    EventType.RECOVERY_FAILED,
                    incident_id,
                    {
                        "action_event_id": action_event_id,
                        "tool_id": contract.tool_id,
                        "reason": "recovery_approval_already_consumed",
                        "approval_id": approval.approval_id,
                    },
                    parent_event_ids=(action_event_id,),
                )
                return RecoveryResult(RecoveryStatus.FAILED, failed, None)
            recovery_parent_event_id = recovery_authority.event_id

        planned = self.ledger.record(
            EventType.RECOVERY_PLANNED,
            incident_id,
            {
                "action_event_id": action_event_id,
                "tool_id": contract.tool_id,
                "recovery_params": recovery_params,
                "expected_state": expected,
                "recovery_generation": generation,
                "idempotency_key": f"recover:{action_event_id}",
            },
            parent_event_ids=(recovery_parent_event_id,),
        )
        recovery_result = contract.recovery_executor(self.state, recovery_params)
        recovered = self.ledger.record(
            EventType.RECOVERY_EXECUTED,
            incident_id,
            {
                "action_event_id": action_event_id,
                "tool_id": contract.tool_id,
                "result": recovery_result,
                "recovery_generation": generation,
                "idempotency_key": f"recover:{action_event_id}",
            },
            parent_event_ids=(planned.event_id,),
        )

        verification_params = self._verification_params(original_params, recovery_params)
        verified_state = contract.verifier(self.state, verification_params)
        verified = verified_state == expected
        verification = self.ledger.record(
            EventType.VERIFICATION,
            incident_id,
            {
                "action_event_id": action_event_id,
                "verified": verified,
                "expected": expected,
                "observed": verified_state,
                "recovery_generation": generation,
            },
            parent_event_ids=(recovered.event_id,),
        )
        result = RecoveryResult(
            RecoveryStatus.VERIFIED if verified else RecoveryStatus.FAILED,
            recovered,
            verification,
        )
        if verified:
            self._recovery_results[action_event_id] = result
        return result

    def reconcile_conflict(
        self,
        *,
        incident_id: str,
        compromised_action_event_id: str,
        trusted_action_event_id: str,
        approval: ReconciliationApproval | None,
    ) -> ReconciliationResult:
        """Resolve an exact same-resource conflict only from fresh, explicit evidence.

        The engine never guesses which concurrent writer is correct. The selected trusted
        writer is part of a parameter-bound approval that is tied to the current ledger
        head. A dedicated contract reconciliation executor then restores the exact observed
        trusted state and verifies it independently.
        """

        self.ledger.verify_integrity()

        def blocked(reason: str) -> ReconciliationResult:
            parents = tuple(
                event_id
                for event_id in (compromised_action_event_id, trusted_action_event_id)
                if any(
                    event.event_id == event_id and event.incident_id == incident_id
                    for event in self.ledger.events()
                )
            )
            event = self.ledger.record(
                EventType.RECONCILIATION_FAILED,
                incident_id,
                {
                    "compromised_action_event_id": compromised_action_event_id,
                    "trusted_action_event_id": trusted_action_event_id,
                    "reason": reason,
                },
                parent_event_ids=parents,
            )
            return ReconciliationResult(
                ReconciliationStatus.BLOCKED,
                event,
                reason=reason,
            )

        try:
            compromised = self.ledger.get(compromised_action_event_id)
            trusted = self.ledger.get(trusted_action_event_id)
        except KeyError:
            return blocked("missing_conflict_action_evidence")

        if compromised.event_type is not EventType.ACTION_EXECUTED:
            return blocked("compromised_event_is_not_executed_action")
        if trusted.event_type is not EventType.ACTION_EXECUTED:
            return blocked("trusted_event_is_not_executed_action")
        if compromised.event_id == trusted.event_id:
            return blocked("conflict_actions_must_be_distinct")
        if compromised.incident_id != incident_id or trusted.incident_id != incident_id:
            return blocked("conflict_incident_mismatch")

        compromised_tool = str(compromised.payload.get("tool_id", ""))
        trusted_tool = str(trusted.payload.get("tool_id", ""))
        if not compromised_tool or compromised_tool != trusted_tool:
            return blocked("cross_contract_reconciliation_not_supported")
        contract = self._contracts.get(compromised_tool)
        if contract is None:
            return blocked("missing_recovery_contract")
        if (
            compromised.payload.get("contract_version") != contract.contract_version
            or trusted.payload.get("contract_version") != contract.contract_version
        ):
            return blocked("reconciliation_contract_version_mismatch")
        if (
            contract.reconciliation_executor is None
            or contract.reconciliation_params_builder is None
        ):
            return blocked("contract_has_no_reconciliation_path")

        graph = IncidentGraph.from_ledger(self.ledger, incident_id=incident_id)
        conflicts = graph.shared_state_conflicts(
            (compromised_action_event_id, trusted_action_event_id)
        )
        if len(conflicts) != 1:
            return blocked("conflict_is_not_one_exact_shared_resource")
        conflict = conflicts[0]

        if approval is None:
            return blocked("missing_reconciliation_approval")
        if self.ledger.authority_consumed(approval.approval_id):
            return blocked("reconciliation_approval_already_consumed")
        if approval.incident_id != incident_id:
            return blocked("reconciliation_approval_incident_mismatch")
        if approval.resource_key != conflict.resource_key:
            return blocked("reconciliation_approval_resource_mismatch")
        if approval.compromised_action_event_id != compromised_action_event_id:
            return blocked("reconciliation_approval_compromised_action_mismatch")
        if approval.trusted_action_event_id != trusted_action_event_id:
            return blocked("reconciliation_approval_trusted_action_mismatch")
        if approval.evidence_head_hash != self.ledger.head_hash:
            return blocked("stale_reconciliation_approval")

        trusted_params = trusted.payload.get("params")
        if not isinstance(trusted_params, Mapping):
            return blocked("trusted_action_params_are_unusable")
        trusted_observed_state = trusted.payload.get("observed_state")

        authority = self.ledger.record_authority_consumption_once(
            incident_id,
            {
                "approval_id": approval.approval_id,
                "purpose": "reconciliation",
                "resource_key": conflict.resource_key,
                "compromised_action_event_id": compromised_action_event_id,
                "trusted_action_event_id": trusted_action_event_id,
                "evidence_head_hash": approval.evidence_head_hash,
            },
            parent_event_ids=(compromised_action_event_id, trusted_action_event_id),
        )
        if authority is None:
            return blocked("reconciliation_approval_already_consumed")

        try:
            reconciliation_params = dict(
                contract.reconciliation_params_builder(
                    trusted_observed_state,
                    trusted_params,
                )
            )
        except Exception:
            failed = self.ledger.record(
                EventType.RECONCILIATION_FAILED,
                incident_id,
                {
                    "resource_key": conflict.resource_key,
                    "reason": "reconciliation_params_unusable",
                },
                parent_event_ids=(authority.event_id,),
            )
            return ReconciliationResult(
                ReconciliationStatus.FAILED,
                failed,
                reason="reconciliation_params_unusable",
            )

        planned = self.ledger.record(
            EventType.RECONCILIATION_PLANNED,
            incident_id,
            {
                "resource_key": conflict.resource_key,
                "compromised_action_event_id": compromised_action_event_id,
                "trusted_action_event_id": trusted_action_event_id,
                "target_observed_state": trusted_observed_state,
                "reconciliation_params": reconciliation_params,
                "idempotency_key": (
                    f"reconcile:{compromised_action_event_id}:{trusted_action_event_id}"
                ),
            },
            parent_event_ids=(authority.event_id,),
        )

        try:
            execution_result = contract.reconciliation_executor(
                self.state,
                reconciliation_params,
            )
        except Exception:
            failed = self.ledger.record(
                EventType.RECONCILIATION_FAILED,
                incident_id,
                {
                    "resource_key": conflict.resource_key,
                    "reason": "reconciliation_executor_failed",
                },
                parent_event_ids=(planned.event_id,),
            )
            return ReconciliationResult(
                ReconciliationStatus.FAILED,
                failed,
                reason="reconciliation_executor_failed",
            )

        executed = self.ledger.record(
            EventType.RECONCILIATION_EXECUTED,
            incident_id,
            {
                "resource_key": conflict.resource_key,
                "compromised_action_event_id": compromised_action_event_id,
                "trusted_action_event_id": trusted_action_event_id,
                "result": execution_result,
                "idempotency_key": (
                    f"reconcile:{compromised_action_event_id}:{trusted_action_event_id}"
                ),
            },
            parent_event_ids=(planned.event_id,),
        )

        observed = contract.verifier(self.state, trusted_params)
        verified = observed == trusted_observed_state
        verification = self.ledger.record(
            EventType.VERIFICATION,
            incident_id,
            {
                "verification_kind": "shared_state_reconciliation",
                "resource_key": conflict.resource_key,
                "compromised_action_event_id": compromised_action_event_id,
                "trusted_action_event_id": trusted_action_event_id,
                "expected": trusted_observed_state,
                "observed": observed,
                "verified": verified,
            },
            parent_event_ids=(executed.event_id,),
        )
        return ReconciliationResult(
            ReconciliationStatus.VERIFIED if verified else ReconciliationStatus.FAILED,
            executed,
            verification_event=verification,
            reason=None if verified else "reconciliation_verification_failed",
        )

    def _reconstruct_containment(self) -> set[str]:
        active: set[str] = set()
        for event in self.ledger.events():
            if event.event_type is not EventType.CONTAINMENT:
                continue
            scope = event.payload.get("scope")
            if not isinstance(scope, str) or not scope:
                continue
            if event.payload.get("active") is True:
                active.add(scope)
            elif event.payload.get("active") is False:
                active.discard(scope)
        return active

    def _record_uncertain_action(
        self,
        *,
        incident_id: str,
        agent_id: str,
        contract: RecoveryContract,
        params: Mapping[str, object],
        resource_keys: tuple[str, ...],
        execution_result: object,
        observed_state: object,
        parent_event_id: str,
        error_stage: str,
        error_type: str,
        approval: Approval | None,
    ) -> LedgerEvent:
        event = self.ledger.record(
            EventType.ACTION_EXECUTED,
            incident_id,
            {
                "agent_id": agent_id,
                "tool_id": contract.tool_id,
                "contract_version": contract.contract_version,
                "recovery_class": contract.recovery_class.value,
                "resource_keys": resource_keys,
                "params": dict(params),
                "params_digest": digest_params(params),
                "execution_result": execution_result,
                "observed_state": observed_state,
                "outcome_uncertain": True,
                "error_stage": error_stage,
                "error_type": error_type,
                "approval_id": approval.approval_id if approval else None,
            },
            parent_event_ids=(parent_event_id,),
        )
        self._executed[event.event_id] = (
            incident_id,
            contract,
            dict(params),
            execution_result,
            observed_state,
        )
        return event

    def _unresolved_later_resource_writers(self, action_event_id: str) -> tuple[str, ...]:
        events = self.ledger.events()
        source_index = next(
            (index for index, event in enumerate(events) if event.event_id == action_event_id),
            None,
        )
        if source_index is None:
            return ()
        source = events[source_index]
        raw_keys = source.payload.get("resource_keys", ())
        if isinstance(raw_keys, str):
            raw_keys = (raw_keys,)
        source_keys = {str(key) for key in raw_keys}
        if not source_keys:
            return ()

        verified_ids = {
            str(event.payload["action_event_id"])
            for event in events
            if event.event_type is EventType.VERIFICATION
            and event.payload.get("verification_kind") != "adversarial_replay"
            and event.payload.get("verified") is True
            and isinstance(event.payload.get("action_event_id"), str)
        }
        unresolved: list[str] = []
        for event in events[source_index + 1 :]:
            if event.event_type is not EventType.ACTION_EXECUTED:
                continue
            raw_other = event.payload.get("resource_keys", ())
            if isinstance(raw_other, str):
                raw_other = (raw_other,)
            other_keys = {str(key) for key in raw_other}
            if source_keys.intersection(other_keys) and event.event_id not in verified_ids:
                unresolved.append(event.event_id)
        return tuple(unresolved)

    def _consume_approval(
        self,
        *,
        incident_id: str,
        approval: Approval,
        purpose: str,
        parent_event_id: str,
        extra_payload: Mapping[str, object] | None = None,
    ) -> LedgerEvent | None:
        payload: dict[str, object] = {
            "approval_id": approval.approval_id,
            "tool_id": approval.tool_id,
            "params_digest": approval.params_digest,
            "purpose": purpose,
        }
        if extra_payload:
            payload.update(extra_payload)
        return self.ledger.record_authority_consumption_once(
            incident_id,
            payload,
            parent_event_ids=(parent_event_id,),
        )

    @staticmethod
    def _approval_matches(
        contract: RecoveryContract,
        params: Mapping[str, object],
        approval: Approval | None,
        *,
        incident_id: str,
    ) -> bool:
        if approval is None or approval.purpose != "action":
            return False
        if approval.tool_id != contract.tool_id or approval.params_digest != digest_params(params):
            return False
        if approval.incident_id is not None and approval.incident_id != incident_id:
            return False
        if approval.contract_version is not None and approval.contract_version != contract.contract_version:
            return False
        return True

    @staticmethod
    def _recovery_approval_matches(
        contract: RecoveryContract,
        recovery_params: Mapping[str, object],
        approval: Approval | None,
        *,
        incident_id: str,
        action_event_id: str,
        recovery_generation: int,
    ) -> bool:
        if approval is None or approval.purpose != "recovery":
            return False
        return (
            approval.tool_id == contract.tool_id
            and approval.params_digest == digest_params(recovery_params)
            and approval.incident_id == incident_id
            and approval.source_action_event_id == action_event_id
            and approval.recovery_generation == recovery_generation
            and approval.contract_version == contract.contract_version
        )

    @staticmethod
    def _verification_params(
        original_params: Mapping[str, object],
        recovery_params: Mapping[str, object],
    ) -> dict[str, object]:
        merged = dict(original_params)
        merged.update(
            {key: value for key, value in recovery_params.items() if key.endswith("_id")}
        )
        return merged

    @staticmethod
    def _expected_recovered_state(
        execution_result: object,
        recovery_params: Mapping[str, object],
    ) -> object:
        if "expected_state" in recovery_params:
            return recovery_params["expected_state"]
        if isinstance(execution_result, Mapping) and "before" in execution_result:
            return execution_result["before"]
        raise ValueError("recovery target must be fixed from preserved pre-action evidence")
