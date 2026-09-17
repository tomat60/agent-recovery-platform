from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .contracts import RecoveryClass, RecoveryContract
from .ledger import ActionLedger, EventType, LedgerEvent


class RestartRecoveryError(ValueError):
    """Raised when persisted evidence cannot safely reconstruct recovery context."""


@dataclass(frozen=True)
class RestartRecoveryContext:
    incident_id: str
    action_event_id: str
    contract: RecoveryContract
    params: Mapping[str, object]
    execution_result: object
    observed_state: object


def reconstruct_recovery_context(
    ledger: ActionLedger,
    *,
    action_event_id: str,
    runtime_contracts: Mapping[str, RecoveryContract],
) -> RestartRecoveryContext:
    """Reconstruct one recoverable action from trusted persisted evidence.

    The ledger is the persisted source of truth. Runtime callables are never deserialized
    from evidence: the caller must supply the currently trusted contract registry and the
    exact tool/version binding must match the executed event. Any ambiguity fails closed.
    """

    ledger.verify_integrity()
    try:
        event = ledger.get(action_event_id)
    except KeyError as exc:
        raise RestartRecoveryError("missing executed action evidence") from exc

    if event.event_type is not EventType.ACTION_EXECUTED:
        raise RestartRecoveryError("restart recovery requires executed action evidence")
    if event.payload.get("outcome_uncertain") is not False:
        raise RestartRecoveryError("uncertain action outcome cannot be reconstructed")

    tool_id = event.payload.get("tool_id")
    version = event.payload.get("contract_version")
    recovery_class = event.payload.get("recovery_class")
    params = event.payload.get("params")
    if not isinstance(tool_id, str) or not tool_id:
        raise RestartRecoveryError("executed action is missing tool identity")
    if not isinstance(version, str) or not version:
        raise RestartRecoveryError("executed action is missing contract version")
    if not isinstance(params, Mapping):
        raise RestartRecoveryError("executed action parameters are unusable")

    contract = runtime_contracts.get(tool_id)
    if contract is None:
        raise RestartRecoveryError("trusted runtime contract is not registered")
    contract.validate()
    if contract.contract_version != version:
        raise RestartRecoveryError("trusted runtime contract version mismatch")
    if contract.recovery_class.value != recovery_class:
        raise RestartRecoveryError("trusted runtime recovery class mismatch")
    if contract.recovery_class is RecoveryClass.IRREVERSIBLE:
        raise RestartRecoveryError("irreversible action has no restart undo path")

    # A verified recovery is terminal. Reconstructing it would permit compensation twice.
    for candidate in ledger.events(incident_id=event.incident_id):
        if candidate.event_type is not EventType.VERIFICATION:
            continue
        if candidate.payload.get("action_event_id") != action_event_id:
            continue
        if candidate.payload.get("verified") is True:
            raise RestartRecoveryError("action already has verified terminal recovery")

    # A recovery execution without a terminal verification is an ambiguous side effect.
    # Retrying compensation after restart could execute it twice, so fail closed.
    executed_recovery: LedgerEvent | None = None
    terminal_verification: LedgerEvent | None = None
    for candidate in ledger.events(incident_id=event.incident_id):
        if candidate.payload.get("action_event_id") != action_event_id:
            continue
        if candidate.event_type is EventType.RECOVERY_EXECUTED:
            executed_recovery = candidate
            terminal_verification = None
        elif candidate.event_type is EventType.VERIFICATION and executed_recovery is not None:
            terminal_verification = candidate
    if executed_recovery is not None and terminal_verification is None:
        raise RestartRecoveryError("recovery outcome is ambiguous after restart")

    return RestartRecoveryContext(
        incident_id=event.incident_id,
        action_event_id=event.event_id,
        contract=contract,
        params=dict(params),
        execution_result=event.payload.get("execution_result"),
        observed_state=event.payload.get("observed_state"),
    )
