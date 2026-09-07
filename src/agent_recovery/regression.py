from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class IncidentRegression:
    regression_id: str
    source_incident_id: str
    scenario: str
    evidence_refs: tuple[str, ...]
    expected_invariants: tuple[str, ...]
    fingerprint: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_incident_regression(
    *,
    source_incident_id: str,
    scenario: str,
    evidence_refs: tuple[str, ...],
    expected_invariants: tuple[str, ...],
) -> IncidentRegression:
    """Convert verified incident evidence into a deterministic regression contract.

    This artifact does not authorize recovery or claim that an incident is repaired.
    It records the evidence anchors and invariants a future replay/test must prove.
    """

    incident = source_incident_id.strip()
    scenario_name = scenario.strip()
    evidence = tuple(sorted({ref.strip() for ref in evidence_refs if ref.strip()}))
    invariants = tuple(sorted({item.strip() for item in expected_invariants if item.strip()}))

    if not incident:
        raise ValueError("source_incident_id is required")
    if not scenario_name:
        raise ValueError("scenario is required")
    if not evidence:
        raise ValueError("at least one evidence reference is required")
    if not invariants:
        raise ValueError("at least one expected invariant is required")

    canonical = {
        "source_incident_id": incident,
        "scenario": scenario_name,
        "evidence_refs": evidence,
        "expected_invariants": invariants,
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    fingerprint = hashlib.sha256(encoded).hexdigest()

    return IncidentRegression(
        regression_id=f"reg-{fingerprint[:16]}",
        source_incident_id=incident,
        scenario=scenario_name,
        evidence_refs=evidence,
        expected_invariants=invariants,
        fingerprint=fingerprint,
    )
