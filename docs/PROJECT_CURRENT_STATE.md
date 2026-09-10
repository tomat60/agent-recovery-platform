# Project Current State

Date: 2026-09-10

## Status

M0, M1 and the deterministic M2 benchmark/recovery core are accepted. M3 now includes the evidence-only Strands advisory chain, deterministic Advisory Gate and B01-B10 measurement, fail-closed rejection/regression conversion, deterministic judge packaging, full deterministic incident evidence across the recovery lifecycle, authority-free judge-console rendering, credential-free one-command incident reproduction, an exact judge evidence index, and a final exact-head package acceptance gate.

Current accepted `main` head:

`7e6107023dff7e5bc8a3293f4e6a22479088c595`

The product remains a **recovery-first control layer for autonomous AI agents**, not a generic AI-security suite.

Category:

**incident -> containment -> evidence -> recovery -> replay -> verified restoration**

Core rules:

**No autonomous write without a recovery path.**

**No restored authority without a verified replay.**

## Deterministic trust boundary

Accepted implementation includes:

1. Recovery Contracts for write-capable tools with fail-closed missing/malformed-contract behavior.
2. Parameter-bound approvals for consequential actions. Model/planner text is never authorization.
3. Tamper-evident append-oriented action/evidence ledger with chained hashes and integrity verification.
4. Incident binding, causal reconstruction and blast-radius evidence across agent handoffs/shared state.
5. Scoped containment and dependency-aware, idempotent recovery controls.
6. Explicit conflict/reconciliation evidence for shared-resource writers.
7. Partial-compensation semantics that keep failed or dependency-blocked effects visible.
8. Irreversible/externalized effects remain residual; local repaired state never rewrites external history.
9. Replay freshness and isolated Replay Lab evidence that can invalidate false restoration claims.
10. Fail-closed authority restoration when replay evidence is absent, stale, cross-incident, forged, tampered or unsuccessful.
11. One-time recovery/approval consumption reconstructed from ledger evidence after runtime recreation.
12. Authority-resurrection protection and bounded runaway-write containment.
13. Recovery-path attack coverage preventing untrusted recovery text from self-authorizing writes.
14. Incident-to-regression contracts bound to source incident/evidence/invariants.
15. Integrity-verified read-only evidence views for investigation.
16. Strands Investigator, Recovery Planner and independent Skeptic/Verifier with no write/restore authority.
17. Deterministic Advisory Gate that rebinds proposals to incident evidence and produces candidate plans only.
18. Versioned deterministic B01-B10 advisory fixtures plus exact-suite, rejection-safety and advisory-evidence scoring.
19. Fail-closed conversion of properly rejected advisory evidence into deterministic regression contracts.
20. Deterministic judge artifacts/package with canonical JSON and SHA-256 manifests.
21. Authority-free judge console/runbook that renders only represented evidence.
22. Full deterministic incident evidence contract for blast radius, containment, recovery execution/result, residual effects, replay and restoration evidence.
23. Judge-console rendering of that verified full incident evidence without granting execution/restoration authority.
24. Credential-free one-command deterministic incident reproduction with canonical round-trip validation and hash manifesting.
25. Final judge-readiness and claim-to-evidence boundaries that prohibit claims not supported by represented deterministic evidence.
26. Judge evidence index tying claims to reproducible artifacts.
27. Exact-head final package acceptance gate covering clean reproduction, canonical round-trip, SHA-256 manifests, residual-risk visibility, replay invalidation, secret/customer-data absence and documentation consistency.

## Benchmark contract coverage

The deterministic aggregate contract covers required competition classes:

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

Additional deterministic coverage includes authority-resurrection/semantic replay attempts, concurrent/shared-state conflict/reconciliation and false-positive containment-scope measurement.

The last explicitly recorded aggregate security checkpoint remains the bounded deterministic report from PR #25:

- benchmark contract coverage: 10/10 classes
- B06 blast-radius recall: 1.0
- B06 blast-radius precision: 1.0
- measured containment success rate: 1.0 across the then-measured deterministic scenarios
- measured replay attack success rate: 0.0 for the then-measured replay scenario
- false-positive containment rate: 0.0 across 3 known-benign scopes in that bounded fixture
- authority-resurrection successes: 0
- unsafe recovery executions across that aggregate deterministic contract report: 0

These are **synthetic deterministic benchmark results only**, not production security-effectiveness claims. Later M3 work adds evidence and packaging machinery but does not create replacement aggregate numbers unless a measured artifact explicitly records them.

