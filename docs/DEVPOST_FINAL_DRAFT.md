# Devpost Final Draft

Status: owner-review draft. Do not publish without explicit owner approval.

## Project name

Agent Recovery Platform

## Tagline

Verified recovery for compromised autonomous AI agents.

## Elevator pitch

Agent Recovery Platform is a recovery-first safety layer for write-capable AI agents. When prevention fails, it reconstructs represented side effects across agents, contains affected authority, recovers what is actually recoverable, preserves residual risk, replays the repaired attack path, and restores only downstream authority supported by current deterministic evidence.

## The problem

As autonomous agents gain permission to modify customer records, shared memory, access controls, configuration and communication systems, failures stop being only bad answers. They become state-changing incidents.

A kill switch can stop future actions, but it cannot answer the operational questions that matter after an incident: what already changed, how far the failure propagated, which effects can be reversed or compensated, which effects are irreversible, and when it is safe to restore authority.

Simple rollback can also be unsafe when later agent actions depend on earlier writes or multiple agents share mutable state.

## The solution

Agent Recovery Platform implements a bounded recovery lifecycle:

`incident -> containment -> evidence -> recovery -> replay -> verified restoration`

Two rules define the system:

1. No autonomous write without a recovery path.
2. No restored authority without complete represented recovery evidence and a current scope-bound replay.

Every consequential action is governed by a Recovery Contract that declares side effects, recovery class, verifier, compensation path and approval requirements. A locally tamper-evident action ledger records represented effects independently from the agent's narration.

After an incident, the system reconstructs represented causal propagation, contains affected authority, executes only policy-bound recovery paths, independently verifies repaired state and keeps failed compensation or irreversible effects explicit as residual risk.

Recovery success is checked against preserved pre-action evidence. Recovery builders and executors cannot redefine the target state that would make their own work appear successful.

An isolated Replay Lab then reruns the represented attack action against repaired state. Replay evidence is bound to incident identity, source action, execution-time state, represented contract versions and the proposed release scope. Stale, superseded, cross-incident, action-mismatched or environment-mismatched evidence fails closed.

Only then can selected downstream authority be restored. The competition path intentionally keeps the compromised source/root agent contained.

## How Strands is used

Strands Agents SDK provides an evidence-only reasoning layer:

- **Investigator** reconstructs likely root cause and causal trajectory from read-only incident evidence.
- **Recovery Planner** proposes ordered candidate recovery or compensation actions and residual risks.
- **Skeptic / Verifier** challenges unsupported assumptions and unsafe recovery claims.

This separation is deliberate. Model output is advisory and cannot authorize writes, execute recovery or restore authority. Deterministic code owns those boundaries.

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
6. verifies recovery against preserved pre-action evidence,
7. preserves residual risk explicitly,
8. runs scope-bound replay of the represented attack,
9. restores two downstream authorities after verification,
10. keeps the compromised root authority contained.

## Measured evidence

Accepted code anchor before presentation-only packaging: `b997384addd8781e0dac153d92adabcf9cc11757`.

Post-merge GitHub Actions run `34762391263` passed on that exact code state with:

- Python 3.10: PASS
- Python 3.12: PASS
- Ruff: PASS
- 153 deterministic tests: PASS
- adversarial benchmark contract B01-B10: PASS
- three-agent blast-radius recall: 1.0 in the bounded fixture
- three-agent blast-radius precision: 1.0 in the bounded fixture
- verified recoveries in selected fixture: 3
- restored downstream authorities in selected fixture: 2
- compromised root remains contained: true
- measured authority-resurrection successes: 0
- credential-free judge reproduction: PASS
- canonical incident evidence validation and round trip: PASS
- SHA-256 manifest verification: PASS
- authority-free judge reproduction manifest: PASS

These are synthetic deterministic measurements. They do not establish global or production security effectiveness.

## Adversarial hardening

