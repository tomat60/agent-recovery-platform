# Agent Recovery Platform — Real-Market Product Strategy

Date: 2026-09-13

Status: strategic working document on a separate branch. Competition submission remains the near-term delivery event, not the product's end state.

## Executive decision

Treat Agent Recovery Platform as a candidate commercial product in a rapidly forming enterprise category: **AI agent resilience, incident response, and verified recovery**.

Do not optimize the roadmap around winning one hackathon. The competition is useful as a forcing function for evidence, positioning, demo quality, and public proof. The product decision must instead answer a harder question:

> When a write-capable autonomous agent has already changed real state, how does an operator know what happened, contain the blast radius, recover what can be recovered, preserve what cannot, and prove which authority is safe to return?

The durable product wedge is not generic agent governance, not a prompt firewall, not agent observability, not checkpointing, and not a simple undo button.

The wedge is:

**verified post-incident recovery for state-changing AI agents and multi-agent systems.**

Core lifecycle:

`detect/trigger -> contain authority -> reconstruct causality -> classify side effects -> recover/compensate -> verify state -> replay the failure/attack -> selectively restore authority -> convert incident into regression evidence`

## Why the market is real

The market is moving quickly from "secure the model" to "control what autonomous software actually does."

Public market signals as of September 2026:

- Gartner forecasts the market for securing AI to reach about $4.8B in 2027, up 68.7% from 2026, and about $7.7B in 2028.
- Cloud Security Alliance reported that 65% of surveyed enterprises had experienced AI-agent-related incidents in the prior 12 months, with reported data exposure, operational disruption, and financial loss.
- A separate CSA study reported 53% of organizations had seen AI agents exceed intended permissions and 47% had experienced an AI-agent security incident.
- Zenity announced a $125M Series C in August 2026.
- Noma Security raised a $100M Series B and reported rapid ARR growth and production enterprise customers.
- WitnessAI raised $58M to expand enterprise AI security and agentic governance.
- Palo Alto Networks acquired Portkey to make the AI Gateway a central control plane for autonomous agents.
- Rubrik has expanded aggressively into Agent Cloud / Agent Rewind and explicitly markets agent rollback and cyber resilience as part of the AI enterprise stack.
- Rewind Software received a strategic growth investment while explicitly positioning AI-driven SaaS changes as a new rollback/recovery problem.

These signals do not prove that our exact product thesis wins. They do establish that enterprises are spending heavily on AI-agent control, security, resilience, and recovery.

## Market map

The market is not one category. It is at least six adjacent layers.

### 1. Discovery, posture, identity and access

Representative vendors:
- CyberArk
- Astrix
- Noma
- Zenity
- Prisma AIRS / Palo Alto Networks
- WitnessAI

Primary job:
- discover agents, MCP servers, skills and identities
- understand privileges and ownership
- enforce least privilege and access policy

This is adjacent to us, not our initial category.

### 2. Runtime prevention and enforcement

Representative vendors:
- Zenity
- Noma AI-DR
- WitnessAI Agentic Control
- Prisma AIRS
- HiddenLayer
- containment.ai

Primary job:
- inspect agent behavior, prompts, tool calls and context
- block dangerous actions before impact
- enforce policy at the action boundary

These systems answer: **should this action execute?**

Our system should integrate with these controls and consume their evidence rather than compete with them head-on.

### 3. Observability, tracing and debugging

Representative technologies:
- LangSmith / LangGraph
- Arize/Phoenix and similar LLM observability stacks
- provider-native traces
- AI runtime platforms

Primary job:
- reconstruct what the agent did
- debug trajectories
- replay or fork model/workflow executions

Observability is necessary evidence, but observation alone is not recovery.

### 4. Durable execution and crash recovery

Representative technologies:
- Temporal
- Restate
- DBOS
- LangGraph persistence/checkpoints
- Crab (research on semantics-aware checkpoint/restore for agent sandboxes)

Primary job:
- survive infrastructure/process failures
- resume workflows without duplicating side effects
- checkpoint agent or workflow state
- support pause/resume, retries and workflow compensation

These systems answer: **how do we keep an agent/workflow running correctly through infrastructure failure?**

Our question is different: **what if execution completed, but the agent made harmful or compromised decisions and changed external state?**

Durable execution should become an integration/primitive, not a competitor we rebuild.

### 5. Undo, rewind and compensation