## Accepted M3 slices

The accepted sequence includes:

- PR #29: deterministic Advisory Gate producing candidate-only plans
- PR #30: advisory-chain deterministic ground-truth scorer
- PRs #31-#40: versioned B01-B10 advisory ground-truth fixtures
- PR #41: aggregate measured advisory benchmark scores
- PR #42: fail-closed exact B01-B10 fixture-suite loader
- PR #43: fail-closed Advisory Gate rejection-safety measurement
- PR #44: aggregate Advisory Gate rejection-safety reporting
- PR #45: exact advisory fixture-suite scoring
- PR #46: rejected advisory evidence to deterministic regression contracts
- PR #47: authority synchronization through advisory/regression milestone
- PR #48: deterministic B01-B10 judge advisory artifact
- PR #49: authority-free judge advisory console
- PR #50: deterministic judge demo runbook
- PR #51: deterministic judge evidence package with SHA-256 manifest
- PR #53: full deterministic incident evidence contract
- PR #54: bounded competitive recovery radar refresh
- PR #55: verified full-incident evidence rendering in judge console
- PR #56: one-command credential-free deterministic incident reproduction
- PR #57: current judge-readiness checkpoint and claim boundary
- PR #58: judge-readiness synchronization with accepted recovery evidence
- PR #59: final judge-package claim-to-evidence boundary review
- PR #60: final judge evidence index and authority synchronization
- PR #61: exact-head final package acceptance gate

Accepted `main` after PR #61 is `7e6107023dff7e5bc8a3293f4e6a22479088c595`.

## Evidence limitations

- The ledger is a prototype tamper-evident in-process log, not WORM storage, remote attestation or an externally anchored transparency log.
- Replay Lab proves bounded replay against synthetic/owned state, not arbitrary production transaction reconstruction.
- Runaway-loop coverage proves post-containment write blocking, not token-cost metering or comprehensive denial-of-wallet prevention.
- Current false-positive containment measurement covers bounded known scopes after the compromised scope is known; it does not measure generic attack-detection quality.
- Advisory and judge metrics/evidence are deterministic synthetic fixture measurements. They do not establish production root-cause accuracy, recovery-plan correctness or global security effectiveness.
- Irreversible external effects are never claimed as undone.
- Production recovery success rate and time-to-containment remain intentionally unclaimed.
- No live Bedrock/AgentCore security-effectiveness claim exists yet.

## Current milestone: final competition package

The strongest credential-free path is the source of truth for judging and CI. Remaining competition work is package consistency, exact-head verification and owner-gated public submission, not scope expansion.

Next order:

1. Keep `docs/JUDGE_EVIDENCE_INDEX.md`, this authority file, README/runbook and exact submitted head consistent.
2. Require exact-head deterministic CI and clean credential-free reproduction before accepting the package.
3. Verify package hashes, residual-effect visibility, replay invalidation behavior and absence of secrets/customer data.
4. Keep model/Strands advisory output visibly separate from deterministic authorization/execution truth.
5. Use Bedrock/AgentCore only if owner-approved access/cost exists and only where it adds verifiable recovery evidence. The deterministic path remains the fallback/source of truth.
6. Prepare public video/Devpost/Builder material, but public upload, terms acceptance and final submission remain owner-only.

Demo story:

**attack -> cross-agent propagation -> blast-radius graph -> scoped containment -> investigator -> recovery planner -> skeptic challenge -> deterministic candidate gate -> dependency-safe recovery -> residual truth -> adversarial replay -> verified restoration**

Agents for Humans deadline: 2026-09-14.

RolePilot is a separate product and must continue independently. Do not mix production RolePilot or RolePilot competition code into this repository.

## Owner-only gates

- AWS login/MFA or Builder ID
- AWS credentials/model access
- promotional credits or new spend/payment
- public video/Devpost/Builder publishing
- competition terms acceptance
- final competition submission

No owner action is required for the current credential-free implementation and package verification.

## Commercial validation after competition

Initial offer: **Agent Recoverability Assessment** for one real write-capable agent workflow.

Within roughly 30 days after competition:

- 10 qualified buyer/partner conversations
- 2 concrete pilot/assessment interests
- 1 MSSP/security/AI consultancy partner candidate
- limited independent senior AppSec/cloud/AI-security review before a serious external pilot

Do not build heavy multi-tenant enterprise SaaS before this validation.
