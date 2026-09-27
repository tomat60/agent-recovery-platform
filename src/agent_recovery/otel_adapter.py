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

_RECOVERY_ATTRIBUTE_KEYS = {
    INCIDENT_ID,
    TOOL_ID,
    ACTION_TYPE,
    CONTRACT_VERSION,
    AGENT_ID,
    PARAMS,
    AUTHORITY_SCOPE,
    RESOURCE_KEYS,
    OBSERVED_AT,
}
_OTLP_ANY_VALUE_KEYS = {
    "stringValue",
    "boolValue",
    "intValue",
    "doubleValue",
    "arrayValue",
    "kvlistValue",
    "bytesValue",
}


def _otlp_sequence(value: Any, label: str) -> Sequence[Any]:
    if isinstance(value, str) or not isinstance(value, Sequence):
        raise IngestionError(f"{label} must be a sequence")
    return value


def _decode_otlp_key_values(value: Any, label: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for item in _otlp_sequence(value, label):
        if not isinstance(item, Mapping):
            raise IngestionError(f"{label} entries must be mappings")
        key = item.get("key")
        if not isinstance(key, str) or not key.strip():
            raise IngestionError(f"{label} keys must be non-empty strings")
        key = key.strip()
        if key in result:
            raise IngestionError(f"{label} keys must be unique: {key}")
        raw_value = item.get("value")
        if not isinstance(raw_value, Mapping):
            raise IngestionError(f"{label} value for {key} must be an OTLP AnyValue")
        result[key] = _decode_otlp_any_value(raw_value, f"{label} value for {key}")
    return result


def _decode_otlp_any_value(value: Mapping[str, Any], label: str) -> Any:
    present = [key for key in _OTLP_ANY_VALUE_KEYS if key in value]
    if len(present) != 1:
        raise IngestionError(f"{label} must contain exactly one supported OTLP AnyValue field")
    key = present[0]
    raw = value[key]
    if key == "stringValue":
        if not isinstance(raw, str):
            raise IngestionError(f"{label} stringValue must be a string")
        return raw
    if key == "boolValue":
        if not isinstance(raw, bool):
            raise IngestionError(f"{label} boolValue must be a boolean")
        return raw
    if key == "intValue":
        if isinstance(raw, bool) or not isinstance(raw, (int, str)):
            raise IngestionError(f"{label} intValue must be a decimal integer")
        try:
            return int(raw)
        except ValueError as exc:
            raise IngestionError(f"{label} intValue must be a decimal integer") from exc
    if key == "doubleValue":
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise IngestionError(f"{label} doubleValue must be numeric")
        return raw
    if key == "arrayValue":
        if not isinstance(raw, Mapping):
            raise IngestionError(f"{label} arrayValue must be a mapping")
        return [
            _decode_otlp_any_value(item, f"{label} array item")
            if isinstance(item, Mapping)
            else (_ for _ in ()).throw(
                IngestionError(f"{label} array items must be OTLP AnyValue mappings")
            )
            for item in _otlp_sequence(raw.get("values", ()), f"{label} array values")
        ]
    if key == "kvlistValue":
        if not isinstance(raw, Mapping):
            raise IngestionError(f"{label} kvlistValue must be a mapping")
        return _decode_otlp_key_values(raw.get("values", ()), f"{label} kvlist")
    if not isinstance(raw, str):
        raise IngestionError(f"{label} bytesValue must be a base64 string")
    return raw


def _otlp_hex_id(value: Any, label: str, length: int) -> str:
    if (
        not isinstance(value, str)
        or len(value) != length
        or any(character not in "0123456789abcdefABCDEF" for character in value)
    ):
        raise IngestionError(f"OTLP {label} must be a {length}-character hexadecimal string")
    return value.lower()


def _otlp_start_time(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise IngestionError("OTLP startTimeUnixNano must be a non-negative decimal integer")
    try:
        parsed = int(value)
    except ValueError as exc:
        raise IngestionError("OTLP startTimeUnixNano must be a non-negative decimal integer") from exc
    if parsed < 0:
        raise IngestionError("OTLP startTimeUnixNano must be a non-negative decimal integer")
    return parsed


def _otlp_recovery_attributes(span: Mapping[str, Any]) -> dict[str, Any]:
    attributes = span.get("attributes", ())
    entries = _otlp_sequence(attributes, "OTLP span attributes")
    selected = []
    seen: set[str] = set()
    for item in entries:
        if not isinstance(item, Mapping):
            raise IngestionError("OTLP span attribute entries must be mappings")
        key = item.get("key")
        if not isinstance(key, str) or not key.strip():
            raise IngestionError("OTLP span attribute keys must be non-empty strings")
        key = key.strip()
        if key in seen:
            raise IngestionError(f"OTLP span attribute keys must be unique: {key}")
        seen.add(key)
        if key in _RECOVERY_ATTRIBUTE_KEYS:
            selected.append(item)
    return _decode_otlp_key_values(selected, "OTLP recovery attributes")


def normalize_otlp_json_action_observation(span: Mapping[str, Any]) -> ActionObservation:
    """Normalize one standard OTLP/HTTP JSON Span into non-authorizing evidence."""

    if not isinstance(span, Mapping):
        raise IngestionError("OTLP JSON span must be a mapping")
    attributes = _otlp_recovery_attributes(span)
    normalized: dict[str, Any] = {
        "trace_id": _otlp_hex_id(span.get("traceId"), "traceId", 32),
        "span_id": _otlp_hex_id(span.get("spanId"), "spanId", 16),
        "attributes": attributes,
    }
    if "startTimeUnixNano" in span:
        normalized["start_time_unix_nano"] = _otlp_start_time(span["startTimeUnixNano"])
    return normalize_otel_action_observation(normalized)


def normalize_otlp_json_trace_export(payload: Mapping[str, Any]) -> tuple[ActionObservation, ...]:
    """Extract recovery action evidence from an OTLP ExportTraceServiceRequest JSON body."""

    if not isinstance(payload, Mapping):
        raise IngestionError("OTLP trace export must be a mapping")
    observations: list[ActionObservation] = []
    observation_ids: set[str] = set()
    for resource in _otlp_sequence(payload.get("resourceSpans", ()), "OTLP resourceSpans"):
        if not isinstance(resource, Mapping):
            raise IngestionError("OTLP resourceSpans entries must be mappings")
        for scope in _otlp_sequence(resource.get("scopeSpans", ()), "OTLP scopeSpans"):
            if not isinstance(scope, Mapping):
                raise IngestionError("OTLP scopeSpans entries must be mappings")
            for span in _otlp_sequence(scope.get("spans", ()), "OTLP spans"):
                if not isinstance(span, Mapping):
                    raise IngestionError("OTLP span entries must be mappings")
                keys = {
                    item.get("key")
                    for item in _otlp_sequence(span.get("attributes", ()), "OTLP span attributes")
                    if isinstance(item, Mapping)
                }
                if not any(key in _RECOVERY_ATTRIBUTE_KEYS for key in keys):
                    continue
                observation = normalize_otlp_json_action_observation(span)
                if observation.observation_id in observation_ids:
                    raise IngestionError(
                        f"duplicate OTLP action observation: {observation.observation_id}"
                    )
                observation_ids.add(observation.observation_id)
                observations.append(observation)
    return tuple(observations)


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
