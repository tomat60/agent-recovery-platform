# Final Package Acceptance

Date: 2026-09-10
Accepted implementation base: `8b8a080d6902665261d423261f2f2e4e50297685`

This file is a competition packaging and verification gate. It does not grant approval, execution, compensation, replay, restoration, AWS access, or public-submission authority.

## Exact-head acceptance contract

The competition package is ready for owner review only when all items below are proven on the exact submitted head:

1. Deterministic CI is green.
2. `python scripts/reproduce_judge_incident.py` succeeds from a clean Python 3.10+ environment without cloud credentials or paid model calls.
3. The reproduced incident evidence survives canonical JSON round-trip validation.
4. The generated SHA-256 manifest validates the packaged evidence bytes.
5. Judge-console output renders only represented incident, containment, recovery, residual-effect, replay, and restoration evidence.
6. Irreversible or unsuccessfully compensated effects remain visible as residual risk.
7. Replay evidence can invalidate a false restoration claim.
8. Strands/model advisory output remains proposal-only and cannot authorize execution or restoration.
9. No secrets, credentials, customer data, production incident data, or private identity data are present in the package.
10. `README.md`, `docs/PROJECT_CURRENT_STATE.md`, `docs/JUDGE_EVIDENCE_INDEX.md`, and the judge runbook describe the same claim boundary.

## Claims allowed by current deterministic evidence

The package may demonstrate bounded synthetic evidence that the system can bind incidents to tamper-evident evidence, reconstruct represented blast radius, record scoped containment, apply controlled recovery in owned/synthetic state, preserve residual external effects, independently verify represented restored state, and reject false restoration through replay.

These are deterministic synthetic benchmark/demo claims only.

## Claims that remain prohibited

Do not claim production security effectiveness, universal attack detection, arbitrary production rollback, reversal of irreversible external effects, production recovery success rate, production time-to-containment, or live Bedrock/AgentCore security effectiveness without new measured evidence.

Model output is never authorization. The source agent cannot restore its own authority.

## Owner-only final gates

The following remain outside this acceptance file and require Paweł's explicit action:

- AWS login, MFA, Builder ID, credentials, or model access
- promotional credits or new paid AWS resources
- competition terms acceptance
- public video, Builder, or Devpost publication
- final competition submission

The credential-free deterministic package remains the source of truth if no owner-approved AWS path is available.
