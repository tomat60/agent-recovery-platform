# First-wave design-partner outreach

Date: 2026-09-24

Status: first wave authorized by Paweł on 2026-09-23. Keep outreach low-volume, evidence-based and personalized; legal terms, spend, production access and customer commitments remain owner-gated.

## Objective

Test willingness to engage around a bounded **Agent Recoverability Assessment** for one write-capable agent workflow. The first conversation is discovery, not a claim of production security effectiveness and not a request for production access.

## Wave 1 order

1. **Composio** — strongest tool-execution boundary fit; initial partnerships outreach sent 2026-09-23; await signal before a follow-up.
2. **n8n** — strongest workflow/side-effect fit; initial outreach sent 2026-09-23 and routed by n8n to Sophie Hillier with Freddie copied. A technical clarification was sent 2026-09-24; await human response rather than duplicating contact.
3. **LangChain / LangSmith** — strong runtime/trace adjacency; initial outreach sent 2026-09-23; await signal before a follow-up.

Wave 2 after signal/no-signal: Pipedream, Dust, Braintrust. Do not broaden merely to increase send count.

## Default 20-minute call ask

The call should answer three questions:

- Is verified recovery of already-executed external side effects a real pain distinct from retries, traces and containment?
- Can one bounded non-production workflow expose enough write boundaries to run an assessment safely?
- Does the buyer value pre-incident Recoverability Assurance, post-incident Verified Recovery, or both?

No credentials, production data, binding terms or paid commitment are needed for the first call.

## Message variants

### Composio

**Subject:** Design-partner test: verified recovery after agent tool writes

Hi — Composio already sits at a unusually high-leverage boundary: managed auth plus agent tool execution across many external apps.

I’m building Agent Recovery Platform around the part that auth, policy and tracing do not by themselves prove after an incident: which external effects were actually recovered or compensated, what remains irreversible, and what exact authority is safe to restore.

I’m looking for a small number of design partners for a bounded Agent Recoverability Assessment on one non-production write-capable workflow. The output is evidence, not a generic security score: write/authority map, Recovery Contract coverage, controlled incident, verified compensation/replay, residual-risk register and restoration decision.

Would a 20-minute technical fit call be useful to test whether this addresses a real gap at Composio’s tool-execution boundary? No production credentials or customer data are needed for the first step.

Paweł Tomczak

### n8n

**Subject:** Design-partner test: recoverability of AI workflow side effects

Hi — n8n’s multi-step AI workflows are exactly the kind of environment where a successful retry can still leave already-completed external side effects in an inconsistent state.

I’m building Agent Recovery Platform to make that post-incident state explicit: reconstruct the causal action chain, verify recovery/compensation outcomes, preserve irreversible residuals, replay against repaired controls, and restore only the scope supported by current evidence.

I’m looking for a small number of design partners for a bounded Agent Recoverability Assessment on one non-production write-capable workflow. We already have a synthetic n8n mapping for the assessment boundary, so the first conversation can stay concrete rather than becoming a generic security pitch.

Would a 20-minute technical fit call be worthwhile to see whether verified recoverability is distinct enough from n8n’s existing retry/error-handling model to matter to customers?

Paweł Tomczak

### LangChain / LangSmith

**Subject:** Design-partner test: recovery evidence beyond agent traces

Hi — LangSmith already provides much of the runtime and trace context needed to understand agent failures. The gap I’m testing is deliberately narrower: traces can show what happened, but do not by themselves prove that external side effects were compensated and that a precise authority scope is safe to restore.

Agent Recovery Platform turns incident evidence into Recovery Contract checks, dependency-aware compensation, replay/regression evidence, explicit irreversible residuals and a scope-bound restoration decision.

I’m looking for a small number of design partners for a bounded Agent Recoverability Assessment on one non-production write-capable workflow. I’d like to test whether this recovery layer complements LangSmith rather than duplicating observability.

Would a 20-minute technical fit call be useful? The first step needs no production credentials or customer data.

Paweł Tomczak

## Qualification / response tracking

For each contact, record only evidence-backed state:

| Target | Route checked | Sent | Response | Technical fit | Sandbox path | Buyer signal | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Composio | partnerships route checked | 2026-09-23 | none observed yet | pending | representative mapping exists | unknown | wait for signal; no duplicate follow-up |
| n8n | sales route routed to Sophie Hillier; Freddie copied | 2026-09-23; clarification 2026-09-24 | routing acknowledgement and named handoff; no human technical response yet | pending | synthetic mapping exists | early routing signal only | wait for Sophie/human response; prepare bounded sandbox discussion if technical fit is confirmed |
| LangChain / LangSmith | hello route checked | 2026-09-23 | none observed yet | pending | trace/runtime evidence route | unknown | wait for signal; no duplicate follow-up |

A positive reply is not yet a pilot. Promote to pilot candidate only when there is a named technical owner, one bounded workflow, a non-production/synthetic execution path, and agreement that recovery evidence addresses a real gap.

## Disqualification signals

Stop pursuing the assessment if the target already provides equivalent dependency-aware verified compensation plus residual truth and scope-bound restoration; has no consequential write workflow; cannot offer a bounded sandbox/non-production path; or only wants generic observability/security scoring.

## Claim boundary

Do not claim universal rollback, prevention, complete causal capture without instrumentation, production replay equivalence, restoration of irreversible effects, or production security effectiveness from owned sandbox evidence. Outreach beyond this authorized first wave, commercial commitments, terms, spend and serious pilot access remain owner-gated.
