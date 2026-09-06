from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .ledger import LedgerEvent


class ReconciliationStatus(str, Enum):
    VERIFIED = "verified"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass(frozen=True)
class ReconciliationApproval:
    """Fresh authority bound to one exact shared-state conflict resolution."""

    incident_id: str
    resource_key: str
    compromised_action_event_id: str
    trusted_action_event_id: str
    evidence_head_hash: str
    approval_id: str

    @classmethod
    def for_conflict(
        cls,
        *,
        incident_id: str,
        resource_key: str,
        compromised_action_event_id: str,
        trusted_action_event_id: str,
        evidence_head_hash: str,
        approval_id: str,
    ) -> ReconciliationApproval:
        return cls(
            incident_id=incident_id,
            resource_key=resource_key,
            compromised_action_event_id=compromised_action_event_id,
            trusted_action_event_id=trusted_action_event_id,
            evidence_head_hash=evidence_head_hash,
            approval_id=approval_id,
        )


@dataclass(frozen=True)
class ReconciliationResult:
    status: ReconciliationStatus
    event: LedgerEvent
    verification_event: LedgerEvent | None = None
    reason: str | None = None
