# Project Current State

Date: 2026-09-08

## Status

M0, M1 and the deterministic M2 benchmark/recovery core are accepted. M3 now has an evidence-only Strands advisory chain, deterministic candidate-plan boundary, versioned B01-B10 advisory ground truth, exact-suite measurement, fail-closed rejection safety measurement, and rejected-advisory incident-to-regression conversion.

**EvidenceView -> Investigator -> Recovery Planner -> Skeptic/Verifier -> deterministic Advisory Gate -> measured evidence / regression contract**

Current accepted `main` head:

`24f249cc816b17bdf580e6033dd8504cbec84717`

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
23. Versioned deterministic advisory ground-truth fixtures for B01-B10 with a fail-closed loader requiring exact class coverage, unique scenario/incident identities, valid ground-truth evidence IDs and no model-output authorization claim.
24. Credential-free scoring of bound Investigator -> Planner -> Skeptic -> Advisory Gate outputs for exact root-cause evidence match, ordered recovery-plan correctness and required advisory evidence completeness.
25. Exact-suite scoring that rejects missing or extra scenario outputs rather than silently averaging partial coverage.
26. Observation-only Advisory Gate rejection-safety measurement that detects acceptance mismatches and candidate-plan exposure when rejection was expected.
27. Aggregate rejection-safety reporting over measured scenarios without granting approval, execution or restoration authority.
28. Fail-closed conversion of properly rejected advisory evidence into deterministic regression contracts. Accepted decisions, missing rejection reasons or candidate-plan exposure cannot be converted as safe rejection regressions.

## Benchmark contract coverage

The deterministic aggregate benchmark contract covers all required competition classes B01-B10:

- B01 indirect prompt injection trajectory
- B02 tool-output poisoning
- B03 memory poisoning
- B04 approval bypass attempt
- B05 over-scoped identity / privilege escalation
- B06 cascading multi-agent failure
- B07 partial compensating workflow failure
- B08 irreversible external effect
- B09 runaway tool / denial-of-wallet loop
- B10 recovery-path attack

Additional deterministic coverage includes authority-resurrection / semantic replay attempts, concurrent/shared-state conflict and reconciliation behavior, and false-positive containment-scope measurement.

The last explicitly recorded aggregate security checkpoint remains the PR #25 deterministic report:

- benchmark contract coverage: 10/10 classes
- B06 blast-radius recall: 1.0
- B06 blast-radius precision: 1.0
- measured containment success rate: 1.0 across the then-measured deterministic scenarios
- measured replay attack success rate: 0.0 for the then-measured replay scenario
- false-positive containment rate: 0.0 across 3 known-benign scopes in that bounded fixture
- authority-resurrection successes: 0
- unsafe recovery executions across that aggregate deterministic contract report: 0

These are **synthetic deterministic benchmark results only**, not production security-effectiveness claims. Later M3 advisory work adds measurement machinery and fixture coverage, but this authority file does not invent replacement aggregate numbers without a measured artifact recording them.

## Latest accepted slices

Accepted M3 advisory slices now include:

- PR #29: deterministic advisory recovery gate producing candidate-only plans
- PR #30: advisory-chain deterministic ground-truth scorer
- PRs #31-#40: versioned B01-B10 advisory ground-truth fixtures
- PR #41: aggregate measured advisory benchmark scores
- PR #42: fail-closed exact B01-B10 fixture-suite loader
- PR #43: fail-closed Advisory Gate rejection-safety measurement
- PR #44: aggregate Advisory Gate rejection-safety reporting
- PR #45: exact advisory fixture-suite scoring
- PR #46: rejected advisory evidence to deterministic regression contracts

PR #46 exact head `74cd13bc8ce364145cf2370821359ffeef0fbdaf` passed `recovery-ci` before squash merge. It was merged into `main` as `24f249cc816b17bdf580e6033dd8504cbec84717`.

## Evidence limitations

- The ledger is a prototype tamper-evident in-process log, not WORM storage, remote attestation or an externally anchored transparency log.
- Replay Lab proves bounded replay against synthetic/owned state, not arbitrary full production transaction reconstruction.
- Runaway-loop coverage proves post-containment write blocking, not token-cost metering or comprehensive denial-of-wallet prevention.
- Current false-positive containment measurement covers bounded known scopes after the compromised scope is known; it does not measure generic attack-detection quality.
- Advisory metrics are deterministic fixture measurements. They do not establish production root-cause accuracy or recovery-plan correctness for arbitrary incidents.
- Global production security effectiveness, broad recovery success rate and time-to-containment remain intentionally unclaimed.
- No live Bedrock/AgentCore security-effectiveness claim exists yet.

## Current milestone: M3 evidence packaging and judge-facing recovery story

The credential-free measured advisory path is now structurally complete enough to package before adding cloud claims. The next highest-leverage work is to make existing measured evidence reproducible and judge-readable while preserving the deterministic trust boundary.

### Next implementation order

1. Produce one reproducible machine-readable judge artifact from the exact B01-B10 advisory suite, including per-scenario scores, Advisory Gate rejection-safety outcomes and regression references where applicable. Do not infer unmeasured aggregate claims.
2. Add a bounded judge-facing incident console/report that renders evidence, blast radius, containment, advisory hypotheses, candidate recovery, residual effects and replay/restoration truth from deterministic artifacts rather than from model narration.
3. Keep the credential-free deterministic/mock path as the competition fallback and CI source of truth.
4. Add a bounded live Strands + Bedrock path only after owner approval for model access/cost.
5. Integrate AgentCore Gateway/Policy/observability only where it strengthens authorization outside the source agent and produces useful recovery evidence.
6. Prepare competition demo/package from reproduced evidence. Public upload/submission remains owner-only.

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

No owner action is required for the current credential-free implementation and packaging work.

## Commercial validation after competition

Initial offer: **Agent Recoverability Assessment** for one real write-capable agent workflow.

Within roughly 30 days after the competition target:

- 10 qualified buyer/partner conversations
- 2 concrete pilot/assessment interests
- 1 MSSP/security/AI consultancy partner candidate
- limited independent senior AppSec/cloud/AI-security review before a serious external pilot

Do not build heavy multi-tenant enterprise SaaS before this validation.
