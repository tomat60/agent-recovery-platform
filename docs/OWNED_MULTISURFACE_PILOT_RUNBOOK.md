# Owned Multi-Surface Recovery Pilot Runbook

This runbook reproduces the bounded P4 owned/sandbox pilot. It is evidence generation only. It performs no external writes, grants no approval/recovery/restoration authority, and makes no production-security-effectiveness claim.

## What the pilot proves

The deterministic fixture represents one incident spanning two consequential side-effect surfaces:

- `shared_support_state`
- `downstream_identity_authority`

The flow keeps the compromised root authority contained, records recovery and independent verification evidence, requires replay with zero unsafe recovery executions, and permits only the downstream restoration represented by current evidence. Controller-restart continuity is part of the evidence contract.

## Reproduce

From a clean checkout at the exact commit under test:

```bash
python scripts/run_owned_multisurface_pilot.py .artifacts/owned-multisurface-pilot
```

The command must exit successfully and print the canonical manifest. Inspect:

```bash
cat .artifacts/owned-multisurface-pilot/manifest.json
cat .artifacts/owned-multisurface-pilot/pilot-evidence.json
```

Expected invariant signals in `manifest.json`:

- `authorization_effect` is `none`;
- `pilot_schema_valid` is `true`;
- `canonical_round_trip` is `true`;
- `multi_surface` is `true`;
- `root_authority_contained` is `true`;
- `unsafe_recovery_executions` is `0`.

The manifest also records the SHA-256 and byte length of `pilot-evidence.json`, so evidence can be compared without relying on prose or UI state.

## Acceptance check

Run the repository's normal deterministic acceptance suite after the targeted reproduction:

```bash
pytest -q
```

CI remains the exact-head acceptance authority. Do not treat the targeted pilot command alone as repository-wide correctness.

## Failure handling

Do not retry blindly. A schema-validation, canonical-round-trip, containment, replay, or evidence-hash failure is a product signal. Preserve the generated artifact directory, identify the first violated invariant, reproduce with the same exact commit, and repair the smallest causal defect before rerunning full acceptance.

## Claim boundary

This is an owned deterministic sandbox proof. It does not establish authenticated distributed-ledger completeness, arbitrary production rollback, universal causal capture, safe restoration of every compromised source agent, or production security effectiveness.
