from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any

from .ingestion import ActionObservation, IngestionError

INCIDENT_ID = "agent.recovery.incident_id"
TOOL_ID = "agent.recovery.tool_id"
ACTION_TYPE = "agent.recovery.action_type"
CONTRACT_VERSION = "agent.recovery.contract_version"
AGENT_ID = "agent.recovery.agent_id"
PARAMS = "agent.recovery.params"
AUTHORITY_SCOPE = "agent.recovery.authority_scope"
RESOURCE_KEYS = "agent.recovery.resource_keys"
OBSERVED_AT = "agent.recovery.observed_at"


def _required_text(values: Mapping[str, Any], key: str) -> str:
    value = values.get(key)
    if not isinstance(value, str) or not value.strip():
        raise IngestionError(f"OTel attribute {key} is required")
    return value.strip()


def _optional_text(values: Mapping[str, Any], key: str) -> str | None:
    value = values.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise IngestionError(f"OTel attribute {key} must be a non-empty string")
    return value.strip()


def _observed_at(span: Mapping[str, Any], attributes: Mapping[str, Any]) -> str:
    explicit = attributes.get(OBSERVED_AT)
    if explicit is not None:
        if not isinstance(explicit, str) or not explicit.strip():
            raise IngestionError(f"OTel attribute {OBSERVED_AT} must be a non-empty string")
        return explicit.strip()

    start_time = span.get("start_time_unix_nano")
    if (
        not isinstance(start_time, int)
        or isinstance(start_time, bool)
        or start_time < 0
    ):
        raise IngestionError(
            "OTel span requires agent.recovery.observed_at or start_time_unix_nano"
        )
    return datetime.fromtimestamp(
        start_time / 1_000_000_000,
        tz=timezone.utc,
    ).isoformat(timespec="milliseconds")


def normalize_otel_action_observation(span: Mapping[str, Any]) -> ActionObservation:
    """Normalize one OTel-compatible span mapping into non-authorizing action evidence.

    This adapter deliberately depends only on mappings so callers can feed exported span
    data without installing an OTel SDK. It does not resolve Recovery Contracts, runtime
    bindings, approvals, callables, or execution authority.
    """

    if not isinstance(span, Mapping):
        raise IngestionError("OTel span must be a mapping")

    attributes = span.get("attributes")
    if not isinstance(attributes, Mapping):
        raise IngestionError("OTel span attributes must be a mapping")

    trace_id = span.get("trace_id")
    span_id = span.get("span_id")
    if not isinstance(trace_id, str) or not trace_id.strip():
        raise IngestionError("OTel trace_id is required")
    if not isinstance(span_id, str) or not span_id.strip():
        raise IngestionError("OTel span_id is required")
    trace_id = trace_id.strip()
    span_id = span_id.strip()

    params = attributes.get(PARAMS)
    if not isinstance(params, Mapping):
        raise IngestionError(f"OTel attribute {PARAMS} must be a mapping")

    resource_keys_raw = attributes.get(RESOURCE_KEYS, ())
    if isinstance(resource_keys_raw, str) or not isinstance(resource_keys_raw, Sequence):
        raise IngestionError(f"OTel attribute {RESOURCE_KEYS} must be a sequence")
    resource_keys = tuple(resource_keys_raw)

    observation = ActionObservation(
        incident_id=_required_text(attributes, INCIDENT_ID),
        tool_id=_required_text(attributes, TOOL_ID),
        action_type=_required_text(attributes, ACTION_TYPE),
        contract_version=_required_text(attributes, CONTRACT_VERSION),
        agent_id=_required_text(attributes, AGENT_ID),
        params=params,
        source_system="otel",
        source_event_id=span_id,
        trace_id=trace_id,
        span_id=span_id,
        authority_scope=_optional_text(attributes, AUTHORITY_SCOPE),
        resource_keys=resource_keys,
        observed_at=_observed_at(span, attributes),
        observation_id=f"otel:{trace_id}:{span_id}",
    )
    observation.validate()
    return observation
