from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from agent_recovery.ingestion import IngestionError

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "normalize_otlp_trace_export.py"
spec = importlib.util.spec_from_file_location("normalize_otlp_trace_export", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def _text(key: str, value: str) -> dict[str, object]:
    return {"key": key, "value": {"stringValue": value}}


def _payload() -> dict[str, object]:
    return {
        "resourceSpans": [
            {
                "scopeSpans": [
                    {
                        "spans": [
                            {
                                "traceId": "5b8efff798038103d269b633813fc60c",
                                "spanId": "eee19b7ec3c1b174",
                                "startTimeUnixNano": "0",
                                "attributes": [
                                    _text("agent.recovery.incident_id", "inc-otlp"),
                                    _text("agent.recovery.tool_id", "crm.contacts"),
                                    _text("agent.recovery.action_type", "contact.update"),
                                    _text("agent.recovery.contract_version", "1"),
                                    _text("agent.recovery.agent_id", "sales-agent"),
                                    {
                                        "key": "agent.recovery.params",
                                        "value": {
                                            "kvlistValue": {
                                                "values": [_text("contact_id", "c-7")]
                                            }
                                        },
                                    },
                                ],
                            }
                        ]
                    }
                ]
            }
        ]
    }


def test_build_evidence_is_deterministic_and_non_authorizing() -> None:
    evidence = module.build_evidence(_payload())

    assert evidence["schema_version"] == "agent-recovery-otlp-evidence/v1"
    assert evidence["authorization_effect"] == "none"
    assert evidence["observation_count"] == 1
    observation = evidence["observations"][0]
    assert observation["observation_id"] == (
        "otel:5b8efff798038103d269b633813fc60c:eee19b7ec3c1b174"
    )
    assert observation["authorization_effect"] == "none"
    assert len(observation["provenance_digest"]) == 64


def test_reproduce_writes_the_exact_evidence_artifact(tmp_path: Path) -> None:
    source = tmp_path / "trace.json"
    output = tmp_path / "evidence.json"
    source.write_text(json.dumps(_payload()), encoding="utf-8")

    evidence = module.reproduce(source, output)

    assert json.loads(output.read_text(encoding="utf-8")) == evidence


def test_build_evidence_fails_closed_on_malformed_recovery_span() -> None:
    payload = _payload()
    span = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][0]
    span["attributes"] = [
        item
        for item in span["attributes"]
        if item["key"] != "agent.recovery.contract_version"
    ]

    with pytest.raises(IngestionError, match="contract_version"):
        module.build_evidence(payload)
