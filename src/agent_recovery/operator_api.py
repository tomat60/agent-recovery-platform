from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict
from typing import Any

from .readiness import RuntimeBindingKey, evaluate_recovery_readiness
from .recovery_contract import RecoveryContract
from .runtime_binding import TrustedRuntimeBinding


def recovery_readiness_response(
    declarations: Iterable[RecoveryContract],
    *,
    runtime_bindings: Mapping[RuntimeBindingKey, TrustedRuntimeBinding],
) -> dict[str, Any]:
    """Return a deterministic, read-only operator view of recovery readiness.

    This boundary exposes coverage evidence and blockers only. It does not return executable
    runtime bindings, approvals, callables, or any other object that can grant action authority.
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
