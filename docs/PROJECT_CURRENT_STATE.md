# Project Current State

Date: 2026-09-07

## Status

M0 and M1 are accepted. The deterministic M2 benchmark/recovery core has reached the intended competition breadth and the project is now entering M3: advisory Strands investigation/planning over a read-only evidence boundary.

Current accepted `main` head before this documentation checkpoint:

`5c1d9fe91841d13f14818ca1b67964d8a0d1ee64`

The product remains a **recovery-first control layer for autonomous AI agents**, not a generic AI-security suite.

Category:

**incident -> containment -> evidence -> recovery -> replay -> verified restoration**

Core rules:

**No autonomous write without a recovery path.**

**No restored authority without a verified replay.**

## Accepted deterministic boundary

Accepted implementation includes:

1. Recovery Contracts for write-capable tools with fail-closed missing/malformed contract behavior.
2. Parameter-bound approvals for consequential actions; model/planner text is never authorization.
3. Tamper-evident append-oriented action/evidence ledger with SHA-256 previous-hash/event-hash chaining and integrity verification.
4. Source-incident binding, causal incident graph and blast-radius reconstruction across agent handoffs and shared state.
5. Scoped containment and reverse-causal, dependency-aware, idempotent recovery.
6. Shared-resource identities, field-scoped conflict preservation and explicit evidence-backed reconciliation for genuine same-resource writer conflicts.
7. Reconciliation authority bound to incident, resource, source action IDs, contract version and fresh ledger evidence.
8. Partial compensation failure semantics: failed and dependency-blocked compensation remain explicit residual effects rather than false recovery.
9. Irreversible/externalized effects remain residual; repaired local state becomes an explicit recovery generation/fork instead of pretending external history was undone.
10. Replay freshness bound to source attack/action evidence and recovery-plane evidence.
11. Isolated Replay Lab whose verdict is derived from observed tamper-evident replay evidence rather than caller-provided success flags.
12. Fail-closed authority restoration when replay evidence is missing, stale, cross-incident, forged, tampered or unsuccessful.
13. One-time recovery-fork proofs and one-time parameter-bound authority consumption reconstructed from ledger evidence after runtime recreation.
14. Authority-resurrection replay protection: a consumed approval cannot be reused by a recreated runtime to duplicate an external effect.
15. Bounded runaway write-loop containment at the deterministic tool boundary.
16. Recovery-path attack coverage: untrusted recovery-plan text cannot turn its own claimed authorization into permission for a high-impact write.
17. Incident-to-regression evidence contracts that bind future regression cases to source incident identity, concrete evidence IDs and explicit invariants.
18. An integrity-verified, incident-scoped read-only investigation boundary for investigator, recovery-planner and skeptic proposals. Prompt payloads carry evidence only, never approvals, executors, capabilities or mutable ledger handles.

## Benchmark contract coverage

The deterministic aggregate report now covers all required competition benchmark classes B01-B10:

- B01 indirect prompt injection trajectory
- B02 tool-output poisoning
- B03 memory poisoning
- B04 approval bypass attempt
- B05 over-scoped identity
- B06 cascading multi-agent failure
- B07 partial compensating workflow failure
- B08 irreversible external effect
- B09 runaway tool loop
- B10 recovery-path attack

Additional coverage includes authority-resurrection / semantic replay attempts, concurrent/shared-state conflict and reconciliation behavior, and false-positive containment-scope measurement.

Latest verified benchmark run on PR #25 head `7511d8afa5ab2ab43e4bba3c25d849b155c449e3` reported:

- benchmark contract coverage: 10/10 classes
- 61 deterministic tests passed on Python 3.12; Python 3.10 test job also passed
- B06 blast-radius recall: 1.0
- B06 blast-radius precision: 1.0
- measured containment success rate: 1.0 across the currently measured deterministic scenarios
- measured replay attack success rate: 0.0 for the currently measured replay scenario
- false-positive containment rate: 0.0 across 3 known-benign scopes in the bounded fixture
- authority-resurrection successes: 0
- unsafe recovery executions across the aggregate deterministic contract report: 0

