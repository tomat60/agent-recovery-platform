# Project Current State

Date: 2026-09-06

## Status

M0 and M1 are accepted on `main`.

The secure distributed-recovery foundation has now advanced through three M2 slices:

1. causal incident graph, ordered recovery plans, incident binding and idempotency
2. shared-state conflict detection plus replay/authority-restoration integrity
3. a deterministic three-agent attack -> contain -> recover -> replay -> restore benchmark

Current accepted `main` commit:

`5e9b62b98587836dea77993fe2e8b5d8a0c7a2b2`

The repository now contains the product strategy, threat model, Recovery Contract specification, deterministic recovery core, synthetic enterprise, causal incident graph, shared-state conflict detector, dependency-safe recovery planner, one-time authority-consumption ledger evidence, adversarial replay binding, fail-closed restoration gate, CI and machine-generated benchmark evidence.

## Product decision

Build a **recovery-first control layer for autonomous AI agents**, not a generic AI-security platform and not a generic agent undo tool.

Category ownership:

**incident -> containment -> evidence -> recovery -> replay -> verified restoration**

Core rules:

**No autonomous write without a recovery path.**

**No restored authority without a verified replay.**

## Competitive differentiation

Current direct and adjacent systems include Rubrik Agent Rewind, Toffoli, Agit, Walkback, Moholo Agent Rewind, OWASP Agent Memory Guard, RAC, Atomix, Mnemosyne, ACRFence and the Agents for Humans competitor Authority Cut.

Therefore:

- "undo for AI agents" is not a novelty claim
- reversibility classification is prior art
- compensation / saga semantics are prior art
- action journals and kill switches are prior art
- single-agent selective rollback is already commercially occupied

The differentiated wedge is:

**distributed multi-agent incident recovery + recovery-path security + adversarial replay + verified restoration**

See `docs/COMPETITIVE_LANDSCAPE.md`.

## Accepted implementation evidence

### M1 vertical slice

M1 release commit:

`70b47a90d84628c63c6f781b9a668a84c08c80c3`

M1 established four deterministic scenarios:

1. reversible CRM corruption
2. memory poisoning
3. compensatable privilege change
4. irreversible external message

Observed evidence remains:

- three recoverable scenarios: one residual effect in stop-only baseline, zero after verified recovery
- three verified recoveries
- irreversible external message remains explicitly residual
- unsafe recovery executions: zero

### M2 causal and shared-state recovery

Accepted capabilities now include:

- causal event graph across external input, tool output, memory reads, agent handoffs and actions
- explicit source-incident binding for recovery
- reverse-causal recovery ordering
- idempotent recovery steps
- canonical resource identities declared by Recovery Contracts
- detection of causally independent writers to the same shared resource
- fail-closed recovery when a concurrent-writer conflict could overwrite legitimate state
- cross-agent conflict evidence

### M2 recovery-path integrity

Merged at:

`c2d8afb2b47401936f556cd989e7a2f6790b4b0f`

Capabilities:

- `AUTHORITY_CONSUMED` ledger evidence
- parameter-bound one-time approval consumption
- consumed authority reconstructed from the ledger after runtime recreation
- replay of a consumed approval is blocked instead of resurrecting stale authority
- adversarial replay evidence bound to a fingerprint of the source incident
- replay evidence becomes stale if new attack/action/authority evidence appears
- fail-closed `RestorationGate`
- authority restoration rejected for missing, stale, cross-incident or failed replay evidence

CI for this slice passed on Python 3.10 and 3.12 with **23 passing deterministic tests**.

### M2 three-agent verified-restoration benchmark

Merged at:

`5e9b62b98587836dea77993fe2e8b5d8a0c7a2b2`

Current judge-facing deterministic scenario:

1. poisoned external support content enters the graph
2. Support Agent writes contaminated shared memory
3. CRM Agent consumes the memory and mutates customer state
4. Identity Agent receives the downstream handoff and changes a high-impact permission
5. the platform reconstructs the cross-agent blast radius
6. the compromised Support Agent is quarantined
7. downstream state is recovered in dependency-safe reverse-causal order
8. the entry path is replayed in isolation under preserved quarantine
9. replay produces zero executed side effects
10. downstream clean-agent authority becomes restorable only after verified replay
11. the compromised root agent remains contained

Accepted CI evidence for the PR that produced this main commit:

- Python 3.10: lint + tests passed
- Python 3.12: lint + tests + benchmark smoke + artifact upload passed
- **24 deterministic tests passed**
- agents involved: 3
- expected blast actions: 3
- detected blast actions: 3
- blast-radius recall: 1.0
- blast-radius precision: 1.0
- verified recoveries: 3
- platform residual effects in this recoverable chain: 0
- adversarial replay verified: true
- downstream authorities restored: 2
- root compromised agent remains contained: true
- unsafe recovery executions: 0

These are synthetic benchmark results, not production effectiveness claims.

## Current milestone

M2 remains active. The foundation now demonstrates the differentiated lifecycle end to end, but it is not yet strong enough to claim production-grade distributed recovery.

### Next implementation slice

Priority order:

1. Replace caller-supplied replay verdict booleans with machine-derived replay evidence from an isolated Replay Lab.
2. Add tamper-evident ledger integrity and a trusted-head / proof model so recovery evidence cannot be silently rewritten.
3. Add explicit replay-or-fork semantics for externalized effects and restored local generations.
4. Add concurrent-writer reconciliation strategies instead of only failing closed.
5. Expand the deterministic benchmark to the full adversarial set:
   - indirect prompt injection trajectory
   - tool-output poisoning
   - approval bypass
   - privilege escalation
   - cascading multi-agent failure
   - concurrent shared-state writers
   - partial compensating workflow failure
   - runaway / denial-of-wallet loop
   - recovery-path attack
   - semantic replay / authority resurrection attempt
6. Expand benchmark metrics:
   - blast-radius recall / precision
   - evidence completeness
   - compensation success rate
   - residual irreversible effects
   - recovery-integrity failures
   - stale-authority resurrection attempts blocked
   - verified replay pass rate
   - safe restoration rate
7. Add fail-closed tests for malformed contracts, broken causal references, tampered ledger evidence, forged replay evidence, recovery re-entry and fabricated recovery success.
8. After the deterministic safety boundary is strong, integrate Strands agents as Investigator / Planner / Skeptic. Model output may propose and critique; it must never become the authorization boundary.

## Competition target

The demo must remain a multi-agent incident-recovery story, not a generic undo demonstration.

Target visible flow:

**attack -> cross-agent propagation -> blast-radius graph -> scoped containment -> dependency-safe recovery -> residual truth -> adversarial replay -> verified restoration**

The strongest judge-facing contrast is that the system does not merely rewind state. It proves which authority may safely come back and keeps compromised authority quarantined.

## Competition deadline

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

Initial commercial offer: **Agent Recoverability Assessment**, explicitly testing multi-agent and shared-state recovery rather than only per-tool reversibility.

Within approximately 30 days after the competition, seek:

- 10 qualified buyer/partner conversations
- at least 2 concrete pilot/assessment interests
- at least 1 MSSP/security/AI consultancy partner candidate
- independent senior security architecture review before a serious external pilot

Buyer-facing metrics should include:

- recoverability coverage of the side-effecting action surface
- blast radius under controlled incident injection
- evidence completeness
- verified recovery rate
- residual irreversible exposure
- restoration time
- percentage of authority safely restorable after replay

If recovery repeatedly fails to map to an owned budget or urgent buyer pain, pivot before building heavy enterprise SaaS infrastructure.
