# Agents for Humans Submission Draft

Status: private draft for owner review. Do not publish without explicit owner approval.

## Project name

Agent Recovery Platform

## Tagline

Verified recovery for compromised autonomous AI agents.

## Track

Professional Agents

## One-line thesis

When an autonomous agent is compromised or goes wrong, the platform reconstructs what changed, contains affected authority, recovers what is recoverable, preserves residual risk, replays the incident and restores authority only after machine-verifiable evidence says it is safe.

## Problem

Organizations are giving AI agents permission to modify customer records, shared memory, access controls, code, configuration and communication systems. Prevention and monitoring matter, but no defense is perfect. Once a write-capable agent is manipulated or fails, teams still need to answer a harder operational question: what changed, how far did the incident propagate, what can be reversed, what requires compensation, what can never be undone, and when is it safe to restore the agent's authority?

A generic kill switch stops future actions but does not reconstruct or repair the state already changed. A simple rollback can also be unsafe in multi-agent workflows because later actions may depend on earlier ones and some external effects are irreversible.

## Solution

Agent Recovery Platform is a recovery-first control layer for autonomous AI agents.

Its recovery lifecycle is:

`incident -> containment -> evidence -> recovery -> replay -> verified restoration`

Two rules define the system:

- No autonomous write without a recovery path.
- No restored authority without a verified replay.

Every consequential action is governed by a Recovery Contract that declares its side effects, recovery class, verifier, compensation path and approval requirements. A tamper-evident action ledger records observed effects independently from the agent's narration.

After an incident, read-only Strands agents investigate the evidence, reconstruct causal propagation and propose a dependency-aware recovery plan. A separate Skeptic challenges that plan. The model still has no authority to execute or restore anything. Deterministic recovery gates rebind every proposed step to the incident, contract version, approval, dependency order and current evidence before any recovery action is allowed.

After recovery, an isolated Replay Lab replays the incident. A failed, stale, incomplete or cross-incident replay proof keeps authority contained. Irreversible external effects remain explicitly visible as residual risk instead of being falsely reported as undone.

## What makes it different

The project is not another prompt-injection firewall, SIEM or generic agent dashboard. Its focus is what happens after prevention fails, especially when one compromised agent contaminates shared state and triggers downstream actions by other agents.

The differentiating loop is:

`cross-agent causality -> recovery integrity -> residual truth -> adversarial replay -> selective restoration`

The platform treats the recovery path itself as a security boundary. Recovery evidence, approvals and replay proofs are incident-bound and freshness-bound so stale or forged proof cannot resurrect authority.

## How Strands is used

Strands Agents SDK provides the evidence-only agentic reasoning layer:

- Investigator: reconstructs likely root cause and blast radius from read-only evidence.
- Recovery Planner: proposes ordered reversible and compensating actions.
- Skeptic / Verifier: independently challenges causal assumptions, missing evidence and unsafe recovery claims.

Strands output is advisory. It cannot authorize writes, recovery execution or authority restoration. Deterministic code owns those boundaries.

## AWS architecture

The competition architecture keeps a credential-free deterministic path as the reproducible source of truth.

Preferred live AWS path, when separately verified and owner-approved:

- Amazon Bedrock for Strands model execution.
- Amazon Bedrock AgentCore Gateway / Policy as an external tool-policy boundary.
- AgentCore / CloudWatch observability as additional trace evidence.

No live AWS security-effectiveness claim should be made until the live path is actually executed and captured as evidence.

## Demonstrated scenario

A synthetic support agent consumes poisoned external content and writes compromised information into shared state. Downstream agents then make additional changes based on that state.

The platform:

1. records the causal chain,
2. identifies the three-agent blast radius,
3. contains the compromised root authority,
4. produces an evidence-bound recovery plan,
5. reverses or compensates recoverable actions in dependency-safe order,
6. keeps failed or irreversible effects explicit,
7. replays the incident in isolation,
8. restores only downstream authority supported by fresh replay evidence,
9. keeps the compromised root agent contained.

## Measured evidence

Current exact-head CI evidence is synthetic and deterministic, not a production-security claim.

On the accepted competition build:

