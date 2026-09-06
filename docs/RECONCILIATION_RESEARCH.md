# Evidence-backed shared-state reconciliation

## Why this slice exists

Recovery cannot safely restore a before-image when two causally independent writers changed the same exact mutable resource. A guessed winner can erase legitimate state.

Primary-source patterns point to the same constraint:

- AWS Saga guidance treats compensating transactions as explicit recovery operations and notes that concurrent sagas can create stale data.
- AWS recommends semantic locking when concurrent saga participants can interfere with one another.
- DynamoDB optimistic locking detects conflicting writes with version checks instead of silently accepting stale state.

For Agent Recovery, the product rule is therefore:

> Ambiguous same-resource recovery may be proposed automatically, but state may only be rewritten when the target state is backed by exact evidence and fresh, parameter-bound reconciliation authority.

## Deterministic design

For the first implementation:

1. both actions must be real `ACTION_EXECUTED` events in the same incident
2. they must be causally independent and conflict on one identical Recovery Contract resource key
3. both actions must use the same contract/tool for this bounded implementation
4. the selected trusted action contributes the exact previously observed post-state
5. a dedicated reconciliation executor writes that target state without replaying the original external side effect
6. the reconciliation approval is bound to incident, resource, both action IDs and the current tamper-evident ledger head
7. any new evidence after approval makes it stale
8. approval is single-use
9. independent verification must match the exact trusted observed state
10. reconciliation events become part of recovery freshness, invalidating older replay evidence

## What this intentionally does not claim

This is not a generic CRDT engine, automatic semantic merge system, or proof that one writer is objectively correct. It is a safe deterministic boundary for the genuinely ambiguous case.

Later automatic reconciliation can be added only for operations whose merge semantics are provably commutative or whose target state can be reconstructed from stronger external authority/version evidence.
