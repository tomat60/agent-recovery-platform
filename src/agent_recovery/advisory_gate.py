from __future__ import annotations

from dataclasses import dataclass

from .investigation import (
    AgentProposal,
    EvidenceView,
    InvestigationBoundaryError,
    bind_agent_proposal,
)
from .strands_recovery_planner import ProposedRecoveryStep, RecoveryPlannerResult
from .strands_skeptic import SkepticResult


class AdvisoryGateError(ValueError):
    """Raised when advisory output cannot be promoted to a candidate recovery plan."""


@dataclass(frozen=True)
class CandidateRecoveryPlan:
    incident_id: str
    summary: str
    steps: tuple[ProposedRecoveryStep, ...]
    residual_risks: tuple[str, ...]
    evidence_event_ids: tuple[str, ...]
    skeptic_evidence_event_ids: tuple[str, ...]


@dataclass(frozen=True)
class AdvisoryGateDecision:
    accepted: bool
    reasons: tuple[str, ...]
    candidate_plan: CandidateRecoveryPlan | None


def _rebind(view: EvidenceView, proposal: AgentProposal, *, role: str) -> AgentProposal:
    if proposal.incident_id != view.incident_id:
        raise AdvisoryGateError(f"{role} proposal belongs to a different incident")
    if proposal.role != role:
        raise AdvisoryGateError(f"expected {role} proposal, got {proposal.role}")
    try:
        return bind_agent_proposal(
            view,
            role=role,
            summary=proposal.summary,
            evidence_event_ids=proposal.evidence_event_ids,
        )
    except InvestigationBoundaryError as exc:
        raise AdvisoryGateError(str(exc)) from exc


def _validate_steps(
    view: EvidenceView,
    steps: tuple[ProposedRecoveryStep, ...],
) -> tuple[str, ...]:
    if not steps:
        return ("recovery planner produced no steps",)
    allowed_evidence = {event.event_id for event in view.events}
    seen: set[str] = set()
    reasons: list[str] = []
    for step in steps:
        if not step.step_id.strip() or step.step_id in seen:
            reasons.append("recovery step IDs must be non-empty and unique")
            continue
        if not step.description.strip():
            reasons.append(f"recovery step {step.step_id} has no description")
        unknown_evidence = sorted(set(step.evidence_event_ids) - allowed_evidence)
        if not step.evidence_event_ids:
            reasons.append(f"recovery step {step.step_id} cites no evidence")
        elif unknown_evidence:
            reasons.append(
                f"recovery step {step.step_id} cites evidence outside incident view: "
                f"{unknown_evidence}"
            )
        unknown_dependencies = sorted(set(step.depends_on) - seen)
        if unknown_dependencies:
            reasons.append(
                f"recovery step {step.step_id} has unresolved dependencies: "
                f"{unknown_dependencies}"
            )
        seen.add(step.step_id)
    return tuple(dict.fromkeys(reasons))


def evaluate_advisory_recovery_plan(
    view: EvidenceView,
    *,
    investigator: AgentProposal,
    planner: RecoveryPlannerResult,
    skeptic: SkepticResult,
    investigator_claim_id: str = "investigator",
    planner_claim_id: str = "recovery_plan",
) -> AdvisoryGateDecision:
    """Fail closed unless independent evidence review supports a candidate-only plan.

    This gate never executes recovery, mints approval, consumes authority, or marks an incident
    recovered. A successful decision only makes the planner output eligible for the later
    deterministic Recovery Contract / approval / execution boundary.
    """

    investigator_bound = _rebind(view, investigator, role="investigator")
    planner_bound = _rebind(view, planner.proposal, role="recovery_planner")
    skeptic_bound = _rebind(view, skeptic.proposal, role="skeptic")

    if not investigator_claim_id.strip() or not planner_claim_id.strip():
        raise AdvisoryGateError("claim IDs are required")
    if investigator_claim_id == planner_claim_id:
        raise AdvisoryGateError("investigator and recovery-plan claim IDs must be distinct")

    reasons = list(_validate_steps(view, planner.steps))
    expected_claims = {investigator_claim_id, planner_claim_id}
    challenges = {challenge.claim_id: challenge for challenge in skeptic.challenges}
    if len(challenges) != len(skeptic.challenges):
        reasons.append("skeptic challenges must use unique claim IDs")
    if set(challenges) != expected_claims:
        reasons.append("skeptic must review exactly the investigator and recovery-plan claims")

    allowed_evidence = {event.event_id for event in view.events}
    for claim_id in sorted(expected_claims):
        challenge = challenges.get(claim_id)
        if challenge is None:
            continue
        unknown_evidence = sorted(set(challenge.evidence_event_ids) - allowed_evidence)
        if not challenge.evidence_event_ids:
            reasons.append(f"skeptic challenge {claim_id} cites no evidence")
        elif unknown_evidence:
            reasons.append(
                f"skeptic challenge {claim_id} cites evidence outside incident view: "
                f"{unknown_evidence}"
            )
        if challenge.verdict != "supported":
            reasons.append(f"skeptic verdict for {claim_id} is {challenge.verdict}")

    if reasons:
        return AdvisoryGateDecision(
            accepted=False,
            reasons=tuple(dict.fromkeys(reasons)),
            candidate_plan=None,
        )

    evidence_ids = tuple(
        dict.fromkeys(
            (
                *investigator_bound.evidence_event_ids,
                *planner_bound.evidence_event_ids,
                *(event_id for step in planner.steps for event_id in step.evidence_event_ids),
            )
        )
    )
    skeptic_evidence_ids = tuple(
        dict.fromkeys(
            (
                *skeptic_bound.evidence_event_ids,
                *(
                    event_id
                    for challenge in skeptic.challenges
                    for event_id in challenge.evidence_event_ids
                ),
            )
        )
    )
    return AdvisoryGateDecision(
        accepted=True,
        reasons=(),
        candidate_plan=CandidateRecoveryPlan(
            incident_id=view.incident_id,
            summary=planner_bound.summary,
            steps=planner.steps,
            residual_risks=planner.residual_risks,
            evidence_event_ids=evidence_ids,
            skeptic_evidence_event_ids=skeptic_evidence_ids,
        ),
    )
