from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .ledger import ActionLedger, LedgerEvent


class InvestigationBoundaryError(ValueError):
    """Raised when read-only investigation evidence cannot be trusted."""


@dataclass(frozen=True)
class EvidenceView:
    incident_id: str
    ledger_head_hash: str
    events: tuple[LedgerEvent, ...]

    def as_prompt_payload(self) -> dict[str, Any]:
        """Return immutable evidence suitable for an investigator/planner prompt.

        The payload intentionally contains evidence only. It carries no approval, capability,
        executor handle, or mutable ledger object, so model output cannot become authorization.
        """

        return {
            "incident_id": self.incident_id,
            "ledger_head_hash": self.ledger_head_hash,
            "events": [
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type.value,
                    "parent_event_ids": list(event.parent_event_ids),
                    "occurred_at": event.occurred_at,
                    "payload": dict(event.payload),
                    "event_hash": event.event_hash,
                }
                for event in self.events
            ],
        }


@dataclass(frozen=True)
class AgentProposal:
    incident_id: str
    role: str
    summary: str
    evidence_event_ids: tuple[str, ...]


_ALLOWED_ROLES = {"investigator", "recovery_planner", "skeptic"}


def build_evidence_view(ledger: ActionLedger, *, incident_id: str) -> EvidenceView:
    if not incident_id:
        raise InvestigationBoundaryError("incident_id is required")
    if not ledger.verify_integrity():
        raise InvestigationBoundaryError("ledger integrity verification failed")

    events = ledger.events(incident_id=incident_id)
    if not events:
        raise InvestigationBoundaryError("incident has no ledger evidence")

    return EvidenceView(
        incident_id=incident_id,
        ledger_head_hash=ledger.head_hash,
        events=events,
    )


def bind_agent_proposal(
    view: EvidenceView,
    *,
    role: str,
    summary: str,
    evidence_event_ids: tuple[str, ...],
) -> AgentProposal:
    """Bind model-authored analysis to evidence without granting execution authority."""

    if role not in _ALLOWED_ROLES:
        raise InvestigationBoundaryError(f"unsupported agent role: {role}")
    if not summary.strip():
        raise InvestigationBoundaryError("proposal summary is required")
    if not evidence_event_ids:
        raise InvestigationBoundaryError("proposal must cite ledger evidence")

    allowed_ids = {event.event_id for event in view.events}
    unknown_ids = sorted(set(evidence_event_ids) - allowed_ids)
    if unknown_ids:
        raise InvestigationBoundaryError(
            f"proposal cites evidence outside incident view: {unknown_ids}"
        )

    return AgentProposal(
        incident_id=view.incident_id,
        role=role,
        summary=summary.strip(),
        evidence_event_ids=tuple(dict.fromkeys(evidence_event_ids)),
    )