Representative products/projects:
- Rubrik Agent Rewind / Agent Cloud
- Rewind AI Resilience
- Toffoli
- Moholo Agent Rewind
- Agit
- Walkback
- RAC research
- transactional/compensation research such as Atomix and Mnemosyne

Primary job:
- record actions
- snapshot or preserve before-state
- undo reversible actions
- run compensating actions
- report irreversible remainder

This is our closest adjacent category.

Do not claim that reversibility, compensation, rollback or agent rewind are unique ideas.

### 6. AI-agent incident response and verified recovery

This category is forming but still fragmented.

Public guidance increasingly describes agent incidents as requiring:
- containment of authority
- preservation of evidence
- reconstruction of action chains
- recovery of external state
- downstream impact analysis
- explicit treatment of irreversible effects
- controlled re-enablement

Our product should deliberately own this layer.

## Closest competitive systems

### Rubrik Agent Cloud / Agent Rewind

Why it matters:
- strongest commercial validation that agent rollback and resilience are valuable
- major enterprise distribution, security credibility, immutable backup roots, integrations
- explicit prompt-to-action auditability and rewind

Where they are stronger:
- production maturity
- enterprise integrations
- backup/restore infrastructure
- distribution and trust

Where our wedge can remain different:
- cross-agent causal reconstruction as a first-class recovery primitive
- explicit incident-scoped containment holds
- recovery-path security
- adversarial replay before re-enablement
- evidence-gated selective authority restoration
- framework/provider-neutral recoverability assessment

Do not position against Rubrik as "better backup." That would be strategically weak.

### Rewind AI Resilience

Why it matters:
- highly adjacent commercial framing: guardrails are not a recovery plan
- cross-SaaS blast radius and recovery is explicitly part of the product story

Implication:
- the real market is moving toward recovery as an independent control plane
- generic "undo" is not enough differentiation

### Toffoli

Why it matters:
- strongest open-source technical reference for reversibility / compensability / irreversibility
- action classification, restitution plan, human escalation, receipts and evaluation

Where our wedge differs:
- multi-agent and shared-state incident reconstruction
- containment and authority lifecycle
- replay-driven restoration proof
- recovery integrity under stale/cross-incident authority and poisoned recovery paths

Treat Toffoli as a benchmark for honesty and recovery receipts, not as code to copy.

### Moholo Agent Rewind

Why it matters:
- strong operator UX: timeline, kill switch, per-action Undo, point-in-time Rewind, blast-radius holds
- honest reporting when external effects are not reversible

Implication:
- our future operator UX must be equally legible
- "what changed / what was undone / what remains" should be visible without reading a security paper

### Runtime-security vendors

Zenity, Noma, WitnessAI, Palo Alto Networks, HiddenLayer and containment.ai increasingly own pre-execution/runtime enforcement.

Implication:
- do not attempt to outbuild a generic runtime firewall
- make their signals inputs to recovery
- product should be valuable even when prevention fails despite those systems

## Strategic positioning

### Category statement

**Agent Recovery Platform is the incident recovery and safe reactivation layer for write-capable AI agents.**

### One-line problem

Guardrails can stop the next action. They do not repair the actions that already happened.

### One-line value

Recover what is recoverable, prove what was repaired, preserve what was not, and restore only authority supported by current evidence.

### What we should not say

Avoid:
- "the first undo button for AI agents"
- "the only agent recovery platform"
- "we solve AI security"
- "we can roll back any agent action"
- "production-grade security" until independently demonstrated

These claims are either false, undefended, or strategically too broad.

## Product architecture direction

Long-term architecture should become a control layer around existing agent and enterprise systems rather than a new agent framework.

### Evidence intake

Adapters should ingest:
- OpenTelemetry / agent traces
- MCP/tool-call records
- framework traces from Strands, LangGraph, OpenAI Agents SDK, etc.
- identity/authorization events
- SaaS/database audit logs
- runtime-security alerts
- durable workflow journals from Temporal/Restate/DBOS where available

### Recovery Contract Registry

For every consequential tool/action:
- side-effect type
- resource identity
- before-state evidence requirements
- reversibility class
- compensator
- verifier
- idempotency behavior
- approval requirements
- dependency semantics

This is a potentially defensible schema/product surface if kept framework-neutral and validated through real integrations.

### Action + Side-Effect Ledger

