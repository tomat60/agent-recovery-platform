# Competitive Landscape and Differentiation

Date: 2026-09-06

## Decision

Do not position this project as a generic "undo button for AI agents".

That category already contains credible open-source prototypes, academic work and a major commercial product. The differentiated target is:

**verified incident recovery for multi-agent systems with shared state**

The product should reconstruct cross-agent causality, contain affected authority, recover only what is provably recoverable, preserve residual truth, replay the triggering incident in isolation and require a verified restoration gate before authority is returned.

Core product rule remains:

**No autonomous write without a recovery path.**

Additional differentiating rule:

**No restored authority without a verified replay.**

## Direct and adjacent systems reviewed

### Rubrik Agent Cloud / Agent Rewind

Commercial product.

Strengths:
- immutable agent activity trail
- prompt, memory and tool-call visibility
- selective rollback of files, data, configurations and code
- enterprise positioning and existing cyber-resilience distribution

Gap we should target:
- do not compete on backup or generic selective rollback
- focus on causal, cross-agent incident recovery and proof that the repaired system resists replay before restoration

Sources:
- https://www.rubrik.com/products/agent-rewind
- https://www.rubrik.com/products/rubrik-agent-cloud

### Toffoli

Open-source, Apache-2.0.

Repository:
- https://github.com/theo-ai-lab/toffoli

Strengths:
- deterministic-first reversibility classification
- reversible / compensable / irreversible taxonomy
- dependency-aware restitution planning
- resumable, idempotent compensation
- explicit escalation of irreversible remainder
- property-based safety checks
- recovery attestation work
- measured evaluation rather than marketing-only claims

Important disclosed limitation:
- current scope is single-agent
- its own related-work document calls true multi-agent shared-state recovery an open frontier

Implication:
- this is the closest open-source reference and must be treated as a benchmark, not copied
- our strongest wedge is distributed multi-agent recovery plus incident-to-regression verification

### Agit

Public repository, no license detected at review time. Do not copy code.

Repository:
- https://github.com/isaffathir/agit

Strengths:
- explicit reversibility contracts
- action history and proof artifacts
- rollback providers for files, packages and PostgreSQL
- MCP integration
- risk gates

Its taxonomy is conceptually close:
- R0 read-only
- R1 file-reversible
- R2 transaction-reversible
- R3 snapshot-reversible
- R4 compensating-action only
- R5 irreversible

Implication:
- reversibility classification itself is not a defensible novelty claim
- our value must come from incident reasoning, shared-state causality, recovery integrity and verified restoration

### Walkback

Open-source, MIT.

Repository:
- https://github.com/tathagat22/walkback

Strengths:
- file snapshots and byte-accurate rollback
- compensating actions for APIs, cloud and database effects
- staged email delivery rather than pretending sent mail can be unsent
- dry-run gating
- MCP integration
- crash and concurrency safety work

Weakness relevant to our design:
- external reversals depend heavily on a recorded inverse / compensator
- it is primarily an undo engine, not a security incident investigation and verified restoration system

### Moholo Agent Rewind

Source-available under Business Source License 1.1. Do not copy code.

Repository:
- https://github.com/moholo-founder/agent-rewind

Strengths:
- transparent MCP interception proxy
- per-action undo and point-in-time rewind
- kill switch stored outside agent context
- append-only journal
- approval holds based on blast radius
- explicit honest failure reporting

Gap:
- current product is focused on interception, journaling and connector-local compensation
- our target is cross-agent causal recovery plus adversarial replay and restoration proof

### OWASP Agent Memory Guard

Open-source, Apache-2.0.

Repository:
- https://github.com/OWASP/www-project-agent-memory-guard

Strengths:
- runtime memory poisoning controls
- integrity checks
- snapshots and rollback
- reproducible security benchmark

Implication:
- memory recovery should be one evidence / side-effect class in our system, not our product category
- integration or adapter work can be considered later with attribution and license review

### Robust Agent Compensation (RAC)

Academic + MIT open-source reference implementation.

Repository:
- https://github.com/wso2-incubator/research-rac

Strengths:
- framework-agnostic compensation architecture
- log-based rollback for agent workflows
- benchmark traces and reproducible results

Gap:
- compensation is a primitive, not the whole incident-response and restoration lifecycle

### Atomix

Academic work on transactional tool calls for agent workflows.

Source:
- https://arxiv.org/abs/2602.14849

Strengths:
- progress-aware transactional semantics
- buffering, commit gates and compensation
- explicit treatment of leaked side effects under speculation and contention

Implication:
- transaction semantics are prior art
- our novelty cannot be "agents need transactions"

### Mnemosyne - Agentic Transaction Processing

Academic work + open-source artifact.

Source:
- https://arxiv.org/abs/2607.00269

