# Technical Diligence Pack

Date: 2026-09-24

Purpose: compact owner-reviewable material for a first design-partner conversation. This document describes accepted product evidence and explicit limits; it is not a production-security certification.

## What we assess

A bounded write-capable agent workflow is mapped across consequential actions, authorities, shared/external state, recovery declarations and trusted runtime bindings. The assessment asks a narrower question than generic agent security: after a bad write sequence, can the affected scope be contained, reconstructed, recovered or compensated, replayed against repaired controls, and restored only when current evidence supports that decision?

## Evidence chain

1. **Action evidence** — framework-neutral action records are normalized into durable provenance, including OTel-compatible inputs where available.
2. **Recovery Contract** — consequential actions declare structural recovery semantics separately from trusted runtime bindings.
3. **Containment** — incident state and affected authority remain persisted across restart; restoration is fail-closed.
4. **Recovery / compensation** — reversible and compensatable effects are handled dependency-aware; irreversible effects remain explicit residuals.
5. **Replay / regression** — the incident becomes a reusable regression case against repaired controls.
6. **Verified restoration** — only evidence-supported scope becomes eligible for restoration; compromised or unverified authority can remain contained.

## Current product evidence

Accepted `main` currently includes:

- framework-neutral action ingestion and OTel-compatible normalization;
- durable evidence/provenance plus persistent incident, containment and recovery state;
- versioned Recovery Contracts separated from trusted runtime bindings;
- deterministic Recovery Readiness / CI coverage;
- read-only operator API and console over canonical persisted incident state;
- a repeatable owned multi-surface sandbox pilot with recovery, replay and restoration evidence;
- deterministic Agent Recoverability Assessment output with evidence identity, residual truth and evidence-derived remediation priorities.

## First assessment scope

Default design-partner scope is one bounded workflow with a small number of consequential write surfaces. We prefer a sandbox or synthetic clone using non-sensitive data. A representative engagement should produce:

- tool / authority map;
- recovery-contract coverage and missing trusted bindings;
- controlled incident and containment evidence;
- causal side-effect map;
- verified recovery / compensation outcomes;
- replay / regression result;
- irreversible residual register;
- exact restoration eligibility;
- prioritized remediation actions;
- evidence identity sufficient to reproduce the assessment result.

## Integration boundary

We do not need to replace the customer's tracing, observability, runtime security or IAM stack. Existing traces and action telemetry can remain evidence sources. The preferred integration is a narrow adapter at consequential write boundaries plus trusted recovery bindings. The first qualification question is therefore not “can we ingest everything?” but “can we identify and safely exercise one bounded consequential workflow?”

## Data and access posture

For initial qualification and demos:

- synthetic or owned environments only unless a real pilot is explicitly approved;
- no customer credentials or secrets in repository artifacts;
- no requirement for production write authority;
- no autonomous external action from model output;
- legal terms, production/private data and serious pilot access remain explicit owner gates.

## Claim boundary

We do **not** claim universal rollback or prevention, authenticated global-ledger completeness, distributed-controller consensus, arbitrary production recovery, complete causal capture without instrumentation, complete production replay equivalence, production security effectiveness from the owned sandbox, restoration of irreversible effects, or safe restoration without current independent evidence.

## Design-partner technical questions

A first 30-minute diligence call should answer:

1. Which agent/tool actions can create consequential external or shared-state writes?
2. Which two surfaces form the smallest useful cross-system recovery case?
3. What telemetry already exists at those boundaries (OTel, traces, workflow history, audit events)?
4. What native rollback, retry or compensation exists today, and what does it fail to prove?
5. Can a non-production sandbox reproduce the write sequence without sensitive data?
6. Who owns approval for containment and restoration decisions?
7. Which effects are inherently irreversible and must remain residual rather than represented as undone?
8. What evidence would make the buyer trust a restoration decision?
9. Would the buyer value pre-incident Recoverability Assurance, post-incident Verified Recovery, or both?
10. What would make a bounded assessment commercially useful enough to repeat across more workflows?

## Initial commercial hypothesis

The current design-partner hypothesis is EUR 1,500–3,000 for one bounded Agent Recoverability Assessment. This is a willingness-to-pay test, not a published price or commitment. Expansion into SaaS, broad connectors, enterprise auth or production infrastructure should follow demand evidence rather than precede it.

## Pilot acceptance gate

A serious external pilot should not begin until scope, data handling, credentials, legal terms and cost are explicitly approved and a bounded independent review by a senior AppSec/cloud/AI-security practitioner is planned. Product evidence must remain distinguishable from advisory/model reasoning throughout the pilot.