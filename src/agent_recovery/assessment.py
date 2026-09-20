from __future__ import annotations

from typing import Any

from agent_recovery.readiness import RecoveryReadiness


CLAIM_LIMITS = (
    "synthetic_owned_environment_only",
    "no_production_security_effectiveness_claim",
    "structural_declarations_do_not_grant_runtime_authority",
    "irreversible_effects_are_residual_risk_not_undo",
)


def build_recoverability_assessment(
    readiness: RecoveryReadiness,
    sandbox_report: dict[str, Any],
) -> dict[str, Any]:
    """Compose existing deterministic evidence into a customer-facing assessment model."""

    status = sandbox_report["operator_status"]
    residuals = tuple(
        sorted(
            item["action_type"]
            for item in sandbox_report["operator_side_effects"]
            if item.get("irreversible") is True
        )
    )

    remediation = [
        {
            "priority": "P0",
            "kind": "readiness_blocker",
            "evidence": blocker,
        }
        for blocker in readiness.blockers
    ]
    remediation.extend(
        {
            "priority": "P1",
            "kind": "irreversible_residual",
            "evidence": effect,
        }
        for effect in residuals
    )

    return {
        "assessment_version": "1",
        "environment": "synthetic_owned_sandbox",
        "readiness": {
            "total_actions": readiness.total_actions,
            "structurally_recoverable": readiness.structurally_recoverable,
            "recoverability_fraction": readiness.recoverability_fraction,
            "reversible": readiness.reversible,
            "compensatable": readiness.compensatable,
            "irreversible": readiness.irreversible,
            "human_approval_required": readiness.human_approval_required,
            "missing_runtime_bindings": readiness.missing_runtime_bindings,
            "blockers": readiness.blockers,
        },
        "controlled_incident": {
            "scenario": sandbox_report["scenario"],
            "incident_id": sandbox_report["incident_id"],
            "recovery_outcomes": sandbox_report["recovery_outcomes"],
            "containment_active": status["containment_active"],
            "verification_status": status["verification_status"],
            "authority": sandbox_report["authority"],
            "irreversible_residuals": residuals,
        },
        "remediation": tuple(remediation),
        "claim_limits": CLAIM_LIMITS,
    }