These are **synthetic deterministic benchmark results only**, not production security-effectiveness claims.

## Latest accepted slices

Since the previous B10 checkpoint, the following product slices were accepted and merged:

- PR #19: judge-legible B01 indirect prompt-injection trajectory
- PR #20: explicit B05 over-scoped identity boundary
- PR #21: aggregate benchmark metrics without invented composite claims
- PR #22: bounded false-positive containment fixture
- PR #23: false-positive containment metric integrated into the benchmark report
- PR #24: incident-to-regression evidence contract
- PR #25: read-only investigation evidence boundary for investigator / recovery planner / skeptic proposals

PR #25 exact-head `recovery-ci` completed successfully on Python 3.10 and 3.12, including lint, tests and benchmark smoke where configured. It was merged into `main` as `5c1d9fe91841d13f14818ca1b67964d8a0d1ee64`.

## Evidence limitations

- The ledger is a prototype tamper-evident in-process log, not WORM storage, remote attestation or an externally anchored transparency log.
- Replay Lab proves bounded replay against synthetic/owned state, not arbitrary full production transaction reconstruction.
- Runaway-loop coverage proves post-containment write blocking, not token-cost metering or comprehensive denial-of-wallet prevention.
- Current false-positive containment measurement covers bounded known scopes after the compromised scope is known; it does not measure generic attack-detection quality.
- Global root-cause accuracy, recovery-plan correctness, full evidence completeness, broad recovery success rate and time-to-containment remain intentionally unclaimed until measured.
- No live Bedrock/AgentCore security-effectiveness claim exists yet.

## Current milestone: M3 advisory intelligence

The next highest-leverage work is no longer more benchmark breadth. It is to add useful agentic intelligence without weakening the deterministic boundary.

### Next implementation order

1. Implement the Strands Investigator over `EvidenceView`, producing evidence-cited root-cause / blast-radius hypotheses only.
2. Implement the Recovery Planner over the same incident-scoped evidence, producing an ordered proposed recovery plan with explicit evidence references, residual-risk assumptions and no execution capability.
3. Implement a separate Skeptic/Verifier that actively challenges investigator/planner claims and can reject unsupported evidence links or unsafe assumptions.
4. Add deterministic validators that turn advisory proposals into either rejected proposals or candidate plans. Model output must never mint approval or bypass Recovery Contracts.
5. Add benchmark fixtures for root-cause accuracy, recovery-plan correctness and evidence completeness so the new AI layer is measured rather than demonstrated only narratively.
6. Add a credential-free deterministic/mock path for CI plus a bounded live Strands + Bedrock path only after owner approval for model access/cost.
7. Integrate AgentCore Gateway/Policy/observability where it strengthens authorization outside the source agent and produces useful evidence.
8. Build the judge-facing incident console only after the advisory-agent path is measured and stable.

## Competition target

Demo story:

**attack -> cross-agent propagation -> blast-radius graph -> scoped containment -> investigator -> recovery planner -> skeptic challenge -> dependency-safe recovery -> residual truth -> adversarial replay -> verified restoration**

Agents for Humans deadline: 2026-09-14.

RolePilot is a separate product and must continue independently. Do not mix production RolePilot or RolePilot competition code into this repository.

## Owner-only gates expected later

- AWS login/MFA or Builder ID
- AWS promotional credits if still available
- Bedrock model access / credentials
- approval of any new AWS spend or persistent paid resource
- public Devpost / Builder / video publishing
- final competition submission

No owner action is required for the current credential-free M3 implementation work.

## Commercial validation after competition

Initial offer: **Agent Recoverability Assessment** for one real write-capable agent workflow.

Within roughly 30 days after the competition target:

- 10 qualified buyer/partner conversations
- 2 concrete pilot/assessment interests
- 1 MSSP/security/AI consultancy partner candidate
- limited independent senior AppSec/cloud/AI-security review before a serious external pilot

Do not build heavy multi-tenant enterprise SaaS before this validation.
