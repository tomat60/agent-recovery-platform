# Judge Readiness Checkpoint

Date: 2026-09-10

This checkpoint records the accepted credential-free competition path through `main` commit `705266a5ffabff3c9c940bc1afb871805442bcf7`.

## Accepted evidence path

The current deterministic judge path now covers:

1. versioned B01-B10 advisory benchmark fixtures and exact-suite scoring;
2. fail-closed advisory-gate rejection safety and incident-to-regression conversion;
3. a judge artifact and authority-free console/runbook;
4. a full deterministic incident evidence contract with independently represented blast-radius, containment, recovery/residual-effect, replay and restoration evidence from accepted PR #53;
5. judge-console rendering of those verified incident phases without granting approval or execution authority from accepted PR #55;
6. a one-command credential-free reproduction path from accepted PR #56 that regenerates the synthetic incident package, validates evidence before and after canonical JSON serialization, and writes SHA-256 manifest evidence;
7. an accepted readiness checkpoint from PR #57 that preserves the competition claim boundary and leaves AWS/live/public submission behind explicit owner gates.

## Trust-boundary statement

The judge path is evidence and reproduction only. It must not be described as granting approval, execution, compensation, replay or restoration authority. Model output remains advisory. Restoration claims remain bound to deterministic state/replay verification. Irreversible external effects remain explicit residual risk.

## Claims allowed for the competition demo

- The synthetic/owned benchmark demonstrates the implemented recovery-control mechanics and their deterministic verification path.
- B01-B10 benchmark and advisory measurements may be quoted only from generated artifacts or repository-recorded measured checkpoints.
- The full incident demo may show attack propagation, blast-radius reconstruction, scoped containment, candidate recovery planning, dependency-safe deterministic recovery evidence, residual effects, adversarial replay and verified restoration where those phases are present in freshly reproduced deterministic evidence.
- The judge package may claim deterministic reproducibility only when the fresh artifact passes its evidence validation, canonical JSON round-trip and SHA-256 manifest verification.

## Claims not allowed

- production security-effectiveness claims;
- generic attack-detection accuracy claims;
- broad time-to-containment or recovery-success claims;
- claims that irreversible third-party effects were undone;
- claims that Bedrock or AgentCore improve security unless a live path is separately run and evidenced.

## Remaining competition work

1. Keep the deterministic/mock reproduction path as CI and demo fallback source of truth.
2. Produce the final judge-facing package from a fresh reproduced artifact and verify its hashes immediately before submission packaging.
3. Reconcile `docs/PROJECT_CURRENT_STATE.md` with accepted PRs #52-#57 and current `main` before final packaging; that file currently trails the accepted implementation.
4. Run a final claim-to-evidence review against the reproduced package so demo wording cannot outrun measured evidence.
5. Add a bounded live Strands + Bedrock/AgentCore path only if owner-approved credentials/access/cost are available and the path produces useful recovery evidence. The credential-free deterministic path remains sufficient as the evidence source of truth.
6. Final public video, Devpost/Builder upload, competition terms and submission remain owner-only actions.

No new AWS spend or external action is required for the deterministic package.
