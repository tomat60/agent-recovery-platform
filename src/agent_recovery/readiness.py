from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from .contracts import RecoveryClass, RecoveryContract


@dataclass(frozen=True)
class RecoveryReadiness:
    """Contract coverage evidence, not a production security score."""

    total_actions: int
    structurally_recoverable: int
    reversible: int
    compensatable: int
    irreversible: int
    human_approval_required: int
    missing_runtime_bindings: tuple[str, ...]
    blockers: tuple[str, ...]

    @property
    def recoverability_fraction(self) -> float:
        if self.total_actions == 0:
            return 0.0
        return self.structurally_recoverable / self.total_actions


def evaluate_recovery_readiness(
    contracts: Iterable[RecoveryContract],
    *,
    runtime_bindings: Mapping[str, RecoveryContract],
) -> RecoveryReadiness:
    """Evaluate deterministic recoverability coverage against trusted runtime bindings.

    A declaration is counted as runtime-ready only when the supplied registry contains the
    exact validated tool/version/recovery-class binding. The registry, not this report,
    remains the executable authority boundary.
    """

    items = tuple(contracts)
    counts = {recovery_class: 0 for recovery_class in RecoveryClass}
    structurally_recoverable = 0
    human_approval_required = 0
    missing: list[str] = []
    blockers: list[str] = []

    seen: set[tuple[str, str]] = set()
    for contract in items:
        contract.validate()
        identity = (contract.tool_id, contract.contract_version)
        if identity in seen:
            blockers.append(f"duplicate_contract:{contract.tool_id}@{contract.contract_version}")
            continue
        seen.add(identity)
        counts[contract.recovery_class] += 1

        if contract.recovery_class in {RecoveryClass.REVERSIBLE, RecoveryClass.COMPENSATABLE}:
            structurally_recoverable += 1
        if contract.approval_before_action or contract.approval_before_recovery:
            human_approval_required += 1

        binding = runtime_bindings.get(contract.tool_id)
        if binding is None:
            missing.append(f"{contract.tool_id}@{contract.contract_version}")
            blockers.append(f"missing_runtime_binding:{contract.tool_id}@{contract.contract_version}")
            continue
        binding.validate()
        if (
            binding.contract_version != contract.contract_version
            or binding.recovery_class is not contract.recovery_class
        ):
            missing.append(f"{contract.tool_id}@{contract.contract_version}")
            blockers.append(f"runtime_binding_mismatch:{contract.tool_id}@{contract.contract_version}")

    return RecoveryReadiness(
        total_actions=len(items),
        structurally_recoverable=structurally_recoverable,
        reversible=counts[RecoveryClass.REVERSIBLE],
        compensatable=counts[RecoveryClass.COMPENSATABLE],
        irreversible=counts[RecoveryClass.IRREVERSIBLE],
        human_approval_required=human_approval_required,
        missing_runtime_bindings=tuple(sorted(set(missing))),
        blockers=tuple(sorted(set(blockers))),
    )
