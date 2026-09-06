# Recovery Integrity Model

Date: 2026-09-06

## Purpose

Recovery is itself a privileged mutation path. A system that can undo actions can also destroy good state, resurrect stale authority, or fabricate a successful restoration. The recovery plane therefore needs its own integrity boundary.

This document defines the deterministic safety controls that must remain below any LLM investigator, planner, or verifier.

## Invariants

1. **No autonomous write without a recovery path.**
2. **No restored authority without a verified replay.**
3. **No recovery decision from unverifiable evidence.**
4. **No replay verdict survives a change to the source incident or recovery evidence.**
5. **No event ledger mutation can be accepted without preserving the tamper-evident chain.**
6. **No recovery action may target a different incident than the evidence that authorized it.**
7. **No stale or already-consumed authority may be resurrected after rollback.**

## Tamper-evident action ledger

Every ledger event is chained to the previous event using a SHA-256 digest over a canonical representation of:

- event id
- event type
- incident id
- payload
- causal parents
- occurrence time
- previous event hash

This is not presented as a substitute for an external transparency log or a production WORM store. It is a deterministic integrity primitive for the prototype and benchmark. Any mutation, deletion, reordering, or forged insertion breaks `verify_integrity()` and causes restoration to fail closed.

Future production hardening should anchor periodic ledger heads to an external immutable store or signed transparency service.

## Replay freshness

A replay verification is bound to two separate fingerprints:

- **source incident fingerprint**: external input, tool output, memory reads, handoffs, action intents/executions/blocks and authority consumption
- **recovery evidence fingerprint**: containment, recovery planning, recovery execution/failure and residual effects

If either fingerprint changes after verification, the replay evidence is stale and cannot restore authority.

This prevents two important classes of failure:

- replaying a successful verification against a later, changed incident
- replaying a successful verification after the recovery plan, execution result, or residual-effect record changed

## Threats explicitly addressed

- evidence deletion or mutation
- event reordering
- recovery evidence substitution
- cross-incident recovery
- stale replay authorization
- authority resurrection
- forged success reporting inside the deterministic prototype

## Threats not yet solved

- compromised process with full access to both runtime memory and persistence
- externally signed ledger anchoring
- distributed consensus over multiple recovery controllers
- real cloud/database rollback attestations
- malicious or compromised recovery provider implementations

Those remain roadmap items and must not be claimed as production guarantees.
