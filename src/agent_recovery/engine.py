from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum

from .contracts import RecoveryClass, RecoveryContract
from .graph import IncidentGraph
from .ledger import ActionLedger, EventType, LedgerEvent
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

    @classmethod
    def for_action(
        cls,
        tool_id: str,
        params: Mapping[str, object],
        approval_id: str,
    ) -> Approval:
        return cls(tool_id=tool_id, params_digest=digest_params(params), approval_id=approval_id)


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
        self._contracts: dict[str, RecoveryContract] = {}
        self._executed: dict[
            str,
            tuple[str, RecoveryContract, dict[str, object], object, object],
        ] = {}
        self._recovery_results: dict[str, RecoveryResult] = {}
        self._contained_scopes: set[str] = set()
        self._consumed_approval_ids: set[str] = {
            str(event.payload["approval_id"])
            for event in self.ledger.events()
            if event.event_type is EventType.AUTHORITY_CONSUMED
            and event.payload.get("approval_id") is not None
        }

    def register(self, contract: RecoveryContract) -> None:
        contract.validate()
        self._contracts[contract.tool_id] = contract

    def contain(self, incident_id: str, scope: str, *, reason: str) -> LedgerEvent:
        self._contained_scopes.add(scope)
        return self.ledger.record(
            EventType.CONTAINMENT,
            incident_id,
            {"scope": scope, "reason": reason, "active": True},
        )

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
        resource_keys = contract.resource_keys(params) if contract is not None else ()
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
                {"tool_id": tool_id, "reason": "missing_recovery_contract"},
                parent_event_ids=(intent.event_id,),
            )
            return ActionResult(ActionDecision.BLOCKED, intent, blocked)

        contract.validate()
        if self.is_contained(f"tool:{tool_id}") or self.is_contained(f"agent:{agent_id}"):
            blocked = self.ledger.record(
                EventType.ACTION_BLOCKED,
                incident_id,
                {"tool_id": tool_id, "reason": "contained"},
                parent_event_ids=(intent.event_id,),
            )
            return ActionResult(ActionDecision.BLOCKED, intent, blocked)

        authority_event: LedgerEvent | None = None
        if contract.approval_before_action:
            if not self._approval_matches(contract, params, approval):
                blocked = self.ledger.record(
                    EventType.ACTION_BLOCKED,
                    incident_id,
                    {"tool_id": tool_id, "reason": "missing_or_mismatched_approval"},
                    parent_event_ids=(intent.event_id,),
                )
                return ActionResult(ActionDecision.BLOCKED, intent, blocked)
            assert approval is not None
            if self._approval_is_consumed(approval):
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
            authority_event = self._consume_approval(
                incident_id=incident_id,
                approval=approval,
                purpose="action",
                parent_event_id=intent.event_id,
            )

        execution_result = contract.executor(self.state, params)
        observed_state = contract.verifier(self.state, params)
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
                "execution_result": execution_result,
                "observed_state": observed_state,
                "approval_id": approval.approval_id if approval else None,
            },
            parent_event_ids=(authority_event.event_id if authority_event else intent.event_id,),
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
        cached = self._recovery_results.get(action_event_id)
        if cached is not None:
            return cached

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

        recovery_parent_event_id = action_event_id
        if contract.approval_before_recovery:
            if not self._approval_matches(contract, original_params, approval):
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
            if self._approval_is_consumed(approval):
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
            recovery_authority = self._consume_approval(
                incident_id=incident_id,
                approval=approval,
                purpose="recovery",
                parent_event_id=action_event_id,
            )
            recovery_parent_event_id = recovery_authority.event_id

        assert contract.recovery_params_builder is not None
        assert contract.recovery_executor is not None
        recovery_params = dict(
            contract.recovery_params_builder(execution_result, observed_after, original_params)
        )
        planned = self.ledger.record(
            EventType.RECOVERY_PLANNED,
            incident_id,
            {
                "action_event_id": action_event_id,
                "tool_id": contract.tool_id,
                "recovery_params": recovery_params,
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
                "idempotency_key": f"recover:{action_event_id}",
            },
            parent_event_ids=(planned.event_id,),
        )

        verification_params = self._verification_params(original_params, recovery_params)
        verified_state = contract.verifier(self.state, verification_params)
        expected = self._expected_recovered_state(execution_result, recovery_result)
        verified = verified_state == expected
        verification = self.ledger.record(
            EventType.VERIFICATION,
            incident_id,
            {
                "action_event_id": action_event_id,
                "verified": verified,
                "expected": expected,
                "observed": verified_state,
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
                if any(event.event_id == event_id for event in self.ledger.events())
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
        if approval.approval_id in self._consumed_approval_ids:
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

        self._consumed_approval_ids.add(approval.approval_id)
        authority = self.ledger.record(
            EventType.AUTHORITY_CONSUMED,
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

    def _approval_is_consumed(self, approval: Approval) -> bool:
        return approval.approval_id in self._consumed_approval_ids

    def _consume_approval(
        self,
        *,
        incident_id: str,
        approval: Approval,
        purpose: str,
        parent_event_id: str,
    ) -> LedgerEvent:
        self._consumed_approval_ids.add(approval.approval_id)
        return self.ledger.record(
            EventType.AUTHORITY_CONSUMED,
            incident_id,
            {
                "approval_id": approval.approval_id,
                "tool_id": approval.tool_id,
                "params_digest": approval.params_digest,
                "purpose": purpose,
            },
            parent_event_ids=(parent_event_id,),
        )

    @staticmethod
    def _approval_matches(
        contract: RecoveryContract,
        params: Mapping[str, object],
        approval: Approval | None,
    ) -> bool:
        if approval is None:
            return False
        return approval.tool_id == contract.tool_id and approval.params_digest == digest_params(params)

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
    def _expected_recovered_state(execution_result: object, recovery_result: object) -> object:
        if isinstance(recovery_result, Mapping) and "after" in recovery_result:
            return recovery_result["after"]
        if isinstance(execution_result, Mapping) and "before" in execution_result:
            return execution_result["before"]
        return recovery_result
