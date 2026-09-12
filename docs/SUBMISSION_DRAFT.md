# Agents for Humans Submission Draft

Status: private draft for owner review. Do not publish without explicit owner approval.

## Project name

Agent Recovery Platform

## Tagline

Verified recovery for compromised autonomous AI agents.

## Track

Professional Agents

## One-line thesis

When an autonomous agent is compromised or goes wrong, the platform reconstructs represented side effects, contains affected authority, recovers what is recoverable, preserves residual risk, runs a bounded adversarial replay and restores only represented authority for which the deterministic evidence gate passes.

## Problem

Organizations are giving AI agents permission to modify customer records, shared memory, access controls, code, configuration and communication systems. Prevention and monitoring matter, but no defense is perfect. Once a write-capable agent is manipulated or fails, teams still need to answer a harder operational question: what changed, how far did the incident propagate, what can be reversed, what requires compensation, what can never be undone, and when is it safe to restore the agent's authority?

A generic kill switch stops future actions but does not reconstruct or repair the state already changed. A simple rollback can also be unsafe in multi-agent workflows because later actions may depend on earlier ones and some external effects are irreversible.

## Solution

Agent Recovery Platform is a recovery-first control layer for autonomous AI agents.

Its recovery lifecycle is:

`incident -> containment -> evidence -> recovery -> replay -> verified restoration`

Two rules define the system:

- No autonomous write without a recovery path.
- No restored authority without complete represented recovery evidence and a current scope-bound replay.

Every consequential action is governed by a Recovery Contract that declares its side effects, recovery class, verifier, compensation path and approval requirements. A locally tamper-evident action ledger records represented effects independently from the agent's narration. The prototype explicitly does not claim authenticated ledger completeness or valid-prefix rollback resistance without external anchoring.

After an incident, read-only Strands agents investigate evidence, reconstruct represented causal propagation and propose a recovery plan. A separate Skeptic challenges that plan. Model output has no authority to execute or restore anything. Deterministic modules independently bind executable recovery operations to trusted runtime contracts, incident identity, exact approvals where required, represented dependency/resource constraints and current ledger evidence.

After recovery, an isolated Replay Lab reruns an exact represented attack action. The replay is bound to the source action, source/recovery state, contract versions used by the represented incident and one proposed release scope. The proposed release scope cannot remain contained during the replay. Stale, superseded, action-mismatched, environment-contract-mismatched or cross-incident replay evidence fails closed. This is a bounded synthetic replay, not proof of complete production topology/provider equivalence.

Irreversible external effects remain explicitly visible as residual risk instead of being falsely reported as undone.

## What makes it different

The project is not another prompt-injection firewall, SIEM or generic agent dashboard. Its focus is what happens after prevention fails, especially when one compromised agent contaminates shared state and triggers downstream actions by other agents.

The differentiating loop is:

`cross-agent causality -> recovery integrity -> residual truth -> adversarial replay -> selective restoration`

The platform treats the recovery path itself as a security boundary. Within the bounded trusted-ledger runtime, approvals are single-use, recovery is incident-bound, containment is reconstructed from represented evidence, replay is execution-time/freshness/scope-bound, and restoration requires complete represented recovery obligations plus the latest applicable positive replay.

This competition build does not claim remote proof-forgery resistance, distributed consensus, production multi-tenancy, externally anchored evidence completeness or live cloud rollback attestation.

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

1. records the represented causal chain,
2. identifies the three-agent blast radius in the bounded fixture,
3. contains the compromised root and dependent authorities,
4. produces an evidence-bound recovery plan,
5. reverses or compensates recoverable actions in the represented dependency-safe order,
6. keeps failed or irreversible effects explicit,
7. runs scope-bound isolated replay against the selected represented attack action,
8. restores only downstream scopes supported by current replay and complete local recovery evidence,
9. keeps the compromised root agent contained.

## Measured evidence

Current PR validation evidence is synthetic and deterministic, not a production-security claim.

On the adversarially hardened validation branch:

- 139 deterministic tests pass on both Python 3.10 and Python 3.12.
- The required adversarial benchmark contract covers B01-B10.
- B06 three-agent blast-radius recall: 1.0 in the bounded fixture.
- B06 three-agent blast-radius precision: 1.0 in the bounded fixture.
- Measured containment success rate: 1.0 across the currently measured deterministic scenarios.
- Replay attack success rate: 0.0 in the currently measured bounded replay scenario.
- False-positive containment rate: 0.0 across three known-benign scopes in the bounded fixture.
- Authority resurrection successes: 0 in the measured attempt.
- Unsafe recovery executions: 0 across the aggregate deterministic benchmark report.
- GPT-6 adversarial counterexamples have been converted into permanent regression tests, including reconstruction, approval reuse, replay freshness/scope/environment binding, shared-state protection, malformed contracts, recovery approval purpose, evidence aliasing, failure accounting and judge-artifact semantics.

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

