from __future__ import annotations

from .advisory_gate import AdvisoryGateDecision
from .regression import IncidentRegression, build_incident_regression

_REJECTION_INVARIANTS = (
    "model output is never authorization",
    "rejected advisory exposes no candidate recovery plan",
    "unsupported or uncertain advisory claims remain rejected",
)


def build_rejected_advisory_regression(
    *,
    source_incident_id: str,
    scenario: str,
    decision: AdvisoryGateDecision,
    evidence_refs: tuple[str, ...],
) -> IncidentRegression:
    """Turn a fail-closed advisory rejection into a deterministic replay contract.

    Only genuine rejections without candidate-plan exposure are eligible. This preserves the
    trust boundary: a plausible model-generated recovery proposal cannot become authorization or
    be recorded as an accepted recovery merely because it sounds correct.
    """

    if decision.accepted:
        raise ValueError("accepted advisory decisions are not rejection regressions")
    if decision.candidate_plan is not None:
        raise ValueError("rejected advisory must not expose a candidate recovery plan")
    if not decision.reasons:
        raise ValueError("rejected advisory requires deterministic rejection reasons")

    return build_incident_regression(
        source_incident_id=source_incident_id,
        scenario=scenario,
        evidence_refs=evidence_refs,
        expected_invariants=_REJECTION_INVARIANTS,
    )
