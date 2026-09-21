from agent_recovery.assessment import build_recoverability_assessment
from agent_recovery.assessment_report import render_recoverability_assessment
from agent_recovery.pilot_sandbox import run_multisurface_recovery_sandbox
from agent_recovery.readiness import RecoveryReadiness


def readiness(*, blockers=(), missing=()):
    return RecoveryReadiness(
        total_actions=4,
        structurally_recoverable=3,
        reversible=2,
        compensatable=1,
        irreversible=1,
        human_approval_required=1,
        missing_runtime_bindings=tuple(missing),
        blockers=tuple(blockers),
    )


def test_report_keeps_residuals_and_claim_limits_visible():
    assessment = build_recoverability_assessment(
        readiness(), run_multisurface_recovery_sandbox()
    )

    rendered = render_recoverability_assessment(assessment)

    assert "Evidence scenario: `owned_sales_ops_multisurface_recovery`" in rendered
    assert "Evidence incident: `sandbox-sales-ops-incident`" in rendered
    assert f"Evidence SHA-256: `{assessment['evidence_identity']['sha256']}`" in rendered
    assert "Recoverability coverage: 75%" in rendered
    assert "`external_communication`: `residual`" in rendered
    assert "### Irreversible residuals\n\n- `external_communication`" in rendered
    assert "Restored authority: `none`" in rendered
    assert "`no_production_security_effectiveness_claim`" in rendered
    assert "does not grant runtime authority" in rendered


def test_report_promotes_missing_runtime_binding_as_p0_remediation():
    blocker = "missing_runtime_binding:mail.send:write@1"
    assessment = build_recoverability_assessment(
        readiness(blockers=(blocker,), missing=("mail.send:write@1",)),
        run_multisurface_recovery_sandbox(),
    )

    rendered = render_recoverability_assessment(assessment)

    assert "Missing trusted runtime bindings: 1" in rendered
    assert f"P0 `readiness_blocker`: `{blocker}`" in rendered
    assert "P1 `irreversible_residual`: `external_communication`" in rendered
