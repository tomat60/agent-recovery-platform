# GPT-6 Targeted Adversarial Re-Audit Handoff

Status: owner-gated pre-merge review for Draft PR #67.

## Purpose

This is **not** a second full repository audit. The full adversarial audit has already been completed against baseline commit:

`de835c3b571261e2398c0dbb619647fa1c2860fa`

That audit found reproducible lifecycle safety failures despite a green 120-test suite. Draft PR #67 (`audit-blockers-2026-09-12`) is the remediation branch.

The purpose of this pass is to try to falsify the **fixes**, detect incomplete remediation or newly introduced safety failures, and decide whether PR #67 is safe enough to merge for the competition build.

## Pin the exact review target

1. Resolve Draft PR #67 in `tomat60/agent-recovery-platform`.
2. Record its exact current head SHA.
3. Verify its merge base is the audited baseline `de835c3b571261e2398c0dbb619647fa1c2860fa` or explain any deviation.
4. Review the diff from that baseline to the exact PR head. Do not silently review `main` instead.
5. Verify current PR CI status and exact test count from GitHub Actions.

If the PR/head cannot be resolved exactly, stop immediately and report the blocker rather than auditing the wrong snapshot.

## Read only what is needed

Start with:

1. this file,
2. the original audit report if present in the Work session/context,
3. PR #67 diff,
4. changed source files,
5. changed/new tests,
6. changed claim-boundary documentation,
7. unchanged surrounding implementation only where necessary to test a specific hypothesis.

Do **not** reread all 37 source modules and all tests from scratch unless a concrete finding requires it.

## Original confirmed findings that must be retested

The baseline audit confirmed:

- C1: restoration authorized unrecovered/unrelated authority.
- C2: replay could use the wrong action, be restamped after state/generation change, and an older success could survive a later failed replay.
- C3: containment was lost after engine reconstruction and one approval could execute twice across pre-existing controllers.
- H1: recovery could destroy a later legitimate writer's shared state across incidents.
- H2: incomplete/out-of-order recovery could resurrect earlier poisoned state.
- H3: malformed contract security metadata could reach an irreversible executor before failure.
- H4: verification could trust a recovery target selected by the compensator itself.
- H5: an original-action approval could authorize a different recovery operation.
- H6: exported nested evidence could alias live recovery evidence and recovery did not fail closed on corrupted evidence.
- H7: adapter/verification failures could leave effects outside recovery/residual accounting.
- M1: cached recovery success could bypass incident binding.
- M2: judge evidence validation accepted contradictory/impossible semantic claims.

For each item, determine one of:

- `FIXED — falsification attempt now fails closed`,
- `PARTIALLY FIXED — residual counterexample remains`,
- `NOT FIXED`,
- `CLAIM NARROWED — implementation does not provide the broader guarantee but public docs now state the exact bounded limitation`.

Do not mark an item fixed merely because a matching new test exists. Inspect and attack the actual implementation.

## Highest-value attack targets in the remediation

Prioritize these new or changed boundaries:

1. **Proposed-release replay policy**
   - Try to prove release of a scope while that same scope remains contained in replay.
   - Try equivalent scope spellings/agent-tool confusion if possible.
   - Check whether downstream restoration is actually justified by the replayed path.

2. **Replay action/environment binding**
   - Wrong tool, params, agent, contract version.
   - Missing or changed source contract in replay runtime.
   - Extra/different relevant policy that makes the replay easier than production.
   - Duplicate matching source actions causing ambiguity.
   - Old ReplayEvidence after source/recovery changes.
   - Later negative verdict followed by older positive consumption.

3. **Restoration completeness**
   - Skip one recoverable action.
   - Leave an uncertain action.
   - Leave an irreversible/uncovered residual.
   - Use reconciliation evidence for the wrong action.
   - Restore an unrelated or never-contained scope.
   - Try release after a prior restoration/containment transition invalidates evidence for another scope.

4. **Shared-state recovery**
   - Same resource across incidents.
   - Later writer with equal value (ABA/value-equality trap).
   - Later writer that was itself recovered.
   - Causal same-resource chain with a caller-supplied incomplete plan.
   - Reconciliation plus subsequent recovery ordering.

