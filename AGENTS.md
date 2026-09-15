# AGENTS.md

## Mission

Build the strongest practical recovery-first safety layer for autonomous AI agents.

The product owns the path from harmful or uncertain agent side effects to verified recovery. It does not try to replace every security control around an agent.

The missed Agents for Humans submission is closed. Competition artifacts remain reusable evidence, but the product roadmap is now commercial-first. Competitions, grants and accelerators are secondary leverage channels only when they materially improve funding, credibility, distribution or customer access without distorting the product.

## Product rule

No autonomous write without a recovery path.

No restored authority without current recovery evidence and scope-bound replay or equivalent verification.

Every consequential action should be classified as one of:

- `REVERSIBLE`
- `COMPENSATABLE`
- `IRREVERSIBLE`

If the system cannot establish an acceptable recovery path, it must fail closed or require explicit human approval before execution.

## Current priorities

1. Reconcile the repository from competition-first packaging to commercial product authority while preserving accepted security evidence.
2. Productize a framework-neutral ingestion and evidence boundary for consequential agent actions, preferring OpenTelemetry-compatible traces and small adapters over a new observability stack.
3. Make Recovery Contracts usable as an SDK/schema and as a recovery-readiness gate for write-capable tools.
4. Add durable incident, containment, recovery and evidence state suitable for one real pilot workflow.
5. Replace judge-first presentation UX with an operator incident-recovery console.
6. Prove one realistic end-to-end sandbox integration with cross-system or shared-state side effects.
7. Turn the engine into a repeatable Agent Recoverability Assessment with machine-generated evidence and remediation output.
8. Validate demand before broad enterprise SaaS work: customer/partner discovery, design partners and one bounded paid assessment are higher priority than dozens of connectors or multi-tenant complexity.

## Three-moves-ahead rule

Before a major feature, ask what direct competitors are likely to add during the next 6-18 months. Generic agent tracing, policy enforcement, kill switches, rollback and single-system undo are expected to converge quickly.

Prefer capabilities that still matter after that convergence:

- cross-agent and cross-system causal provenance
- recovery-path integrity and stale-authority rejection
- dependency-aware compensation with explicit residual truth
- incident-to-regression conversion
- verified selective restoration
- framework-neutral recovery contracts and ingestion
- a growing Recovery Intelligence dataset of side effects, recovery strategies and verified outcomes

Do not add broad novelty features that increase operational complexity without improving customer value, pilot feasibility or defensibility.

## Scope discipline

Do not turn this into a generic AI-security suite.

In scope:

- recoverability classification
- Recovery Contract registry and readiness checks
- action and side-effect ledger / durable evidence
- containment orchestration
- causal incident reconstruction
- compensation planning
- policy-bound recovery execution
- independent state verification
- replay / regression verification
- incident-to-regression conversion
- selective verified restoration
- recovery-readiness assessment and reporting
- lightweight framework/MCP/OTel adapters needed to observe and recover agent side effects

Out of scope unless directly required for recovery:

- generic malware detection
- full SIEM replacement
- full IAM replacement
- generic prompt-injection firewall
- offensive exploitation of third-party systems
- broad compliance platform
- autonomous retaliation or counterattack
- a generic LLM debugger or observability product
- backup/storage infrastructure already owned by specialists

Integrate with prevention, identity, SIEM, EDR, observability, model-security and backup products instead of rebuilding them.

## Security invariants

- Never trust model output as authorization.
- High-impact actions require deterministic policy checks outside the model.
- Recovery actions need equal or stronger controls than original actions.
- Preserve forensic evidence before mutating incident state.
- Never claim recovery success until independent verification passes.
- Never claim reversibility for irreversible external effects.
- Fail closed on missing contracts, broken audit logging, ambiguous identity, stale approvals, unverifiable side effects or stale replay evidence.
- Synthetic and owned environments only for attack/recovery testing unless an explicitly authorized pilot defines stronger controls.
- No real destructive external actions in demo or CI.
- No secrets, customer data, private credentials or private incident details in the public repository.

## Architecture direction

Python 3.10+.

Use deterministic modules for contracts, policy, ledger, side-effect state, approval, recovery execution, verification, restoration and scoring. Use Strands or other LLM agents only for investigation, hypothesis generation, recovery planning and skeptical review. The model may propose; the deterministic execution layer decides what may actually happen.

Prefer framework-neutral interfaces. OpenTelemetry-compatible trace ingestion, MCP/tool adapters and ordinary HTTP/API wrappers should feed one recovery evidence model rather than creating framework-specific product forks.

Cloud-specific integrations such as Amazon Bedrock AgentCore are optional adapters, not product identity. Do not add paid cloud infrastructure unless a concrete pilot, benchmark or commercial milestone justifies it and owner approval exists.

## Commercial validation

Initial offer: Agent Recoverability Assessment for one bounded agent workflow.

Target evidence over roughly 30 days:

- 10 qualified buyer or partner conversations
- at least 2 concrete pilot / assessment interests
- at least 1 MSSP, AppSec, cloud-security or AI consultancy partner signal
- one realistic integration or sandbox proving the commercial workflow

Prepare customer research, demo packages, assessment reports, pricing hypotheses and outreach drafts autonomously. External outreach, legal acceptance, credentials and spend remain owner-gated.

Do not overbuild enterprise features before buyer validation. Build proof, benchmark evidence, a repeatable assessment and a pilot-ready integration before multi-tenant SaaS complexity.

## Definition of done

Code committed is not done.

A milestone is done only when:

- deterministic tests pass
- relevant benchmark and unsafe paths are explicitly tested
- generated evidence matches actual state transitions
- exact-head CI is green
- direct behavior / operator workflow is reviewed where applicable
- docs reflect current behavior and claim boundaries
- no sensitive data is present
- the change improves customer value, pilot feasibility, measurable recoverability or defensibility
- the next commercial validation step is clear
