from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

SUPPORTED_RECOVERY_CONTRACT_VERSION = "1"


class RecoveryContractError(ValueError):
    """Raised when a write-capable action does not declare a usable recovery path."""


class RecoveryClass(str, Enum):
    REVERSIBLE = "reversible"
    COMPENSATABLE = "compensatable"
    IRREVERSIBLE = "irreversible"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


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
    risk_level: RiskLevel = RiskLevel.MEDIUM
    action_approval_required: bool = False
    recovery_approval_required: bool = False
    parameter_bound_approval_required: bool = True
    containment_scopes: tuple[str, ...] = ("tool", "session")
    recovery_window_seconds: int | None = None
    reconciliation_operation: str | None = None
    resource_key_operation: str | None = None
    side_effects: tuple[str, ...] = ()

    def canonical_json(self) -> str:
        """Return deterministic, non-authorizing contract evidence."""
        value = asdict(self)
        value["recovery_class"] = self.recovery_class.value
        value["risk_level"] = self.risk_level.value
        value["containment_scopes"] = list(self.containment_scopes)
        value["side_effects"] = list(self.side_effects)
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _required_text(raw: Mapping[str, Any], key: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RecoveryContractError(f"missing or invalid {key}")
    return value.strip()


def _optional_text(raw: Mapping[str, Any], key: str) -> str | None:
    value = raw.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise RecoveryContractError(f"invalid {key}")
    return value.strip()


def _boolean(raw: Mapping[str, Any], key: str, default: bool) -> bool:
    value = raw.get(key, default)
    if not isinstance(value, bool):
        raise RecoveryContractError(f"invalid {key}")
    return value


def _text_tuple(
    raw: Mapping[str, Any],
    key: str,
    *,
    default: tuple[str, ...] = (),
) -> tuple[str, ...]:
    value = raw.get(key, default)
    if not isinstance(value, (list, tuple)) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise RecoveryContractError(f"invalid {key}")
    normalized = tuple(item.strip() for item in value)
    if len(normalized) != len(set(normalized)):
        raise RecoveryContractError(f"duplicate {key}")
    return normalized


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
    try:
        risk_level = RiskLevel(str(raw.get("risk_level", "medium")))
    except ValueError as exc:
        raise RecoveryContractError("unsupported risk_level") from exc

    recovery_operation = _optional_text(raw, "recovery_operation")
    requires_recovery = recovery_class in {
        RecoveryClass.REVERSIBLE,
        RecoveryClass.COMPENSATABLE,
    }
    if requires_recovery and recovery_operation is None:
        raise RecoveryContractError(f"{recovery_class.value} action requires recovery_operation")
    if recovery_class is RecoveryClass.IRREVERSIBLE and recovery_operation is not None:
        raise RecoveryContractError("irreversible action must not claim a recovery_operation")

    action_approval_required = _boolean(raw, "action_approval_required", False)
    recovery_approval_required = _boolean(raw, "recovery_approval_required", False)
    parameter_bound_approval_required = _boolean(
        raw, "parameter_bound_approval_required", True
    )
    if (
        action_approval_required or recovery_approval_required
    ) and not parameter_bound_approval_required:
        raise RecoveryContractError("declared approvals must be parameter-bound")
    if (
        risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}
        and recovery_class is RecoveryClass.IRREVERSIBLE
        and not action_approval_required
    ):
        raise RecoveryContractError("high-impact irreversible action requires pre-action approval")

    containment_scopes = _text_tuple(
        raw,
        "containment_scopes",
        default=("tool", "session"),
    )
    if not containment_scopes:
        raise RecoveryContractError("at least one containment scope is required")

    recovery_window = raw.get("recovery_window_seconds")
    if recovery_window is not None and (
        not isinstance(recovery_window, int)
        or isinstance(recovery_window, bool)
        or recovery_window <= 0
    ):
        raise RecoveryContractError("invalid recovery_window_seconds")

    return RecoveryContract(
        version=version,
        tool_id=_required_text(raw, "tool_id"),
        action_id=_required_text(raw, "action_id"),
        recovery_class=recovery_class,
        recovery_operation=recovery_operation,
        verification_operation=_required_text(raw, "verification_operation"),
        parameter_binding=_required_text(raw, "parameter_binding"),
        context_binding=_required_text(raw, "context_binding"),
        risk_level=risk_level,
        action_approval_required=action_approval_required,
        recovery_approval_required=recovery_approval_required,
        parameter_bound_approval_required=parameter_bound_approval_required,
        containment_scopes=containment_scopes,
        recovery_window_seconds=recovery_window,
        reconciliation_operation=_optional_text(raw, "reconciliation_operation"),
        resource_key_operation=_optional_text(raw, "resource_key_operation"),
        side_effects=_text_tuple(raw, "side_effects"),
    )


def parse_recovery_contract_json(payload: str) -> RecoveryContract:
    """Parse canonical/external JSON without dynamic imports or executable bindings."""
    try:
        raw = json.loads(payload)
    except (TypeError, json.JSONDecodeError) as exc:
        raise RecoveryContractError("contract must be valid JSON") from exc
    if not isinstance(raw, Mapping):
        raise RecoveryContractError("contract JSON must contain an object")
    return parse_recovery_contract(raw)
