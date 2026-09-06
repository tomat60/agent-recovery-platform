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
    """Return irreversible/residual effects recorded for an incident."""

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
    """Return residual effects not acknowledged by the latest recovery generation."""

    residuals = residual_effect_event_ids(ledger, incident_id=incident_id)
    if not residuals:
        return ()

    forks = _incident_forks(ledger, incident_id)
    if not forks:
        return residuals

    covered = {
        str(event_id)
        for event_id in forks[-1].payload.get("residual_effect_event_ids", ())
    }
    return tuple(event_id for event_id in residuals if event_id not in covered)


def _validate_local_recovery_verification(
    ledger: ActionLedger,
    *,
    incident_id: str,
    verification_event_id: str,
) -> LedgerEvent:
    verification = ledger.get(verification_event_id)
    if verification.incident_id != incident_id:
        raise RecoveryGenerationError("verified recovery event belongs to another incident")
    if verification.event_type is not EventType.VERIFICATION:
        raise RecoveryGenerationError("recovery fork requires a verification event")
    if verification.payload.get("verified") is not True:
        raise RecoveryGenerationError("recovery fork requires verified local recovery")
    if verification.payload.get("verification_kind") == "adversarial_replay":
        raise RecoveryGenerationError("replay verification cannot establish a local recovery fork")

    action_event_id = verification.payload.get("action_event_id")
    if not isinstance(action_event_id, str) or not action_event_id:
        raise RecoveryGenerationError("recovery verification must identify its source action")

    recovery_parents = []
    for parent_event_id in verification.parent_event_ids:
        parent = ledger.get(parent_event_id)
        if (
            parent.incident_id == incident_id
            and parent.event_type is EventType.RECOVERY_EXECUTED
            and parent.payload.get("action_event_id") == action_event_id
        ):
            recovery_parents.append(parent)
    if len(recovery_parents) != 1:
        raise RecoveryGenerationError(
            "recovery verification must be causally bound to one recovery execution"
        )
    return verification


def record_recovery_fork(
    ledger: ActionLedger,
    *,
    incident_id: str,
    verified_recovery_event_id: str,
    residual_event_ids: tuple[str, ...] | None = None,
) -> RecoveryFork:
    """Record restored local state as a new generation without rewriting external history."""

    ledger.verify_integrity()
    verification = _validate_local_recovery_verification(
        ledger,
        incident_id=incident_id,
        verification_event_id=verified_recovery_event_id,
    )

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

    existing_forks = _incident_forks(ledger, incident_id)
    inherited: tuple[str, ...] = ()
    if existing_forks:
        inherited = tuple(
            str(event_id)
            for event_id in existing_forks[-1].payload.get("residual_effect_event_ids", ())
        )
    acknowledged = tuple(sorted(set(inherited).union(selected)))

    parent_generation = current_generation(ledger, incident_id=incident_id)
    generation = parent_generation + 1
    parent_ids = [verification.event_id, *acknowledged]
    if existing_forks:
        parent_ids.append(existing_forks[-1].event_id)

    event = ledger.record(
        EventType.RECOVERY_FORKED,
        incident_id,
        {
            "generation": generation,
            "parent_generation": parent_generation,
            "verified_recovery_event_id": verification.event_id,
            "residual_effect_event_ids": acknowledged,
            "external_history_rewritten": False,
            "semantics": "fork_after_externalized_effect",
        },
        parent_event_ids=tuple(parent_ids),
    )
    return RecoveryFork(
        event=event,
        generation=generation,
        parent_generation=parent_generation,
        residual_effect_event_ids=acknowledged,
    )
