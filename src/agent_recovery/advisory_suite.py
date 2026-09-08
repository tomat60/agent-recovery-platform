from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .advisory_benchmark import AdvisoryBenchmarkAggregate, aggregate_advisory_scores, score_advisory_chain
from .advisory_fixture import AdvisoryBenchmarkFixture
from .advisory_gate import AdvisoryGateDecision
from .investigation import AgentProposal
from .strands_recovery_planner import RecoveryPlannerResult
from .strands_skeptic import SkepticResult


@dataclass(frozen=True)
class AdvisoryScenarioOutputs:
    investigator: AgentProposal
    planner: RecoveryPlannerResult
    skeptic: SkepticResult
    decision: AdvisoryGateDecision


def score_advisory_fixture_suite(
    fixtures: tuple[AdvisoryBenchmarkFixture, ...],
    outputs_by_scenario: Mapping[str, AdvisoryScenarioOutputs],
) -> AdvisoryBenchmarkAggregate:
    """Score an exact versioned fixture suite against already-produced advisory outputs.

    This function is measurement-only. It validates exact scenario coverage and delegates to the
    incident-bound scorer; it cannot create approvals, execute recovery, or restore authority.
    """

    fixture_ids = tuple(fixture.scenario_id for fixture in fixtures)
    if not fixture_ids:
        raise ValueError("at least one advisory fixture is required")
    if len(set(fixture_ids)) != len(fixture_ids):
        raise ValueError("advisory fixture suite has duplicate scenario IDs")

    supplied_ids = set(outputs_by_scenario)
    expected_ids = set(fixture_ids)
    if supplied_ids != expected_ids:
        missing = sorted(expected_ids - supplied_ids)
        extra = sorted(supplied_ids - expected_ids)
        raise ValueError(
            "advisory outputs must cover the fixture suite exactly; "
            f"missing={missing}, extra={extra}"
        )

    scores = []
    for fixture in fixtures:
        outputs = outputs_by_scenario[fixture.scenario_id]
        scores.append(
            score_advisory_chain(
                fixture.ground_truth,
                investigator=outputs.investigator,
                planner=outputs.planner,
                skeptic=outputs.skeptic,
                decision=outputs.decision,
            )
        )
    return aggregate_advisory_scores(scores)
