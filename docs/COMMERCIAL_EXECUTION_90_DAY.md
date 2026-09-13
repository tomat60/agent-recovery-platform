# Agent Recovery Platform — 90-Day Commercial Execution Plan

Date: 2026-09-13

Status: post-competition commercial execution plan. Keep separate from the competition submission branch until owner review.

## Objective

Use the competition as a public proof point, then validate whether verified post-incident recovery for write-capable AI agents is a separately purchasable enterprise capability.

The first 90 days are not a race to build a large SaaS platform. They are a race to answer four questions with evidence:

1. Will a real buyer pay for agent recoverability work now?
2. Which workflows create the most painful recovery gap?
3. Which integrations are mandatory for a repeatable product?
4. Is the strongest business path consulting-to-product, licensing/OEM, or a strategic sale?

## Commercial wedge

Do not sell a generic AI security platform.

Sell one narrow outcome:

**When a write-capable agent has already changed real state, prove what happened, recover what is recoverable, preserve what is not, and determine which authority can safely return.**

Initial product category:

**AI Agent Incident Recovery / Agent Resilience Control Plane**

Core loop:

`contain -> reconstruct causality -> classify effects -> recover/compensate -> verify -> replay -> selectively restore`

## Why now

Public market signals show the category is moving quickly:

- Rubrik reported that 98% of surveyed businesses had experienced a disruptive agent-related incident and only 30% had robust, tested containment/reversal/recovery capability.
- Rubrik also reported 88% of surveyed organizations lacked the ability to roll back agent actions without system disruption.
- Palo Alto Networks acquired Portkey and positioned the AI Gateway as a mission-critical control plane for autonomous agents.
- Zenity raised $125M in 2026 to expand agent security and governance.
- WitnessAI raised $58M and reported rapid ARR growth in enterprise AI security.
- Temporal raised $300M at a $5B valuation around durable execution for reliable agentic systems.
- Restate and DBOS are expanding durable execution for agent workflows.

Interpretation:

The market already spends on prevention, identity, observability, governance and durable execution. The remaining opening is not generic safety. It is trustworthy recovery after harmful state-changing behavior has already occurred.

## Initial ICP order

### ICP 1 — AI-native SaaS with write-capable support or operations agents

Best first target.

Signals:
- agents modify CRM, tickets, shared memory, internal workflow state or customer data
- small enough engineering/security team to buy a focused external assessment
- already moving from pilots into production
- visible concern about rollback, incident response or governance

Likely buyers:
- VP Engineering
- Head of AI Platform
- Head of Security / CISO
- Staff/Principal Platform Engineer
- SRE / Reliability lead

Why first:
- shorter sales cycle than regulated enterprise
- real writable systems
- strong need for proof without a giant procurement process

### ICP 2 — Fintech / payments / financial workflow agents

High pain and high willingness to pay, but slower sales and greater compliance burden.

Focus only on owned/synthetic test environments until legal/security posture is mature.

### ICP 3 — Devtools / autonomous coding / deployment agents

Good fit because agents can alter code, infrastructure, CI/CD, configuration and secrets-adjacent systems.

Integration opportunity with GitHub, CI platforms, cloud change logs, Temporal/Restate and agent gateways.

### ICP 4 — Security vendors and AI infrastructure vendors

Treat primarily as partnership/OEM/acquisition candidates rather than first end customers.

Examples of strategic adjacency:
- Rubrik
- Palo Alto Networks / Prisma AIRS
- CyberArk / Idira
- Zenity
- Noma
- WitnessAI
- Temporal
- Restate
- cloud AI platforms

## First paid offer

### Agent Recoverability Assessment

Scope: exactly one write-capable agent workflow.

Target duration: 7-10 business days.

Deliverables:
- action / side-effect inventory
- recoverability classification for consequential writes
- Recovery Contract map
- synthetic incident fixture
- causal blast-radius reconstruction
- recovery and residual-risk report
- replay verification scenario
- restoration-gate recommendations
- prioritized remediation backlog
- executive one-page risk summary

The engagement must produce reusable product evidence, not a disposable PDF.

Every assessment should add anonymized structure to:
- Recovery Contract library
- side-effect taxonomy
- recovery failure taxonomy
- incident-to-regression templates
- integration requirements

### Pricing hypothesis

Founding-customer range:
- EUR 4k-10k for one bounded workflow

After 2-3 successful references:
- EUR 10k-25k per assessment

Do not discount below the level needed to learn whether the buyer values the outcome.

A free assessment is acceptable only when the design partner provides unusually valuable evidence, access or a public reference.

## Second offer

### Recovery Pilot

Duration: roughly 4-6 weeks.

Target price hypothesis:
- EUR 15k-50k depending on workflow and integration scope

Pilot objective:
- connect one real workflow to the recovery control plane
- capture represented side effects
- enforce recovery contracts for a small consequential write surface
- run at least one owned/synthetic incident
- produce replay-backed recovery evidence
- measure time to containment/recovery and residual truth

Do not promise arbitrary rollback or production-wide protection.

## Product packaging hypothesis

After repeated paid assessments reveal common integration patterns, package the recurring layer.

Likely product components:
- Recovery Contract registry
- action/side-effect evidence ingest
- causal incident graph
- containment adapters
- recovery executor adapters
- residual-risk ledger
- Replay Lab
- restoration gate
- recoverability score / control coverage
- incident-to-regression export

Initial annual contract hypothesis after real product proof:
- EUR 25k-100k ARR for smaller enterprise / growth customers
- higher enterprise pricing only after production evidence and support capability exist

Pricing should follow protected workflows / consequential write surface rather than raw token volume.

