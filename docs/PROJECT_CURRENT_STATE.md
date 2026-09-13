# Project Current State

Date: 2026-09-13

## Status

Pre-audit competition baseline:

`de835c3b571261e2398c0dbb619647fa1c2860fa`

That exact build had green CI with 120 deterministic tests on Python 3.10 and 3.12, benchmark smoke and credential-free judge reproduction. A GPT-6 adversarial architecture audit found reproducible lifecycle counterexamples that the green suite did not cover.

Draft PR #67 on `audit-blockers-2026-09-12` remediated the original audit and reached a green 139-test exact head. A targeted GPT-6 re-audit then attacked exact head `9251510b94e8da42e59b7878b0826d5c519b7e0e` and found four additional submission-blocking lifecycle flaws. Those findings have now been remediated on the same Draft PR and converted into permanent regressions.

Current frozen candidate head for final narrow verification:

`85b877577b1ec1cb8ba26f03e452dddbb26a7c1a`

Exact-head CI run `34738049109` is green on Python 3.10 and 3.12 with Ruff, **152 passed tests**, B01-B10 benchmark smoke, credential-free judge reproduction, canonical semantic validation and SHA-256 manifest verification.

The candidate is not accepted main authority until final narrow read-only GPT-6 verification and merge gate pass.

The product remains a recovery-first control layer for autonomous AI agents, not a generic AI-security suite.

Category:

**incident -> containment -> evidence -> recovery -> replay -> verified restoration**

Core rules for the bounded competition implementation:

**No autonomous write without a validated Recovery Contract.**

**No represented downstream authority release without complete represented recovery evidence and a current scope-bound replay.**

The competition path intentionally keeps the compromised replay source/root agent contained rather than claiming that its own replay proves it safe to restore.

## Adversarial hardening history

The first audit exposed composed lifecycle failures including incomplete restoration gates, wrong-action/stale replay use, containment loss after reconstruction, duplicate approval use across controllers, shared-state recovery hazards, malformed contract metadata, compensator-selected verification targets, recovery approval misuse, evidence aliasing and missing failure accounting.

The targeted re-audit of `9251510...` found four further blockers:

1. A source agent could be released after a replay that was made safe only by a different or hidden containment boundary.
2. An authorized restoration decision could become stale before application or be reused after a renewed hold.
3. Containment was cached per controller, so a controller created before another controller's containment could still execute.
4. One incident's release of a scope could erase another incident's independent hold on the same scope.

The current candidate addresses those findings rather than narrowing them away.

## Candidate deterministic trust boundary in PR #67

The candidate now includes:

1. Strict Recovery Contract validation before executor invocation.
2. Advisory-only model/planner output with no execution authority.
3. Parameter-bound action approvals and context-bound recovery approvals.
4. Single-use approval consumption at the shared in-memory ledger boundary.
5. Shared-ledger authoritative active containment, observed by already-created and recreated controllers.
6. Independent containment holds per incident and scope, with union-of-active-holds enforcement.
7. Fresh, single-use restoration application bound to one exact active hold.
8. Fail-closed positive replay admission when a replay would authorize restoration of its own source agent.
9. Direct ledger append paths subject to the same source-agent positive-replay and exact containment-release admission policy.
10. Deep-detached ledger/event payloads so exported evidence cannot alias stored nested state.
11. Integrity verification before privileged recovery/restoration decisions and before cached recovery reuse.
12. Incident binding before recovery-result cache reuse.
13. Cross-incident and later-writer protection for represented mutable resources.
14. Recovery targets fixed from preserved pre-action evidence before compensation executes.
15. Pre-existing permissions preserved when recovering a no-op grant.
16. Ambiguous action executor/verifier outcomes recorded as uncertain represented effects and residual obligations.
17. Direct recovery executor/verifier failures recorded as explicit recovery failure and residual evidence.
18. Exact source-action replay binding for agent, tool, parameter digest and contract version.
19. Replay bound to source ledger head and recovery generation at run time.
20. Replay runtime contract-manifest checks for represented executed source actions.
21. One proposed release scope per replay; that exact release scope may not remain explicitly listed in replay containment.
22. Later applicable replay verdicts supersede earlier ones for the same release scope.
23. Re-stamping old ReplayEvidence after source/recovery change is rejected.
24. Restoration requires active containment, complete represented local recovery obligations, no uncovered residual and the latest applicable current positive replay for the exact scope.
25. Judge incident evidence validates semantic ranges, cross-field correspondence and bounded upper relationships.
26. Original audit, targeted re-audit and mutation-survivor counterexamples are represented as permanent deterministic regressions.

