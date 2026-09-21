from copy import deepcopy

from agent_recovery.assessment import build_recoverability_assessment
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


def test_assessment_composes_readiness_and_controlled_incident_evidence():
    report = build_recoverability_assessment(
        readiness(), run_multisurface_recovery_sandbox()
    )

    assert report["assessment_version"] == "1"
    assert report["environment"] == "synthetic_owned_sandbox"
    assert report["evidence_identity"]["scenario"] == "owned_sales_ops_multisurface_recovery"
    assert report["evidence_identity"]["incident_id"] == "sandbox-sales-ops-incident"
    assert len(report["evidence_identity"]["sha256"]) == 64
    assert report["readiness"]["recoverability_fraction"] == 0.75
    assert report["readiness"]["blockers"] == ()

    incident = report["controlled_incident"]
    assert incident["recovery_outcomes"] == {
        "memory": "verified",
        "crm": "verified",
        "external_communication": "residual",
    }
    assert incident["containment_active"] is True
    assert incident["verification_status"] == "verified"
    assert incident["authority"] == "none"
    assert incident["irreversible_residuals"] == ("external_communication",)

    assert report["remediation"] == (
        {
            "priority": "P1",
            "kind": "irreversible_residual",
            "evidence": "external_communication",
        },
    )
    assert "no_production_security_effectiveness_claim" in report["claim_limits"]
    assert "irreversible_effects_are_residual_risk_not_undo" in report["claim_limits"]


def test_assessment_evidence_digest_is_deterministic_and_changes_with_evidence():
    sandbox = run_multisurface_recovery_sandbox()
    first = build_recoverability_assessment(readiness(), sandbox)
    second = build_recoverability_assessment(readiness(), deepcopy(sandbox))

    assert first["evidence_identity"]["sha256"] == second["evidence_identity"]["sha256"]

    changed = deepcopy(sandbox)
    changed["recovery_outcomes"]["crm"] = "failed"
    changed_report = build_recoverability_assessment(readiness(), changed)

    assert changed_report["evidence_identity"]["sha256"] != first["evidence_identity"]["sha256"]


def test_assessment_evidence_digest_changes_with_readiness_evidence():
    sandbox = run_multisurface_recovery_sandbox()
    baseline = build_recoverability_assessment(readiness(), sandbox)
    blocker = "missing_runtime_binding:mail.send:write@1"
    changed = build_recoverability_assessment(
        readiness(blockers=(blocker,), missing=("mail.send:write@1",)),
        sandbox,
    )

    assert changed["evidence_identity"]["sha256"] != baseline["evidence_identity"]["sha256"]


def test_assessment_exposes_exact_digest_evidence_manifest():
    sandbox = run_multisurface_recovery_sandbox()
    report = build_recoverability_assessment(readiness(), sandbox)
    manifest = report["evidence_identity"]["manifest"]

    assert manifest["readiness"] == report["readiness"]
    assert manifest["controlled_incident"]["scenario"] == sandbox["scenario"]
    assert manifest["controlled_incident"]["incident_id"] == sandbox["incident_id"]
    assert manifest["controlled_incident"]["recovery_outcomes"] == sandbox["recovery_outcomes"]
    assert manifest["controlled_incident"]["operator_status"] == sandbox["operator_status"]
    assert manifest["controlled_incident"]["operator_side_effects"] == sandbox["operator_side_effects"]
    assert manifest["controlled_incident"]["authority"] == sandbox["authority"]


def test_assessment_keeps_missing_runtime_binding_as_p0_blocker():
    blocker = "missing_runtime_binding:mail.send:write@1"
    report = build_recoverability_assessment(
        readiness(blockers=(blocker,), missing=("mail.send:write@1",)),
        run_multisurface_recovery_sandbox(),
    )

    assert report["readiness"]["missing_runtime_bindings"] == ("mail.send:write@1",)
    assert report["readiness"]["blockers"] == (blocker,)
    assert report["remediation"][0] == {
        "priority": "P0",
        "kind": "readiness_blocker",
        "evidence": blocker,
    }
    assert report["controlled_incident"]["authority"] == "none"