- 120 deterministic tests pass on Python 3.12.
- The required adversarial benchmark contract covers B01-B10.
- B06 three-agent blast-radius recall: 1.0 in the bounded fixture.
- B06 three-agent blast-radius precision: 1.0 in the bounded fixture.
- Measured containment success rate: 1.0 across the currently measured deterministic scenarios.
- Replay attack success rate: 0.0 in the currently measured replay scenario.
- False-positive containment rate: 0.0 across three known-benign scopes in the bounded fixture.
- Authority resurrection successes: 0 in the measured attempt.
- Unsafe recovery executions: 0 across the aggregate deterministic benchmark report.

The repository explicitly records the limits of those measurements. They do not establish global or production effectiveness.

## Adversarial benchmark classes

- B01 indirect prompt injection trajectory
- B02 tool-output poisoning
- B03 memory poisoning
- B04 approval bypass
- B05 over-scoped identity / privilege escalation
- B06 cascading multi-agent failure
- B07 partial compensating workflow failure
- B08 irreversible external effect
- B09 runaway tool / denial-of-wallet style loop
- B10 recovery-path attack

Additional deterministic tests cover authority resurrection, replay freshness, cross-incident proof misuse, shared-state conflict, reconciliation and false-positive containment scope.

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
- exact-head CI reproduction artifact.

Judges can reproduce the strongest evidence without AWS credentials or paid model calls.

## Why it matters

As agents gain real write permissions, failures stop being only bad answers. They become state-changing incidents across multiple systems. Organizations need a way to reduce operational downtime and blast radius after an incident without pretending every side effect is reversible.

The commercial path starts with an Agent Recoverability Assessment for one write-capable workflow, then expands only after real customer validation.

## Build journey

The project began with a simple recovery-contract and action-ledger thesis. Competitive research showed that single-agent rollback and rewind already had credible implementations, so the design moved toward the harder gap: multi-agent causal recovery with shared state, recovery-path integrity and verified restoration.

The build was developed benchmark-first. Each security claim was paired with deterministic evidence, and the project repeatedly added fail-closed tests for ways its own recovery mechanism could be attacked, including stale replay proof, authority resurrection, cross-incident evidence misuse, partial compensation and direct recovery-path attacks.

## Challenges

The hardest design problem was keeping AI useful without making it an authority boundary. The solution was to separate investigation and planning from execution completely. Strands can reason over evidence and propose candidate actions, but deterministic modules must independently bind those actions back to contracts, approvals, incident state and replay freshness.

A second challenge was truthful recovery semantics. An external message that has already been delivered cannot be called rolled back. The platform therefore separates recovered local state from explicit residual external effects.

## Accomplishments

- Built an end-to-end recovery lifecycle rather than a detection-only agent.
- Added multi-agent causal blast-radius reconstruction.
- Protected the recovery path itself against stale, forged and cross-incident evidence.
- Added partial-compensation and irreversible-effect semantics.
- Added adversarial replay as a restoration requirement.
- Kept the complete judge path reproducible without credentials or paid model calls.
- Built claim-to-evidence boundaries so the demo cannot silently overstate what the benchmark proves.

## What is next

After the competition:

- validate the Agent Recoverability Assessment with AI-native SaaS, fintech, devtools and security teams,
- add framework-neutral trace ingestion and production-grade durable evidence storage,
- add topology/provenance binding for larger multi-agent systems,
- expand mutation/property testing of safety gates,
- integrate with existing SIEM, identity and agent-security products rather than replacing them,
- build a Recovery Intelligence Dataset from verified incident and replay outcomes.

## Demo video outline - target under 5 minutes

0:00-0:30 - The problem: prevention fails and write-capable agents leave real side effects.

0:30-1:00 - Architecture: Strands reasons, deterministic controls hold authority.

1:00-2:00 - Attack and cross-agent propagation through shared state.

2:00-2:45 - Blast radius and scoped containment.

2:45-3:30 - Investigator, Planner and Skeptic propose and challenge recovery.

3:30-4:15 - Deterministic recovery, residual truth and isolated adversarial replay.

4:15-4:40 - Selective restoration, root agent remains contained.

4:40-4:55 - Evidence: tests, benchmark coverage and reproducible package.

4:55-5:00 - Close: `No restored authority without a verified replay.`

## Final submission owner checklist

- Confirm final public repository head.
- Confirm MIT license is visible in repository metadata/About.
- Attach/export the architecture diagram.
- Record and publish a public YouTube or Vimeo video no longer than 5 minutes.
- Provide AWS Builder ID.
- Decide whether a verified live AWS path can truthfully be claimed.
- Review final text and required disclosure of any pre-existing work.
- Accept competition terms and submit on Devpost.
