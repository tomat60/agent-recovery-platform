from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from json import dumps
from typing import Any

from .ingestion import ActionObservation, IngestionError


@dataclass(frozen=True)
class OCSFEvidenceEnvelope:
    """Non-authorizing OCSF security-runtime evidence.

    OCSF policy outcomes such as Allowed or Blocked are evidence only. They never
    grant recovery authority and never imply that an external side effect is safe
    to reverse or compensate.
    """

    event_uid: str
    class_uid: int
    activity_id: int
    event_time_ms: int
    schema_version: str
    product_name: str
    vendor_name: str | None
    product_version: str | None
    sandbox_uid: str | None
    action: str | None
    disposition: str | None
    raw_event: Mapping[str, Any]

    def validate(self) -> None:
        for name, value in (
            ("event_uid", self.event_uid),
            ("schema_version", self.schema_version),
            ("product_name", self.product_name),
        ):
            if not isinstance(value, str) or not value.strip():
                raise IngestionError(f"OCSF {name} is required")

        for name, value in (
            ("class_uid", self.class_uid),
            ("activity_id", self.activity_id),
            ("event_time_ms", self.event_time_ms),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise IngestionError(f"OCSF {name} must be a non-negative integer")

        for name, value in (
            ("vendor_name", self.vendor_name),
            ("product_version", self.product_version),
            ("sandbox_uid", self.sandbox_uid),
            ("action", self.action),
            ("disposition", self.disposition),
        ):
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise IngestionError(f"OCSF {name} must be a non-empty string when provided")

        if not isinstance(self.raw_event, Mapping):
            raise IngestionError("OCSF raw_event must be a mapping")

    def evidence_payload(self) -> dict[str, Any]:
        self.validate()
        payload: dict[str, Any] = {
            "source_system": "ocsf",
            "source_event_id": self.event_uid,
            "class_uid": self.class_uid,
            "activity_id": self.activity_id,
            "event_time_ms": self.event_time_ms,
            "schema_version": self.schema_version,
            "product_name": self.product_name,
            "authorization_effect": "none",
            "raw_event": deepcopy(dict(self.raw_event)),
        }
        for key, value in (
            ("vendor_name", self.vendor_name),
            ("product_version", self.product_version),
            ("sandbox_uid", self.sandbox_uid),
            ("action", self.action),
            ("disposition", self.disposition),
        ):
            if value is not None:
                payload[key] = value
        return payload

    def provenance_digest(self) -> str:
        canonical = dumps(
            self.evidence_payload(),
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )
        return sha256(canonical.encode("utf-8")).hexdigest()


def _required_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise IngestionError(f"OCSF {label} must be a mapping")
    return value


def _required_text(values: Mapping[str, Any], key: str, label: str) -> str:
    value = values.get(key)
    if not isinstance(value, str) or not value.strip():
        raise IngestionError(f"OCSF {label} is required")
    return value.strip()


def _optional_text(values: Mapping[str, Any], key: str, label: str) -> str | None:
    value = values.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise IngestionError(f"OCSF {label} must be a non-empty string")
    return value.strip()


def _non_negative_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise IngestionError(f"OCSF {label} must be a non-negative integer")
    return value


def normalize_ocsf_evidence_event(event: Mapping[str, Any]) -> OCSFEvidenceEnvelope:
    """Normalize one OCSF v1.8-style event into evidence with zero authority effect."""

    if not isinstance(event, Mapping):
        raise IngestionError("OCSF event must be a mapping")

    metadata = _required_mapping(event.get("metadata"), "metadata")
    product = _required_mapping(metadata.get("product"), "metadata.product")
    container = event.get("container")
    if container is not None and not isinstance(container, Mapping):
        raise IngestionError("OCSF container must be a mapping when provided")

    envelope = OCSFEvidenceEnvelope(
        event_uid=_required_text(metadata, "uid", "metadata.uid"),
        class_uid=_non_negative_int(event.get("class_uid"), "class_uid"),
        activity_id=_non_negative_int(event.get("activity_id"), "activity_id"),
        event_time_ms=_non_negative_int(event.get("time"), "time"),
        schema_version=_required_text(metadata, "version", "metadata.version"),
        product_name=_required_text(product, "name", "metadata.product.name"),
        vendor_name=_optional_text(product, "vendor_name", "metadata.product.vendor_name"),
        product_version=_optional_text(product, "version", "metadata.product.version"),
        sandbox_uid=(
            _optional_text(container, "uid", "container.uid")
            if isinstance(container, Mapping)
            else None
        ),
        action=_optional_text(event, "action", "action"),
        disposition=_optional_text(event, "disposition", "disposition"),
        raw_event=deepcopy(dict(event)),
    )
    envelope.validate()
    return envelope


def normalize_ocsf_json_events(
    events: Sequence[Mapping[str, Any]],
) -> tuple[OCSFEvidenceEnvelope, ...]:
    """Normalize OCSF events and reject duplicate source identities."""

    if isinstance(events, (str, bytes, bytearray)) or not isinstance(events, Sequence):
        raise IngestionError("OCSF events must be a sequence")

    normalized: list[OCSFEvidenceEnvelope] = []
    seen: set[str] = set()
    for event in events:
        envelope = normalize_ocsf_evidence_event(event)
        if envelope.event_uid in seen:
            raise IngestionError(f"duplicate OCSF source event: {envelope.event_uid}")
        seen.add(envelope.event_uid)
        normalized.append(envelope)
    return tuple(normalized)


def promote_ocsf_action_observation(
    envelope: OCSFEvidenceEnvelope,
    recovery: Mapping[str, Any],
) -> ActionObservation:
    """Promote OCSF evidence only with an explicit recovery-identity mapping.

    The caller must supply recovery semantics deliberately. OCSF action or disposition
    fields are never interpreted as authorization and never infer a Recovery Contract.
    """

    envelope.validate()
    if not isinstance(recovery, Mapping):
        raise IngestionError("OCSF recovery mapping must be a mapping")

    params = recovery.get("params")
    if not isinstance(params, Mapping):
        raise IngestionError("OCSF recovery mapping params must be a mapping")

    resource_keys = recovery.get("resource_keys", ())
    if isinstance(resource_keys, str) or not isinstance(resource_keys, Sequence):
        raise IngestionError("OCSF recovery mapping resource_keys must be a sequence")

    observed_at = recovery.get("observed_at")
    if observed_at is None:
        observed_at = datetime.fromtimestamp(
            envelope.event_time_ms / 1000,
            tz=timezone.utc,
        ).isoformat(timespec="milliseconds")
    elif not isinstance(observed_at, str) or not observed_at.strip():
        raise IngestionError("OCSF recovery mapping observed_at must be a non-empty string")
    else:
        observed_at = observed_at.strip()

    def required(key: str) -> str:
        value = recovery.get(key)
        if not isinstance(value, str) or not value.strip():
            raise IngestionError(f"OCSF recovery mapping {key} is required")
        return value.strip()

    def optional(key: str) -> str | None:
        value = recovery.get(key)
        if value is None:
            return None
        if not isinstance(value, str) or not value.strip():
            raise IngestionError(
                f"OCSF recovery mapping {key} must be a non-empty string"
            )
        return value.strip()

    observation = ActionObservation(
        incident_id=required("incident_id"),
        tool_id=required("tool_id"),
        action_type=required("action_type"),
        contract_version=required("contract_version"),
        agent_id=required("agent_id"),
        params=params,
        source_system="ocsf",
        source_event_id=envelope.event_uid,
        trace_id=optional("trace_id"),
        span_id=optional("span_id"),
        authority_scope=optional("authority_scope"),
        resource_keys=tuple(resource_keys),
        observed_at=observed_at,
        observation_id=f"ocsf:{envelope.event_uid}",
    )
    observation.validate()
    return observation