## Exact-head validation evidence

On frozen candidate `85b877577b1ec1cb8ba26f03e452dddbb26a7c1a`, CI run `34738049109` passed:

- Ruff,
- Python 3.10,
- Python 3.12,
- 152 deterministic tests,
- B01-B10 contract coverage 10/10,
- B06 bounded three-agent blast-radius recall 1.0,
- B06 bounded three-agent blast-radius precision 1.0,
- B06 verified recoveries 3,
- B06 restored downstream authorities 2,
- B06 root agent remains contained true,
- measured authority-resurrection successes 0,
- B07 explicit residual effects 2,
- credential-free judge reproduction,
- canonical incident evidence round-trip and semantic validation,
- SHA-256 judge manifest verification,
- authority-free judge reproduction manifest.

Scenario-specific `unsafe_recovery_executions` fields remain part of benchmark outputs, but the project does not present their aggregate as one globally comparable execution-rate metric because individual scenarios have different bounded meanings.

## Integrity and replay limits

The project states these boundaries explicitly:

- The ledger is a locally tamper-evident retained history, not an authenticated transparency log or WORM store.
- Hash chaining detects chain-breaking mutation/reordering/internal deletion within retained history; without an externally committed head/length it does not prove completeness or detect rollback to a self-consistent valid prefix.
- Single-use approval and containment-hold behavior is demonstrated for controllers sharing one in-memory `ActionLedger`; distributed/persistent consensus is not implemented.
- Replay is a bounded synthetic replay of one exact represented attack action. It binds source/recovery state, represented source contract versions and one proposed release scope, but it is not proof of full production topology, provider state, delayed-effect or time-dependent equivalence.
- The compromised source/root agent is not claimed safe to restore and remains contained in the demonstrated competition path.
- Causal and shared-resource guarantees are limited to relationships/resource identities represented in ledger/contracts. Missing instrumentation cannot be inferred away.
- Runaway-loop coverage demonstrates post-containment write blocking, not complete token/read cost control.
- Judge artifacts and benchmark results are synthetic deterministic evidence, not global or production security effectiveness.
- No live Bedrock/AgentCore security-effectiveness claim exists.
- Production multi-tenancy, external attestation, malicious recovery providers, distributed controllers and authenticated capability issuance remain outside the competition implementation.

## Competition evidence boundary

Allowed claims must remain bounded to deterministic evidence. The project may claim that the represented fixtures demonstrate:

- fail-closed missing/malformed contract handling before represented side effects,
- parameter/context-bound approvals in the bounded engine,
- shared-ledger authoritative containment and independent incident holds,
- represented cross-agent blast-radius reconstruction,
- explicit recovery/residual truth,
- rejection of the audited source-agent replay/restoration counterexample,
- fresh single-use application of scoped downstream restoration,
- prevention of the audited same-resource recovery clobber/resurrection sequences,
- credential-free deterministic reproduction and packaging.

Do not convert these into claims of universal attack prevention, arbitrary production rollback, globally complete evidence, remote forgery resistance or production recovery effectiveness.

## Current gate: final narrow verification before merge

Draft PR #67 remains unmerged until all are true:

1. Exact current PR-head CI is green on Python 3.10 and 3.12 with the complete 152-test suite, benchmark smoke and judge reproduction. **PASS on `85b877...`, run `34738049109`.**
2. `docs/GPT6_FINAL_VERIFY_HANDOFF.md` is used for a narrow read-only GPT-6 verification that retests N1-N4, M-SEM, M-DIRECT and mutation gaps M07/M10/M12 rather than repeating a full repository audit.
3. Any new confirmed Critical/High submission blocker is fixed and regression-tested.
4. README, this file, `RECOVERY_INTEGRITY_MODEL.md`, `JUDGE_EVIDENCE_INDEX.md` and `SUBMISSION_DRAFT.md` describe the same bounded guarantees.
5. Final exact-head package acceptance and clean judge reproduction remain green on the frozen candidate.

Only then should PR #67 be merged and the visual/demo/submission branches synchronized onto accepted main.

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
