from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from .recovery_contract import RecoveryClass, RecoveryContract
from .runtime_binding import TrustedRuntimeBinding, bind_recovery_contract

RuntimeBindingKey = tuple[str, str, str]


@dataclass(frozen=True)
class RecoveryReadiness:
    """Declarative contract coverage evidence, not a production security score."""

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
    declarations: Iterable[RecoveryContract],
    *,
    runtime_bindings: Mapping[RuntimeBindingKey, TrustedRuntimeBinding],
) -> RecoveryReadiness:
    """Evaluate non-authorizing declarations against a separately trusted runtime registry.

    The declarative document contributes coverage evidence only. Executable authority remains
    exclusively in runtime_bindings. Bindings are keyed by complete
    (tool_id, action_id, version) identity and must match policy metadata plus trusted
    operation identifiers before they count as runtime-ready.
    """

    items = tuple(declarations)
    counts = {recovery_class: 0 for recovery_class in RecoveryClass}
    structurally_recoverable = 0
    human_approval_required = 0
    missing: list[str] = []
    blockers: list[str] = []

    seen: set[RuntimeBindingKey] = set()
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
        if declaration.action_approval_required or declaration.recovery_approval_required:
            human_approval_required += 1

        binding = runtime_bindings.get(identity)
        if binding is None:
            missing.append(label)
            blockers.append(f"missing_runtime_binding:{label}")
            continue
        try:
            bind_recovery_contract(declaration, binding)
        except ValueError:
            missing.append(label)
            blockers.append(f"runtime_binding_mismatch:{label}")

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
