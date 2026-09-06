# Agent Recovery Platform

A recovery-first safety layer for autonomous AI agents.

## Thesis

Most agent security products focus on prevention, monitoring, permissions, or detection. Those controls matter, but production incidents still happen. The hard question becomes: what exactly changed, what can be reversed, what requires compensation, what remains irrecoverable, and how can an operator prove that recovery actually worked?

This project is built around one rule:

> No autonomous write without a recovery path.

The platform records consequential agent actions, classifies their recoverability, contains compromised authority, reconstructs blast radius, builds a recovery plan, executes only policy-approved recovery actions, and verifies the result through replay before authority can be restored.

## Product boundary

This is not intended to replace SIEM, IAM, EDR, model guardrails, prompt-injection scanners, or general AI governance suites. It integrates with those systems and owns a narrower outcome:

**incident -> containment -> evidence -> recovery -> replay -> verified restoration**

That scope keeps the product defensible and measurable while still addressing a large enterprise problem.

## Core capabilities

1. **Recovery Contract Registry**
   - Every write-capable tool declares its side effects, risk, reversibility, compensation path, verification method, and approval requirements.
2. **Action Ledger**
   - Records intended and observed side effects independently from the agent's natural-language claims.
3. **Containment Plane**
   - Freezes tool, session, identity, or memory authority without destroying forensic evidence.
4. **Investigation and Blast Radius**
   - Reconstructs the causal chain across prompts, tool calls, memory, approvals, identities, and downstream actions.
5. **Recovery Planner**
   - Produces an ordered compensation plan with deterministic policy checks around consequential actions.
6. **Skeptic / Verifier**
   - Independently challenges the root-cause hypothesis and recovery plan.
7. **Replay Lab**
   - Replays the incident in isolation and proves whether the same failure still succeeds after remediation.
8. **Incident-to-Regression Loop**
   - Converts confirmed incidents into permanent adversarial regression tests.

## Initial buyer

The first target is not government or a global bank. The initial buyer is an AI-native SaaS, fintech, devtools, or security company with roughly 20-500 employees that already operates agents with real write permissions but does not yet have a mature internal AI-security program.

The first commercial offer should be a bounded **Agent Recoverability Assessment**, not a large enterprise platform contract. It maps one agent workflow, exercises controlled incidents, measures recovery coverage, verifies containment and compensation, and produces a remediation report.

## Competition build

The first implementation is being built during the 2026 Agents for Humans competition window. Strands Agents SDK will be used for investigation, recovery planning, and verification. AWS AgentCore Gateway, Policy, and observability are preferred for the live path because they allow authorization and evidence collection outside the agent itself.

The competition version will use synthetic systems and safe simulated side effects. It will never attack third-party infrastructure or perform real destructive actions.

## Benchmark-first development

A product claim is only accepted when the benchmark can prove it. Initial metrics:

- containment success rate
- time to containment
- blast-radius recall and precision
- root-cause accuracy
- recovery-plan correctness
- recovery execution success
- residual side effects after recovery
- replay attack success rate after remediation
- evidence completeness
- unsafe recovery action rate
- false-positive containment rate

See `docs/BENCHMARK.md` for the evaluation contract.

## Repository map

- `docs/PRODUCT_STRATEGY.md` - market wedge, scope, buyer, monetization and kill criteria
- `docs/THREAT_MODEL.md` - threats and safety boundaries
- `docs/RECOVERY_CONTRACT_SPEC.md` - contract model for reversible and compensatable actions
- `docs/BENCHMARK.md` - benchmark scenarios and metrics
- `docs/ARCHITECTURE.md` - target system architecture
- `docs/PROJECT_CURRENT_STATE.md` - durable execution checkpoint
- `src/agent_recovery/` - product code
- `tests/` - deterministic safety and recovery tests

## Safety

All development and demos use owned or synthetic environments. The project is defensive. It does not include credential theft, malware deployment, persistence, destructive third-party actions, or instructions for compromising external systems.

## Status

Bootstrap phase. Product strategy and benchmark are being defined before UI work.

## License

MIT
