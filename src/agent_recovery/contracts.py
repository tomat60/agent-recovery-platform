from __future__ import annotations

from collections.abc import Callable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass, field
from enum import Enum


class RecoveryClass(str, Enum):
    REVERSIBLE = "reversible"
    COMPENSATABLE = "compensatable"
    IRREVERSIBLE = "irreversible"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


State = MutableMapping[str, object]
Params = Mapping[str, object]
Verifier = Callable[[State, Params], object]
Executor = Callable[[State, Params], object]
RecoveryBuilder = Callable[[object, object, Params], Mapping[str, object]]


class ContractError(ValueError):
    """Raised when a Recovery Contract is unsafe or incomplete."""


@dataclass(frozen=True)
class RecoveryContract:
    tool_id: str
    action_type: str
    risk_level: RiskLevel
    recovery_class: RecoveryClass
    executor: Executor
    verifier: Verifier
    recovery_executor: Executor | None = None
    recovery_params_builder: RecoveryBuilder | None = None
    approval_before_action: bool = False
    approval_before_recovery: bool = False
    parameter_bound_approval: bool = True
    containment_scopes: Sequence[str] = field(default_factory=lambda: ("tool", "session"))
    recovery_window_seconds: int | None = None
    contract_version: str = "0.1"

    def validate(self) -> None:
        if not self.tool_id.strip():
            raise ContractError("tool_id is required")
        if not self.action_type.strip():
            raise ContractError("action_type is required")
        if not self.contract_version.strip():
            raise ContractError("contract_version is required")
        if not callable(self.executor):
            raise ContractError("executor must be callable")
        if not callable(self.verifier):
            raise ContractError("verifier must be callable")
        if self.recovery_window_seconds is not None and self.recovery_window_seconds < 0:
            raise ContractError("recovery_window_seconds cannot be negative")

        recoverable = self.recovery_class in {
            RecoveryClass.REVERSIBLE,
            RecoveryClass.COMPENSATABLE,
        }
        if recoverable and not callable(self.recovery_executor):
            raise ContractError("recoverable actions require recovery_executor")
        if recoverable and not callable(self.recovery_params_builder):
            raise ContractError("recoverable actions require recovery_params_builder")

        high_impact_irreversible = (
            self.recovery_class is RecoveryClass.IRREVERSIBLE
            and self.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}
        )
        if high_impact_irreversible and not self.approval_before_action:
            raise ContractError("high-impact irreversible actions require explicit pre-action approval")

        if self.approval_before_action and not self.parameter_bound_approval:
            raise ContractError("approvals for consequential actions must be parameter-bound")

        if self.approval_before_recovery and not self.parameter_bound_approval:
            raise ContractError("recovery approvals must be parameter-bound")

        if not self.containment_scopes:
            raise ContractError("at least one containment scope is required")
