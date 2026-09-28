# Kyvvu + Agent Recovery TechEx integration scenario

Date: 2026-09-28

Purpose: bring one concrete scenario to the TechEx conversation with Kyvvu. This is a discussion artifact, not a claim that an integration exists.

## Boundary

Kyvvu ASK:
- decides whether an agent action should be allowed before execution;
- supplies policy / decision context around the action.

Agent Recovery:
- tracks the resulting side effects;
- contains authority after an incident;
- reconstructs what changed;
- recovers or compensates what can be recovered;
- keeps irreversible effects explicit;
- verifies restoration before authority is resumed.

The integration hypothesis is complementary:

pre-action enforcement -> action execution -> side-effect evidence -> incident containment -> recovery / compensation -> replay -> verified restoration -> scoped authority resume

## Concrete scenario

A customer-service agent is allowed to:
- update a CRM record;
- issue a support credit;
- send a customer email.

The action is legitimate under current policy, so ASK allows it.

The source context is stale or incomplete. The agent therefore performs a technically allowed but operationally wrong sequence:
1. CRM customer tier is changed incorrectly.
2. A support credit is issued with the wrong amount.
3. A customer email is sent confirming the wrong resolution.

This is not a simple policy-denial case. The action looked valid before execution.

## Evidence handoff

Before or at execution, preserve:
- agent identity;
- tool and action name;
- normalized parameters;
- ASK decision identifier;
- policy / rule version where available;
- approval result;
- trace / request identity;
- timestamp.

Agent Recovery treats ASK decision data as evidence about why execution was allowed. It does not treat that evidence as authorization to perform recovery.

The current Agent Recovery evidence path can already accept framework-neutral evidence and standard OTLP JSON. A future Kyvvu adapter should stay outside core recovery semantics.

## Recovery Contracts

Illustrative classification:

### CRM tier change
Recovery class: reversible.

Possible recovery:
- restore prior tier if the current record still matches the incident lineage;
- fail closed if the record has changed independently since the incident.

### Support credit
Recovery class: compensatable or reversible depending on the payment / credit system.

Possible recovery:
- cancel if still pending;
- otherwise issue an explicit compensating transaction;
- preserve both the original and compensating transaction in evidence.

### Customer email
Recovery class: irreversible.

Possible recovery:
- do not pretend to unsend;
- preserve the email as an irreversible residual;
- optionally create an approved corrective communication task.

## Incident flow

1. Detect incorrect outcome or receive operator incident signal.
2. Freeze the affected agent authority or route further actions through a stricter policy state.
3. Bind evidence to the exact action / policy / trace identity.
4. Reconstruct CRM, credit and email side effects.
5. Build ordered recovery plan.
6. Require human approval for consequential compensation where appropriate.
7. Restore CRM state or apply safe compensation.
8. Record the email as an irreversible residual.
9. Verify current source-system state.
10. Replay the triggering workflow in a controlled environment.
11. Confirm the same failure is blocked, corrected or no longer produces the harmful state.
12. Resume only the minimum authority supported by current evidence.

## Possible Kyvvu interaction points

### A. Decision evidence into Agent Recovery
Kyvvu supplies the decision / policy context associated with an allowed action.

Value:
- stronger causal reconstruction;
- clearer explanation of why a bad action was permitted;
- better regression evidence after policy changes.

### B. Recovery state back into Kyvvu
Agent Recovery supplies non-authorizing recovery state such as:
- incident active;
- containment active;
- recovery verification pending;
- verified restoration complete for scope X.

Kyvvu could use that state as one input to policy enforcement.

Important boundary:
Agent Recovery does not grant authority. Kyvvu / the customer's policy system remains responsible for enforcement.

### C. Replay result as policy regression evidence
A controlled replay demonstrates whether:
- the same action path is now denied;
- the same action is allowed but produces a safe result;
- a recovery gap still exists.

This can become a durable regression test spanning prevention and recovery.

## What would make the integration valuable

A real integration is worth pursuing only if at least one is true:
- Kyvvu customers ask what happens after an allowed action creates a bad outcome;
- Kyvvu can expose stable action / decision identifiers that can be bound to recovery evidence;
- Agent Recovery can return recovery-state signals without creating circular authority;
- one customer workflow contains side effects that policy enforcement alone cannot reverse;
- both products remain clearly differentiated.

## What would make it unnecessary

Do not force a partnership if:
- Kyvvu already owns end-to-end cross-system compensation and verified restoration;
- its customer workflows rarely create recoverable external side effects;
- integration would require Agent Recovery core semantics to become Kyvvu-specific;
- the only value is generic telemetry exchange.

## Questions for Jeroen at TechEx

1. What identifier can reliably bind an ASK decision to the actual downstream tool action?
2. Does Kyvvu already persist decision context long enough for post-incident forensics?
3. Do customers ask about recovery after an action was correctly allowed but produced the wrong business outcome?
4. Can policy consume an external incident / recovery state without that external system becoming an authority source?
5. Which real Kyvvu workflow would best expose whether this boundary is useful?

## Success condition for the meeting

Do not seek a partnership commitment.

A successful TechEx meeting produces one of:
- one real workflow to model together;
- agreement to exchange a small technical artifact;
- a bounded integration experiment;
- a clear reason the products do not need to integrate.

Any of those is useful validation.