Before submission, the project deliberately underwent repeated adversarial review instead of treating a green test suite as proof.

A GPT-6 architecture audit against a green 120-test baseline found unsafe lifecycle compositions that ordinary tests had missed. A targeted re-audit of the hardened 139-test build found four more blockers around source-agent restoration, stale/reusable restoration authority, shared-ledger containment and independent incident holds. After those fixes, the suite reached 152 tests.

A final Codex acceptance audit then found one additional High recovery-target provenance flaw: recovery-side code could influence the expected state used to declare recovery successful. That issue was fixed so verification targets derive from preserved pre-action evidence, and the exact counterexample became the 153rd permanent regression.

Confirmed blockers were treated as release blockers rather than hidden or reclassified.

## Architecture

The architecture has two explicit trust zones.

### Advisory reasoning

Incident evidence -> Investigator -> Recovery Planner -> Skeptic

Built with Strands Agents SDK. This zone has no execution authority.

### Deterministic recovery control plane

Recovery Contracts -> Action Ledger -> Causal Graph -> Containment -> Recovery Engine -> Independent Verification -> Replay Lab -> Restoration Gate -> Judge Evidence / Console

The Judge Console is presentation-only. It renders represented evidence and grants no approval, execution, compensation, replay or restoration authority.

## AWS path

The deterministic credential-free path is the reproducible competition baseline.

Amazon Bedrock can be used as a Strands model provider, and AgentCore can strengthen the live cloud integration when separately verified. No live AWS security-effectiveness claim is made unless that path is actually executed and captured as evidence.

## Technical challenges

The hardest problem was preventing individually valid transitions from composing into an unsafe lifecycle.

Examples included stale replay evidence, cross-incident proof confusion, lost containment after runtime reconstruction, approval reuse, independent containment holds, later writers of shared resources, recovery-target provenance and irreversible effects that cannot truthfully be called rolled back.

The project therefore separates advisory AI reasoning from deterministic authorization and treats every restoration decision as an evidence-gated state transition.

## Impact

The target users are teams operating write-capable autonomous agents in AI-native SaaS, fintech, developer tooling, security and internal automation.

As agent autonomy increases, organizations need operational recovery controls analogous to incident response and disaster recovery for conventional infrastructure, but adapted to causal multi-agent workflows, shared mutable state and model-driven behavior.

The commercial path starts with an Agent Recoverability Assessment for one write-capable workflow, then expands only after real customer validation.

## Reproducibility

The public repository contains:

- MIT license,
- README and setup instructions,
- benchmark definitions,
- architecture documentation and diagram,
- deterministic tests,
- credential-free one-command incident reproduction,
- canonical JSON evidence,
- SHA-256 manifests,
- judge evidence index and claim boundaries,
- exact-head CI reproduction artifacts,
- an interactive presentation-only Judge Console.

Judges can reproduce the strongest bounded evidence without AWS credentials or paid model calls.

## Repository

https://github.com/tomat60/agent-recovery-platform

Final submitted SHA: `[READ FROM GIT AFTER FINAL PRESENTATION-ONLY MERGE]`

## Demo video

`[PUBLIC YOUTUBE OR VIMEO URL]`

## Optional live demo

Omit unless a hosted Judge Console is separately verified before submission.

## Claim boundary

This competition build does not claim:

- production security effectiveness,
- universal attack detection or prevention,
- arbitrary production rollback,
- reversal of irreversible external effects,
- authenticated ledger completeness or valid-prefix rollback resistance,
- distributed-controller consensus,
- remote proof or approval forgery resistance without an authenticated issuer boundary,
- globally complete causal capture with missing instrumentation,
- full production replay topology, provider or time equivalence,
- safe restoration of the compromised source/root agent,
- live cloud rollback or security effectiveness unless separately measured.

Its claims are deliberately bounded to represented, reproducible evidence in the included deterministic fixtures and any separately captured live path.
