from __future__ import annotations

from dataclasses import dataclass

from .readiness import RecoveryReadiness


@dataclass(frozen=True)
class RecoveryReadinessGate:
    """Deterministic CI decision derived only from Recovery Readiness evidence."""

    passed: bool
    reasons: tuple[str, ...]


def evaluate_readiness_gate(
    readiness: RecoveryReadiness,
    *,
    minimum_recoverability_fraction: float = 1.0,
    allow_irreversible: bool = False,
) -> RecoveryReadinessGate:
    """Fail closed when declared write actions are not recovery-ready.

    This gate is policy over non-authorizing readiness evidence. It never receives or returns
    executable runtime bindings, callables, approvals, or restoration authority.
    """

    if not 0.0 <= minimum_recoverability_fraction <= 1.0:
        raise ValueError("minimum_recoverability_fraction must be between 0 and 1")

    reasons = list(readiness.blockers)
    if readiness.recoverability_fraction < minimum_recoverability_fraction:
        reasons.append(
            "recoverability_below_threshold:"
            f"{readiness.recoverability_fraction:.6f}<"
            f"{minimum_recoverability_fraction:.6f}"
        )
    if readiness.irreversible and not allow_irreversible:
        reasons.append(f"irreversible_actions:{readiness.irreversible}")

    return RecoveryReadinessGate(
        passed=not reasons,
        reasons=tuple(sorted(set(reasons))),
    )
