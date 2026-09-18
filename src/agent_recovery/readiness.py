from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from .contracts import RecoveryClass as RuntimeRecoveryClass
from .contracts import RecoveryContract as RuntimeRecoveryContract
from .recovery_contract import RecoveryClass, RecoveryContract


@dataclass(frozen=True)
class RecoveryReadiness:
    """Declarative contract coverage evidence, not a production security score."""

    total_actions: int
    structurally_recoverable: int
    reversible: int
    compensatable: int
    irreversible: int
    missing_runtime_bindings: tuple[str, ...]
    blockers: tuple[str, ...]

    @property
    def recoverability_fraction(self) -> float:
        if self.total_actions == 0:
            return 0.0
        return self.structurally_recoverable / self.total_actions


def evaluate_recovery_readiness(
    declarations: Iterable[RecoveryContract],
    *,
    runtime_bindings: Mapping[str, RuntimeRecoveryContract],
) -> RecoveryReadiness:
    """Evaluate non-authorizing declarations against a separately trusted runtime registry.

    The declarative document contributes coverage evidence only. Executable authority remains
    exclusively in ``runtime_bindings`` and every identity field available in the declaration
    must match the validated runtime contract. Any missing or mismatched binding fails closed.
    """

    items = tuple(declarations)
    counts = {recovery_class: 0 for recovery_class in RecoveryClass}
    structurally_recoverable = 0
    missing: list[str] = []
    blockers: list[str] = []

    seen: set[tuple[str, str, str]] = set()
    for declaration in items:
        identity = (declaration.tool_id, declaration.action_id, declaration.version)
        label = f"{declaration.tool_id}:{declaration.action_id}@{declaration.version}"
        if identity in seen:
            blockers.append(f"duplicate_declaration:{label}")
            continue
        seen.add(identity)
        counts[declaration.recovery_class] += 1

        if declaration.recovery_class in {RecoveryClass.REVERSIBLE, RecoveryClass.COMPENSATABLE}:
            structurally_recoverable += 1

        binding = runtime_bindings.get(declaration.tool_id)
        if binding is None:
            missing.append(label)
            blockers.append(f"missing_runtime_binding:{label}")
            continue
        binding.validate()
        runtime_class = RuntimeRecoveryClass(declaration.recovery_class.value)
        if (
            binding.action_type != declaration.action_id
            or binding.contract_version != declaration.version
            or binding.recovery_class is not runtime_class
        ):
            missing.append(label)
            blockers.append(f"runtime_binding_mismatch:{label}")

    return RecoveryReadiness(
        total_actions=len(items),
        structurally_recoverable=structurally_recoverable,
        reversible=counts[RecoveryClass.REVERSIBLE],
        compensatable=counts[RecoveryClass.COMPENSATABLE],
        irreversible=counts[RecoveryClass.IRREVERSIBLE],
        missing_runtime_bindings=tuple(sorted(set(missing))),
        blockers=tuple(sorted(set(blockers))),
    )
