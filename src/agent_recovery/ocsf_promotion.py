from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
from json import dumps
from typing import Any

from .ingestion import ActionObservation, IngestionError
from .ocsf_adapter import (
    OCSFEvidenceEnvelope,
    normalize_ocsf_json_events,
    promote_ocsf_action_observation,
)


@dataclass(frozen=True)
class OCSFRecoveryPromotion:
    """An explicit, non-authorizing binding from OCSF evidence to recovery identity."""

    source_event_id: str
    source_provenance_digest: str
    recovery_mapping_digest: str
    recovery_mapping: Mapping[str, Any]
    observation: ActionObservation

    def validate(self) -> None:
        self.observation.validate()
        if self.observation.source_system != "ocsf":
            raise IngestionError("OCSF promotion observation source_system must be ocsf")
        if self.observation.source_event_id != self.source_event_id:
            raise IngestionError(
                "OCSF promotion observation does not match source event identity"
            )
        if not isinstance(self.recovery_mapping, Mapping):
            raise IngestionError("OCSF promotion recovery_mapping must be a mapping")
        for name, value in (
            ("source_provenance_digest", self.source_provenance_digest),
            ("recovery_mapping_digest", self.recovery_mapping_digest),
        ):
            if (
                not isinstance(value, str)
                or len(value) != 64
                or any(character not in "0123456789abcdef" for character in value)
            ):
                raise IngestionError(f"OCSF promotion {name} must be lowercase SHA-256")
        if recovery_mapping_digest(self.recovery_mapping) != (
            self.recovery_mapping_digest
        ):
            raise IngestionError("OCSF promotion recovery_mapping_digest mismatch")

    def payload(self) -> dict[str, Any]:
        self.validate()
        return {
            "source_system": "ocsf",
            "source_event_id": self.source_event_id,
            "source_provenance_digest": self.source_provenance_digest,
            "recovery_mapping_digest": self.recovery_mapping_digest,
            "recovery_mapping": deepcopy(dict(self.recovery_mapping)),
            "observation": deepcopy(self.observation.payload()),
            "authorization_effect": "none",
        }


def recovery_mapping_digest(mapping: Mapping[str, Any]) -> str:
    if not isinstance(mapping, Mapping):
        raise IngestionError("OCSF recovery mapping must be a mapping")
    canonical = dumps(
        dict(mapping),
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


def _promotion(
    envelope: OCSFEvidenceEnvelope,
    mapping: Mapping[str, Any],
) -> OCSFRecoveryPromotion:
    mapping_snapshot = deepcopy(dict(mapping))
    observation = promote_ocsf_action_observation(envelope, mapping_snapshot)
    promotion = OCSFRecoveryPromotion(
        source_event_id=envelope.event_uid,
        source_provenance_digest=envelope.provenance_digest(),
        recovery_mapping_digest=recovery_mapping_digest(mapping_snapshot),
        recovery_mapping=mapping_snapshot,
        observation=observation,
    )
    promotion.validate()
    return promotion


def promote_ocsf_evidence_batch(
    events: Sequence[Mapping[str, Any]],
    recovery_mappings: Mapping[str, Mapping[str, Any]],
) -> tuple[OCSFRecoveryPromotion, ...]:
    """Promote OCSF evidence only through an exact source-to-recovery manifest.

    Every normalized source event must have exactly one mapping and the manifest may
    not contain mappings for absent events. OCSF action and disposition values remain
    evidence only and never contribute authority.
    """

    if not isinstance(recovery_mappings, Mapping):
        raise IngestionError("OCSF recovery mappings must be a mapping")

    envelopes = normalize_ocsf_json_events(events)
    source_event_ids = {envelope.event_uid for envelope in envelopes}
    mapping_ids = set(recovery_mappings)
    if any(not isinstance(event_id, str) or not event_id.strip() for event_id in mapping_ids):
        raise IngestionError("OCSF recovery mapping identities must be non-empty strings")

    missing = sorted(source_event_ids - mapping_ids)
    unexpected = sorted(mapping_ids - source_event_ids)
    if missing:
        raise IngestionError(
            "missing OCSF recovery mappings for: " + ", ".join(missing)
        )
    if unexpected:
        raise IngestionError(
            "unexpected OCSF recovery mappings for: " + ", ".join(unexpected)
        )

    promotions = []
    for envelope in envelopes:
        mapping = recovery_mappings[envelope.event_uid]
        if not isinstance(mapping, Mapping):
            raise IngestionError(
                f"OCSF recovery mapping for {envelope.event_uid} must be a mapping"
            )
        promotions.append(_promotion(envelope, mapping))
    return tuple(promotions)
