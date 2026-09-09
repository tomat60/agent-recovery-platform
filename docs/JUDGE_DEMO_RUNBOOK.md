# Judge Demo Runbook

## Purpose

This runbook packages the accepted deterministic recovery evidence into one judge-facing story without expanding the measured security claims.

The demo must preserve the product boundary:

**incident -> containment -> evidence -> recovery -> replay -> verified restoration**

Core rules remain:

- No autonomous write without a recovery path.
- No restored authority without a verified replay.
- Model output is advisory evidence, never authorization.
- Irreversible or unsuccessfully compensated effects remain explicit residual risk.

## What is already accepted

The repository contains deterministic recovery-contract, ledger, containment, causal reconstruction, compensation, replay, authority-restoration and incident-to-regression behavior together with the credential-free Strands advisory chain.

The accepted M3 advisory packaging path now includes:

- B01-B10 advisory fixtures and exact-suite validation.
- deterministic advisory scoring.
- fail-closed Advisory Gate rejection-safety measurement.
- rejected-advisory regression conversion.
- a machine-readable judge advisory artifact.
- a deterministic judge advisory console that renders only evidence represented by that artifact.

These components do not grant approval, execute recovery or restore authority.

## Demo sequence

Use one synthetic or owned incident only. Do not use customer data, private incidents or destructive external systems.

1. **Show the incident and side-effect evidence**
   - identify the source action and incident identity.
   - show the tamper-evident evidence/ledger boundary.
   - state whether the consequential action is reversible, compensatable or irreversible.

2. **Show blast radius and containment from deterministic evidence**
   - identify affected agents/resources from the causal incident graph.
   - show the exact containment scope.
   - do not imply generic attack-detection effectiveness.

3. **Run the advisory chain**
   - Investigator proposes an evidence-cited root-cause hypothesis.
   - Recovery Planner proposes ordered candidate compensation/recovery steps and residual risks.
   - Skeptic/Verifier challenges unsupported or unsafe claims.
   - emphasize that none of these agents can authorize execution.

4. **Show the deterministic Advisory Gate**
   - rebind the proposal to incident evidence.
   - demonstrate fail-closed behavior for stale, cross-incident, unsupported or malformed advisory evidence where the selected fixture provides it.
   - an accepted advisory result is only a candidate plan.

5. **Show the judge artifact and judge console**
   - use the deterministic artifact as the source of truth.
   - show per-scenario evidence and rejection-safety outcomes only where represented.
   - keep unrepresented fields visibly unclaimed instead of filling them from model narration.

6. **Show controlled recovery in the deterministic/owned environment**
   - preserve evidence before mutation.
   - execute only through the policy-bound recovery path.
   - show compensation failure or irreversible residuals explicitly when present.

7. **Show replay and restoration truth**
   - verify repaired state independently.
   - run replay/fork verification.
   - show that stale/forged/unsuccessful replay evidence cannot restore authority.
   - only claim restored authority after deterministic verification succeeds.

8. **Convert the incident into a regression**
   - show the regression contract bound to the source incident/evidence.
   - explain that future safety claims must remain reproducible from deterministic evidence.

## Required claim discipline

The current deterministic benchmark results are synthetic fixture results, not production security-effectiveness claims.

Do not claim:

- a global production recovery success rate.
- generic prompt-injection detection accuracy.
- universal blast-radius accuracy outside the measured deterministic fixtures.
- production time-to-containment.
- live Bedrock or AgentCore security effectiveness until separately measured.
- that an irreversible external effect was undone.

When a field is absent from the judge artifact, the console should continue to present it as unrepresented rather than infer a favorable result.

## Competition fallback

The credential-free deterministic path is the source of truth and must remain fully demonstrable without AWS credentials or paid model calls.

A live Strands + Bedrock or AgentCore path is additive only. It must not weaken the deterministic authorization boundary or become required for reproducing the benchmark evidence.

## Judge-facing narrative

The differentiator is not another prevention dashboard. The product starts where autonomous-agent security failures become operationally expensive:

**contain the incident, reconstruct what happened, recover what is actually recoverable, expose what is not, replay the repaired path, and restore authority only after independent verification.**

The strongest proof is the separation of trust boundaries: model agents investigate and propose; deterministic controls decide what can execute and what can be called recovered.

## Final pre-submission checklist

- exact-head CI green.
- deterministic benchmark path reproducible without paid services.
- judge artifact generated from the exact fixture suite used for the demo.
- judge console renders artifact truth without inferred claims.
- no secrets, credentials, customer data or private incident data in repository/demo materials.
- no real destructive external action in demo.
- residual irreversible or failed-compensation effects remain visible.
- public video, Devpost/Builder publication and final competition submission remain owner-only actions.
