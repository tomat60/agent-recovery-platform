# Agent Recovery Platform

A recovery-first safety layer for autonomous AI agents.

## Thesis

Most agent security products focus on prevention, monitoring, permissions or detection. Those controls matter, but production incidents still happen. The hard question becomes: what exactly changed, what can be reversed, what requires compensation, what remains irrecoverable, and how can an operator prove that recovery actually worked?

This project is built around two rules:

> No autonomous write without a recovery path.
>
> No restored authority without a verified replay.

The platform records consequential agent actions, classifies recoverability, contains compromised authority, reconstructs blast radius, builds recovery candidates, executes only deterministic policy-approved recovery actions in owned/synthetic environments, verifies resulting state independently, and uses replay evidence before authority can be restored.

## Product boundary

This is not a SIEM, IAM, EDR, generic prompt-injection firewall or broad AI-governance suite. It integrates with prevention, detection and identity systems and owns a narrower outcome:

**incident -> containment -> evidence -> recovery -> replay -> verified restoration**

Irreversible external effects are never represented as undone. Failed compensation remains visible as residual risk.

## Core capabilities

1. **Recovery Contract Registry**
   - Every write-capable tool declares side effects, risk, reversibility, compensation path, verification method and approval requirements.
2. **Action + Side-Effect Ledger**
   - Records intended and observed effects independently from agent narration and protects represented evidence with chained integrity checks.
3. **Containment Plane**
   - Freezes tool, session, identity or memory authority without destroying evidence.
4. **Investigation and Blast Radius**
   - Reconstructs causal chains across prompts, tool calls, memory, approvals, identities and downstream actions.
5. **Recovery Planner + Deterministic Gate**
   - Strands can propose recovery steps; deterministic controls rebind proposals to incident evidence and decide whether a candidate is executable.
6. **Skeptic / Verifier**
   - Independently challenges root-cause and recovery hypotheses. Model output never authorizes execution or restoration.
7. **Recovery Executor + State Verification**
   - Applies bounded reversible/compensating actions in synthetic or owned state and verifies the result independently.
8. **Replay Lab**
   - Replays the incident in isolation and can invalidate a false restoration claim.
9. **Incident-to-Regression Loop**
   - Converts confirmed incident evidence into permanent adversarial regression contracts.

## Competition build

The 2026 Agents for Humans build has a fully credential-free deterministic judge path. It covers B01-B10 adversarial fixture classes, full incident evidence, authority-free judge-console rendering, canonical JSON packaging with SHA-256 manifests, one-command incident reproduction and an exact-head package acceptance gate.

Strands Agents SDK is used for evidence-only investigation, recovery planning and skeptical review. Deterministic modules retain authority over contracts, approvals, recovery execution, verification and scoring.

Amazon Bedrock and AgentCore remain optional live-path integrations. They are not required to reproduce the accepted deterministic evidence and no live AWS security-effectiveness claim is made without separate evidence and owner-approved access/cost.

See:

- `docs/JUDGE_EVIDENCE_INDEX.md` for the final claim-to-evidence boundary,
- `docs/PROJECT_CURRENT_STATE.md` for the durable accepted-state checkpoint,
- `docs/BENCHMARK.md` for the benchmark contract.

## Benchmark-first development

A product claim is accepted only when represented evidence can support it. The benchmark contract covers:

- containment success
- blast-radius recall and precision
- root-cause evidence where applicable
- recovery-plan correctness where measured
- recoverable-state restoration
- residual-effect accuracy
- unsafe recovery execution
- replay attack success after remediation
- evidence completeness
- safe restoration
- false-positive containment

Recorded aggregate numbers in the repository are synthetic deterministic fixture measurements only. They are not production security-effectiveness claims.

## Judge reproduction

The default judge path is credential-free and deterministic:

1. reproduce the bounded synthetic incident,
2. validate the full incident evidence contract,
3. render only represented evidence,
4. canonicalize/package evidence and validate SHA-256 manifests,
5. verify recovery/residual truth and replay behavior,
6. run the exact-head final package acceptance gate.

Public video, Devpost/Builder publishing, competition terms and final submission remain explicit owner actions.

## Initial buyer

The first target is an AI-native SaaS, fintech, devtools or security company already operating agents with real write permissions but without mature recovery controls.

The first commercial offer is a bounded **Agent Recoverability Assessment** for one workflow, not a large enterprise-platform contract. It maps the workflow, classifies recovery paths, exercises controlled incidents, measures recovery coverage, verifies containment/compensation behavior and produces a remediation report.

## Repository map

- `docs/PRODUCT_STRATEGY.md` - market wedge, scope, buyer, monetization and kill criteria
- `docs/THREAT_MODEL.md` - threats and safety boundaries
- `docs/RECOVERY_CONTRACT_SPEC.md` - contract model for reversible and compensatable actions
- `docs/BENCHMARK.md` - benchmark scenarios and metrics
- `docs/ARCHITECTURE.md` - target system architecture
- `docs/PROJECT_CURRENT_STATE.md` - durable execution checkpoint
- `docs/JUDGE_EVIDENCE_INDEX.md` - final judge claim/evidence map
- `src/agent_recovery/` - deterministic recovery/control code
- `tests/` - deterministic safety, benchmark and recovery tests

## Safety

All adversarial development and demos use owned or synthetic environments. The project is defensive. It does not include credential theft, malware deployment, persistence, destructive third-party actions or instructions for compromising external systems.

## Current status

Final competition packaging and exact-head verification. Core deterministic recovery evidence and the credential-free judge path are implemented; remaining work is consistency/acceptance verification and owner-gated public submission, not expansion into a generic AI-security suite.

## License

MIT
