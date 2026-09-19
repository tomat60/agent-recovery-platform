from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict
from typing import Any

from .readiness import RuntimeBindingKey, evaluate_recovery_readiness
from .recovery_contract import RecoveryContract
from .runtime_binding import TrustedRuntimeBinding


def recovery_readiness_report(
    declarations: Iterable[RecoveryContract],
    *,
    runtime_bindings: Mapping[RuntimeBindingKey, TrustedRuntimeBinding],
) -> dict[str, Any]:
    """Return deterministic CI evidence for recoverability coverage and blockers.

    The report is deliberately non-authorizing. It exposes coverage and exact blocker
    labels only; trusted runtime objects and executable callables never leave the registry.
    """

    readiness = evaluate_recovery_readiness(
        declarations,
        runtime_bindings=runtime_bindings,
    )
    payload = asdict(readiness)
    payload["recoverability_fraction"] = readiness.recoverability_fraction
    payload["ready"] = not readiness.blockers
    payload["authority"] = "none"
    return payload


def assert_recovery_ready(
    declarations: Iterable[RecoveryContract],
    *,
    runtime_bindings: Mapping[RuntimeBindingKey, TrustedRuntimeBinding],
) -> dict[str, Any]:
    """Fail a CI gate when any declared action lacks trusted recovery readiness."""

    report = recovery_readiness_report(
        declarations,
        runtime_bindings=runtime_bindings,
    )
    if not report["ready"]:
        blockers = ", ".join(report["blockers"])
        raise RuntimeError(f"recovery readiness blocked: {blockers}")
    return report
