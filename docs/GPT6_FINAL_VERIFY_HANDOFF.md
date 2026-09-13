# GPT-6 Final Narrow Verification Handoff

Status: final read-only pre-merge verification after the targeted PR #67 re-audit remediation.

## Purpose

This is not a new repository audit and not a repeat of the prior re-audit. Reuse the existing Work-session context, original audit findings, prior re-audit report and executable counterexamples.

Resolve Draft PR #67 independently, record its exact current head and compare it with the previously re-audited head `9251510b94e8da42e59b7878b0826d5c519b7e0e`. Stop if you cannot inspect the exact current PR head.

Verify exact-head CI status and test count before judging the remediation.

## Primary goal

Try to falsify only the remediation added after `9251510...`, with priority on the four confirmed re-audit blockers and the mutation survivors.

### N1: source-agent restoration safety

The competition path now intentionally does not support positive replay proof that restores the source agent of the replayed compromised action.

Attack the trusted admission boundary, not only the helper:

- replay blocked only by `tool:memory.write` while proposing `agent:support-agent` release,
- replay runtime/factory that already contains the source agent even though `containment_scopes` omits it,
- direct `ActionLedger.append()` of a positive adversarial replay event,
- missing/substituted `source_action_event_id`, source incident, parent binding or authority scope,
- any path that can still produce/apply an authorized source-agent release without a newly demonstrated post-release safety control.

A safe result is fail-closed. Do not require support for source-agent restoration in this competition build.

### N2: restoration freshness and single use

Try:

- authorize, append any new incident/work event, then apply old restoration,
- apply the same restoration twice,
- release, re-contain, then reuse old restoration,
- direct containment-release ledger append without exact authorized restoration and exact active hold evidence.

A restoration decision must be fresh at application time and consume only one exact hold.

### N3/N4: shared containment and independent holds

With two engines created before containment and sharing one `ActionLedger`:

- contain through one and execute through the other,
- create two incidents holding the same scope,
- release one incident and verify the other hold still blocks both existing controllers,
- recreate a controller from the same ledger and verify union-of-active-holds semantics.

### Medium/mutation closure

Recheck only these prior gaps:

- M-SEM: impossible judge semantics such as 999 verified recoveries in a 3-action represented fixture must fail.
- M-DIRECT: direct `RecoveryEngine.recover()` executor/verifier exceptions must leave deterministic failure/residual evidence.
- M07: active containment cannot be skipped for restoration.
- M10: compensation output cannot choose its own expected success state.
- M12: cached recovery success cannot bypass ledger-integrity verification.

Also verify the new tests assert safe state/effect outcomes rather than labels alone.

## Compact mutation pass

Prefer a small mutation pass only against guards changed after `9251510...`:

- bypass shared-ledger containment lookup,
- bypass exact hold release,
- remove restoration head freshness,
- remove source-agent positive-replay admission rule,
- bypass direct recovery failure accounting,
- bypass judge semantic upper bounds.

A surviving mutation that restores one of the prior exploits is a blocker.

## Claim boundary

Check `README.md`, `docs/PROJECT_CURRENT_STATE.md`, `docs/RECOVERY_INTEGRITY_MODEL.md`, `docs/JUDGE_EVIDENCE_INDEX.md`, `docs/SUBMISSION_DRAFT.md` and `docs/FINAL_PACKAGE_ACCEPTANCE.md` only for claims affected by the remediation.

Preserve these explicit non-claims:

- no authenticated ledger completeness or valid-prefix rollback resistance,
- no distributed-controller consensus,
- no remote proof/approval forgery resistance without an authenticated issuer boundary,
- no globally complete causal capture with missing instrumentation,
- no full production replay topology/provider/time equivalence,
- no live AWS/production security-effectiveness claim,
- no demonstrated safe restoration of the compromised source/root agent.

Do not treat an explicitly stated limitation as a defect.

## Repository safety

READ ONLY. Do not modify files, commits, branches, PR state or merge anything. Synthetic/local probes are allowed. No credentials, paid calls or third-party actions.

## Output

Return exactly:

### 1. Final verdict
`MERGE CANDIDATE`, `MERGE WITH BLOCKERS`, or `DO NOT MERGE`, exact head SHA, exact CI/test evidence and one paragraph of reasoning.

### 2. Re-audit blocker closure
N1, N2, N3, N4: `FIXED`, `PARTIAL`, or `NOT FIXED`, with executable evidence.

### 3. Medium/mutation closure
M-SEM, M-DIRECT, M07, M10, M12 plus compact mutation results.

### 4. Any new Critical/High blocker
Only concrete executable findings. If none, say `None found in this narrow pass`.

### 5. Claim check
Only concrete remaining overclaims affected by this remediation.

### 6. Merge gate
If no blocker remains, say `No code blocker found in this narrow pass` and list only exact-head CI/package/final submission actions. Otherwise list the minimum mandatory fixes.

Spend effort on executable falsification, not prose or broad research.
