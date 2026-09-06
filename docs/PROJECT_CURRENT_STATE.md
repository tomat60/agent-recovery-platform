# Project Current State

Date: 2026-09-06

## Status

M0 and M1 are accepted on `main`.

The repository now contains the product strategy, threat model, Recovery Contract specification, benchmark contract, deterministic recovery core, synthetic enterprise, safety tests, CI, and machine-generated benchmark evidence.

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
- causal incident / blast-radius graph
- Strands investigator
- recovery planner
- skeptic/verifier
- ordered compensation execution
- replay verification
- incident-to-regression loop
- Agent Recoverability Assessment as initial commercial offer

## Scope rejected for now

- broad SIEM replacement
- EDR
- generic prompt firewall
- broad IAM platform
- generic compliance suite
- offensive counterattack
- government/critical-infrastructure-first GTM

## Accepted implementation evidence

Merged release commit:

`70b47a90d84628c63c6f781b9a668a84c08c80c3`

The exact `main` commit completed `recovery-ci` successfully on Python 3.10 and 3.12. CI performs linting, deterministic tests, benchmark smoke, and uploads the benchmark result as a workflow artifact.

Current deterministic test suite: 9 passing tests.

Current benchmark vertical slice has four scenarios:

1. reversible CRM corruption
2. memory poisoning
3. compensatable privilege change
4. irreversible external message

Observed benchmark evidence:

- all three recoverable scenarios have one residual effect in the stop-only baseline and zero residual effects after verified platform recovery
- all three recoverable scenarios finish with verified recovery
- the irreversible external message remains residual and is explicitly reported rather than falsely marked recovered
- unsafe recovery executions: zero in the current slice

These are early synthetic benchmark results, not production effectiveness claims.

## Current milestone

M2 - causal incident graph, ordered multi-action compensation, idempotency/dependency safety, and full 10-scenario deterministic benchmark.

### Next implementation slice

1. Causal graph across action, memory, identity, agent and external-content events.
2. Ordered multi-action recovery plan with dependency validation and reverse compensation where appropriate.
3. Recovery idempotency keys and replay-safe compensation.
4. Complete deterministic fixtures for:
   - indirect prompt injection trajectory
   - tool-output poisoning
   - approval bypass
   - privilege escalation
   - cascading multi-agent failure
   - partial compensating workflow failure
   - runaway / denial-of-wallet loop
   - recovery-path attack
5. Expand benchmark metrics from residual-state evidence to blast-radius recall/precision and evidence completeness.
6. Add fail-closed tests for malformed contracts, stale approvals, broken ledger references, recovery re-entry and unsafe planner proposals.

Strands agents are deliberately scheduled after this deterministic foundation. The model may investigate and propose; it must never become the authorization boundary.

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
- at least 2 concrete pilot/assessment interests
- at least 1 potential MSSP/security/AI consultancy partner
- independent senior security architecture review before a serious external pilot

If recovery repeatedly fails to map to an owned budget or urgent buyer pain, pivot before building heavy enterprise SaaS infrastructure.
