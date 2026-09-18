from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from json import dumps
from typing import Any
from uuid import uuid4

from .ledger import ActionLedger, EventType, LedgerEvent


class IngestionError(ValueError):
    """Raised when external action evidence is incomplete or ambiguous."""


@dataclass(frozen=True)
class ActionObservation:
    """Framework-neutral evidence envelope for an observed agent/tool action.

    Adapters (OTel, MCP, HTTP, framework SDKs) should normalize into this shape rather
    than teaching the recovery engine framework-specific semantics. The envelope records
    evidence only; ingesting it never grants authority or executes recovery.
    """

    incident_id: str
    tool_id: str
    action_type: str
    contract_version: str
    agent_id: str
    params: Mapping[str, Any]
    source_system: str
    source_event_id: str
    trace_id: str | None = None
    span_id: str | None = None
    authority_scope: str | None = None
    resource_keys: Sequence[str] = field(default_factory=tuple)
    observed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="milliseconds")
    )
    observation_id: str = field(default_factory=lambda: str(uuid4()))

    def validate(self) -> None:
        required = {
            "incident_id": self.incident_id,
            "tool_id": self.tool_id,
            "action_type": self.action_type,
            "contract_version": self.contract_version,
            "agent_id": self.agent_id,
            "source_system": self.source_system,
            "source_event_id": self.source_event_id,
            "observed_at": self.observed_at,
            "observation_id": self.observation_id,
        }
        for name, value in required.items():
            if not isinstance(value, str) or not value.strip():
                raise IngestionError(f"{name} is required")
        if not isinstance(self.params, Mapping):
            raise IngestionError("params must be a mapping")
        for name, value in (
            ("trace_id", self.trace_id),
            ("span_id", self.span_id),
            ("authority_scope", self.authority_scope),
        ):
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise IngestionError(f"{name} must be a non-empty string when provided")
        if isinstance(self.resource_keys, str):
            raise IngestionError("resource_keys must be a sequence, not a string")
        if any(not isinstance(key, str) or not key.strip() for key in self.resource_keys):
            raise IngestionError("resource_keys must be non-empty strings")
        normalized = tuple(key.strip() for key in self.resource_keys)
        if len(set(normalized)) != len(normalized):
            raise IngestionError("resource_keys must be unique")

    def evidence_payload(self) -> dict[str, Any]:
        """Return canonical source evidence before ledger-specific metadata is added."""

        self.validate()
        payload: dict[str, Any] = {
            "observation_id": self.observation_id,
            "tool_id": self.tool_id,
            "action_type": self.action_type,
            "contract_version": self.contract_version,
            "agent_id": self.agent_id,
            "params": deepcopy(dict(self.params)),
            "source_system": self.source_system,
            "source_event_id": self.source_event_id,
            "observed_at": self.observed_at,
            "resource_keys": tuple(sorted(key.strip() for key in self.resource_keys)),
        }
        if self.trace_id is not None:
            payload["trace_id"] = self.trace_id
        if self.span_id is not None:
            payload["span_id"] = self.span_id
        if self.authority_scope is not None:
            payload["authority_scope"] = self.authority_scope
        return payload

    def provenance_digest(self) -> str:
        """Bind normalized source evidence to a deterministic, framework-neutral digest."""

        canonical = dumps(
            self.evidence_payload(), sort_keys=True, separators=(",", ":"), default=str
        )
        return sha256(canonical.encode("utf-8")).hexdigest()

    def payload(self) -> dict[str, Any]:
        payload = self.evidence_payload()
        payload["provenance_digest"] = self.provenance_digest()
        payload["authorization_effect"] = "none"
        return payload


def ingest_action_observation(
    ledger: ActionLedger,
    observation: ActionObservation,
    *,
    parent_event_ids: Sequence[str] = (),
) -> LedgerEvent:
    """Append observed action intent as detached evidence with zero authorization effect."""

    observation.validate()
    return ledger.record(
        EventType.ACTION_INTENT,
        observation.incident_id,
        observation.payload(),
        parent_event_ids=parent_event_ids,
    )
