# Commercial Roadmap

Date: 2026-09-15

## Executive decision

Continue Agent Recovery Platform as a serious commercial project.

Do not broaden into a generic AI-security suite. The market is moving quickly into agent discovery, identity, runtime enforcement, governance, kill switches and generic rollback. The commercial opportunity is narrower and harder:

**verified incident recovery for write-capable AI agents across multiple systems and shared state.**

The first revenue objective is not a large enterprise SaaS contract. It is a bounded paid **Agent Recoverability Assessment** for one agent workflow, backed by the product's deterministic evidence engine.

## Product lifecycle

The product should own one coherent lifecycle:

1. **Recovery Readiness**
   - identify write-capable actions
   - require a Recovery Contract
   - classify reversible / compensatable / irreversible side effects
   - measure recovery coverage before production

2. **Runtime Evidence + Containment**
   - ingest action/tool traces
   - preserve intended and observed side effects
   - bind identity, authority, approval and contract version
   - contain exact affected scopes without erasing evidence

3. **Incident Recovery**
   - reconstruct causal blast radius across agents and systems
   - propose dependency-aware recovery / compensation
   - admit only deterministic evidence-bound actions
   - independently verify resulting state

4. **Replay / Regression**
   - convert confirmed incidents into reproducible regression artifacts
   - replay against repaired controls
   - reject stale or mismatched evidence

5. **Verified Restoration**
   - restore only exact downstream authority supported by current evidence
   - keep compromised or unresolved scope contained
   - report irreversible residuals honestly

This lifecycle is the product. Features that do not strengthen it need a high burden of proof.

## Three moves ahead

### Move 1 - Recovery Contracts become the adoption wedge

Make the Recovery Contract useful before an incident.

A lightweight SDK / CLI should inspect declared tool actions or adapter metadata and answer:

- which actions can write?
- what side effects can they create?
- what is the recovery class?
- what prior state / idempotency / compensator / verifier is required?
- which actions lack an acceptable recovery path?

Output: a machine-readable contract plus a human-readable recoverability report.

This creates an entry point for developers and for the paid assessment without becoming a generic vulnerability scanner.

### Move 2 - Incident-to-regression becomes the durable differentiator

Every confirmed incident should be convertible into a portable regression package containing:

- triggering evidence
- source action / tool / contract identity
- causal dependencies
- expected recovery obligations
- residual-risk expectations
- replay inputs
- restoration scope

A customer's incident corpus becomes increasingly valuable over time. This is both product value and the beginning of a Recovery Intelligence moat.

### Move 3 - Recovery Intelligence becomes the long-term data advantage

For every controlled incident or customer assessment, preserve structured non-sensitive metadata such as:

- action type and side-effect class
- failure / attack pattern
- causal shape
- containment strategy
- compensation strategy
- verifier type
- recovery success / partial failure
- replay result
- residual effect
- time-to-contain and time-to-verify

Over time this can answer which recovery strategies actually work for which agent action classes. The moat should be verified outcomes and recovery knowledge, not an LLM prompt or dashboard.

## 0-30 day plan

### Week 1 - Productization foundation

Deliver the smallest path from external agent evidence to the existing recovery engine.

Acceptance target:

- framework-neutral action / incident envelope
- OpenTelemetry-compatible ingestion path or import format where practical
- Recovery Contract SDK/schema usable outside the synthetic fixture
- persistent local evidence / incident storage suitable for a pilot
- one adapter for a write-capable agent/tool path
- no regression to the accepted security invariants

Avoid:

- multi-tenant SaaS
- billing
- broad cloud deployment
- dozens of connectors
- generic observability UI

### Week 2 - Operator workflow + assessment output

Evolve the presentation console into an operator workflow and create a real assessment report artifact.

Acceptance target:

- incident timeline / causal graph
- affected authority / containment view
- recovery obligations and status
- deterministic vs advisory separation
- residual-risk view
- replay / regression proof
- exact restoration decision
- generated assessment report from the same evidence

### Week 3 - Realistic sandbox integration

Choose one representative workflow with at least two side-effect surfaces.

Preferred characteristics:

- common in AI-native SaaS / devtools
- mostly reversible or compensatable, with at least one intentionally externalized / irreversible edge
- can run safely in owned sandbox accounts
- demonstrates cross-system causality rather than single-file undo

Candidate direction: software / support operations workflow spanning issue/task state plus repository or messaging state. Do not use real payments for the first integration.

### Week 4 - Buyer / partner validation

Prepare and execute owner-approved discovery.

Target:

- 10 qualified CTO / CISO / Head of Platform / Head of AI / security consultancy conversations
- 2 concrete pilot / assessment interests
- 1 channel partner signal from MSSP, AppSec, cloud-security or AI consultancy
- one pricing test for a bounded assessment

The engineering roadmap after day 30 must be conditioned on this evidence.

## Initial commercial offer

### Agent Recoverability Assessment

Scope: one bounded agent workflow.

Deliverables:

- write-capable tool and authority map
- Recovery Contract coverage
- recovery-readiness scorecard
- controlled incident suite
- containment and blast-radius evidence
- recovery / compensation results
- independent verification results
- replay / regression package
- irreversible residual-risk register
- prioritized remediation plan

### Pricing hypothesis

Treat pricing as a test, not a commitment.

Suggested design-partner range for the first few assessments: **EUR 1,500-3,000** for a tightly bounded workflow where access and scope are clean.

After credible proof and references, test higher four-figure pricing for broader assessments.

Do not build recurring subscription infrastructure until customers ask to keep the control plane running after the assessment.

## Build / buy / integrate rules

Integrate rather than rebuild:

- OpenTelemetry / existing observability for traces
- cloud / IAM policy systems for identity enforcement
- existing backup / snapshot systems for storage-level rollback
- SIEM / EDR / runtime security for detection signals

Build ourselves where differentiation lives:

- Recovery Contracts
- recovery evidence model
- cross-agent causal recovery graph
- recovery-path security
- dependency-aware recovery obligations
- independent verification binding
- incident-to-regression artifacts
- exact restoration logic
- recoverability metrics

## Kill criteria / pivot triggers

Do not keep investing only because the technology is interesting.

Reconsider the wedge if, after disciplined outreach:

- qualified buyers consistently call recovery interesting but non-budgeted
- no one will expose even a sandbox workflow for assessment
- customers prefer their existing backup / SOAR / runtime-security vendor to own recovery and see no reason for an independent layer
- direct competitors demonstrate a clearly superior cross-system verified-recovery product with distribution we cannot route around
- integration cost per workflow is too high for a repeatable assessment business

Possible pivot if demand exists but product placement is wrong:

- Recovery Readiness / CI as a developer tool
- partner-only assessment engine for security consultancies
- incident-to-regression testing product rather than always-on runtime

Do not pivot merely because large vendors enter adjacent agent security. Their entry also validates the budget category.

## Competition and grant policy

Competitions are secondary.

Enter only when at least one is true:

- meaningful non-dilutive funding
- customer / enterprise access
- strategic cloud credits
- credibility with the exact buyer
- little or no throwaway work

Use the product roadmap as the source of truth. Never build a separate competition architecture unless the commercial product itself needs the capability.
