from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum

from .contracts import RecoveryClass, RecoveryContract
from .graph import IncidentGraph
from .ledger import ActionLedger, EventType, LedgerEvent


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

        if contract.approval_before_action and not self._approval_matches(
            contract,
            params,
            approval,
        ):
            blocked = self.ledger.record(
                EventType.ACTION_BLOCKED,
                incident_id,
                {"tool_id": tool_id, "reason": "missing_or_mismatched_approval"},
                parent_event_ids=(intent.event_id,),
            )
            return ActionResult(ActionDecision.BLOCKED, intent, blocked)

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
            parent_event_ids=(intent.event_id,),
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

        if contract.approval_before_recovery and not self._approval_matches(
            contract,
            original_params,
            approval,
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
            parent_event_ids=(action_event_id,),
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