## Build vs integrate

Do not rebuild adjacent platforms.

Integrate with:
- agent frameworks: Strands, OpenAI Agents SDK, LangGraph and similar
- durable execution: Temporal, Restate, DBOS
- gateways/runtime controls: Portkey/Prisma AIRS class products
- identity: CyberArk/Idira class products
- storage/SaaS change surfaces: PostgreSQL, Salesforce/CRM, GitHub/CI, cloud configuration
- observability/security evidence sources

Our product should consume evidence and orchestrate recovery policy across these layers.

## 30-day plan after competition

Success target:
- 10 qualified buyer/partner conversations
- 2 concrete paid-assessment or pilot opportunities
- 1 serious security/infrastructure partner conversation

Execution:
- publish one strong technical launch narrative, not generic startup marketing
- build a 25-company target list
- identify exact Head of AI Platform / VP Eng / CISO / platform leads
- send evidence-led outreach around the recovery gap, not a product feature list
- offer a bounded Recoverability Assessment
- run discovery interviews against a fixed question set
- record objections and required integrations

Discovery questions:
- Which agents can mutate production state today?
- What is the current recovery procedure after an agent makes a harmful change?
- Can you attribute downstream changes to one agent action?
- Which effects are reversible, compensatable or irreversible?
- Who decides when authority is restored?
- Can you replay an incident safely before re-enabling the agent?
- What would a failed recovery cost operationally or commercially?
- Which current product is expected to solve this today?

Do not ask whether they like the idea. Ask how they handle the incident now and what it costs.

## 31-60 day plan

If no buyer is willing to pay after strong outreach, stop broad product building and reassess the category.

If one or more buyers engage:
- deliver first assessment
- convert the strongest repeated requirement into one product integration
- create anonymized before/after recovery evidence
- improve the benchmark from real workflow structure without exposing customer data
- ask explicitly for paid pilot conversion

Do not build multi-tenant enterprise SaaS yet.

## 61-90 day plan

Target state:
- 2-3 paid customers/assessments OR one meaningful paid pilot
- one repeatable integration pattern
- clear evidence of which buyer owns budget
- a decision between bootstrap/product, OEM/partnership, or strategic-sale exploration

If traction exists:
- package recurring control plane
- formalize security review and support boundaries
- start partner discussions with adjacent security / durable-execution vendors

If traction is weak:
- do not spend another year building in isolation
- test licensing or strategic-sale interest with the strongest technical proof

## Strategic buyer / partner path

Do not proactively sell the project cheaply before customer evidence exists.

A strategic buyer will value:
- working technical wedge
- customer pull
- recurring revenue or paid pilots
- proprietary incident/recovery dataset
- reusable integration adapters
- benchmark authority
- experienced domain team

Today we mainly have the technical wedge and evidence discipline.

Therefore the default plan is to create 3-6 months of commercial evidence before entertaining a full sale, unless an unusually strong inbound offer appears.

Potential strategic fit categories:
- cyber resilience / backup vendors
- AI security platforms
- identity/security control-plane vendors
- durable execution/orchestration vendors
- cloud AI platforms

## Moat plan

Code alone is not the moat.

Build compounding assets:

### Recovery Contract Library

Reusable schemas for consequential tools and state surfaces.

### Recovery Intelligence Dataset

Anonymized incident/recovery patterns:
- side-effect types
- causal structures
- failed compensation modes
- residual classes
- replay outcomes
- restoration decisions

### Incident-to-Regression Compiler

Convert an incident into a deterministic replay/regression scenario.

### Recoverability Benchmark

A credible standard for measuring whether an agent workflow is operationally recoverable.

### Integration graph

Adapters across agent runtimes, evidence sources, identity, durable execution and business systems.

## Kill criteria

Stop or materially pivot if after 90 days of disciplined outreach:
- no credible buyer will pay for assessment/pilot
- all target buyers believe existing backup/runtime/durable-execution products already solve the problem sufficiently
- required integrations make the product economically impossible for a small team
- buyers value only consulting with no repeatable product surface

Do not interpret polite interest as validation.

## Scale criteria

Invest more aggressively if:
- at least 2 customers pay for similar recoverability work
- one workflow pattern repeats across companies
- customers ask for continuous rather than one-off recovery control
- recovery evidence becomes a security/compliance requirement
- a partner wants an OEM or embedded recovery capability

## Founder operating constraint

Current team is one human founder plus AI assistance.

Therefore:
- keep implementation narrow
- automate evidence and QA aggressively
- avoid 24/7 production promises before support capacity exists
- sell fixed-scope assessments before enterprise-wide runtime commitments
- use partners for deep AppSec/cloud review before serious production pilots

## Public positioning

Primary line:

**Prevention failed. Prove what can safely come back.**

Supporting message:

Most agent-security products try to stop bad actions. Durable-execution systems help workflows resume after failures. Backup/rewind products reverse known changes. Agent Recovery Platform focuses on the incident between them: harmful state has already propagated, and the operator must recover the represented system and prove which authority is safe to restore.

## Source watchlist

Recheck monthly:
- Rubrik Agent Cloud / Agent Rewind
- Palo Alto Networks Prisma AIRS / AI Gateway / Idira
- Zenity
- Noma Security
- WitnessAI
- CyberArk
- Temporal
- Restate
- DBOS
- Toffoli and other open-source reversibility/recovery projects
- OWASP agent-security guidance and projects
- new academic work on transactional agents, compensation, rollback, replay and authority restoration

A market change is important only if it changes our wedge, buyer, benchmark, architecture or acquisition strategy.
