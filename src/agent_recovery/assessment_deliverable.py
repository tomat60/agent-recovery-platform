from __future__ import annotations

from typing import Any


def render_assessment_markdown(assessment: dict[str, Any]) -> str:
    """Render the validated assessment artifact as a buyer-readable Markdown report."""

    coverage = assessment["recoverability_coverage"]
    incident = assessment["controlled_incident"]
    recovery = assessment["recovery"]
    replay = assessment["replay_regression"]
    restoration = assessment["restoration"]
    residual = assessment["residual_risk"]

    lines = [
        "# Agent Recoverability Assessment",
        "",
        f"Evidence mode: `{assessment['assessment_mode']}`",
        f"Scenario: `{assessment['scenario']}`",
        f"Schema: `{assessment['schema_version']}`",
        "",
        "## Recoverability coverage",
        "",
        f"- Consequential actions: {coverage['consequential_actions']}",
        f"- Verified recoveries: {coverage['verified_recoveries']}",
        f"- Coverage: {coverage['ratio']:.0%}",
        "",
        "## Controlled incident",
        "",
        f"- Incident: `{incident['incident_id']}`",
        f"- Expected consequential actions: {incident['expected_actions']}",
        f"- Verified recoveries: {recovery['verified_recoveries']}",
        f"- Replay verified: `{str(replay['verified']).lower()}`",
        f"- Restored downstream authorities: {restoration['restored_downstream_authorities']}",
        f"- Root authority restored: `{str(restoration['root_authority_restored']).lower()}`",
        "",
        "## Residual risk",
        "",
    ]
    effects = residual["platform_residual_effects"]
    if effects:
        lines.extend(f"- `{effect}`" for effect in effects)
    else:
        lines.append("- No platform residual effects represented by this evidence.")

    lines.extend(["", "## Prioritized remediation", ""])
    for item in assessment["prioritized_remediation"]:
        lines.append(
            f"- {item['priority']} `{item['blocker']}`: {item['action']}"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            (
                "- Bounded downstream restoration verified: "
                f"`{str(assessment['decision']['bounded_downstream_restoration_verified']).lower()}`"
            ),
            "- Production security effectiveness claimed: `false`",
            "",
            "## Claim boundary",
            "",
            str(assessment["claim_boundary"]),
            "",
            (
                "This report is generated from validated owned-sandbox evidence. "
                "It grants no runtime authority and must not be represented as production security evidence."
            ),
            "",
        ]
    )
    return "\n".join(lines)
