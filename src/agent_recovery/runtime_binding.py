from __future__ import annotations

from dataclasses import dataclass

from .contracts import RecoveryClass as RuntimeRecoveryClass
from .contracts import RecoveryContract as RuntimeRecoveryContract
from .contracts import RiskLevel as RuntimeRiskLevel
from .recovery_contract import RecoveryClass, RecoveryContract


class RuntimeBindingError(ValueError):
    """Raised when a trusted runtime binding does not match its declaration."""


@dataclass(frozen=True)
class TrustedRuntimeBinding:
    """Trusted executable implementation metadata for one declarative contract.

    Identifiers are registry labels supplied by trusted application code. They are
    compared with the declarative document but never imported or executed from
    declaration text.
    """

    runtime_contract: RuntimeRecoveryContract
    verification_operation: str
    parameter_binding: str
    context_binding: str
    recovery_operation: str | None = None
    reconciliation_operation: str | None = None
    resource_key_operation: str | None = None


def _require_text(value: str | None, name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise RuntimeBindingError(f"invalid trusted {name}")
    return value.strip()


def bind_recovery_contract(
    declaration: RecoveryContract,
    binding: TrustedRuntimeBinding,
) -> RuntimeRecoveryContract:
    """Validate a data-only declaration against separately trusted executable code.

    The returned runtime contract is exactly the trusted object supplied by the caller.
    No declaration field is interpreted as a Python import, callable, or authorization.
    """

    runtime = binding.runtime_contract
    runtime.validate()

    expected_class = RuntimeRecoveryClass(declaration.recovery_class.value)
    expected_risk = RuntimeRiskLevel(declaration.risk_level.value)

    scalar_mismatches = (
        runtime.tool_id != declaration.tool_id
        or runtime.action_type != declaration.action_id
        or runtime.contract_version != declaration.version
        or runtime.recovery_class is not expected_class
        or runtime.risk_level is not expected_risk
        or runtime.approval_before_action != declaration.action_approval_required
        or runtime.approval_before_recovery != declaration.recovery_approval_required
        or runtime.parameter_bound_approval != declaration.parameter_bound_approval_required
        or runtime.recovery_window_seconds != declaration.recovery_window_seconds
    )
    if scalar_mismatches:
        raise RuntimeBindingError("trusted runtime contract metadata mismatch")

    if tuple(sorted(runtime.containment_scopes)) != tuple(sorted(declaration.containment_scopes)):
        raise RuntimeBindingError("trusted containment scope mismatch")

    verification_operation = _require_text(
        binding.verification_operation,
        "verification_operation",
    )
    parameter_binding = _require_text(binding.parameter_binding, "parameter_binding")
    context_binding = _require_text(binding.context_binding, "context_binding")
    recovery_operation = _require_text(binding.recovery_operation, "recovery_operation")
    reconciliation_operation = _require_text(
        binding.reconciliation_operation,
        "reconciliation_operation",
    )
    resource_key_operation = _require_text(
        binding.resource_key_operation,
        "resource_key_operation",
    )

    if verification_operation != declaration.verification_operation:
        raise RuntimeBindingError("trusted verification operation mismatch")
    if parameter_binding != declaration.parameter_binding:
        raise RuntimeBindingError("trusted parameter binding mismatch")
    if context_binding != declaration.context_binding:
        raise RuntimeBindingError("trusted context binding mismatch")
    if recovery_operation != declaration.recovery_operation:
        raise RuntimeBindingError("trusted recovery operation mismatch")
    if reconciliation_operation != declaration.reconciliation_operation:
        raise RuntimeBindingError("trusted reconciliation operation mismatch")
    if resource_key_operation != declaration.resource_key_operation:
        raise RuntimeBindingError("trusted resource-key operation mismatch")

    if declaration.recovery_class is RecoveryClass.IRREVERSIBLE and (
        runtime.recovery_executor is not None or runtime.recovery_params_builder is not None
    ):
        raise RuntimeBindingError("irreversible runtime must not expose an undo binding")
    if reconciliation_operation is not None and (
        runtime.reconciliation_executor is None or runtime.reconciliation_params_builder is None
    ):
        raise RuntimeBindingError("trusted reconciliation binding is incomplete")
    if resource_key_operation is not None and runtime.resource_key_builder is None:
        raise RuntimeBindingError("trusted resource-key binding is incomplete")

    return runtime
