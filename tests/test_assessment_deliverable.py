from scripts.build_recoverability_assessment import build_assessment, validate_assessment
from agent_recovery.assessment_deliverable import render_assessment_markdown


def test_buyer_deliverable_preserves_evidence_and_claim_boundary():
    assessment = build_assessment()
    validate_assessment(assessment)

    rendered = render_assessment_markdown(assessment)

    assert "# Agent Recoverability Assessment" in rendered
    assert f"Scenario: `{assessment['scenario']}`" in rendered
    assert "## Recoverability coverage" in rendered
    assert "## Residual risk" in rendered
    assert "## Prioritized remediation" in rendered
    assert "Production security effectiveness claimed: `false`" in rendered
    assert "grants no runtime authority" in rendered
    for effect in assessment["residual_risk"]["platform_residual_effects"]:
        assert f"`{effect}`" in rendered
