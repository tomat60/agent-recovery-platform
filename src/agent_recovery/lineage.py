from __future__ import annotations

from dataclasses import dataclass

from .ledger import ActionLedger, EventType, LedgerEvent


class RecoveryGenerationError(ValueError):
    """Raised when a recovery fork cannot be proven from trusted incident evidence."""


@dataclass(frozen=True)
class RecoveryFork:
    event: LedgerEvent
    generation: int
    parent_generation: int
    residual_effect_event_ids: tuple[str, ...]


def _incident_forks(ledger: ActionLedger, incident_id: str) -> tuple[LedgerEvent, ...]:
    return tuple(
        event
        for event in ledger.events(incident_id=incident_id)
        if event.event_type is EventType.RECOVERY_FORKED
    )


def current_generation(ledger: ActionLedger, *, incident_id: str) -> int:
    """Return the current local recovery generation for one incident."""

    ledger.verify_integrity()
    forks = _incident_forks(ledger, incident_id)
    if not forks:
        return 0

    expected = 1
    for event in forks:
        generation = int(event.payload.get("generation", -1))
        parent_generation = int(event.payload.get("parent_generation", -1))
        if generation != expected or parent_generation != expected - 1:
            raise RecoveryGenerationError("recovery fork generations are not contiguous")
        expected += 1
    return expected - 1


def residual_effect_event_ids(
    ledger: ActionLedger,
    *,
    incident_id: str,
) -> tuple[str, ...]:
    """Return every irreversible/residual effect currently recorded for an incident."""

    ledger.verify_integrity()
    return tuple(
        event.event_id
        for event in ledger.events(incident_id=incident_id)
        if event.event_type is EventType.RESIDUAL_EFFECT
    )


def uncovered_residual_effect_event_ids(
    ledger: ActionLedger,
    *,
    incident_id: str,
) -> tuple[str, ...]:
    """Return residual effects not acknowledged by the latest recovery fork."""

    residuals = residual_effect_event_ids(ledger, incident_id=incident_id)
    if not residuals:
        return ()

    forks = _incident_forks(ledger, incident_id)
    if not forks:
        return residuals

    latest = forks[-1]
    covered = {
        str(event_id)
        for event_id in latest.payload.get("residual_effect_event_ids", ())
    }
    return tuple(event_id for event_id in residuals if event_id not in covered)


def record_recovery_fork(
    ledger: ActionLedger,
    *,
    incident_id: str,
    verified_recovery_event_id: str,
    residual_event_ids: tuple[str, ...] | None = None,
) -> RecoveryFork:
    """Record that restored local state is a new generation, not rewritten history.

    Externalized effects remain part of the immutable incident history. A fork explicitly
    separates the newly restored local generation from those already-observed effects.
    """

    ledger.verify_integrity()
    verification = ledger.get(verified_recovery_event_id)
    if verification.incident_id != incident_id:
        raise RecoveryGenerationError("verified recovery event belongs to another incident")
    if verification.event_type is not EventType.VERIFICATION:
        raise RecoveryGenerationError("recovery fork requires a verification event")
    if verification.payload.get("verified") is not True:
        raise RecoveryGenerationError("recovery fork requires verified local recovery")

    all_residuals = residual_effect_event_ids(ledger, incident_id=incident_id)
    selected = all_residuals if residual_event_ids is None else tuple(residual_event_ids)
    if not selected:
        raise RecoveryGenerationError("recovery fork requires at least one residual effect")
    if len(set(selected)) != len(selected):
        raise RecoveryGenerationError("residual effect event ids must be unique")

    all_residual_set = set(all_residuals)
    unknown = tuple(event_id for event_id in selected if event_id not in all_residual_set)
    if unknown:
        raise RecoveryGenerationError(
            f"recovery fork references unknown residual effect events: {unknown}"
        )

    parent_generation = current_generation(ledger, incident_id=incident_id)
    generation = parent_generation + 1
    existing_forks = _incident_forks(ledger, incident_id)
    parent_ids = [verified_recovery_event_id, *selected]
    if existing_forks:
        parent_ids.append(existing_forks[-1].event_id)

    event = ledger.record(
        EventType.RECOVERY_FORKED,
        incident_id,
        {
            "generation": generation,
            "parent_generation": parent_generation,
            "verified_recovery_event_id": verified_recovery_event_id,
            "residual_effect_event_ids": tuple(sorted(selected)),
            "external_history_rewritten": False,
            "semantics": "fork_after_externalized_effect",
        },
        parent_event_ids=tuple(parent_ids),
    )
    return RecoveryFork(
        event=event,
        generation=generation,
        parent_generation=parent_generation,
        residual_effect_event_ids=tuple(sorted(selected)),
    )
