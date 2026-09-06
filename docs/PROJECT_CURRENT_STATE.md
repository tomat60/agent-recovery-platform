# Project Current State

Date: 2026-09-06

## Status

M0 and M1 are accepted on `main`.

The first M2 slice has also landed on `main` at:

`d6b424d7261a6a7d1a4a0a86db4e35e59f0d6895`

That slice adds causal incident graph support, ordered recovery-plan validation, causal action links, recovery idempotency, causal evidence event types and an explicit external-input causal root.

The repository now contains the product strategy, threat model, Recovery Contract specification, benchmark contract, deterministic recovery core, synthetic enterprise, safety tests, CI, machine-generated benchmark evidence and the first causal multi-action recovery primitives.

## Product decision

Build a **recovery-first control layer for autonomous AI agents**, not a generic AI-security platform and not a generic agent undo tool.

Category ownership:

**incident -> containment -> evidence -> recovery -> replay -> verified restoration**

Core rules:

**No autonomous write without a recovery path.**

**No restored authority without a verified replay.**

## Competitive differentiation update

A September 6 competitive scan found several credible systems covering portions of agent rollback / reversibility, including Rubrik Agent Rewind, Toffoli, Agit, Walkback, Moholo Agent Rewind, OWASP Agent Memory Guard, RAC, Atomix, Mnemosyne and ACRFence.

A current Agents for Humans competitor, Authority Cut, also implements action-DAG correction propagation and compensation after human revocation.

Therefore:

- "undo for AI agents" is not a novelty claim
- reversibility classification is prior art
- compensation / saga semantics are prior art
- action journals and kill switches are prior art
- single-agent selective rollback is already commercially occupied

The differentiated wedge is now:

**distributed multi-agent incident recovery + recovery-path security + adversarial replay + verified restoration**

See `docs/COMPETITIVE_LANDSCAPE.md`.

## Scope accepted

- Recovery Contract Registry
- Action + Side-Effect Ledger
- deterministic action/recovery gates
- containment plane
- causal incident / blast-radius graph
- cross-agent shared-state causality
- distributed dependency-safe compensation
- recovery-path integrity and anti-replay controls
- Strands investigator
- recovery planner
- skeptic/verifier
- ordered compensation execution
- replay verification
- verified restoration gate
- incident-to-regression loop
- recoverability metrics / SLO surface
- Agent Recoverability Assessment as initial commercial offer

## Scope rejected for now

- broad SIEM replacement
- EDR
- generic prompt firewall
- broad IAM platform
- generic compliance suite
- generic agent undo product
- offensive counterattack
- government/critical-infrastructure-first GTM
- dozens of production connectors before the competition deadline

## Accepted implementation evidence

M1 release commit:

`70b47a90d84628c63c6f781b9a668a84c08c80c3`

The exact M1 commit completed `recovery-ci` successfully on Python 3.10 and 3.12. CI performs linting, deterministic tests, benchmark smoke, and uploads benchmark evidence as a workflow artifact.

M1 deterministic test suite: 9 passing tests.

M1 benchmark vertical slice has four scenarios:

1. reversible CRM corruption
2. memory poisoning
3. compensatable privilege change
4. irreversible external message

Observed M1 benchmark evidence:

- all three recoverable scenarios have one residual effect in the stop-only baseline and zero residual effects after verified platform recovery
- all three recoverable scenarios finish with verified recovery
- the irreversible external message remains residual and is explicitly reported rather than falsely marked recovered
- unsafe recovery executions: zero in the accepted slice

These are early synthetic benchmark results, not production effectiveness claims.

M2 first implementation slice on `main`:

`d6b424d7261a6a7d1a4a0a86db4e35e59f0d6895`

Merged functionality includes:

- causal incident graph
- ordered recovery plan validation
- causal action links
- recovery idempotency
- causal evidence event types
- explicit external-input causal root

## Current milestone

M2 - secure distributed recovery foundation and full deterministic benchmark.

### Next implementation slice

1. Finish cross-agent causal graph across action, memory, identity, agent and external-content events.
2. Add at least one shared-state scenario with two autonomous writers and deterministic ownership / conflict rules.
3. Add ordered multi-agent recovery with dependency validation and reverse compensation where appropriate.
4. Complete incident binding so an executed action cannot be recovered under another incident.
5. Add replay-safe idempotency and authority-consumption checks so a recovery path cannot resurrect stale authority.
6. Complete deterministic fixtures for:
   - indirect prompt injection trajectory
   - tool-output poisoning
   - approval bypass
   - privilege escalation
   - cascading multi-agent failure
   - concurrent shared-state writers
   - partial compensating workflow failure
   - runaway / denial-of-wallet loop
   - recovery-path attack
   - semantic replay / authority resurrection attempt
7. Expand benchmark metrics from residual-state evidence to:
   - blast-radius recall / precision
   - evidence completeness
   - compensation success rate
   - residual irreversible effects
   - recovery integrity failures
   - verified replay pass rate
8. Add fail-closed tests for malformed contracts, stale approvals, broken ledger references, cross-incident recovery, recovery re-entry, unsafe planner proposals and fabricated recovery success.

Strands agents are deliberately scheduled after this deterministic foundation. The model may investigate and propose; it must never become the authorization boundary.

## Competition target

The judge-facing demo should use a three-agent synthetic enterprise, not a single-agent undo demonstration.

Target flow:

1. poisoned external content enters through Support Agent
2. shared state influences a second agent
3. a third agent creates a downstream side effect
4. platform contains only the affected scopes
5. Investigator reconstructs cross-agent causality
6. Planner proposes recovery
7. Skeptic finds a missing dependency or unsafe assumption
8. deterministic gate admits only the corrected plan
9. compensation executes dependency-safely
10. irreversible residue remains visible
11. Replay Lab reruns the original incident against repaired controls
12. unauthorized side effects = 0
13. human restoration becomes available only after verification

This is intentionally different from existing single-agent rewind demos and from Authority Cut's human-revocation workflow.

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

Initial commercial offer remains an Agent Recoverability Assessment, but it should explicitly test multi-agent and shared-state recovery rather than only per-tool reversibility.

Within approximately 30 days, seek:

- 10 qualified buyer/partner conversations
- at least 2 concrete pilot/assessment interests
- at least 1 potential MSSP/security/AI consultancy partner
- independent senior security architecture review before a serious external pilot

Potential buyer-facing metrics:

- recoverability coverage of side-effecting action surface
- blast radius under controlled incident injection
- evidence completeness
- verified recovery rate
- residual irreversible exposure
- restoration time
- percentage of authority safely restorable after replay

If recovery repeatedly fails to map to an owned budget or urgent buyer pain, pivot before building heavy enterprise SaaS infrastructure.