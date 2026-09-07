from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .catalog import synthetic_contracts
from .engine import RecoveryEngine
from .simulator import SyntheticEnterprise


@dataclass(frozen=True)
class FalsePositiveContainmentScore:
    scenario: str
    malicious_scopes_expected_contained: int
    malicious_scopes_contained: int
    benign_scopes_observed: int
    benign_scopes_incorrectly_contained: int
    false_positive_containment_rate: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_false_positive_containment_scenario() -> FalsePositiveContainmentScore:
    """Measure deterministic containment-scope precision without claiming detection quality.

    One compromised agent is explicitly contained while three known-benign agent scopes
    remain outside containment. This measures whether the deterministic containment
    primitive overreaches once the incident scope is known; it does not measure whether
    an upstream detector correctly identified the malicious agent.
    """

    engine = RecoveryEngine(SyntheticEnterprise())
    for contract in synthetic_contracts():
        engine.register(contract)

    incident_id = "bench-false-positive-containment"
    compromised_scope = "agent:support-agent"
    benign_scopes = (
        "agent:billing-agent",
        "agent:catalog-agent",
        "agent:analytics-agent",
    )

    engine.contain(
        incident_id,
        compromised_scope,
        reason="synthetic benchmark marks only the support agent as compromised",
    )

    malicious_scopes_contained = int(engine.is_contained(compromised_scope))
    benign_scopes_incorrectly_contained = sum(
        engine.is_contained(scope) for scope in benign_scopes
    )

    return FalsePositiveContainmentScore(
        scenario="known_bad_agent_scoped_containment",
        malicious_scopes_expected_contained=1,
        malicious_scopes_contained=malicious_scopes_contained,
        benign_scopes_observed=len(benign_scopes),
        benign_scopes_incorrectly_contained=benign_scopes_incorrectly_contained,
        false_positive_containment_rate=(
            benign_scopes_incorrectly_contained / len(benign_scopes)
        ),
    )
