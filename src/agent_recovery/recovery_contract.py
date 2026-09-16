from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any

SUPPORTED_RECOVERY_CONTRACT_VERSION = "1"


class RecoveryContractError(ValueError):
    """Raised when a write-capable action does not declare a usable recovery path."""


class RecoveryClass(str, Enum):
    REVERSIBLE = "reversible"
    COMPENSATABLE = "compensatable"
    IRREVERSIBLE = "irreversible"


@dataclass(frozen=True)
class RecoveryContract:
    version: str
    tool_id: str
    action_id: str
    recovery_class: RecoveryClass
    recovery_operation: str | None
    verification_operation: str
    parameter_binding: str
    context_binding: str


def _required_text(raw: Mapping[str, Any], key: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RecoveryContractError(f"missing or invalid {key}")
    return value.strip()


def parse_recovery_contract(raw: Mapping[str, Any]) -> RecoveryContract:
    if not isinstance(raw, Mapping):
        raise RecoveryContractError("contract must be a mapping")

    version = _required_text(raw, "version")
    if version != SUPPORTED_RECOVERY_CONTRACT_VERSION:
        raise RecoveryContractError(f"unsupported recovery contract version: {version}")

    try:
        recovery_class = RecoveryClass(_required_text(raw, "recovery_class"))
    except ValueError as exc:
        raise RecoveryContractError("unsupported recovery_class") from exc

    recovery_operation_raw = raw.get("recovery_operation")
    recovery_operation = None
    if recovery_operation_raw is not None:
        if not isinstance(recovery_operation_raw, str) or not recovery_operation_raw.strip():
            raise RecoveryContractError("invalid recovery_operation")
        recovery_operation = recovery_operation_raw.strip()

    requires_recovery = recovery_class in {
        RecoveryClass.REVERSIBLE,
        RecoveryClass.COMPENSATABLE,
    }
    if requires_recovery and recovery_operation is None:
        raise RecoveryContractError(f"{recovery_class.value} action requires recovery_operation")
    if recovery_class is RecoveryClass.IRREVERSIBLE and recovery_operation is not None:
        raise RecoveryContractError("irreversible action must not claim a recovery_operation")

    return RecoveryContract(
        version=version,
        tool_id=_required_text(raw, "tool_id"),
        action_id=_required_text(raw, "action_id"),
        recovery_class=recovery_class,
        recovery_operation=recovery_operation,
        verification_operation=_required_text(raw, "verification_operation"),
        parameter_binding=_required_text(raw, "parameter_binding"),
        context_binding=_required_text(raw, "context_binding"),
    )
