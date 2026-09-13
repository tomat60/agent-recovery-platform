# Agents for Humans Submission Draft

Status: private owner-review draft. Do not publish without explicit owner approval.

Canonical long-form Devpost copy for final review: `docs/DEVPOST_FINAL_DRAFT.md`.

## Project name

Agent Recovery Platform

## Tagline

Verified recovery for compromised autonomous AI agents.

## Track

Professional Agents

## One-line thesis

When an autonomous agent is compromised or goes wrong, the platform reconstructs represented side effects, contains affected authority, recovers what is actually recoverable, preserves residual risk, runs a bounded replay, and restores only represented downstream authority supported by current deterministic evidence.

## Problem

Organizations are giving AI agents permission to modify customer records, shared memory, access controls, configuration and communication systems. Prevention and monitoring matter, but no defense is perfect. Once a write-capable agent fails or is manipulated, teams still need to answer what changed, how far it propagated, what can be reversed or compensated, what remains irreversible, and when authority is safe to restore.

A kill switch stops future actions. It does not reconstruct or repair state already changed. Simple rollback can also be unsafe when later agent actions depend on earlier writes or multiple agents share mutable state.

## Solution

Agent Recovery Platform owns the post-incident lifecycle:

`incident -> containment -> evidence -> recovery -> replay -> verified restoration`

Two rules define the competition build:

- No autonomous write without a recovery path.
- No restored downstream authority without complete represented recovery evidence and a current scope-bound replay.

Every consequential action is governed by a Recovery Contract. A locally tamper-evident ledger records represented effects independently from agent narration. Strands agents investigate evidence, propose recovery and challenge unsafe assumptions, but model output has no authority to execute or restore anything.

Deterministic modules bind recovery to current incident evidence, represented dependency/resource constraints and approvals where required. Recovery success is checked against preserved pre-action evidence, not a target chosen by recovery-side code.

After recovery, an isolated Replay Lab reruns the exact represented source action. Stale, superseded, cross-incident, action-mismatched or represented environment-contract-mismatched evidence fails closed. Selective downstream restoration is permitted only from fresh exact-scope evidence. The compromised source/root agent remains contained in the demonstrated competition path.

Failed compensation or irreversible external effects remain explicit residual risk instead of being described as undone.

## Strands role

Strands Agents SDK provides the evidence-only reasoning layer:

- Investigator: likely root cause and causal trajectory from read-only evidence.
- Recovery Planner: ordered candidate recovery/compensation actions and residual risks.
- Skeptic / Verifier: challenges unsupported assumptions and unsafe recovery claims.

Deterministic code owns contracts, write admission, containment, recovery verification, replay admission and restoration.

## Demonstrated scenario

In the bounded fixture, poisoned external content reaches a support agent and contaminates shared state. Downstream workflow and identity authority are affected.

The platform:

1. records the represented causal chain,
2. identifies the three-agent blast radius,
3. contains the compromised root and dependent authority,
4. executes deterministic recovery paths,
5. verifies recovered state against preserved pre-action evidence,
6. preserves residual risk explicitly,
7. runs bounded exact-action replay,
8. restores two downstream authorities after current evidence passes,
9. keeps the compromised root agent contained.

## Accepted measured evidence

Accepted security code anchor before presentation-only packaging:

`b997384addd8781e0dac153d92adabcf9cc11757`

Post-merge GitHub Actions run `34762391263` passed with:

- Python 3.10: PASS
- Python 3.12: PASS
- Ruff: PASS
- deterministic tests: 153 passed
- required benchmark contract B01-B10: PASS
- B06 three-agent blast-radius recall: 1.0 in the bounded fixture
- B06 three-agent blast-radius precision: 1.0 in the bounded fixture
- B06 verified recoveries: 3
- B06 restored downstream authorities: 2
- B06 root remains contained: true
- measured authority-resurrection successes: 0
- credential-free judge reproduction: PASS
- canonical semantic validation and round trip: PASS
- SHA-256 manifest verification: PASS
- authority-free judge reproduction manifest: PASS

These are synthetic deterministic measurements, not production-security claims.

## Adversarial hardening

The project deliberately challenged green builds before submission.

A GPT-6 architecture audit attacked a green 120-test baseline and found lifecycle counterexamples ordinary tests had missed. A targeted GPT-6 re-audit of the hardened 139-test build found four more blockers around source-agent restoration, restoration freshness/reuse, shared-ledger containment and independent incident holds. Those findings were fixed and converted into permanent regressions, reaching 152 tests.

A final Codex acceptance audit found one additional High recovery-target provenance flaw. PR #70 fixed it by deriving recovery verification targets from preserved pre-action evidence and added the exact counterexample as the 153rd regression.

Confirmed blockers were treated as release blockers, not hidden or reclassified.

## Competition architecture

Two trust zones are explicit.

### Advisory reasoning zone

Incident Evidence -> Investigator -> Recovery Planner -> Skeptic

No execution authority.

### Deterministic recovery control plane

Recovery Contracts -> Action Ledger -> Causal Graph -> Containment -> Recovery Engine -> Independent Verification -> Replay Lab -> Restoration Gate -> Judge Evidence / Console

The interactive `demo/index.html` Judge Console is presentation-only and grants zero execution authority.

## AWS path

The credential-free deterministic path is the reproducible competition baseline.

Amazon Bedrock can be used as a Strands model provider, and AgentCore can strengthen a separately verified live integration. No live AWS security-effectiveness claim is made unless that path is actually executed and captured as evidence.

## Reproducibility

The public repository contains:

- MIT license,
- setup documentation,
- benchmark definitions,
- deterministic tests,
- credential-free one-command incident reproduction,
- canonical JSON evidence and SHA-256 manifests,
- architecture diagram,
- Judge Console,
- claim/evidence boundary documents,
- GitHub Actions reproduction artifacts.

## Video plan

Use `docs/VIDEO_PRODUCTION_PLAN.md`.

Target runtime: 3:20-3:50, never over 5:00. Primary visual is the one-page Judge Console, with short architecture and GitHub Actions inserts. Paweł records voiceover sections; the visual edit follows the prepared storyboard.

## Claim boundary

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
- safe restoration of the compromised source/root agent.

## Final owner actions

- confirm public video upload,
- provide AWS Builder ID,
- review final Devpost text and any required disclosure,
- accept competition terms,
- perform final Devpost Submit.

The exact final submitted SHA must be read from Git after presentation-only packaging is merged and exact-head CI is green.
