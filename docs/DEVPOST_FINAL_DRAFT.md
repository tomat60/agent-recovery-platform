# Devpost Final Draft

Status: near-final competition copy. Refresh exact-head facts after final merge and owner-review before publication.

## Project name

Agent Recovery Platform

## Tagline

Verified recovery for compromised autonomous AI agents.

## Elevator pitch

Agent Recovery Platform is a recovery-first safety layer for write-capable AI agents. When prevention fails, it reconstructs represented side effects across agents, contains affected authority, recovers what is actually recoverable, preserves residual risk, replays the repaired attack path, and restores only authority supported by current deterministic evidence.

## The problem

As autonomous agents gain permission to modify customer records, shared memory, access controls, configuration and communication systems, failures stop being only bad answers. They become state-changing incidents.

A kill switch can stop future actions, but it cannot answer the operational questions that matter after an incident:

- What already changed?
- How far did the failure propagate across other agents?
- Which effects can be safely reversed or compensated?
- Which effects are irreversible?
- When is it safe to restore authority?

Simple rollback is also unsafe when later agent actions depend on earlier writes or multiple agents share mutable state.

## The solution

Agent Recovery Platform implements a bounded recovery lifecycle:

`incident -> containment -> evidence -> recovery -> replay -> verified restoration`

Two rules define the system:

1. No autonomous write without a recovery path.
2. No restored authority without complete represented recovery evidence and a current scope-bound replay.

Every consequential action is governed by a Recovery Contract that declares side effects, recovery class, verifier, compensation path and approval requirements. A locally tamper-evident action ledger records represented effects independently from the agent's narration.

After an incident, the system reconstructs represented causal propagation, contains affected authority, executes only policy-bound recovery paths, independently verifies repaired state and keeps failed compensation or irreversible effects explicit as residual risk.

An isolated Replay Lab then reruns the represented attack action against repaired state. Replay evidence is bound to incident identity, source action, execution-time state, contract versions and the proposed release scope. Stale, superseded, cross-incident, action-mismatched or environment-mismatched evidence fails closed.

Only then can selected downstream authority be restored. The compromised root can remain contained.

## How Strands is used

Strands Agents SDK provides an evidence-only reasoning layer:

- **Investigator** — reconstructs likely root cause and causal trajectory from read-only incident evidence.
- **Recovery Planner** — proposes ordered candidate recovery/compensation actions and residual risks.
- **Skeptic / Verifier** — challenges unsupported assumptions and unsafe recovery claims.

This separation is deliberate: model output is advisory and cannot authorize writes, execute recovery or restore authority. Deterministic code owns those boundaries.

The credential-free deterministic path remains the reproducible source of truth. A live Strands + Amazon Bedrock / AgentCore path is additive only when separately verified.

## What makes it different

Most agent-security tools focus on prevention, monitoring or stopping future actions. Agent Recovery Platform focuses on the harder post-incident problem:

`cross-agent causality -> recovery integrity -> residual truth -> adversarial replay -> selective restoration`

The project treats the recovery path itself as a security boundary. It does not assume that rollback is always safe or that a successful model explanation is proof of recovery.

## Demonstrated scenario

In the bounded deterministic fixture, poisoned external content reaches a support agent and contaminates shared state. Downstream workflow and identity authority are affected.

The platform:

1. records the represented causal chain,
2. identifies the three-agent blast radius,
3. contains the compromised root and dependent authority,
4. produces evidence-bound advisory reasoning,
5. executes deterministic recovery paths,
6. preserves residual risk explicitly,
7. runs scope-bound replay of the represented attack,
8. restores two downstream authorities after verification,
9. keeps the compromised root authority contained.

## Measured evidence

Final exact-head values to refresh after merge:

- Python 3.10 CI: `[FINAL STATUS]`
- Python 3.12 CI: `[FINAL STATUS]`
- Deterministic tests: `[FINAL TEST COUNT]`
- Adversarial benchmark: B01-B10
- Three-agent blast-radius recall: 1.0 in the bounded fixture
- Three-agent blast-radius precision: 1.0 in the bounded fixture
- Verified recoveries in selected fixture: 3
- Restored downstream authorities in selected fixture: 2
- Root authority restored: no
- Unsafe recovery executions in selected fixture: 0

All of these are synthetic deterministic measurements. They do not establish global or production security effectiveness.

## Adversarial hardening

Before submission, the project deliberately underwent a GPT-6 adversarial architecture audit against a green 120-test baseline. The audit found lifecycle counterexamples ordinary tests had missed, including restoration authorization gaps, replay-context confusion, containment reconstruction loss, approval reuse across controllers and shared-state recovery hazards.

Those findings were treated as release blockers. Confirmed issues were converted into permanent regression coverage and a hardened remediation branch, followed by targeted re-audit before merge.

## Architecture

The architecture has two explicit trust zones:

### Advisory reasoning

Incident evidence -> Investigator -> Recovery Planner -> Skeptic

Built with Strands Agents SDK. This zone has no execution authority.

### Deterministic recovery control plane

Recovery Contracts -> Action Ledger -> Causal Graph -> Containment -> Recovery Engine -> Independent Verification -> Replay Lab -> Restoration Gate -> Judge Evidence/Console

The Judge Console is presentation-only. It renders represented evidence and grants no approval, execution, compensation, replay or restoration authority.

## AWS path

AWS Builder ID/account: ready.

The project can use Amazon Bedrock as a Strands model provider and optionally AgentCore for the live cloud path when verified. The deterministic credential-free path remains the reproducible competition baseline, so judges can reproduce the strongest bounded evidence without paid inference.

Final live AWS claim: `[REFRESH AFTER LIVE SMOKE TEST]`

## Technical challenges

The hardest problem was not generating a recovery plan. It was preventing individually valid transitions from composing into an unsafe lifecycle.

Examples include stale replay evidence, cross-incident proof confusion, lost containment after runtime reconstruction, approval reuse, later writers of shared resources and irreversible effects that cannot truthfully be called rolled back.

The project therefore separates advisory AI reasoning from deterministic authorization and treats every restoration decision as an evidence-gated state transition.

## Impact

The target users are teams operating write-capable autonomous agents in AI-native SaaS, fintech, developer tooling, security and internal automation.

As agent autonomy increases, organizations need operational recovery controls analogous to incident response and disaster recovery for conventional infrastructure — but adapted to causal multi-agent workflows, shared mutable state and model-driven behavior.

The long-term commercial path begins with an Agent Recoverability Assessment for one write-capable workflow, then expands into continuous recovery readiness and incident-response infrastructure.

## Repository

`https://github.com/tomat60/agent-recovery-platform`

Final submitted SHA: `[FINAL MAIN SHA]`

## Demo video

`[PUBLIC YOUTUBE OR VIMEO URL]`

## Optional live demo

`[LIVE JUDGE CONSOLE URL OR OMIT IF NOT VERIFIED]`

## Claim boundary

This competition build does not claim:

- production multi-tenancy,
- remote proof-forgery resistance,
- distributed consensus,
- externally anchored ledger completeness,
- universal blast-radius accuracy,
- generic prompt-injection detection effectiveness,
- live cloud rollback attestation unless separately measured,
- that irreversible external effects can be undone.

Its claims are deliberately bounded to represented, reproducible evidence in the included deterministic fixtures and any separately captured live AWS path.
