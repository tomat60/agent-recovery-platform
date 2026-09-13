# Final Package Acceptance

Date: 2026-09-13
Historical pre-audit accepted package base: `8b8a080d6902665261d423261f2f2e4e50297685`
Pre-audit competition baseline: `de835c3b571261e2398c0dbb619647fa1c2860fa`
Targeted re-audited hardened head: `9251510b94e8da42e59b7878b0826d5c519b7e0e`

The exact final submitted head must be read from Git and verified after PR #67 is accepted. Do not embed a self-invalidating claim that this document's own parent SHA is the final package head.

This file is a competition packaging and verification gate. It does not grant approval, execution, compensation, replay, restoration, AWS access, or public-submission authority.

## Exact-head acceptance contract

The competition package is ready for owner review only when all items below are proven on the exact submitted head:

1. Deterministic CI is green on Python 3.10 and 3.12 with the complete final test suite.
2. Final narrow GPT-6 verification reports no unresolved submission-blocking Critical/High issue in the PR #67 remediation.
3. `python scripts/reproduce_judge_incident.py` succeeds from a clean Python 3.10+ environment without cloud credentials or paid model calls.
4. The reproduced incident evidence survives canonical JSON round-trip and semantic validation.
5. The generated SHA-256 manifest validates the packaged evidence bytes.
6. Judge-console output renders only represented incident, containment, recovery, residual-effect, replay and restoration evidence.
7. Irreversible or unsuccessfully compensated effects remain visible as residual risk.
8. Replay evidence can invalidate a false restoration claim.
9. The demonstrated compromised source/root agent remains contained; the competition path does not claim its own replay proves it safe to restore.
10. Authorized downstream restoration is applied only while fresh and to one exact represented active containment hold.
11. Controllers sharing the in-memory ledger observe the same represented containment holds, including independent holds from different incidents.
12. Strands/model advisory output remains proposal-only and cannot authorize execution or restoration.
13. No secrets, credentials, customer data, production incident data or private identity data are present in the package.
14. `README.md`, `docs/PROJECT_CURRENT_STATE.md`, `docs/RECOVERY_INTEGRITY_MODEL.md`, `docs/JUDGE_EVIDENCE_INDEX.md`, `docs/SUBMISSION_DRAFT.md` and the judge runbook describe the same bounded claim boundary.

## Claims allowed by current deterministic evidence

The package may demonstrate bounded synthetic evidence that the system can bind incidents to locally tamper-evident evidence, reconstruct represented blast radius, enforce shared-ledger containment holds, apply controlled recovery in owned/synthetic state, preserve residual external effects, independently verify represented restored state, reject the audited source-agent self-restoration proof pattern, and apply selective downstream restoration only from current evidence.

These are deterministic synthetic benchmark/demo claims only.

## Claims that remain prohibited

Do not claim:

- production security effectiveness,
- universal attack detection or prevention,
- arbitrary production rollback,
- reversal of irreversible external effects,
- authenticated ledger completeness or valid-prefix rollback resistance,
- distributed-controller consensus,
- remote proof/approval forgery resistance without an authenticated issuer boundary,
- globally complete causal capture with missing instrumentation,
- full production replay topology/provider/time equivalence,
- a global unsafe-recovery execution rate synthesized from scenario fields with different semantics,
- production recovery success rate or time-to-containment,
- live Bedrock/AgentCore security effectiveness,
- demonstrated safe restoration of the compromised source/root agent.

Model output is never authorization.

## Owner-only final gates

The following remain outside this acceptance file and require Paweł's explicit action:

- AWS login, MFA, Builder ID, credentials, or model access
- promotional credits or new paid AWS resources
- competition terms acceptance
- public video, Builder, or Devpost publication
- final competition submission

The credential-free deterministic package remains the source of truth if no owner-approved AWS path is used.
