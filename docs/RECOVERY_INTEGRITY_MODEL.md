# Recovery Integrity Model

Date: 2026-09-13

## Purpose

Recovery is itself a privileged mutation path. A system that can undo actions can also destroy good state, resurrect stale authority, or fabricate a successful restoration. The recovery plane therefore needs its own integrity boundary.

This document defines the deterministic safety controls that must remain below any LLM investigator, planner, or verifier.

## Invariants

1. **No autonomous write without a recovery path.**
2. **No restored downstream authority without complete local recovery evidence and a current scope-bound replay.**
3. **The replayed compromised source agent is not restored by its own positive replay in the competition path.**
4. **No recovery decision from evidence that fails the local ledger-integrity check.**
5. **No replay verdict survives a relevant change to source incident or recovery evidence.**
6. **No accepted in-ledger mutation may break the locally verified tamper-evident chain.**
7. **No recovery action may target a different incident than the evidence that authorized it.**
8. **No stale or already-consumed authority may be reused inside the bounded shared-ledger runtime.**
9. **Containment is the union of outstanding represented incident holds on a scope.**
10. **A restoration application consumes one exact active hold and must be fresh at application time.**

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

Security-sensitive local admission policy is enforced on both ordinary `record()` and direct `append()` paths for positive source-agent replay claims and represented containment releases. A represented containment release must cite an authorized restoration and the exact still-active hold it consumes.

This is **not** an authenticated transparency log and is not presented as a substitute for a production WORM store. Within one retained ledger history, mutation, internal deletion/reordering, or forged insertion that breaks the chain is detected. A self-consistent prefix or alternate history cannot be distinguished from the intended complete history without an independently committed head/length or external authentication. Therefore the prototype does **not** claim suffix-truncation resistance, completeness, authenticity, or rollback resistance against a process that controls persistence.

Future production hardening should anchor ledger heads and sequence commitments to an authenticated external immutable store or signed transparency service.

## Shared containment semantics

A containment event with `active=true` creates one represented hold identified by that event. The effective containment of a scope is the union of all outstanding holds for that scope, including holds from different incidents.

Controllers sharing one in-memory `ActionLedger` query this authoritative ledger state at action admission time. A controller created before another controller places a hold therefore observes that hold without requiring local cache synchronization. Recreated controllers derive the same result from the retained ledger.

A release event must identify exactly one authorized restoration decision and one exact active hold. Releasing incident A cannot remove incident B's independent hold on the same scope.

## Replay freshness and release-policy binding

A replay verification is bound to:

- source incident and exact source action,
- action agent, tool, parameters and contract version,
- source ledger head and current recovery generation at replay execution,
- contract versions used by executed actions in the source incident,
- one proposed authority release scope,
- source-incident and recovery-evidence fingerprints.

The proposed release scope may not be explicitly listed as contained in the replay specification. A later replay verdict for the same release scope supersedes an earlier one. Replay evidence can be recorded only against the execution-time source head, which prevents re-stamping the same replay after source history changes.

A targeted re-audit demonstrated that this condition alone is not sufficient to prove the compromised source agent safe to restore, because another containment boundary can make replay safe. The competition path therefore rejects positive replay admission when the proposed release scope is the agent that performed the replayed source action. The demonstrated root/source agent remains contained. Downstream restoration may still rely on persistent source/root containment that is not being released.

The current replay remains a **bounded synthetic replay of the selected represented attack action**, not proof of full production-environment, provider, topology or time-dependent equivalence.

## Restoration boundary

The deterministic restoration gate requires, within the bounded prototype:

- active containment for the exact scope being considered,
- complete local handling of represented executed actions,
- no uncovered residual effect,
- latest applicable replay verdict for that exact scope,
- matching current recovery generation and evidence fingerprints,
- successful action/environment binding in replay.

Authorization is not the final mutation. `RecoveryEngine.release_containment()` then requires the authorized restoration event to still be the current ledger head, resolves one exact active hold for the same incident and scope, and records a release bound to both. Any intervening ledger work makes the restoration stale. Reuse after an earlier release or a renewed hold also fails closed.

## Recovery failure boundary

Direct `RecoveryEngine.recover()` execution is itself evidence-producing. If a recovery executor or recovery verifier raises after the recovery plan has begun, the engine records a deterministic `RECOVERY_FAILED` event plus an explicit `RESIDUAL_EFFECT` before re-raising. The recovery workflow wrapper reuses that canonical evidence instead of double-counting it.

Recovery success targets are fixed from preserved pre-action evidence before compensation executes. Compensation output cannot select its own success target.

## Threats explicitly addressed in the bounded implementation

- nested evidence alias mutation through exported views,
- hash-chain-breaking event mutation/reordering/internal deletion,
- cross-incident recovery result reuse,
- cached recovery reuse after ledger-integrity failure,
- stale or re-stamped replay authorization,
- superseded positive replay use,
- source-agent positive replay used for self-restoration,
- stale or reusable restoration application,
- containment invisibility across already-created shared-ledger controllers,
- one incident release erasing another incident hold,
- runtime containment loss on reconstruction from the same ledger,
- duplicate approval consumption across controllers sharing one in-memory ledger,
- recovery over a later writer of the same represented resource,
- malformed contract metadata reaching an executor,
- impossible judge-evidence upper relationships,
- ambiguous verifier/compensation failures disappearing from residual accounting.

## Threats not yet solved

- compromised process with full control of runtime memory and persistence,
- authenticated remote proof/approval issuer boundaries,
- external signed ledger anchoring and valid-prefix rollback detection,
- distributed consensus across independently persisted recovery controllers,
- production multi-tenancy,
- real cloud/database rollback attestations,
- malicious or compromised recovery provider implementations,
- safe restoration of the compromised source/root agent,
- complete production replay equivalence for topology, provider state, delayed effects or time-dependent behavior,
- live AWS/AgentCore security effectiveness without separate evidence.

Those remain roadmap items and must not be claimed as production guarantees.
