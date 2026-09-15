# Project Current State

Date: 2026-09-15

## Status

The Agents for Humans submission window is closed for this project. The competition package remains useful historical evidence and demo material, but it is no longer the execution target.

Agent Recovery Platform is now a **commercial-product-first** project. Competitions, grants, accelerators and demo days are secondary leverage channels only when they materially improve funding, credibility, distribution or customer access without creating throwaway architecture.

Current accepted `main`:

`4689b07b320a490708b0afca0e02714584df2e63`

Accepted security code anchor:

`b997384addd8781e0dac153d92adabcf9cc11757`

GitHub Actions run `34762391263` passed on that security code state with Python 3.10, Python 3.12, Ruff, **153 deterministic tests**, B01-B10 benchmark smoke, credential-free judge reproduction, canonical semantic validation, authority-free packaging and SHA-256 manifest verification.

Presentation/documentation work merged through PRs #71-#74 did not expand runtime authority. The verified live Strands + Amazon Bedrock proof remains advisory-only: model agents had no tools exposed and `authorization_effect` remained `none`.

## Product thesis

Agent Recovery Platform is a recovery-first control layer for autonomous and write-capable AI agents.

Lifecycle:

**incident -> containment -> evidence -> recovery / compensation -> replay / regression -> verified restoration**

Core rules:

**No autonomous write without a validated Recovery Contract.**

**Model output is never authorization.**

**No downstream authority release without complete current recovery evidence and scope-bound replay or equivalent verification.**

Irreversible external effects remain explicit residual risk. The product never claims that an irreversible side effect was undone.

## Why continue

The project should continue aggressively, but not by broadening into a generic AI-security platform.

The market is validating the underlying problem: major security vendors and startups are moving into agent runtime security, governance, identity, kill-switch and rollback products, while standards bodies are formalizing agent-specific risks. Direct recovery products now exist, so a generic "undo button for agents" is not a defensible category.

The strongest wedge remains:

**verified incident recovery for multi-agent and cross-system side effects, with recovery-path security, incident-to-regression replay and exact selective restoration.**

The current prototype already contains unusually deep primitives for that wedge: Recovery Contracts, explicit reversible/compensatable/irreversible semantics, shared containment, cross-incident hold isolation, blast-radius evidence, dependency-aware recovery, independent verification, replay binding, stale-evidence rejection and scope-bound restoration.

## Three-moves-ahead strategy

Assume that within 6-18 months observability vendors, runtime-security vendors and large resilience vendors can all add more tracing, policy gates, kill switches and basic rollback.

Do not compete on those features alone.

Build durable value around:

1. **Cross-agent causal provenance** across shared state, identities and external side effects.
2. **Recovery-path security** so compromised or stale actors cannot forge recovery or restoration.
3. **Framework-neutral Recovery Contracts** and a recoverability-readiness gate for write-capable actions.
4. **Incident-to-regression conversion** so a real incident becomes a portable replay / regression artifact after remediation.
5. **Verified selective restoration** that proves exactly which authority may return and which remains contained.
6. **Recovery Intelligence** accumulated from action types, failure patterns, recovery strategies, verification results and residual effects.

These capabilities form a more durable moat than another dashboard or single-system undo provider.

## Current commercial execution order

### P0 - Commercial authority and roadmap

Reconcile project authority away from competition-specific execution. Preserve accepted evidence, but treat the competition video, Devpost draft and judge-only assets as historical/reusable material rather than active blockers.

### P1 - Productization foundation

Build the smallest framework-neutral path from a real agent/tool trace into the recovery engine:

- OpenTelemetry-compatible ingestion where practical
- small MCP / tool / HTTP adapters rather than a new observability stack
- persistent incident/action/evidence identifiers
- durable Recovery Contract representation
- durable containment/recovery state suitable for one pilot
- operator-grade APIs around evidence, plan, verification and restoration

### P2 - Recovery Readiness / CI gate