Strengths:
- generated repair plans are treated as untrusted proposals
- deterministic admission boundary
- append-only transition log
- dependency-safe compensation
- evidence-preserving repair

Implication:
- deterministic authorization around model-proposed recovery is required for us too
- model output must never become the execution authority

### ACRFence

Academic work on semantic rollback attacks.

Source:
- https://arxiv.org/abs/2603.20625

Strengths:
- identifies Action Replay and Authority Resurrection after checkpoint restore
- proposes replay-or-fork semantics

Implication:
- the recovery path itself is an attack surface
- incident binding, anti-replay, stale-authority rejection and recovery integrity are first-class requirements

### Authority Cut

Current Agents for Humans competition project.

Public source:
- https://github.com/moneyparking/evidencebound-authority-cut

Strengths:
- action DAG
- policy-bounded authority
- later human revocation propagates through downstream execution
- reversible descendants are compensated
- irreversible pending actions can be invalidated
- verified AgentCore runtime path

Implication:
- human correction propagation is not enough differentiation for this competition
- our demo must visibly solve a different and harder problem: compromise or failure crossing several agents and shared systems, followed by verified recovery

## Differentiated product wedge

### 1. Cross-agent causal recovery

The system must reconstruct causality across:
- agent A and agent B
- shared memory
- identities and delegated authority
- API / MCP tool calls
- database or SaaS side effects
- external content that triggered the incident

A recovery plan must not be a simple reverse chronological list. It must respect causal and dependency relationships and concurrent writers.

### 2. Recovery integrity as a security boundary

A compromised caller must not be able to:
- re-parent an action to another incident
- replay a consumed authority grant
- fabricate recovery success
- alter recovery evidence
- trigger compensation against unrelated state
- restore authority from stale evidence

Recovery execution must fail closed.

### 3. Incident-to-regression loop

Every accepted incident should be convertible into a repeatable regression scenario.

The system should:
1. preserve the triggering evidence
2. reconstruct the causal chain
3. apply recovery / mitigation
4. replay the same attack or failure in isolation
5. compare side effects against policy
6. produce a machine-verifiable result

### 4. Verified restoration gate

Recovery completion is not equivalent to safe restoration.

Authority should return only when:
- required compensation steps are verified
- residual irreversible effects are explicitly listed
- evidence completeness passes the configured threshold
- isolated replay produces no unauthorized side effects
- required human approval is present

### 5. Recoverability as an enterprise metric

The commercial assessment should measure more than whether an undo exists.

Candidate metrics:
- recoverability coverage of side-effecting action surface
- blast-radius recall and precision
- evidence completeness
- compensation success rate
- recovery integrity failures
- residual irreversible effects
- verified replay pass rate
- recovery time for synthetic incidents
- percentage of authority that can be safely restored automatically

## Competition demo target

Use a three-agent synthetic enterprise rather than a single agent.

Example:
1. Support Agent reads a poisoned support ticket.
2. The poisoned content alters shared memory or a task artifact.
3. CRM Agent performs an unauthorized customer mutation.
4. Billing Agent changes a privilege or financial workflow state.
5. One irreversible external effect is attempted or executed.
6. Recovery platform contains only affected scopes.
7. Investigator reconstructs the cross-agent causal graph.
8. Recovery Planner proposes compensation.
9. Skeptic challenges the plan and exposes one missing dependency.
10. Deterministic gate admits the corrected plan.
11. Compensation executes dependency-safely.
12. Irreversible residue is reported honestly.
13. Replay Lab reruns the original attack against the repaired control state.
14. Unauthorized side effects = 0.
15. Human restoration gate becomes available.

The judge should be able to understand the value without reading documentation.

## What not to build before the deadline

- generic SIEM
- generic prompt firewall
- broad identity platform
- broad compliance dashboard
- EDR replacement
- dozens of production connectors
- offensive counterattack tooling
- a generic "undo" UI with no security proof

## Legal and originality rules

- Public competitor repositories are research references only unless their licenses are explicitly reviewed.
- Do not copy code, text, tests, benchmark fixtures, UI or naming from competitors into the competition project.
- Agit currently has no detected license, so treat its code as all-rights-reserved for reuse purposes.
- Moholo Agent Rewind uses BSL 1.1, so do not incorporate its source into this project.
- Apache-2.0 / MIT projects can be studied and, if later needed, reused only with proper attribution and license compliance. For the competition, prefer independent implementation so the core contribution remains clearly ours.

## Current strategic conclusion

The existence of these systems validates the market but removes "agent undo" as a novelty claim.

Continue the project, but compete on the harder layer:

**distributed incident recovery + recovery-path security + adversarial replay + verified restoration.**

That is both more defensible commercially and more clearly differentiated for the current hackathon.