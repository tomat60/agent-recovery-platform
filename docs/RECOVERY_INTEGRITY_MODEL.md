# Recovery Integrity Model

Date: 2026-09-12

## Purpose

Recovery is itself a privileged mutation path. A system that can undo actions can also destroy good state, resurrect stale authority, or fabricate a successful restoration. The recovery plane therefore needs its own integrity boundary.

This document defines the deterministic safety controls that must remain below any LLM investigator, planner, or verifier.

## Invariants

1. **No autonomous write without a recovery path.**
2. **No restored authority without complete local recovery evidence and a current scope-bound replay.**
3. **No recovery decision from evidence that fails the local ledger-integrity check.**
4. **No replay verdict survives a relevant change to the source incident or recovery evidence.**
5. **No accepted in-ledger mutation may break the locally verified tamper-evident chain.**
6. **No recovery action may target a different incident than the evidence that authorized it.**
7. **No stale or already-consumed authority may be reused inside the bounded shared-ledger runtime.**

## Tamper-evident action ledger

Every ledger event is chained to the previous event using a SHA-256 digest over a canonical representation of:

- event id
- event type
- incident id
- payload
- causal parents
- occurrence time
- previous event hash

The ledger detaches nested payload data at append/read boundaries so an exported evidence object cannot silently mutate the stored event. Recovery and restoration verify the chain before privileged mutation or release decisions.

This is **not** an authenticated transparency log and is not presented as a substitute for a production WORM store. Within one retained ledger history, mutation, internal deletion/reordering, or forged insertion that breaks the chain is detected. A self-consistent prefix or alternate history cannot be distinguished from the intended complete history without an independently committed head/length or external authentication. Therefore the prototype does **not** claim suffix-truncation resistance, completeness, authenticity, or rollback resistance against a process that controls persistence.

Future production hardening should anchor ledger heads and sequence commitments to an authenticated external immutable store or signed transparency service.

## Replay freshness and release-policy binding

A replay verification is bound to:

- the source incident and exact source action,
- action agent, tool, parameters and contract version,
- the source ledger head and current recovery generation at replay execution,
- the contract versions used by executed actions in the source incident,
- one proposed authority release scope,
- source-incident and recovery-evidence fingerprints.

The proposed release scope may not remain contained inside the replay. Other containment may be preserved when it is part of the proposed post-restoration policy. A later replay verdict for the same release scope supersedes an earlier one. Replay evidence can be recorded only against the execution-time source head, which prevents re-stamping the same replay after the source history changes.

The current replay remains a **bounded synthetic replay of the selected represented attack action**, not proof of full production-environment, provider, topology or time-dependent equivalence.

## Restoration boundary

The deterministic restoration gate requires, within the bounded prototype:

- active containment for the exact scope being considered,
- complete local handling of represented executed actions,
- no uncovered residual effect,
- the latest applicable replay verdict for that exact scope,
- matching current recovery generation and evidence fingerprints,
- successful action/environment binding in replay.

An authorized restoration event does not silently change runtime authority. `RecoveryEngine.release_containment()` applies the exact authorized event and records the corresponding containment release.

## Threats explicitly addressed in the bounded implementation

- nested evidence alias mutation through exported views,
- hash-chain-breaking event mutation/reordering/internal deletion,
- cross-incident recovery result reuse,
- stale or re-stamped replay authorization,
- superseded positive replay use,
- unrelated release-scope reuse,
- runtime containment loss on reconstruction from the same ledger,
- duplicate approval consumption across controllers sharing one in-memory ledger,
- recovery over a later writer of the same represented resource,
- malformed contract metadata reaching an executor,
- ambiguous verifier/compensation failures disappearing from residual accounting.

## Threats not yet solved

- compromised process with full control of both runtime memory and persistence,
- external signed ledger anchoring and valid-prefix rollback detection,
- distributed consensus across independently persisted recovery controllers,
- production multi-tenancy,
- real cloud/database rollback attestations,
- malicious or compromised recovery provider implementations,
- complete production replay equivalence for topology, provider state, delayed effects or time-dependent behavior,
- live AWS/AgentCore security effectiveness without separate evidence.

Those remain roadmap items and must not be claimed as production guarantees.
