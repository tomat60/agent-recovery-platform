# Judge Evidence Index

Date: 2026-09-12

Pre-audit baseline: `de835c3b571261e2398c0dbb619647fa1c2860fa`

Candidate hardened branch: `audit-blockers-2026-09-12` / Draft PR #67.

This index is a competition-packaging map only. It does not grant approval, execution, compensation, replay, restoration or production-security authority. PR #67 remains unaccepted until targeted adversarial re-review and final exact-head verification pass.

## Reproducible judge path

The credential-free path is the default source of truth for judging and CI:

1. reproduce the bounded synthetic incident,
2. validate the represented deterministic incident evidence and cross-field semantics,
3. render only represented evidence in the judge console,
4. package canonical evidence with SHA-256 manifest entries,
5. run bounded exact-action replay under the proposed release policy,
6. keep advisory/model output separate from authorization and execution truth,
7. run exact-head CI and final package acceptance before owner review.

## Adversarial hardening evidence

The original green 120-test baseline was independently adversarially audited. Confirmed counterexamples were converted into code changes and permanent regression tests on PR #67. The branch includes evidence for:

- containment surviving recreation from the same retained ledger,
- one-shot approval consumption across pre-existing controllers sharing one `ActionLedger`,
- malformed Recovery Contract metadata failing before executor side effects,
- recovery preserving pre-existing valid permissions,
- recovery approval purpose/context binding,
- exported nested evidence not aliasing stored ledger/recovery state,
- ledger corruption blocking recovery before mutation,
- ambiguous post-effect observation and compensation failure remaining explicit,
- cached recovery result incident binding,
- later/cross-incident shared-resource writers blocking unsafe before-image recovery,
- exact source-action replay binding,
- execution-time replay freshness and anti-restamping,
- supersession of older replay success by a later applicable failure,
- proposed release scope not remaining contained during its replay,
- represented source contract-version presence in the replay runtime,
- restoration requiring complete represented recovery and exact scope-bound replay,
- semantic judge-evidence validation.

The latest green validation run before documentation synchronization passed 139 tests on Python 3.10 and 3.12, plus benchmark smoke and judge reproduction. A later documentation/code head must rerun CI before it can inherit that evidence.

## Claims allowed by current candidate evidence

Only claims directly represented by deterministic artifacts may be made. The hardened bounded implementation can claim evidence that it can:

- reject missing or malformed represented Recovery Contracts before executor invocation,
- bind consequential approvals to represented requests and prevent duplicate use in controllers sharing one in-memory ledger,
- reconstruct represented active containment from the retained ledger after runtime recreation,
- reconstruct represented blast radius from recorded causal edges,
- prevent the audited same-resource recovery clobber/resurrection sequences,
- expose unsuccessful compensation, uncertain effects and irreversible effects as residual risk,
- compare recovered state against a target fixed from preserved pre-action evidence,
- reject stale, restamped, superseded, wrong-action, release-scope-mismatched and represented contract-environment-mismatched replay evidence,
- require complete represented local recovery before scoped restoration authorization,
- keep the compromised root contained while selectively releasing downstream scopes in the bounded B06 fixture,
- reproduce the bounded judge incident without cloud credentials,
- validate canonical evidence/manifest bytes and reject contradictory judge-artifact semantics.

These are synthetic deterministic benchmark/demo claims only.

## Claims prohibited without new evidence

Do not claim:

- production security effectiveness,
- universal attack detection or prevention,
- arbitrary production rollback,
- reversal of irreversible external effects,
- authenticated completeness of the in-process hash-chain ledger,
- resistance to rollback to a self-consistent valid ledger prefix without an external head commitment,
- remote proof/approval forgery resistance without an authenticated capability/issuer boundary,
- distributed single-use authority across independently persisted controllers,
- globally complete causal capture when instrumentation edges are missing,
- complete production replay equivalence for topology, provider state, delayed side effects or time-dependent behavior,
- production recovery success rate or time-to-containment,
- live Bedrock or AgentCore security effectiveness,
- that Strands/model output authorizes execution,
- that the compromised root agent has been demonstrated safe to restore.

## Integrity interpretation

SHA-256 chaining in the prototype proves internal consistency of the retained local history. It is useful for detecting chain-breaking mutation, internal deletion/reordering and payload tampering. It is not an external authenticity/completeness proof. Production claims would require authenticated durable append provenance and independently committed head/sequence information.

## Replay interpretation

The Replay Lab currently proves a narrower statement than full environment reconstruction:

- the selected replay action must correspond to exactly one represented source action on the source trigger path,
- agent/tool/parameters/contract version must match,
- the source ledger head and recovery generation are captured at run time,
- represented contract versions used by executed incident actions must exist in the replay runtime,
- one release scope is bound to the proof and that scope may not remain contained during replay,
- later applicable replay evidence supersedes earlier evidence for that scope.

This is sufficient for the bounded competition fixture and regression claims. It is not a claim that all production environment state/topology has been reconstructed.

## Owner-only gates

The deterministic package is allowed to advance without AWS credentials. The following remain owner-only:

- AWS login/MFA or Builder ID actions,
- Bedrock/model access or credentials,
- new AWS spend or paid persistent resources,
- public video/Devpost/Builder publishing,
- final competition submission or terms acceptance.

## Final packaging acceptance

Before public submission, accept the package only when the exact submitted head proves all of the following:

- deterministic CI is green on supported Python versions,
- GPT-6 targeted re-audit of the hardened diff reports no unresolved submission-blocking Critical/High finding,
- original confirmed adversarial counterexamples are covered by regressions or an explicit narrowed claim boundary,
- one-command judge reproduction succeeds from a clean environment without paid model calls,
- canonical incident evidence survives round-trip and semantic validation,
- packaged SHA-256 hashes validate,
- the console contains no authority claim not backed by represented deterministic evidence,
- residual external effects remain visible,
- replay can invalidate a false restoration assertion and cannot justify releasing the same scope by keeping it contained,
- no secret, credential, customer data or production incident data is included,
- README/current-state/integrity model/submission draft and this index agree on the bounded evidence boundary.

Public submission remains a separate explicit owner action.
