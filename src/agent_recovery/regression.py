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


PORTABLE_REGRESSION_SCHEMA_VERSION = (
    "agent-recovery-portable-incident-regression/v1"
)


@dataclass(frozen=True)
class PortableIncidentRegression:
    schema_version: str
    regression_id: str
    source_incident_id: str
    scenario: str
    evidence_refs: tuple[str, ...]
    causal_dependencies: tuple[str, ...]
    recovery_obligations: tuple[str, ...]
    residual_expectations: tuple[str, ...]
    replay_inputs: tuple[str, ...]
    restoration_scopes: tuple[str, ...]
    expected_invariants: tuple[str, ...]
    authorization_effect: str
    fingerprint: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "regression_id": self.regression_id,
            "source_incident_id": self.source_incident_id,
            "scenario": self.scenario,
            "evidence_refs": list(self.evidence_refs),
            "causal_dependencies": list(self.causal_dependencies),
            "recovery_obligations": list(self.recovery_obligations),
            "residual_expectations": list(self.residual_expectations),
            "replay_inputs": list(self.replay_inputs),
            "restoration_scopes": list(self.restoration_scopes),
            "expected_invariants": list(self.expected_invariants),
            "authorization_effect": self.authorization_effect,
            "fingerprint": self.fingerprint,
        }


def _normalize_package_items(
    values: tuple[str, ...],
    label: str,
    *,
    required: bool,
) -> tuple[str, ...]:
    if not isinstance(values, tuple) or any(not isinstance(item, str) for item in values):
        raise ValueError(f"{label} must be a tuple of strings")
    normalized = tuple(sorted({item.strip() for item in values if item.strip()}))
    if required and not normalized:
        raise ValueError(f"at least one {label} entry is required")
    return normalized


def build_portable_incident_regression(
    *,
    source_incident_id: str,
    scenario: str,
    evidence_refs: tuple[str, ...],
    causal_dependencies: tuple[str, ...],
    recovery_obligations: tuple[str, ...],
    residual_expectations: tuple[str, ...],
    replay_inputs: tuple[str, ...],
    restoration_scopes: tuple[str, ...],
    expected_invariants: tuple[str, ...],
) -> PortableIncidentRegression:
    """Build a portable, non-authorizing incident-to-regression package.

    References identify retained evidence and replay inputs; they do not embed
    private incident payloads or grant recovery/restoration authority.
    """

    if not isinstance(source_incident_id, str) or not source_incident_id.strip():
        raise ValueError("source_incident_id is required")
    if not isinstance(scenario, str) or not scenario.strip():
        raise ValueError("scenario is required")

    canonical = {
        "schema_version": PORTABLE_REGRESSION_SCHEMA_VERSION,
        "source_incident_id": source_incident_id.strip(),
        "scenario": scenario.strip(),
        "evidence_refs": list(
            _normalize_package_items(evidence_refs, "evidence reference", required=True)
        ),
        "causal_dependencies": list(
            _normalize_package_items(
                causal_dependencies,
                "causal dependency",
                required=False,
            )
        ),
        "recovery_obligations": list(
            _normalize_package_items(
                recovery_obligations,
                "recovery obligation",
                required=True,
            )
        ),
        "residual_expectations": list(
            _normalize_package_items(
                residual_expectations,
                "residual expectation",
                required=True,
            )
        ),
        "replay_inputs": list(
            _normalize_package_items(replay_inputs, "replay input", required=True)
        ),
        "restoration_scopes": list(
            _normalize_package_items(
                restoration_scopes,
                "restoration scope",
                required=True,
            )
        ),
        "expected_invariants": list(
            _normalize_package_items(
                expected_invariants,
                "expected invariant",
                required=True,
            )
        ),
        "authorization_effect": "none",
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    fingerprint = hashlib.sha256(encoded).hexdigest()

    return PortableIncidentRegression(
        regression_id=f"regpkg-{fingerprint[:16]}",
        fingerprint=fingerprint,
        **{
            key: tuple(value) if isinstance(value, list) else value
            for key, value in canonical.items()
        },
    )


def verify_portable_incident_regression(
    payload: dict[str, Any],
) -> PortableIncidentRegression:
    """Rebuild and exactly verify a serialized portable regression package."""

    expected_fields = {
        "schema_version",
        "regression_id",
        "source_incident_id",
        "scenario",
        "evidence_refs",
        "causal_dependencies",
        "recovery_obligations",
        "residual_expectations",
        "replay_inputs",
        "restoration_scopes",
        "expected_invariants",
        "authorization_effect",
        "fingerprint",
    }
    if not isinstance(payload, dict) or set(payload) != expected_fields:
        raise ValueError("portable incident regression fields mismatch")
    if payload["schema_version"] != PORTABLE_REGRESSION_SCHEMA_VERSION:
        raise ValueError("portable incident regression schema_version mismatch")
    if payload["authorization_effect"] != "none":
        raise ValueError("portable incident regression must remain non-authorizing")

    list_fields = (
        "evidence_refs",
        "causal_dependencies",
        "recovery_obligations",
        "residual_expectations",
        "replay_inputs",
        "restoration_scopes",
        "expected_invariants",
    )
    for field in list_fields:
        value = payload[field]
        if not isinstance(value, list) or any(
            not isinstance(item, str) for item in value
        ):
            raise ValueError(f"portable incident regression {field} must be strings")

    rebuilt = build_portable_incident_regression(
        source_incident_id=payload["source_incident_id"],
        scenario=payload["scenario"],
        evidence_refs=tuple(payload["evidence_refs"]),
        causal_dependencies=tuple(payload["causal_dependencies"]),
        recovery_obligations=tuple(payload["recovery_obligations"]),
        residual_expectations=tuple(payload["residual_expectations"]),
        replay_inputs=tuple(payload["replay_inputs"]),
        restoration_scopes=tuple(payload["restoration_scopes"]),
        expected_invariants=tuple(payload["expected_invariants"]),
    )
    if payload != rebuilt.to_dict():
        raise ValueError("portable incident regression package mismatch")
    return rebuilt