5. **Approval single-use and binding**
   - Two pre-existing engines sharing one ledger.
   - Action-vs-recovery purpose confusion.
   - Incident, generation, contract-version and source-action substitution.
   - Reconciliation approval reuse.
   - State whether atomicity is only in-process/shared-ActionLedger, not distributed.

6. **Evidence integrity**
   - Mutate exported nested evidence.
   - Directly corrupt retained ledger before recovery.
   - Valid-prefix truncation/alternate valid history: verify this is now claimed only as a limitation, not falsely fixed.

7. **Failure accounting**
   - Executor raises before mutation.
   - Executor mutates then raises.
   - Verifier raises after effect.
   - Recovery executor raises a non-RuntimeError.
   - Ensure restoration cannot treat uncertain recoverable effects as complete.

8. **Judge/benchmark truth**
   - Contradictory semantic values.
   - Hardcoded/proxy unsafe-execution metrics.
   - Confirm public submission wording is no stronger than executable evidence.

## New-regression quality check

Inspect `tests/test_gpt6_audit_regressions.py`, `tests/test_audit_recovery_integrity.py` and changed existing tests.

Look for tests that merely assert the implementation's new label rather than an independent safe outcome. Prefer state/effect assertions and negative authorization outcomes.

Check whether any original unsafe expectation was simply renamed instead of corrected.

## Mutation/falsification pass

Do a compact targeted mutation pass against the changed guards. Prefer at least these mutations if practical:

- allow replay release scope to remain in `containment_scopes`,
- remove exact source-action match,
- ignore source contract-manifest mismatch,
- allow ReplayEvidence to be recorded against a changed source head,
- consume an older positive replay after a later negative replay,
- skip recovery-obligation completeness in restoration,
- skip active-containment requirement in restoration,
- disable shared-ledger one-shot approval consumption,
- allow recovery cache lookup before incident binding,
- trust recovery executor `after` as expected state,
- bypass contract enum/type validation,
- skip ledger integrity check at recovery entry.

Report which current tests kill each mutation. If a mutation survives, treat that as a finding even if no exploit sequence is immediately demonstrated.

## Claim audit

Review at minimum:

- `README.md`
- `docs/PROJECT_CURRENT_STATE.md`
- `docs/RECOVERY_INTEGRITY_MODEL.md`
- `docs/JUDGE_EVIDENCE_INDEX.md`
- `docs/SUBMISSION_DRAFT.md`

The docs intentionally narrow several guarantees. Do not penalize an explicitly stated limitation for not being implemented. Instead flag any wording that still implies more than the code/evidence supports.

Especially preserve these limits unless new evidence proves otherwise:

- no authenticated ledger completeness / valid-prefix rollback resistance,
- no distributed-controller consensus guarantee,
- no remote proof/approval-forgery guarantee without authenticated issuer/capability boundary,
- no globally complete causal capture when instrumentation edges are missing,
- no full production replay topology/provider/time equivalence,
- no production or live AWS security-effectiveness claim.

## Repository safety

This re-audit is READ-ONLY.

Do not modify files, create commits, push, merge, change PR state, or implement fixes.

Synthetic/local test probes are allowed. Do not interact with third-party systems or request credentials.

## Output

Produce exactly these sections:

### 1. Re-audit verdict
- `MERGE CANDIDATE`, `MERGE WITH BLOCKERS`, or `DO NOT MERGE`
- exact PR head SHA
- CI status/test count verified
- one-paragraph reason

### 2. Original finding closure matrix
For C1-C3, H1-H7, M1-M2: status, evidence, residual risk.

### 3. New Critical/High findings
For each: severity, confidence, exact references, minimal counterexample, violated invariant, smallest correction, falsification test.

### 4. Medium/low findings worth fixing before submission
Only concrete findings, not style advice.

### 5. Targeted mutation results
Mutation, killed/survived, killing test or missing test.

### 6. Competition claim audit
Any remaining overclaim, with exact file/text reference and safer wording.

### 7. Merge gate
A short ordered list of mandatory actions before merge. If none, explicitly say `No code blocker found in this targeted pass` and list only verification/final-package steps.

## Allowance discipline

Spend effort on falsification, not prose. Reuse the original audit context if available. Do not restart the full audit. Do not perform broad external research. Prefer executable counterexamples and exact code/test references.

The most valuable result is a new concrete counterexample that still passes the hardened test suite.