Production direction:
- durable append-only evidence storage
- externally anchored head/length or authenticated event source
- explicit provenance
- adapter identity/version
- source action and resource binding

Do not pretend the current local hash chain is sufficient for enterprise trust.

### Causal Recovery Graph

This should become one of the primary differentiated assets.

The graph should connect:
- triggering inputs
- model/agent decisions
- tool calls
- resource mutations
- delegated identities
- shared-state writers
- downstream agents
- external effects

The goal is not only blast-radius display. The graph should drive dependency-safe recovery and determine which authority can be restored.

### Recovery Engine

Must remain deterministic and policy-bound.

LLMs may:
- investigate
- propose plans
- summarize evidence
- challenge assumptions

LLMs must not:
- declare recovery success
- issue their own recovery authority
- define verification targets
- erase residual risk
- restore authority

### Replay / Verification Lab

Long-term versions should support multiple replay modes:
- exact represented action replay
- deterministic mock/sandbox replay
- production-like staging replay
- regression replay from historical incidents

Replay should explicitly report environment equivalence rather than imply it.

### Restoration Gate

This is a major differentiation point.

Recovery is not complete until the platform can answer:
- what obligations are complete?
- what residuals remain?
- what evidence is current?
- what policy would exist after release?
- which exact authority is safe to restore?

## Buyer and beachhead

Do not start with "all enterprises using agents."

Initial ICP:
- AI-native SaaS / developer-tool / fintech / security company
- already running at least one write-capable agent in production or late-stage pilot
- agent touches a database, CRM, repository, ticketing system, identity, messaging or workflow system
- small platform/security/SRE team
- high cost of a silent bad write
- enough engineering maturity to expose traces and tool boundaries

Avoid as first customer:
- chatbot-only organizations
- companies with no write-capable agents
- highly regulated enterprises requiring years of procurement before a pilot
- teams that only need prompt filtering

## Initial commercial offer

Sell the problem before selling a large platform.

### Agent Recoverability Assessment

A bounded 2–4 week engagement for one real workflow.

Outputs:
- inventory of side-effecting actions
- recoverability coverage score
- irreversible-effect map
- evidence gaps
- blast-radius reconstruction readiness
- top recovery integrity risks
- synthetic incident drill
- recovery plan / integration roadmap
- optional prototype adapter for one critical tool

Why this is a good first offer:
- can be sold before multi-tenant SaaS is complete
- produces real customer evidence
- reveals connector priorities
- generates benchmark/data assets
- creates a natural path to a pilot

## Pricing hypothesis

Do not lock pricing yet.

Test willingness to pay through interviews and pilots.

Working hypotheses:
- assessment: low five figures USD for a serious AI-native company
- pilot: higher five figures depending on integrations and scope
- product later: platform fee + number of protected agent workflows / consequential actions / connected systems rather than token-based pricing

The goal of the first 10 conversations is not to defend a price list. It is to identify which recovery failure is expensive enough that a team will fund remediation now.

## Moat strategy

The code itself will not be enough.

Potential defensibility:

### 1. Recovery Contract ecosystem

A maintained library of verified recovery semantics for real tools and enterprise systems.

### 2. Recovery Intelligence Dataset

De-identified / synthetic / consented corpus of:
- agent incident graphs
- side-effect classes
- failed recovery attempts
- compensation patterns
- residual effects
- replay failures
- restoration decisions

This can power better assessments, benchmarks and future automated planning without making LLM output the authority.

### 3. Incident-to-regression compiler

Turn real incidents into repeatable tests and replay fixtures.

This creates compounding customer value: every incident improves future resilience.

### 4. Recoverability benchmark

A credible framework-neutral score for whether a write-capable agent system can be safely recovered.

Potential metrics:
- side-effect coverage
- preserved before-state coverage
- dependency completeness
- compensation correctness
- residual-truth accuracy
- replay success/failure
- safe-restoration coverage
- mean verified recovery time

### 5. Integration position

If the platform becomes the layer that receives evidence from runtime security and durable execution systems, but owns recovery and reactivation, replacement cost increases.

## Build vs integrate

Build:
- recovery contracts
- causal recovery graph
- recovery integrity
- residual truth
- replay evidence binding
- restoration gate
- recoverability assessment / score

Integrate:
- runtime threat detection
- broad agent discovery
- identity governance
- durable workflow execution
- generic tracing/observability
- data backup infrastructure
- SIEM/SOAR

