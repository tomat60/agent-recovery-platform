# Project Current State

Date: 2026-09-12

## Status

The pre-audit competition baseline was exact `main` commit:

`de835c3b571261e2398c0dbb619647fa1c2860fa`

That build had green exact-head CI with 120 deterministic tests on Python 3.10 and 3.12, benchmark smoke and credential-free judge reproduction. A GPT-6 adversarial architecture audit then deliberately tried to falsify the safety guarantees and found reproducible lifecycle counterexamples that the green suite did not cover.

Those findings are being remediated in **Draft PR #67** from branch `audit-blockers-2026-09-12`. This file describes the candidate hardened state on that branch. It is **not accepted main authority until the PR passes targeted adversarial re-review, exact-head CI and merge approval**.

The product remains a **recovery-first control layer for autonomous AI agents**, not a generic AI-security suite.

Category:

**incident -> containment -> evidence -> recovery -> replay -> verified restoration**

Core rules for the bounded competition implementation:

**No autonomous write without a validated Recovery Contract.**

**No represented authority release without complete represented recovery evidence and a current scope-bound replay.**

## Why the adversarial hardening exists

The original green suite missed composed lifecycle failures, including:

- restoration authorization without completed recovery or scope binding,
- replay of the wrong action and re-stamping old replay evidence,
- use of an earlier positive replay after a later negative replay,
- containment loss after runtime reconstruction,
- duplicate one-shot approval use across pre-existing controllers sharing one ledger,
- recovery clobbering a later legitimate writer,
- incomplete dependency handling that could resurrect earlier bad state,
- malformed contract metadata reaching an executor before failure,
- recovery verification against a target selected by the compensator itself,
- original-action approval being reused for a different recovery operation,
- exported nested evidence aliasing live ledger/recovery inputs,
- adapter failures escaping residual accounting,
- cached recovery success crossing incident identity,
- judge-artifact validation accepting contradictory semantic claims.

The fixes are kept as permanent falsification regressions rather than hidden as one-off patches.

## Candidate deterministic trust boundary in PR #67

The hardened branch now includes:

1. Strict typed Recovery Contract validation before executor invocation.
2. Model/planner text remains advisory and is never authorization.
3. Parameter-bound action approvals and context-bound recovery approvals.
4. Single-use approval consumption at the shared in-memory ledger boundary.
5. Active containment reconstruction from retained ledger evidence after engine recreation.
6. Deep-detached ledger/event payloads so exported evidence cannot alias stored nested state.
7. Integrity verification before privileged recovery/restoration decisions.
8. Incident binding before recovery-result cache reuse.
9. Cross-incident and later-writer protection for represented mutable resources.
10. Recovery targets fixed from preserved pre-action evidence before compensation executes.
11. Pre-existing permissions preserved when recovering a no-op grant.
12. Ambiguous executor/verifier outcomes recorded as uncertain represented effects and residual obligations.
13. Broader compensation-adapter failures converted into explicit failure/residual evidence.
14. Exact source-action binding for replay: agent, tool, parameter digest and contract version.
15. Replay execution bound to source ledger head and recovery generation at run time.
16. Replay checks that the isolated runtime contains the contract versions used by represented executed source actions.
17. One proposed release scope per replay; that exact release scope may not remain contained during the replay.
18. Later applicable replay verdicts supersede earlier ones for the same release scope.
19. Re-stamping old ReplayEvidence after source/recovery change is rejected.
20. Restoration requires active containment, complete represented local recovery obligations, no uncovered residual and the latest applicable current positive replay for the exact scope.
21. Runtime containment release is a separate recorded transition that consumes an authorized restoration decision for that exact scope.
22. Judge incident evidence validates semantic ranges and correspondence to the measured score, not only object shape.
23. GPT-6 counterexamples are represented as permanent deterministic regression tests.

## Current validation evidence on the branch

Latest verified CI before documentation synchronization passed on both Python 3.10 and 3.12 with:

