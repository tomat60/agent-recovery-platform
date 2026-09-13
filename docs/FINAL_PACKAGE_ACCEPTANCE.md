# Final Package Acceptance

Date: 2026-09-13

Accepted technical code anchor before presentation-only packaging:

`b997384addd8781e0dac153d92adabcf9cc11757`

Post-merge validation run:

`recovery-ci` `34762391263`

This file is a competition packaging and verification gate. It grants no execution, restoration, AWS access or public-submission authority.

The exact final submitted SHA must be read from Git after all presentation-only packaging changes are merged.

## Accepted validation

The code anchor above has passed:

- Python 3.10
- Python 3.12
- Ruff
- 153 deterministic tests
- B01-B10 benchmark smoke
- credential-free judge reproduction
- canonical incident evidence validation and round trip
- SHA-256 judge manifest verification
- authority-free judge reproduction manifest

The pre-submission review cycle is complete and all confirmed release-blocking findings were converted into permanent regression coverage.

## Exact final-head acceptance contract

After the presentation/docs branch is merged, the package is ready for owner review only when all items below are true on final `main`:

1. CI is green on Python 3.10 and 3.12 with the complete final suite.
2. Ruff passes.
3. Benchmark smoke B01-B10 passes.
4. Credential-free judge reproduction succeeds.
5. Reproduced evidence survives canonical JSON round trip and semantic validation.
6. SHA-256 manifest validation succeeds.
7. Judge Console renders only represented evidence and has zero execution authority.
8. The demonstrated source/root agent remains contained.
9. Selective downstream restoration is shown only from current represented evidence.
10. Recovery success remains bound to preserved pre-action evidence.
11. Failed or irreversible effects remain visible as residual risk.
12. Strands/model output remains proposal-only.
13. README, current-state docs, integrity model, evidence index, submission copy, architecture and video script use the same bounded claim boundary.
14. No secrets, credentials, customer data, production incident data or private identity data appear in the package or capture.

If security/runtime code changes after `b997384a...`, reopen the security gate. Presentation-only docs/demo changes require exact-head CI/package verification but not another broad architecture audit.

## Claims allowed by deterministic evidence

The package may demonstrate bounded synthetic evidence for represented incident reconstruction, shared containment, controlled recovery, verification from preserved pre-action state, explicit residual risk, bounded replay and selective downstream restoration.

These are synthetic deterministic benchmark/demo claims only.

## Claims that remain prohibited

Do not claim:

- production security effectiveness
- universal attack prevention
- arbitrary production rollback
- reversal of irreversible external effects
- authenticated ledger completeness or valid-prefix rollback resistance
- distributed-controller consensus
- globally complete causal capture with missing instrumentation
- full production replay topology/provider/time equivalence
- live Bedrock/AgentCore security effectiveness without separate evidence
- demonstrated safe restoration of the compromised source/root agent

Model output is never authorization.

## Owner-only final gates

The following require Paweł's explicit action:

- AWS login/MFA, Builder ID, credentials or model access
- new paid AWS resources or plan changes
- public YouTube/Vimeo upload
- public Builder/Devpost publication
- competition terms acceptance
- final competition submission

The credential-free deterministic package remains the source of truth if no separately verified live AWS path is used.
