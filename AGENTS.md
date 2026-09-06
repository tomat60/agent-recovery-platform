# AGENTS.md

## Mission

Build the strongest practical recovery-first safety layer for autonomous AI agents.

The product owns the path from harmful or uncertain agent side effects to verified recovery. It does not try to replace every security control around an agent.

## Product rule

No autonomous write without a recovery path.

Every consequential action should be classified as one of:

- `REVERSIBLE`
- `COMPENSATABLE`
- `IRREVERSIBLE`

If the system cannot establish an acceptable recovery path, it must fail closed or require explicit human approval before execution.

## Current priorities

1. Benchmark and recovery contracts before UI.
2. Deterministic action ledger and safety invariants.
3. Synthetic incident environment with measurable side effects.
4. Strands investigator, recovery planner, and skeptic/verifier.
5. Containment and replay.
6. AgentCore live path only after the local path is reliable.
7. Product UI, competition materials, and commercial assessment workflow.

## Scope discipline

Do not turn this into a generic AI-security suite.

In scope:

- recoverability classification
- action and side-effect ledger
- containment orchestration
- causal incident reconstruction
- compensation planning
- policy-bound recovery execution
- replay verification
- incident-to-regression conversion
- recovery-readiness assessment

Out of scope unless directly required for recovery:

- generic malware detection
- full SIEM replacement
- full IAM replacement
- generic prompt-injection firewall
- offensive exploitation of third-party systems
- broad compliance platform
- autonomous retaliation or counterattack

Integrate with prevention, identity, SIEM, EDR, and model-security products instead of rebuilding them.

## Security invariants

- Never trust model output as authorization.
- High-impact actions require deterministic policy checks outside the model.
- Recovery actions need equal or stronger controls than original actions.
- Preserve forensic evidence before mutating incident state.
- Never claim recovery success until independent verification passes.
- Never claim reversibility for irreversible external effects.
- Fail closed on missing contracts, broken audit logging, ambiguous identity, stale approvals, or unverifiable side effects.
- Synthetic and owned environments only for attack/recovery testing.
- No real destructive external actions in demo or CI.
- No secrets, customer data, private credentials, or private incident details in the public repository.

## Architecture direction

Python 3.10+.

Use deterministic modules for contracts, policy, ledger, side-effect state, and scoring. Use Strands agents for investigation, hypothesis generation, recovery planning, and adversarial verification. The LLM may propose; the deterministic execution layer decides what may actually happen.

Prefer Amazon Bedrock AgentCore Gateway and Policy for the competition live path because authorization outside the agent is materially stronger than prompt-only controls. Observability should produce evidence, not merely dashboards.

## Definition of done

Code committed is not done.

A milestone is done only when:

- deterministic tests pass
- the benchmark executes end to end
- unsafe paths are explicitly tested
- generated evidence matches actual state transitions
- exact-head CI is green
- docs reflect current behavior
- no sensitive data is present
- demo claims can be reproduced

## Commercial direction

Initial offer: Agent Recoverability Assessment for one bounded agent workflow.

Do not overbuild enterprise features before buyer validation. Build proof, benchmark evidence, and a repeatable assessment before multi-tenant SaaS complexity.
