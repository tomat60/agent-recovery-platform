# Project Current State

Date: 2026-09-07

## Status

M0 and M1 are accepted. M2 remains active on `main`.

Authoritative implementation head before this documentation checkpoint:

`c1f40cb4450167ed53d5d56d7d00c65f60537418`

The product remains a **recovery-first control layer for autonomous AI agents**, not a generic AI-security suite.

Category:

**incident -> containment -> evidence -> recovery -> replay -> verified restoration**

Core rules:

**No autonomous write without a recovery path.**

**No restored authority without a verified replay.**

## Accepted deterministic boundary

Accepted implementation now includes:

1. Recovery Contracts for write-capable tools with fail-closed missing/malformed contract behavior.
2. Parameter-bound approvals for consequential actions; model/planner text is never authorization.
3. Tamper-evident append-oriented action/evidence ledger with SHA-256 previous-hash/event-hash chaining and integrity verification.
4. Source-incident binding, causal incident graph and blast-radius reconstruction across agent handoffs and shared state.
5. Scoped containment and reverse-causal, dependency-aware, idempotent recovery.
6. Shared-resource identities plus fail-closed same-resource conflict handling; independent writes to different CRM fields are preserved.
7. Explicit reconciliation controls for genuinely conflicting writes, including incident and Recovery Contract version binding.
8. Partial compensation failure semantics: failed and dependency-blocked compensation remain explicit residual effects rather than false recovery.
9. Irreversible/externalized effects remain residual; repaired local state becomes an explicit recovery generation/fork instead of pretending external history was undone.
10. Replay freshness bound to source attack/action evidence and recovery-plane evidence.
11. Isolated Replay Lab whose verdict is derived from observed tamper-evident replay evidence rather than caller-provided success flags.
12. Fail-closed authority restoration when replay evidence is missing, stale, cross-incident, forged, tampered or unsuccessful.
13. One-time recovery-fork proofs and one-time parameter-bound authority consumption reconstructed from ledger evidence after runtime recreation.
14. Authority-resurrection replay protection: a consumed approval cannot be reused by a recreated runtime to duplicate an external effect.
15. Bounded runaway write-loop containment at the deterministic tool boundary.
16. Recovery-path attack coverage: an untrusted recovery plan cannot turn its own claimed authorization into permission for a high-impact write.

## Benchmark coverage accepted to date

The deterministic suite now has direct coverage for the following benchmark classes or equivalent accepted fixtures:

- B02 tool-output poisoning
- B03 memory poisoning
- B04 approval bypass
- B06 cascading multi-agent failure
- B07 partial compensating workflow failure
- B08 irreversible external effect semantics
- B09 runaway write-loop containment
- B10 recovery-path attack
- authority-resurrection / semantic replay attempts
- concurrent/shared-state conflict and reconciliation behavior

The remaining benchmark-contract work should focus first on any scenario whose behavior is only indirectly covered, especially a judge-legible B01 indirect prompt-injection trajectory and explicit B05 over-scoped-identity fixture, then on fuller metric aggregation across all scenarios.

Do not invent benchmark numbers. Existing numeric results are deterministic synthetic evidence only, not production effectiveness claims.

## Latest accepted slice

PR #18 `Benchmark recovery-path attack authorization` was accepted after exact-head CI on `0538f5bacaaa172ceff77de4638f83fcb99ac0d5`.

Both Python 3.10 and Python 3.12 jobs passed install, lint and tests. Python 3.12 additionally passed benchmark smoke and uploaded benchmark evidence. PR #18 was squash-merged as:

`c1f40cb4450167ed53d5d56d7d00c65f60537418`

The B10 fixture deliberately supplies malicious planner output that claims authorization to grant `deploy:prod`. The deterministic execution boundary receives the proposed tool and parameters but no real `Approval`; the action is blocked and no unauthorized permission side effect is created. This proves the deterministic authorization boundary only. It does **not** claim generic prompt-injection prevention.

## Evidence limitations

- The ledger is a prototype tamper-evident in-process log, not WORM storage, remote attestation or an externally anchored transparency log.
- Replay Lab currently proves bounded replay against synthetic/owned state, not arbitrary full production transaction reconstruction.
- Runaway-loop coverage proves post-containment write blocking, not token-cost metering or comprehensive denial-of-wallet prevention.
- Deterministic fixtures do not establish production security effectiveness by themselves.

## Current milestone

M2 should now finish benchmark breadth and metric aggregation rather than accumulate more unmeasured primitives.

### Next highest-leverage implementation work

1. Add a judge-legible B01 indirect prompt-injection trajectory fixture from synthetic external input through contaminated agent behavior to a consequential action attempt and recovery evidence.
2. Add an explicit B05 over-scoped identity / privilege-boundary fixture if existing privilege coverage does not already expose that metric cleanly.
3. Aggregate the benchmark contract metrics across scenarios: containment, blast-radius recall/precision, root-cause accuracy where applicable, recovery-plan correctness, restoration, residual-effect accuracy, unsafe recovery action rate, replay attack success, evidence completeness, safe restoration and false-positive containment.
4. Add incident-to-regression conversion and fuller Replay Lab semantics where they improve measurable evidence.
5. Then integrate Strands Investigator / Recovery Planner / Skeptic over read-only evidence. Model output may investigate, propose and critique; it must never authorize execution.
6. After the deterministic boundary is broad and measured, pursue the bounded Bedrock / AgentCore competition path and judge-facing UX.

## Competition target

Demo story:

**attack -> cross-agent propagation -> blast-radius graph -> scoped containment -> dependency-safe recovery -> residual truth -> adversarial replay -> verified restoration**

Agents for Humans deadline: 2026-09-14.

RolePilot is a separate product and must continue independently. Do not mix production RolePilot or RolePilot competition code into this repository.

## Owner-only gates expected later

- AWS login/MFA or Builder ID
- AWS promotional credits if still available
- Bedrock model access / credentials
- approval of any new AWS spend or persistent paid resource
- public Devpost / Builder / video publishing
- final competition submission

No owner action is required for the current deterministic implementation.

## Commercial validation after competition

Initial offer: **Agent Recoverability Assessment** for one real write-capable agent workflow.

Within roughly 30 days after the competition target:

- 10 qualified buyer/partner conversations
- 2 concrete pilot/assessment interests
- 1 MSSP/security/AI consultancy partner candidate
- limited independent senior AppSec/cloud/AI-security review before a serious external pilot

Do not build heavy multi-tenant enterprise SaaS before this validation.
