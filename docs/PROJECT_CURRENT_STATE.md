# Project Current State

Date: 2026-09-06

## Status

M0 and M1 are accepted on `main`. M2 is active and now includes the differentiated recovery lifecycle, recovery-plane integrity, machine-derived replay evidence, explicit recovery lineage for irreversible effects, and narrower shared-state recovery that avoids clobbering legitimate peer-agent writes.

Current accepted `main` commit before this documentation checkpoint:

`41d9b5364afac28c05bdb4be55688401afd9ea7e`

Accepted M2 capabilities now include:

1. causal incident graph, source-incident binding, reverse-causal ordered recovery and idempotency
2. canonical shared-resource identities and fail-closed concurrent-writer conflict detection
3. deterministic three-agent attack -> containment -> blast-radius reconstruction -> dependency-safe recovery -> replay -> verified downstream restoration
4. tamper-evident SHA-256 action-ledger hash chain with full-ledger integrity verification
5. replay freshness bound to both source attack/action evidence and recovery-plane evidence
6. isolated Replay Lab whose restoration verdict is derived from observed tamper-evident replay evidence rather than caller-supplied success booleans
7. fail-closed authority restoration for missing, stale, cross-incident, forged, tampered or unsuccessful replay evidence
8. explicit recovery generations for repaired local state after irreversible/externalized effects, while preserving external history
9. recovery-fork proofs bound to real verified recovery execution and consumable only once
10. residual-effect coverage tracking across recovery generations
11. parameter-bound approval-bypass benchmark coverage
12. field-scoped CRM recovery that can restore one compromised field without overwriting an independent legitimate field update
13. same-field independent-writer conflicts remain fail-closed

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

Established scenarios now include:

1. reversible CRM corruption
2. memory poisoning
3. parameter-bound approval bypass attempt
4. compensatable privilege change
5. irreversible external message

Observed benchmark properties remain truthful:

- recoverable scenarios remove the synthetic residual state they are designed to repair
- the approval-bypass fixture fails closed and produces no unauthorized privilege side effect
- irreversible external message remains explicitly residual
- unsafe recovery executions remain zero in the current deterministic benchmark

### M2 causal/shared-state recovery

Accepted capabilities:

- causal event graph across external input, tool output, memory reads, agent handoffs and actions
- explicit source-incident binding for recovery
- reverse-causal recovery ordering
- idempotent recovery steps
- Recovery-Contract resource identities
- detection of causally independent writers to the same mutable resource
- fail-closed recovery when concurrent state could be overwritten
- one-time parameter-bound authority consumption reconstructed from ledger evidence after runtime recreation
- CRM resources now identify exact contact fields rather than an entire contact
- recovery of one compromised CRM field preserves independent legitimate writes to other fields
- independent writers to the same exact field still require explicit reconciliation and fail closed

### M2 recovery-plane integrity

Accepted through merge commit:

`cf127a7241573eedfd0f5d7ea7e7dd132861aeec`

Capabilities:

- append-oriented action ledger with SHA-256 previous-hash/event-hash chain
- `verify_integrity()` detects payload mutation, deletion, reordering and hash-chain discontinuity
- Restoration Gate fails closed when source-ledger integrity is uncertain
- replay verification is bound to a source-evidence fingerprint and recovery-state fingerprint
- later attack/action evidence invalidates source replay freshness
- later containment/recovery/residual-effect/fork evidence invalidates recovery freshness

This is a prototype tamper-evident in-process ledger. It is **not** a production WORM store, signed transparency log, remote attestation mechanism or externally anchored proof. Production hardening should anchor trusted ledger heads outside the protected agent process.

### M2 machine-derived Replay Lab

Accepted through merge commit:

`80f653e88a4732bcfcbad05b4a4237ed4d65223c`

The restoration boundary no longer accepts caller-provided replay success booleans.

The isolated Replay Lab:

- verifies source-ledger integrity before replay
- creates a fresh synthetic recovery runtime with its own tamper-evident ledger
- preserves configured containment for the replayed path
- copies the actual source `EXTERNAL_INPUT` payload into the isolated replay
- executes the bounded replay recipe
- verifies isolated replay-ledger integrity
- derives source-payload match, blocked entry action and actual side-effect events from ledger evidence
- binds the recorded verification to the isolated replay ledger head
- requires `isolated_replay_lab` provenance before restoration

### M2 recovery fork lineage

Accepted through merge commit:

`e27222d291b29c8d3cf4ecf41bff70b42061900b`

Capabilities:

- repaired local state after an externalized/irreversible effect becomes a new recovery generation rather than pretending history was rewritten
- `RECOVERY_FORKED` evidence is part of the tamper-evident ledger
- a fork requires a real local recovery verification causally bound to `RECOVERY_EXECUTED`
- adversarial replay verification cannot substitute for local recovery proof
- one verified recovery proof cannot be reused to mint multiple generations
- residual external effects stay referenced cumulatively across later generations
- new residual effects after a fork remain explicitly uncovered until a later verified generation acknowledges them
- fork evidence participates in replay freshness, so authority restoration cannot rely on replay evidence from an older recovery generation

### Current exact-head CI evidence

PR #12 exact head `20cf50af27fdd8a9c2fa4a59378697d422ec75e1` passed `recovery-ci` on Python 3.10 and Python 3.12.

On Python 3.12:

- lint passed
- **39 deterministic tests passed**
- benchmark smoke passed
- benchmark evidence artifact uploaded successfully

Current judge-facing synthetic benchmark still reports:

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

M2 remains active, but the two previously highest-priority gaps have now materially advanced:

- explicit replay/fork semantics for externalized effects are implemented at the deterministic evidence layer
- shared-state handling is less over-conservative because independent writes to different fields can be recovered without clobbering each other

The remaining hard case is genuinely ambiguous same-field or same-resource concurrent reconciliation.

### Next implementation priority

1. Add an explicit, evidence-backed reconciliation strategy for truly conflicting same-resource writers without allowing heuristic state overwrite.
2. Expand deterministic fixtures toward the full benchmark contract:
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
   - authority resurrection / semantic replay attempt
3. Expand measured evidence: evidence completeness, recovery-plan correctness, compensation success, residual-effect accuracy, recovery-integrity failure, replay attack success after remediation, safe restoration rate and false-positive containment.
4. Add incident-to-regression conversion and fuller Replay Lab semantics.
5. Once this deterministic boundary is broad enough, integrate Strands Investigator / Recovery Planner / Skeptic over read-only evidence. Model output may propose and critique; it must never become authorization.
6. Then integrate the bounded AWS/AgentCore competition path and judge-facing UX.

## Competition target

The demo remains a multi-agent incident-recovery story:

**attack -> cross-agent propagation -> blast-radius graph -> scoped containment -> dependency-safe recovery -> residual truth -> adversarial replay -> verified restoration**

The strongest judge-facing contrast is that the system does not merely rewind state. It proves which authority may safely return while compromised authority remains quarantined.

Agents for Humans deadline: 2026-09-14.

RolePilot remains a separate project and must continue developing independently. Do not mix RolePilot production or competition code into this repository.

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
