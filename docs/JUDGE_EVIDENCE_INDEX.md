# Judge Evidence Index

Date: 2026-09-13

Accepted technical code anchor before presentation-only packaging:

`b997384addd8781e0dac153d92adabcf9cc11757`

Accepted GitHub Actions run:

`34762391263`

This document is a competition packaging map. It grants no execution or restoration authority.

## Reproducible judge path

1. Reproduce the bounded synthetic incident.
2. Validate represented deterministic incident evidence and cross-field semantics.
3. Render represented evidence in the Judge Console.
4. Package canonical evidence with SHA-256 manifest entries.
5. Run the bounded replay and restoration checks used by the deterministic fixture.
6. Keep Strands/model output separate from deterministic authority.
7. Run exact-head CI and package acceptance before owner submission.

## Accepted evidence

For the accepted code anchor and run above:

- Python 3.10: PASS
- Python 3.12: PASS
- Ruff: PASS
- deterministic tests: 153 passed
- benchmark contract B01-B10: PASS
- B06 blast-radius recall: 1.0 in the bounded fixture
- B06 blast-radius precision: 1.0 in the bounded fixture
- B06 verified recoveries: 3
- B06 restored downstream authorities: 2
- B06 compromised root remains contained: true
- measured authority-resurrection successes: 0
- credential-free judge reproduction: PASS
- canonical incident evidence validation and round trip: PASS
- SHA-256 judge manifest verification: PASS
- authority-free judge reproduction manifest: PASS

These are synthetic deterministic fixture measurements only.

## Review history

The project completed three pre-submission review stages. Confirmed release-blocking findings were fixed and converted into permanent regression coverage. The accepted suite grew from the original 120 tests to 153 tests.

The final accepted implementation includes regression coverage for shared containment, independent incident holds, current/single-use restoration, retained evidence integrity, recovery verification from preserved pre-action state, replay freshness/binding, residual-risk truth and judge-evidence semantics.

## Claims allowed by current evidence

The bounded implementation may demonstrate represented evidence for:

- locally tamper-evident retained incident history,
- represented cross-agent blast-radius reconstruction,
- shared containment holds,
- controlled recovery in owned/synthetic state,
- verification from preserved pre-action evidence,
- explicit residual risk,
- bounded replay,
- selective downstream restoration from current represented evidence,
- credential-free deterministic reproduction and packaging.

## Claims prohibited without new evidence

Do not claim:

- production security effectiveness,
- universal attack prevention,
- arbitrary production rollback,
- reversal of irreversible external effects,
- authenticated ledger completeness or valid-prefix rollback resistance,
- distributed-controller consensus,
- globally complete causal capture with missing instrumentation,
- full production replay topology/provider/time equivalence,
- live Bedrock/AgentCore security effectiveness without separate evidence,
- demonstrated safe restoration of the compromised source/root agent.

## Presentation package

Judge-facing assets:

- `demo/index.html` — interactive presentation-only Judge Console
- `docs/assets/architecture-competition.svg` — trust-boundary diagram
- `docs/VIDEO_PRODUCTION_PLAN.md` — storyboard and voiceover
- `docs/DEVPOST_FINAL_DRAFT.md` — final owner-review copy
- `docs/SUBMISSION_FINAL_CHECKLIST.md` — execution checklist

After the presentation-only branch is merged, the final `main` head must pass exact-head CI/package checks again. Copy that final SHA into the submission form only after the run is green.

## Owner-only gates

- AWS login/MFA or Builder ID
- AWS credentials/model access
- new paid AWS resources or plan changes
- public video/Devpost/Builder publishing
- competition terms acceptance
- final competition submission
