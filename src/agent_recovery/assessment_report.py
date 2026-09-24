from __future__ import annotations

import hashlib
import json
from typing import Any


def _validate_evidence_identity(report: dict[str, Any]) -> None:
    """Fail closed if buyer-facing assessment evidence is stale or tampered."""

    identity = report["evidence_identity"]
    manifest = identity["manifest"]
    encoded = json.dumps(
        manifest,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    if hashlib.sha256(encoded).hexdigest() != identity["sha256"]:
        raise ValueError("assessment evidence digest mismatch")

    if manifest["readiness"] != report["readiness"]:
        raise ValueError("assessment readiness does not match evidence manifest")

    incident = report["controlled_incident"]
    manifest_incident = manifest["controlled_incident"]
    for field in ("scenario", "incident_id", "recovery_outcomes", "authority"):
        if manifest_incident[field] != incident[field]:
            raise ValueError(f"assessment controlled incident {field} does not match evidence manifest")


def render_recoverability_assessment(report: dict[str, Any]) -> str:
    """Render a deterministic, claim-bounded assessment deliverable."""

    _validate_evidence_identity(report)
    readiness = report["readiness"]
    incident = report["controlled_incident"]
    evidence_identity = report["evidence_identity"]
    remediation = report["remediation"]

    lines = [
        "# Agent Recoverability Assessment",
        "",
        f"Environment: `{report['environment']}`",
        f"Assessment schema: `{report['assessment_version']}`",
        f"Evidence scenario: `{evidence_identity['scenario']}`",
        f"Evidence incident: `{evidence_identity['incident_id']}`",
        f"Evidence SHA-256: `{evidence_identity['sha256']}`",
        "",
        "## Recovery readiness",
        "",
        f"- Consequential actions: {readiness['total_actions']}",
        f"- Structurally recoverable: {readiness['structurally_recoverable']}",
        f"- Recoverability coverage: {readiness['recoverability_fraction']:.0%}",
        f"- Missing trusted runtime bindings: {len(readiness['missing_runtime_bindings'])}",
        "",
        "## Controlled incident evidence",
        "",
        f"- Scenario: `{incident['scenario']}`",
        f"- Incident: `{incident['incident_id']}`",
        f"- Containment active: `{str(incident['containment_active']).lower()}`",
        f"- Verification status: `{incident['verification_status']}`",
        f"- Restored authority: `{incident['authority']}`",
        f"- Restoration eligible: `{str(incident['restoration_eligible']).lower()}`",
        "",
        "### Recovery outcomes",
        "",
    ]
    lines.extend(
        f"- `{surface}`: `{outcome}`"
        for surface, outcome in sorted(incident["recovery_outcomes"].items())
    )

    lines.extend(["", "### Irreversible residuals", ""])
    residuals = incident["irreversible_residuals"]
    if residuals:
        lines.extend(f"- `{effect}`" for effect in residuals)
    else:
        lines.append("- None observed in this controlled incident.")

    lines.extend(["", "## Prioritized remediation", ""])
    if remediation:
        lines.extend(
            f"- {item['priority']} `{item['kind']}`: `{item['evidence']}`"
            for item in remediation
        )
    else:
        lines.append("- No remediation items derived from current evidence.")

    lines.extend(
        [
            "",
            "## Evidence manifest",
            "",
            "The SHA-256 identity above covers this exact canonical evidence manifest:",
            "",
            "```json",
            json.dumps(
                evidence_identity["manifest"],
                sort_keys=True,
                indent=2,
                ensure_ascii=True,
            ),
            "```",
        ]
    )

    lines.extend(["", "## Claim limits", ""])
    lines.extend(f"- `{limit}`" for limit in report["claim_limits"])
    lines.extend(
        [
            "",
            (
                "This report summarizes deterministic evidence from the stated environment. "
                "It does not grant runtime authority or claim production security effectiveness."
            ),
            "",
        ]
    )
    return "\n".join(lines)