Productize a developer-facing check that identifies write-capable actions and requires a valid recovery path before production. It should output a measurable recoverability report rather than a generic security score.

This is deliberately recovery-specific and can support the first commercial assessment without turning the company into a broad pre-deployment scanner.

### P3 - Operator Console

Evolve the Judge Console into an incident-response workflow showing:

- incident and affected authority
- causal graph and side effects
- recovery class and recovery obligations
- proposed recovery vs deterministic admission
- independent state verification
- residual irreversible effects
- replay / regression evidence
- exact restoration decision and remaining containment

Evidence and advisory reasoning must remain visually and semantically separate.

### P4 - One realistic integration

Prove one end-to-end sandbox workflow with real integration semantics and more than one side-effect surface. Prefer a high-signal developer / SaaS workflow over dozens of shallow connectors.

### P5 - Agent Recoverability Assessment

Turn the engine into a repeatable service deliverable for one customer workflow:

- tool and authority map
- Recovery Contract coverage
- controlled incident suite
- containment and blast-radius evidence
- recovery / compensation verification
- replay / regression result
- residual-risk register
- prioritized remediation plan

### P6 - Commercial validation

Before broad SaaS work, seek evidence of willingness to pay.

Target over roughly 30 days:

- 10 qualified buyer / partner conversations
- at least 2 concrete pilot or assessment interests
- at least 1 MSSP / AppSec / cloud-security / AI consultancy partner signal
- one realistic pilot-ready integration

External outreach remains owner-gated. Research, prospect lists, tailored briefs, demo packages, pricing hypotheses and drafts can be prepared autonomously.

## Accepted security foundation

The accepted implementation includes, among other controls:

- strict Recovery Contract validation before represented side effects
- advisory-only model output with no execution authority
- parameter-bound action approvals and context-bound recovery approvals
- shared authoritative containment with independent holds per incident and scope
- fresh single-use restoration application bound to one exact active hold
- deep-detached evidence payloads
- integrity verification before privileged recovery / restoration decisions
- incident binding before recovery-result cache reuse
- cross-incident / later-writer protection for represented mutable resources
- verification targets derived from preserved pre-action evidence, not recovery-side claims
- explicit failure / residual evidence for recovery executor and verifier failures
- replay bound to source action, source ledger head, recovery generation, contract versions and one release scope
- replay freshness / supersession checks
- restoration requiring complete represented recovery, no uncovered residual and current positive exact-scope replay
- permanent regressions for audit, re-audit, mutation and final acceptance counterexamples

## Explicit limits

The project does **not** yet claim:

- authenticated ledger completeness or valid-prefix rollback resistance
- distributed-controller consensus
- remote proof / approval forgery resistance without an authenticated issuer boundary
- globally complete causal capture when instrumentation is missing
- complete production replay topology / provider / time equivalence
- arbitrary production rollback
- universal attack prevention
- production security effectiveness
- safe restoration of every compromised source agent

These are engineering or evidence gaps, not marketing footnotes. Do not widen public claims ahead of proof.

## Competition assets

The following remain reusable but are no longer active execution priorities:

- `demo/index.html` Judge Incident Recovery Console
- `docs/assets/architecture-competition.svg`
- `docs/VIDEO_PRODUCTION_PLAN.md`
- `docs/DEVPOST_FINAL_DRAFT.md`
- `docs/SUBMISSION_FINAL_CHECKLIST.md`
- verified live Strands + Bedrock advisory proof

Do not finish the abandoned competition video unless it becomes useful for a customer, investor, partner or a new high-fit opportunity.

## Owner-only gates

- new spend or paid model/provider calls
- credentials, secrets, login/MFA and cloud account changes
- customer/private production data
- destructive real-world actions
- legal terms and contracts
- final external outreach, publication or customer commitments

Repo-only product work, zero-cost research, branch/PR/CI/review/merge, sandbox implementation, demo preparation, assessment templates and prospect research remain autonomous.