- Ruff lint green,
- 139 deterministic tests green,
- B01-B10 benchmark smoke green,
- B06 bounded three-agent blast-radius recall 1.0,
- B06 bounded three-agent blast-radius precision 1.0,
- measured containment success 1.0 in represented scenarios,
- measured replay attack success 0.0 in the represented replay scenario,
- measured authority-resurrection successes 0,
- aggregate represented unsafe recovery executions 0,
- credential-free judge reproduction green,
- canonical incident evidence round-trip green,
- SHA-256 judge manifest verification green,
- authority-free judge reproduction manifest green.

Documentation commits after that CI require a fresh exact-head run before merge. Do not treat the numbers above as evidence for a later untested head.

## Integrity and replay limits

The project now states these boundaries explicitly:

- The ledger is a locally tamper-evident retained history, not an authenticated transparency log or WORM store.
- A hash chain detects chain-breaking mutation/reordering/internal deletion within the retained history; without an externally committed head/length it does not prove completeness or detect rollback to a self-consistent valid prefix.
- Single-use approval atomicity is demonstrated for controllers sharing one in-memory `ActionLedger`; distributed/persistent consensus is not implemented.
- Replay is a bounded synthetic replay of one exact represented attack action. It binds source/recovery state, represented source contract versions and one proposed release scope, but it is not proof of full production topology, provider state, delayed-effect or time-dependent equivalence.
- Causal and shared-resource guarantees are limited to relationships/resource identities represented in the ledger and contracts. Missing instrumentation cannot be inferred away.
- Runaway-loop coverage demonstrates post-containment write blocking, not complete token/read cost control.
- The judge artifact and benchmark are synthetic deterministic evidence, not global or production security effectiveness.
- No live Bedrock/AgentCore security-effectiveness claim exists.
- Production multi-tenancy, external attestation, malicious recovery providers, distributed controllers and authenticated capability issuance remain outside the competition implementation.

## Competition evidence boundary

Allowed claims must remain phrased as bounded deterministic evidence. In particular, the project may claim that the current represented fixture demonstrates:

- fail-closed missing/malformed contract handling before represented side effects,
- parameter/context-bound approvals in the bounded engine,
- retained-ledger containment reconstruction,
- represented cross-agent blast-radius reconstruction,
- explicit recovery/residual truth,
- prevention of the audited replay/restoration counterexamples by regression tests,
- scoped downstream restoration while the compromised root remains contained,
- credential-free deterministic reproduction and packaging.

Do not convert those into claims of universal attack prevention, arbitrary production rollback, globally complete evidence, remote forgery resistance or production recovery effectiveness.

## Current gate: targeted re-audit before merge

Draft PR #67 must remain unmerged until all of the following are true:

1. Exact PR-head CI is green on Python 3.10 and 3.12.
2. All original confirmed GPT-6 counterexample classes have explicit regression coverage or a documented narrowed claim boundary.
3. A targeted adversarial re-audit of the PR diff attempts to bypass the new guards rather than rereading the repository from scratch.
4. Any new confirmed Critical/High submission blocker is fixed and regression-tested.
5. README, this file, `RECOVERY_INTEGRITY_MODEL.md`, `JUDGE_EVIDENCE_INDEX.md` and `SUBMISSION_DRAFT.md` describe the same bounded guarantees.
6. Final exact-head package acceptance and clean judge reproduction pass after the final code/document head is frozen.

Only then should the PR be considered for merge and final competition packaging.

## Post-competition research backlog

Priority research remains:

- stateful/property/model checking over lifecycle transitions,
- true concurrency, TOCTOU and ABA schedules,
- authenticated durable evidence with externally committed sequence/head,
- distributed controller/approval consensus,
- framework-neutral causal trace ingestion and independent recall measurement,
- full replay topology/provider/environment reconstruction,
- authenticated capability/issuer boundaries around approval and recovery-control APIs,
- denial-of-wallet budgets/cancellation/backpressure,
- production multi-tenancy and cloud rollback attestation.

## Owner-only gates

- AWS login/MFA or Builder ID
- AWS credentials/model access
- promotional credits or new spend/payment
- public video/Devpost/Builder publishing
- competition terms acceptance
- final competition submission

Agents for Humans deadline: 2026-09-14.

RolePilot is a separate product and must continue independently. Do not mix production RolePilot or RolePilot competition code into this repository.
