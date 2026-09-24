# Agent Recovery Platform — ECCC Partner One-Pager

Date: 2026-09-24
Purpose: partner / consortium discussion for DIGITAL-ECCC-2027-DEPLOY-CYBER-11

## One-line proposition

**Verified recovery for autonomous AI-agent side effects across multiple tools and systems.**

Agent Recovery Platform sits between prevention/detection and business restoration. It records consequential agent actions, contains compromised authority, reconstructs blast radius, determines what is reversible/compensatable/irreversible, executes only policy-approved recovery paths, independently verifies resulting state and uses bounded replay evidence before represented authority is restored.

## Why now

AI agents increasingly receive write access to CRM, messaging, ticketing, deployment, identity, memory and workflow systems.

Prevention, guardrails and observability are necessary but cannot guarantee zero incidents.

The unresolved operational question is:

> after an AI agent makes a harmful or compromised change, how do we prove what changed, safely recover what can be recovered, keep irreversible effects explicit and know when authority may be restored?

## Existing product evidence

The current implementation already includes:

- framework-neutral action observation / ingestion;
- versioned Recovery Contracts separated from runtime implementation bindings;
- append-oriented tamper-evident action and side-effect evidence;
- containment scopes and active incident holds;
- causal / blast-radius reconstruction;
- deterministic recovery and compensation gates;
- independent state verification;
- bounded replay / incident-to-regression;
- selective restoration with freshness/scope checks;
- a repeatable owned multi-surface synthetic enterprise pilot;
- deterministic Agent Recoverability Assessment output.

Accepted evidence is intentionally bounded. Synthetic tests and owned pilots are **not** represented as global production security effectiveness.

## ECCC fit

### AI4SME — preferred track

Potential contribution:
- deploy recovery-readiness controls for SME AI-agent workflows;
- reduce time from detected incident to verified recovery;
- identify actions with no valid recovery path before production;
- provide explicit incident/recovery evidence and residual-risk reporting;
- package low-friction adapters and assessment tooling for SMEs.

### CYBERAI — secondary track

Potential contribution:
- AI-assisted incident investigation and blast-radius reconstruction;
- safe recovery-plan generation as advisory input;
- deterministic authorization/verification outside the model;
- incident recovery and cybersecure/trustworthy AI operations.

The model may investigate and propose. **Model output is never authorization.**

## Proposed consortium role

Preferred role: **technology provider + recovery work-package owner**.

We are seeking:

1. an experienced EU cybersecurity coordinator/integrator;
2. SME end users operating write-capable AI/automation;
3. an MSSP/AppSec/cloud-security/AI-security implementation partner;
4. optionally, an independent research/test partner for evaluation.

## Pilot structure

For one SME workflow:

1. map write-capable tools, identities and side effects;
2. create/version Recovery Contracts;
3. run controlled incident scenarios;
4. measure containment and blast-radius reconstruction;
5. verify recovery/compensation behavior;
6. replay the incident;
7. record irreversible residuals;
8. produce a remediation and recovery-readiness report.

Candidate KPIs:
- recovery-path coverage;
- time to containment;
- time to verified recovery;
- number/class of irreversible residuals surfaced;
- false restoration attempts rejected;
- integration effort;
- operator task completion/usability.

## Commercial wedge

This is **not** a general SIEM, EDR, IAM, prompt-injection firewall or generic AI-governance suite.

Category focus:

> incident -> containment -> evidence -> recovery / compensation -> replay -> verified restoration

Initial commercial offer:
**Agent Recoverability Assessment** for one bounded write-capable workflow.

Current design-partner price hypothesis in the product strategy: EUR 1,500–3,000, to be validated rather than treated as a fixed public price.

## Technical principles

- no autonomous write without a validated recovery path;
- model output never grants execution/restoration authority;
- irreversible effects are never represented as undone;
- recovery verification targets derive from trusted pre-action evidence;
- restoration is scoped, current and evidence-bound;
- adapters and telemetry do not silently become authorization.

## Partner discussion

We want to determine:

- which SME agent workflows produce the highest-cost recoverability gap;
- whether the product should enter AI4SME as a standalone recovery work package;
- what existing partner telemetry/detection stack should feed the recovery plane;
- which 2–4 SME deployments can create measurable cross-border evidence;
- what integration and independent evaluation work belongs in the proposal.

Current call deadline: **2027-01-14, 17:00 CET**.

Current target topics:
- **DIGITAL-ECCC-2027-DEPLOY-CYBER-11-AI4SME** — preferred;
- **DIGITAL-ECCC-2027-DEPLOY-CYBER-11-CYBERAI** — secondary.

Near-term partner-search milestone:
**German-Polish Cybersecurity Matchmaking & Proposal Writing Workshop, Warsaw, 1–2 October 2026.**

Agent Recovery is currently pre-incorporation. The intended consortium role is technology provider + recovery work-package owner; entity formation should happen only when a real consortium/commercial path requires it.
