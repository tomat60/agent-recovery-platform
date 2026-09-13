# Project Current State

Date: 2026-09-13

## Status

Security acceptance is complete for the accepted code anchor:

`b997384addd8781e0dac153d92adabcf9cc11757`

Post-merge GitHub Actions run `34762391263` passed on that exact code state with Python 3.10, Python 3.12, Ruff, **153 deterministic tests**, B01-B10 benchmark smoke, credential-free judge reproduction, canonical semantic validation, authority-free packaging and SHA-256 manifest verification.

The current execution lane is **presentation-only competition packaging**: interactive Judge Console, architecture diagram, final video, Devpost copy and final exact-head CI after those non-security assets are merged.

Security/runtime code is frozen unless a concrete new blocker appears.

## Product thesis

Agent Recovery Platform is a recovery-first control layer for autonomous AI agents.

Lifecycle:

**incident -> containment -> evidence -> recovery -> replay -> verified restoration**

Core rules:

**No autonomous write without a validated Recovery Contract.**

**No represented downstream authority release without complete represented recovery evidence and a current scope-bound replay.**

The competition path intentionally keeps the compromised source/root agent contained rather than claiming that its own replay proves it safe to restore.

## Adversarial hardening history

The build was intentionally attacked after green CI rather than treating passing tests as proof.

1. The original GPT-6 architecture audit attacked a green 120-test baseline and found lifecycle counterexamples ordinary tests had missed.
2. After remediation, a targeted GPT-6 re-audit attacked the 139-test hardened build and found four further blockers:
   - source-agent restoration could be justified by replay made safe by another/hidden containment boundary,
   - restoration authority could become stale or reusable at application time,
   - already-created shared-ledger controllers could miss new containment,
   - one incident's release could erase another incident's hold on the same scope.
3. Those findings were fixed and converted into permanent regressions, reaching 152 tests.
4. A final Codex acceptance audit found one additional High finding: recovery-side code could influence the expected state used to declare recovery successful.
5. PR #70 fixed recovery-target provenance so the verification target derives from preserved pre-action evidence, not builder or executor claims, and added the exact malicious-builder + no-op-executor counterexample as the 153rd permanent regression.

Confirmed blockers were fixed rather than hidden or reclassified.

## Accepted deterministic trust boundary

The accepted competition implementation includes:

1. Strict Recovery Contract validation before represented side effects.
2. Advisory-only Strands/model output with no execution authority.
3. Parameter-bound action approvals and context-bound recovery approvals.
4. Single-use approval consumption at the shared in-memory ledger boundary.
5. Shared-ledger authoritative active containment, observed by already-created and recreated controllers.
6. Independent containment holds per incident and scope.
7. Fresh, single-use restoration application bound to one exact active hold.
8. Fail-closed positive replay admission for source-agent self restoration.
9. Direct ledger append paths subject to the same trusted restoration/replay admission rules.
10. Deep-detached event payloads so exported evidence cannot alias stored nested state.
11. Integrity verification before privileged recovery/restoration decisions and cached recovery reuse.
12. Incident binding before recovery-result cache reuse.
13. Cross-incident/later-writer protection for represented mutable resources.
14. Recovery verification targets derived from preserved pre-action evidence before recovery-side code executes.
15. Explicit failure/residual evidence for direct recovery executor/verifier exceptions and verification mismatches.
16. Exact source-action replay binding for agent, tool, parameter digest and contract version.
17. Replay bound to source ledger head, recovery generation and represented source contract versions.
18. Supersession/freshness checks for replay evidence.
19. Restoration requiring active containment, complete represented local recovery obligations, no uncovered residual and current positive exact-scope replay.
20. Judge incident evidence semantic validation and bounded cross-field relationships.
21. Permanent regressions for original audit, re-audit, mutation-survivor and final acceptance counterexamples.

## Accepted validation evidence

For `b997384addd8781e0dac153d92adabcf9cc11757`:

- GitHub Actions run: `34762391263`
- Python 3.10: PASS
- Python 3.12: PASS
- Ruff: PASS
- deterministic tests: 153 passed
- B01-B10 contract coverage: 10/10
- B06 blast-radius recall: 1.0 in the bounded fixture
- B06 blast-radius precision: 1.0 in the bounded fixture
- B06 verified recoveries: 3
- B06 restored downstream authorities: 2
- B06 compromised root remains contained: true
- measured authority-resurrection successes: 0
- credential-free judge reproduction: PASS
- canonical incident evidence round trip and semantic validation: PASS
- SHA-256 judge manifest verification: PASS
- authority-free judge reproduction manifest: PASS

Scenario-specific unsafe-recovery fields remain visible, but the project does not present them as one globally comparable production metric.

## Integrity and replay limits

The project explicitly does not claim:

- authenticated ledger completeness or valid-prefix rollback resistance,
- distributed-controller consensus,
- remote proof/approval forgery resistance without an authenticated issuer boundary,
- globally complete causal capture when instrumentation is missing,
- complete production replay topology/provider/time equivalence,
- arbitrary production rollback,
- universal attack prevention,
- live Bedrock/AgentCore security effectiveness,
- demonstrated safe restoration of the compromised source/root agent.

The ledger is a locally tamper-evident retained history, not a signed/WORM transparency log. Single-use approval and containment behavior is demonstrated for controllers sharing one in-memory `ActionLedger`. Replay is bounded to represented synthetic evidence.

## Current submission lane

Active branch: `submission-final-2026-09-13`, based on accepted main code anchor `b997384a...`.

Presentation-only work in this lane:

- `demo/index.html` interactive Judge Incident Recovery Console,
- `docs/assets/architecture-competition.svg`,
- `docs/VIDEO_PRODUCTION_PLAN.md`,
- `docs/DEVPOST_FINAL_DRAFT.md`,
- `docs/SUBMISSION_FINAL_CHECKLIST.md`,
- synchronization of README and final package claim language.

After this lane is complete:

1. open a presentation-only PR to `main`,
2. require exact-head CI/package verification,
3. record final `main` SHA from Git,
4. capture Judge Console + architecture + CI evidence for the demo video,
5. record Paweł's voiceover in short sections,
6. assemble and review the final video,
7. add the public video URL to Devpost,
8. owner enters AWS Builder ID, accepts competition terms and performs final Submit.

## Owner-only gates

- AWS login/MFA, Builder ID, credentials or model access
- promotional credits or new spend/payment
- public YouTube/Vimeo upload
- public Builder/Devpost publication
- competition terms acceptance
- final competition submission

Agents for Humans deadline: 2026-09-14.
