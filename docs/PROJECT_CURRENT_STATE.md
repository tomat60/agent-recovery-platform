# Project Current State

Date: 2026-09-06

## Status

Repository bootstrapped. Strategy, threat model, architecture, Recovery Contract specification, and benchmark-first evaluation contract are defined before UI work.

## Product decision

Build a **recovery-first control layer for autonomous AI agents**, not a generic AI-security platform.

Category ownership:

**incident -> containment -> evidence -> recovery -> replay -> verified restoration**

Core rule:

**No autonomous write without a recovery path.**

## Scope accepted

- Recovery Contract Registry
- Action + Side-Effect Ledger
- deterministic action/recovery gates
- containment plane
- Strands investigator
- recovery planner
- skeptic/verifier
- compensation execution
- replay verification
- incident-to-regression loop
- Agent Recoverability Assessment as initial commercial offer

## Scope rejected for now

- broad SIEM replacement
- EDR
- general prompt firewall
- broad IAM platform
- generic compliance suite
- offensive counterattack
- government/critical-infrastructure-first GTM

## Current milestone

M0 - benchmark and contract foundation.

### Completed

- public repository created
- MIT license
- README thesis and product boundary
- AGENTS.md execution rules
- product strategy and ICP
- benchmark with 10 initial incident classes
- Recovery Contract specification
- threat model
- target architecture

### Next implementation slice

1. Python project skeleton and CI.
2. Recovery Contract datamodel + validation.
3. Deterministic Action Ledger.
4. Synthetic enterprise state model.
5. First three benchmark scenarios:
   - indirect prompt injection trajectory fixture
   - partial compensating workflow failure
   - irreversible external effect
6. Baseline `stop-only` recovery implementation.
7. Recovery-platform implementation sufficient to beat baseline on state recovery and residual-risk reporting.

## Competition deadline

Agents for Humans deadline: 2026-09-14.

RolePilot remains a separate maintenance project. Do not mix its competition code into this repository.

## Owner gates expected later

- AWS login/MFA or Builder ID
- AWS promotional credit request if still available
- Bedrock model access / credentials
- approval of any new AWS spend or persistent paid resource
- public Devpost / Builder / video publishing
- final competition submission

No owner action is required for local deterministic implementation.

## Commercial validation after competition

Within approximately 30 days, seek:

- 10 qualified buyer/partner conversations
- 2 concrete pilot/assessment interests
- 1 potential MSSP/security/AI consultancy partner
- independent senior security architecture review

If recovery repeatedly fails to map to an owned budget or urgent buyer pain, pivot before building heavy enterprise SaaS infrastructure.
