# Project Current State

Date: 2026-09-07

## Status

M0, M1 and the deterministic M2 benchmark/recovery core are accepted. M3 now has an evidence-only Strands advisory chain plus a deterministic candidate-plan boundary:

**EvidenceView -> Investigator -> Recovery Planner -> Skeptic/Verifier -> deterministic Advisory Gate**

Current accepted `main` head before this documentation commit:

`cc92d25a817a6c8152b00bf39e2dd64f6333c29d`

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
18. An integrity-verified, incident-scoped read-only investigation boundary. Prompt payloads carry evidence only, never approvals, executors, capabilities or mutable ledger handles.
19. A Strands Investigator that produces evidence-cited incident hypotheses without write tools or execution authority.
20. A Strands Recovery Planner that produces ordered evidence-cited candidate steps and explicit residual risks without execution authority.
21. An independent Strands Skeptic/Verifier that challenges investigator/planner claims against incident evidence and cannot restore authority.
22. A deterministic Advisory Gate that rebinds all advisory proposals to the incident evidence view and fails closed on cross-incident evidence, missing/duplicate claim review, unsupported or uncertain skeptic verdicts, forged step evidence and unresolved dependencies. Passing this gate creates only a candidate recovery plan; it does not approve or execute recovery.

## Benchmark contract coverage

The deterministic aggregate report covers all required competition benchmark classes B01-B10:

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

The last explicitly recorded benchmark checkpoint in this document remains the PR #25 deterministic report:

- benchmark contract coverage: 10/10 classes
- B06 blast-radius recall: 1.0
- B06 blast-radius precision: 1.0
- measured containment success rate: 1.0 across the currently measured deterministic scenarios
- measured replay attack success rate: 0.0 for the currently measured replay scenario
- false-positive containment rate: 0.0 across 3 known-benign scopes in the bounded fixture
- authority-resurrection successes: 0
- unsafe recovery executions across the aggregate deterministic contract report: 0

These are **synthetic deterministic benchmark results only**, not production security-effectiveness claims. Do not infer new benchmark numbers from later code changes until a measured artifact records them.

## Latest accepted slices

Recent accepted product slices:

- PR #24: incident-to-regression evidence contract
- PR #25: read-only investigation evidence boundary
- PR #26: read-only Strands Investigator runtime
- PR #27: read-only Strands Recovery Planner runtime
- PR #28: independent Strands Skeptic/Verifier runtime
- PR #29: deterministic advisory recovery gate producing candidate-only plans

PR #29 exact-head `943cfb2146ea2b4686e29924ae3004bb86719621` passed `recovery-ci` before squash merge. It was merged into `main` as `cc92d25a817a6c8152b00bf39e2dd64f6333c29d`.

## Evidence limitations

- The ledger is a prototype tamper-evident in-process log, not WORM storage, remote attestation or an externally anchored transparency log.
- Replay Lab proves bounded replay against synthetic/owned state, not arbitrary full production transaction reconstruction.
- Runaway-loop coverage proves post-containment write blocking, not token-cost metering or comprehensive denial-of-wallet prevention.
- Current false-positive containment measurement covers bounded known scopes after the compromised scope is known; it does not measure generic attack-detection quality.
- The advisory gate establishes evidence and skeptic requirements for candidate plans; it does not yet measure broad root-cause or recovery-plan correctness.
- Global root-cause accuracy, recovery-plan correctness, full evidence completeness, broad recovery success rate and time-to-containment remain intentionally unclaimed until measured.
- No live Bedrock/AgentCore security-effectiveness claim exists yet.

## Current milestone: M3 measured advisory intelligence

The advisory chain now exists. The next highest-leverage work is to measure it before adding judge-facing UI or live-cloud claims.

### Next implementation order

1. Add deterministic benchmark fixtures for root-cause accuracy, recovery-plan correctness and advisory evidence completeness.
2. Make the benchmark scorer consume the Investigator -> Planner -> Skeptic -> Advisory Gate outputs without allowing model text to become authorization.
3. Add incident-to-regression cases where an unsupported or uncertain advisory claim must remain rejected even when the proposed recovery would otherwise look plausible.
4. Keep a credential-free deterministic/mock path for CI.
5. Add a bounded live Strands + Bedrock path only after owner approval for model access/cost.
6. Integrate AgentCore Gateway/Policy/observability only where it strengthens authorization outside the source agent and produces useful recovery evidence.
7. Build the judge-facing incident console after the measured advisory path is stable.

## Competition target

Demo story:

**attack -> cross-agent propagation -> blast-radius graph -> scoped containment -> investigator -> recovery planner -> skeptic challenge -> deterministic candidate gate -> dependency-safe recovery -> residual truth -> adversarial replay -> verified restoration**

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
