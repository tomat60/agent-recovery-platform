from __future__ import annotations

from typing import Any

from .assessment import build_recoverability_assessment
from .pilot_sandbox import run_multisurface_recovery_sandbox
from .readiness import RecoveryReadiness


def build_app_fixture() -> dict[str, Any]:
    """Build one read-only commercial app payload from accepted product evidence."""

    readiness = RecoveryReadiness(
        total_actions=4,
        structurally_recoverable=3,
        reversible=2,
        compensatable=1,
        irreversible=1,
        human_approval_required=2,
        missing_runtime_bindings=(),
        blockers=(),
    )
    sandbox = run_multisurface_recovery_sandbox()
    assessment = build_recoverability_assessment(readiness, sandbox)

    return {
        "fixture_version": "1",
        "source": "owned_deterministic_sandbox",
        "product": {
            "name": "Agent Recovery Platform",
            "mode": "read_only_operator_console",
            "authority": "none",
        },
        "overview": {
            "recoverability_fraction": assessment["readiness"]["recoverability_fraction"],
            "consequential_actions": assessment["readiness"]["total_actions"],
            "structurally_recoverable": assessment["readiness"]["structurally_recoverable"],
            "missing_runtime_bindings": len(
                assessment["readiness"]["missing_runtime_bindings"]
            ),
            "containment_active": assessment["controlled_incident"]["containment_active"],
            "verification_status": assessment["controlled_incident"]["verification_status"],
            "irreversible_residual_count": len(
                assessment["controlled_incident"]["irreversible_residuals"]
            ),
            "restoration_eligible": assessment["controlled_incident"][
                "restoration_eligible"
            ],
        },
        "incident": {
            "scenario": sandbox["scenario"],
            "incident_id": sandbox["incident_id"],
            "status": sandbox["operator_status"],
            "next_action": sandbox["operator_next_action"],
            "recovery_candidates": sandbox["operator_recovery_candidates"],
            "side_effects": sandbox["operator_side_effects"],
            "recovery_outcomes": sandbox["recovery_outcomes"],
            "before": sandbox["before"],
            "after_incident": sandbox["after_incident"],
            "after_recovery": sandbox["after_recovery"],
            "authority": sandbox["authority"],
        },
        "assessment": assessment,
    }
