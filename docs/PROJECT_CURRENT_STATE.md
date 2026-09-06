# Project Current State

Date: 2026-09-06

## Status

M0 and M1 are accepted on `main`. M2 is active and now includes the differentiated recovery lifecycle plus recovery-plane integrity hardening.

Current accepted `main` commit before this documentation checkpoint:

`80f653e88a4732bcfcbad05b4a4237ed4d65223c`

Accepted M2 capabilities now include:

1. causal incident graph, source-incident binding, reverse-causal ordered recovery and idempotency
2. canonical shared-resource identities and fail-closed concurrent-writer conflict detection
3. deterministic three-agent attack -> containment -> blast-radius reconstruction -> dependency-safe recovery -> replay -> verified downstream restoration
4. tamper-evident SHA-256 action-ledger hash chain with full-ledger integrity verification
5. replay freshness bound to both source attack/action evidence and recovery-plane evidence
6. isolated Replay Lab whose restoration verdict is derived from observed tamper-evident replay evidence rather than caller-supplied success booleans
7. fail-closed authority restoration for missing, stale, cross-incident, forged, tampered or unsuccessful replay evidence

## Product decision

Build a **recovery-first control layer for autonomous AI agents**, not a generic AI-security platform and not a generic undo tool.

Category ownership:

**incident -> containment -> evidence -> recovery -> replay -> verified restoration**

Core rules:

**No autonomous write without a recovery path.**

**No restored authority without a verified replay.**

The differentiated wedge remains:

**distributed multi-agent incident recovery + recovery-path security + adversarial replay + verified restoration**

## Accepted implementation evidence

### M1 deterministic vertical slice

Four deterministic scenarios remain established:

1. reversible CRM corruption
2. memory poisoning
3. compensatable privilege change
4. irreversible external message

Observed evidence:

- three recoverable scenarios: one residual effect in stop-only baseline, zero after verified recovery
- irreversible external message remains explicitly residual
- unsafe recovery executions: zero

### M2 causal/shared-state recovery

Accepted capabilities:

- causal event graph across external input, tool output, memory reads, agent handoffs and actions
- explicit source-incident binding for recovery
- reverse-causal recovery ordering
- idempotent recovery steps
- Recovery-Contract resource identities
- detection of causally independent writers to the same shared resource
- fail-closed recovery when concurrent state could be overwritten
- one-time parameter-bound authority consumption reconstructed from ledger evidence after runtime recreation

### M2 recovery-plane integrity

Accepted on `main` through merge commit:

`cf127a7241573eedfd0f5d7ea7e7dd132861aeec`

Capabilities:

- append-oriented action ledger with SHA-256 previous-hash/event-hash chain
- `verify_integrity()` detects payload mutation, deletion, reordering and hash-chain discontinuity
- Restoration Gate fails closed when source-ledger integrity is uncertain and does not append new evidence to an already untrusted ledger
- replay verification is bound to a source-evidence fingerprint and recovery-state fingerprint
- later attack/action evidence invalidates source replay freshness
- later containment/recovery/residual-effect evidence invalidates recovery freshness

This is a prototype tamper-evident in-process ledger. It is **not** a production WORM store, signed transparency log, remote attestation mechanism or externally anchored proof. Production hardening should anchor trusted ledger heads outside the protected agent process.

### M2 machine-derived Replay Lab

Accepted on `main` through squash merge:

`80f653e88a4732bcfcbad05b4a4237ed4d65223c`

The restoration boundary no longer accepts caller-provided `attack_blocked` / `evidence_complete` success booleans.

The isolated Replay Lab now:

- verifies source-ledger integrity before replay
- creates a fresh synthetic recovery runtime with its own tamper-evident ledger
- preserves configured containment for the replayed path
- copies the actual source `EXTERNAL_INPUT` payload into the isolated replay
- executes the bounded replay recipe
- verifies isolated replay-ledger integrity
- derives source-payload match, blocked entry action and actual `ACTION_EXECUTED` side-effect event IDs from ledger events
- binds the recorded verification to the isolated replay ledger head
- requires `isolated_replay_lab` provenance before restoration

Exact-head CI for the accepted PR passed on Python 3.10 and 3.12. On Python 3.12:

- lint passed
- **31 deterministic tests passed**
- benchmark smoke passed
- benchmark evidence artifact uploaded successfully

Judge-facing synthetic benchmark evidence remains:

- agents involved: 3
- expected blast actions: 3
- detected blast actions: 3
- blast-radius recall: 1.0
- blast-radius precision: 1.0
- verified recoveries: 3
- platform residual effects in the recoverable chain: 0
- adversarial replay verified: true
- downstream authorities restored: 2
- root compromised agent remains contained: true
- unsafe recovery executions: 0

These are deterministic synthetic benchmark results, not production effectiveness claims.

## Replay limitation

The Replay Lab currently proves a **bounded entry-path replay** against synthetic/owned state. It does not yet reconstruct or attest an arbitrary full production transaction trajectory, external irreversible effect or compromised-process runtime. Do not market it as full transaction replay or remote attestation.

## Current milestone

M2 remains active. Recovery-path integrity and machine-derived replay evidence are now strong enough to move the implementation frontier away from point hardening and toward broader replay semantics and benchmark coverage.

### Next implementation priority

1. Add explicit replay/fork semantics for externalized effects and restored local generations.
2. Add safe reconciliation strategies for concurrent writers instead of only failing closed.
3. Expand deterministic fixtures toward the full benchmark contract:
   - indirect prompt injection trajectory
   - tool-output poisoning
   - memory poisoning
   - approval bypass
   - privilege escalation
   - cascading multi-agent failure
   - partial compensating workflow failure
   - irreversible external effect
   - runaway / denial-of-wallet loop
   - recovery-path attack
4. Expand measured evidence: evidence completeness, recovery-plan correctness, compensation success, residual-effect accuracy, recovery-integrity failure, replay attack success after remediation, safe restoration rate and false-positive containment.
5. Add incident-to-regression conversion and fuller Replay Lab semantics.
6. Once this deterministic boundary is sufficiently broad, integrate Strands Investigator / Recovery Planner / Skeptic over read-only evidence. Model output may propose and critique; it must never become authorization.

## Competition target

The demo remains a multi-agent incident-recovery story:

**attack -> cross-agent propagation -> blast-radius graph -> scoped containment -> dependency-safe recovery -> residual truth -> adversarial replay -> verified restoration**

The strongest judge-facing contrast is that the system does not merely rewind state. It proves which authority may safely return while compromised authority remains quarantined.

Agents for Humans deadline: 2026-09-14.

RolePilot remains a separate maintenance project. Do not mix its competition code into this repository.

## Owner gates expected later

- AWS login/MFA or Builder ID
- AWS promotional credit request if still available
- Bedrock model access / credentials
- approval of any new AWS spend or persistent paid resource
- public Devpost / Builder / video publishing
- final competition submission

No owner action is required for the current deterministic implementation.

## Commercial validation after competition

Initial offer: **Agent Recoverability Assessment** for one real write-capable agent workflow, explicitly covering shared-state and multi-agent recovery.

Within roughly 30 days after the competition target:

- 10 qualified buyer/partner conversations
- 2 concrete pilot/assessment interests
- 1 MSSP/security/AI consultancy partner candidate
- independent senior AppSec/cloud/AI-security review before a serious external pilot

Do not build heavy multi-tenant enterprise SaaS before this validation.