This boundary is strategically important. Rebuilding Palo Alto, Zenity, Noma, Temporal or Rubrik would kill the company before product-market fit.

## 30-day post-competition plan

### Week 1
- freeze competition build as public proof
- publish one technically serious architecture/recovery article
- create a customer-facing 10-slide assessment deck
- define one assessment worksheet and sample report
- shortlist 25 AI-native companies with write-capable agents

### Week 2
- run 5–8 discovery calls with platform/security/SRE leaders
- ask for real failure stories, not opinions about the product
- identify top three side-effect surfaces (likely code/repos, SaaS records, databases/permissions)

### Week 3
- secure one design partner or unpaid/low-cost assessment if necessary
- implement only the connector needed by that workflow
- run one synthetic recovery drill using customer-shaped architecture without customer secrets

### Week 4
- convert evidence into a paid pilot proposal
- revise category/positioning based on what buyers actually pay to fix
- decide whether to raise, bootstrap, partner with MSSP/consultancy, or continue design-partner development

Target outcome after 30 days:
- 10 qualified conversations
- 2 concrete assessment/pilot interests
- 1 design partner
- 1 validated expensive recovery problem

## Kill criteria / strategic honesty

Do not continue indefinitely because the technology is interesting.

Reassess the thesis if:
- buyers consistently say existing backup/rewind products solve the problem adequately
- write-capable agent deployments remain too immature to create budget
- customers refuse instrumentation needed for causal recovery
- the recovery problem is owned entirely by existing workflow/database vendors
- 10–15 qualified buyer conversations produce no urgent pain and no pilot willingness

If that happens, pivot toward the highest-value proven component, likely Recoverability Assessment, recovery-contract tooling, or incident-to-regression testing.

## Sources reviewed in this update

Commercial / enterprise:
- Rubrik Agent Cloud / Agent Rewind: https://www.rubrik.com/products/rubrik-agent-cloud
- Rubrik Agent Rewind: https://www.rubrik.com/products/agent-rewind
- Rewind AI Resilience: https://rewind.com/ai-resilience/
- Zenity: https://zenity.io/
- Noma Security: https://noma.security/
- WitnessAI: https://witness.ai/
- Palo Alto Networks Prisma AIRS: https://www.paloaltonetworks.com/ai-security/prisma-airs
- HiddenLayer: https://www.hiddenlayer.com/platform/ai-runtime-security
- containment.ai: https://www.containment.ai/
- Astrix agent security: https://astrix.security/product/secure-ai-agents/
- CyberArk agent/identity research: https://www.cyberark.com/resources/blog/will-ai-agents-get-real-in-2026

Durability / checkpointing:
- Temporal: https://docs.temporal.io/
- Restate durable agents: https://docs.restate.dev/ai/patterns/durable-agents
- DBOS AI durable workflows: https://docs.dbos.dev/ai/ai-quickstart
- LangGraph persistence/time travel: https://docs.langchain.com/oss/python/langgraph/persistence
- Crab checkpoint/restore paper: https://arxiv.org/abs/2604.28138

Recovery / open-source / research:
- Toffoli: https://github.com/theo-ai-lab/toffoli
- Moholo Agent Rewind: https://github.com/moholo-founder/agent-rewind
- existing references in `docs/COMPETITIVE_LANDSCAPE.md`

Market evidence:
- Gartner AI security forecast: https://www.gartner.com/en/newsroom/press-releases/2026-08-26-gartner-forecasts-the-market-for-securing-ai-will-reach-almost-5-billion-in-2027
- CSA survey on unknown agents / incidents: https://cloudsecurityalliance.org/press-releases/2026/04/21/new-cloud-security-alliance-survey-reveals-82-of-enterprises-have-unknown-ai-agents-in-their-environments
- CSA survey on scope violations: https://cloudsecurityalliance.org/press-releases/2026/04/16/more-than-half-of-organizations-experience-ai-agent-scope-violations-cloud-security-alliance-study-finds

## Current conclusion

The category is more commercially credible than it was when the project started, but the competitive bar is much higher.

The opportunity is not to become another AI guardrail company.

The opportunity is to become the **recovery and safe-reactivation control layer that starts working after guardrails fail**.

That thesis is strong enough to justify post-competition customer discovery and a real pilot attempt.