Additional deterministic tests cover authority reconstruction, approval single-use across shared controllers, replay freshness and supersession, cross-incident proof misuse, proposed-release-policy replay, source contract-manifest binding, cross-incident shared-state writers, reconciliation, evidence integrity at recovery entry and false-positive containment scope.

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
- exact-head CI reproduction artifacts.

Judges can reproduce the strongest bounded evidence without AWS credentials or paid model calls.

## Why it matters

As agents gain real write permissions, failures stop being only bad answers. They become state-changing incidents across multiple systems. Organizations need a way to reduce operational downtime and blast radius after an incident without pretending every side effect is reversible.

The commercial path starts with an Agent Recoverability Assessment for one write-capable workflow, then expands only after real customer validation.

## Build journey

The project began with a simple recovery-contract and action-ledger thesis. Competitive research showed that single-agent rollback and rewind already had credible implementations, so the design moved toward the harder gap: multi-agent causal recovery with shared state, recovery-path integrity and verified restoration.

The build was developed benchmark-first. A pre-submission GPT-6 adversarial architecture audit then deliberately tried to falsify the safety thesis against a green 120-test build. It found lifecycle counterexamples that ordinary tests had missed, including false restoration authorization, replay-context confusion, containment loss after reconstruction, approval reuse across controllers and shared-state recovery hazards. Those findings were treated as blockers rather than hidden: the fixes and falsification cases became the adversarial hardening branch and permanent regression coverage.

## Challenges

The hardest design problem was keeping AI useful without making it an authority boundary. The solution was to separate investigation and planning from execution. Strands can reason over evidence and propose candidate actions, but deterministic modules must independently enforce the executable safety boundary.

A second challenge was truthful recovery semantics. An external message that has already been delivered cannot be called rolled back. The platform therefore separates recovered local state from explicit residual external effects.

A third challenge was recognizing that a green test suite is not a proof. The adversarial audit exposed individually valid transitions that composed into unsafe lifecycle behavior, forcing the project to strengthen replay, restoration, shared-state and reconstruction invariants rather than merely add more happy-path fixtures.

## Accomplishments

- Built an end-to-end recovery lifecycle rather than a detection-only agent.
- Added multi-agent causal blast-radius reconstruction.
- Made active containment reconstructable from the retained ledger.
- Made approvals single-use across controllers sharing the bounded in-memory ledger.
- Added fail-closed malformed-contract, evidence-integrity and ambiguous-effect accounting.
- Bound replay to the represented source action, execution-time state, source contract versions and proposed release scope.
- Required complete represented recovery evidence before selective restoration.
- Preserved irreversible effects and failed compensation as explicit residual truth.
- Converted an external adversarial architecture audit into permanent regression coverage.
- Kept the complete judge path reproducible without credentials or paid model calls.
- Narrowed claims where the prototype does not provide production-grade evidence.

## What is next

After the competition:

- validate the Agent Recoverability Assessment with AI-native SaaS, fintech, devtools and security teams,
- add authenticated durable evidence storage with externally committed heads/sequence numbers,
- add framework-neutral trace ingestion and stronger causal completeness measurement,
- add full topology/provider/environment binding for larger replay systems,
- expand stateful mutation/property/model-checking of safety gates including true concurrency/ABA schedules,
- define authenticated capability/issuer boundaries for approvals and recovery-control APIs,
- integrate with existing SIEM, identity and agent-security products rather than replacing them,
- build a Recovery Intelligence Dataset from verified incident and replay outcomes.

## Demo video outline - target under 5 minutes

0:00-0:30 - The problem: prevention fails and write-capable agents leave real side effects.

0:30-1:00 - Architecture: Strands reasons, deterministic controls hold authority.

1:00-2:00 - Attack and cross-agent propagation through shared state.

2:00-2:45 - Blast radius and scoped containment.

2:45-3:30 - Investigator, Planner and Skeptic propose and challenge recovery.

3:30-4:15 - Deterministic recovery, residual truth and bounded adversarial replay.

4:15-4:40 - Selective downstream restoration, root agent remains contained.

4:40-4:55 - Evidence: adversarial audit, regression tests, benchmark coverage and reproducible package.

4:55-5:00 - Close: `No restored authority without complete recovery evidence and a current scope-bound replay.`

## Final submission owner checklist

- Merge only after the hardened PR is green and the targeted adversarial re-audit has no submission blocker.
- Confirm final public repository head and rerun exact-head acceptance.
- Confirm MIT license is visible in repository metadata/About.
- Attach/export the architecture diagram.
- Record and publish a public YouTube or Vimeo video no longer than 5 minutes.
- Provide AWS Builder ID.
- Decide whether a verified live AWS path can truthfully be claimed.
- Review final text and required disclosure of any pre-existing work.
- Accept competition terms and submit on Devpost.
