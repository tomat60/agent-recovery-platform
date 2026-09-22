# Commercial Launch Pack

Date: 2026-09-23
Owner-facing external identity: `hello@paweltomczak.com`

## Product category

Agent Recovery Platform is positioned as an **Agent Recoverability Control Plane** with two linked modes:

1. **Recoverability Assurance** — prove before deployment that consequential agent actions have valid, testable recovery paths.
2. **Verified Recovery** — after an incident, prove what was recovered, what remains irreversible, and which exact authority can safely return.

Do not position the product as a generic rewind button, observability dashboard, backup layer, MCP proxy, or broad AI-security suite.

## Initial commercial offer

### Agent Recoverability Assessment

A bounded engagement for one write-capable agent workflow.

Customer deliverables:
- write-capable action and authority map;
- Recovery Contract coverage and missing-path register;
- controlled incident exercise;
- containment and causal blast-radius evidence;
- verified recovery / compensation results;
- replay / regression evidence;
- irreversible residual register;
- restoration-eligibility decision;
- prioritized remediation;
- evidence identity for the exact assessment inputs/results.

Current design-partner pricing hypothesis: **EUR 1,500–3,000** for a tightly bounded first workflow. Treat this as a pricing test, not a published commitment.

## Ideal customer profile

Prioritize teams that have:
- production or near-production agents with real write permissions;
- more than one side-effect surface (CRM, ticketing, messaging, repositories, memory/state, internal APIs);
- a platform/security owner who already worries about blast radius, rollback, incident evidence, or deployment gates;
- enough urgency to run a controlled sandbox exercise within weeks;
- a small enough decision chain to test a design partnership quickly.

Likely buyer roles: CTO, CISO, Head of Platform, Head of AI/Agent Engineering, Staff/Principal Platform Engineer, AI Security lead.

Disqualify early when:
- agents are read-only demos;
- the team only wants generic LLM evaluation;
- no owner can expose even a sandbox workflow;
- the expected answer is simply storage backup/restore;
- integration access would require production credentials before trust is established.

## 20–30 minute buyer demo

1. **2 min — problem:** agents can act across systems, but rollback alone cannot prove safe restoration.
2. **4 min — readiness:** show consequential actions, recovery classes, missing bindings and CI/deployment gate.
3. **8 min — controlled incident:** run the owned multi-surface pilot; show containment, causal evidence and recovery candidates.
4. **5 min — verified recovery:** show independently verified recovery, irreversible residual truth and replay/regression.
5. **4 min — assessment:** show evidence identity, remediation priorities and restoration eligibility.
6. **3 min — design-partner ask:** select one sandbox workflow and define a two-week bounded assessment.

## Buyer message

Subject: Can you prove your AI agent is recoverable before production?

Hi {{name}},

I’m building Agent Recovery Platform for teams deploying AI agents that can write across real systems.

The product is not another observability or “undo” dashboard. It tests whether consequential agent actions have valid recovery paths before deployment, then preserves enough evidence to verify recovery and decide which authority is actually safe to restore after an incident.

We now have a bounded Agent Recoverability Assessment for one agent workflow: recovery-path coverage, a controlled incident, blast-radius evidence, verified recovery/compensation, irreversible residuals, replay/regression and a prioritized remediation report.

I’m looking for a small number of design partners with a real write-capable agent workflow and a safe sandbox where we can test this end to end.

Would a 20-minute walkthrough be relevant to the team owning your agent platform/security work?

Paweł
hello@paweltomczak.com

## Proof available today

Current accepted product proof includes:
- framework-neutral action evidence and OTel-compatible normalization;
- versioned declarative Recovery Contracts separated from trusted runtime bindings;
- restart-safe evidence and incident state;
- deterministic Recovery Readiness and CI gate;
- read-only operator console over persisted incident evidence;
- repeatable owned multi-surface pilot with replay/restoration evidence;
- deterministic Agent Recoverability Assessment with evidence-derived remediation;
- explicit claim limits and irreversible residual truth.

## Claim boundary

Do not claim:
- universal rollback or prevention;
- authenticated global ledger completeness;
- arbitrary production recovery;
- production security effectiveness from the owned sandbox;
- restoration of irreversible effects;
- safe restoration without current independent evidence.

## Commercial decision rule

Engineering work after this point must answer one of:
- does it unblock a design-partner assessment?
- does it make the buyer proof materially stronger?
- does it reduce integration cost?
- does it improve trustworthy restoration evidence?

If not, defer it until after buyer validation.
