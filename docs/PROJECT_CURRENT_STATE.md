# Project Current State

Date: 2026-09-16

## Status

The Agents for Humans submission window is closed for this project. Competition material remains historical/reusable evidence, not the execution target.

Agent Recovery Platform is a **commercial-product-first** project. Competitions, grants, accelerators and demo days are secondary leverage channels only when they materially improve funding, credibility, distribution or customer access without creating throwaway architecture.

Current accepted `main`:

`c0bb57a2566a78b3bb4bc65522ca0033f65debdb`

Latest accepted product slice:

PR #78 `Persist framework-neutral evidence across restart`

Exact-head `recovery-ci #271` and post-merge `recovery-ci #272` passed. The accepted product now has a framework-neutral observation boundary plus a local append-oriented durable evidence/provenance store that preserves stable observation/event identity and causal bindings across process restart, rejects tampered or truncated persisted evidence during reconstruction, and keeps telemetry explicitly non-authoritative (`authorization_effect: none`).

## Product thesis

Agent Recovery Platform is a recovery-first control layer for autonomous and write-capable AI agents.

Lifecycle:

**incident -> containment -> evidence -> recovery / compensation -> replay / regression -> verified restoration**

Core rules:

**No autonomous write without a validated Recovery Contract.**

**Model output is never authorization.**

**No downstream authority release without complete current recovery evidence and scope-bound replay or equivalent verification.**

Irreversible external effects remain explicit residual risk. The product never claims that an irreversible side effect was undone.

## Commercial wedge

Generic agent rollback is crowded prior art. The durable wedge remains:

1. cross-agent causal provenance across shared state, identities and external side effects;
2. recovery-path security so compromised or stale actors cannot forge recovery or restoration;
3. framework-neutral Recovery Contracts and measurable recoverability coverage;
4. dependency-aware reversible / compensatable / irreversible recovery with explicit residual truth;
5. incident-to-regression conversion and replay against repaired controls;
6. verified selective restoration of only the exact safe scope;
7. Recovery Intelligence accumulated from action types, failure patterns, recovery strategies, verification outcomes and residual effects.

Assume observability, runtime-security and resilience vendors will add tracing, policy gates, kill switches and basic rollback. Do not compete on those alone.

## Current commercial execution order

### P1 - Productization foundation

PR #77 established framework-neutral action evidence ingestion. PR #78 made that evidence durable across restart with deterministic integrity reconstruction.

The next bounded slice is the **Recovery Contract SDK/schema boundary**. It should answer a pilot-critical integration question: can a write-capable tool declare its recovery obligations in a framework-neutral, versioned contract that the deterministic gate can validate without trusting agent/model narration?

Requirements for the next slice:

- versioned framework-neutral Recovery Contract schema/SDK surface;
- explicit action classification as reversible, compensatable or irreversible;
- declared recovery/compensation operation and verification obligations where applicable;
- stable tool/action identity and parameter/context binding compatible with the existing deterministic gate;
- fail closed for missing, malformed, unsupported-version or semantically incomplete contracts;
- deterministic fixtures covering reversible, compensatable and irreversible actions;
- no new model authority, paid infrastructure, cloud dependency or customer data;
- leave room for MCP/tool/HTTP/framework adapters rather than coupling the contract to one agent framework.

After the SDK/schema boundary, continue P1 with persistent containment/recovery state and operator-grade APIs.

### P2 - Recovery Readiness / CI gate

Productize a developer-facing check that identifies write-capable actions and requires a valid recovery path before production. Output measurable recoverability coverage rather than a generic security score.

### P3 - Operator Console

Evolve the judge-era console into an incident-response workflow showing incident, affected authority, causal graph, side effects, recovery class and obligations, proposed recovery versus deterministic admission, independent state verification, residual irreversible effects, replay/regression evidence, exact restoration decision and remaining containment. Evidence and advisory reasoning remain visibly separate.

### P4 - One realistic integration

Prove one end-to-end owned/sandbox workflow with real integration semantics and more than one side-effect surface. Prefer a high-signal developer/SaaS workflow over many shallow connectors.

### P5 - Agent Recoverability Assessment

Turn the engine into a repeatable service deliverable: tool/authority map, Recovery Contract coverage, controlled incident suite, containment/blast-radius evidence, recovery/compensation verification, replay/regression result, residual-risk register and prioritized remediation plan.

### P6 - Commercial validation

Before broad SaaS work, seek willingness-to-pay evidence. Target roughly 10 qualified buyer/partner conversations, at least 2 concrete pilot/assessment interests, at least 1 MSSP/AppSec/cloud-security/AI consultancy partner signal, and one realistic pilot-ready integration. External outreach remains owner-gated; research, briefs, demo packages, pricing hypotheses and drafts are autonomous.

## Accepted security foundation

The accepted implementation includes strict Recovery Contract validation, advisory-only model output, parameter/context-bound approvals, independent containment holds, fresh scope-bound restoration, deep-detached evidence payloads, integrity checks before privileged recovery/restoration, incident-bound recovery-result reuse, later-writer protection, verification targets derived from preserved pre-action evidence, explicit residual evidence, replay freshness/supersession checks and restoration requiring complete represented recovery plus current positive exact-scope replay.

PR #77 adds a framework-neutral observation boundary without expanding runtime authority. PR #78 adds durable local evidence persistence and fail-closed reconstruction across restart without turning evidence metadata into authorization.

## Explicit limits

The project does **not** yet claim authenticated ledger completeness, distributed-controller consensus, remote proof/approval forgery resistance without an authenticated issuer boundary, globally complete causal capture when instrumentation is missing, complete production replay topology/provider/time equivalence, arbitrary production rollback, universal attack prevention, production security effectiveness, or safe restoration of every compromised source agent.

These are engineering/evidence gaps, not marketing footnotes.

## Competition assets

Judge console, competition architecture asset, video plan, Devpost draft, submission checklist and verified Strands + Bedrock advisory proof remain reusable historical material. Do not finish the abandoned competition video unless it becomes useful for a customer, investor, partner or a new high-fit opportunity.

## Owner-only gates

- new spend or paid model/provider calls
- credentials, secrets, login/MFA and cloud account changes
- customer/private production data
- destructive real-world actions
- legal terms and contracts
- final external outreach, publication or customer commitments

Repo-only product work, zero-cost research, branch/PR/CI/review/merge, sandbox implementation, demo preparation, assessment templates and prospect research remain autonomous.
