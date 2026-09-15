# Competitive Radar — 2026-09-15

## Executive conclusion

The market signal is stronger than it was one week ago, but the category is becoming crowded quickly.

Continue Agent Recovery Platform.

Do **not** compete as a generic agent-security, agent-observability or undo product. The strongest path is to own the harder recovery lifecycle:

**cross-agent / cross-system incident -> containment -> evidence -> dependency-aware recovery -> replay/regression -> verified selective restoration**

The biggest near-term risk is commercial validation, not lack of engineering sophistication.

## Market validation

### NIST: agent security is now a standards problem

NIST / CAISI has explicitly identified AI agents as systems that autonomously act on real systems and has called out indirect prompt injection, poisoned models, harmful autonomous behavior, identity, authorization, auditing and non-repudiation as distinct security concerns.

Sources:
- https://www.nist.gov/news-events/news/2026/01/caisi-issues-request-information-about-securing-ai-agent-systems
- https://www.nist.gov/publications/summary-analysis-responses-request-information-regarding-security-considerations-ai
- https://www.nist.gov/news-events/news/2026/02/announcing-ai-agent-standards-initiative-interoperable-and-secure
- https://www.nist.gov/news-events/news/2026/02/new-concept-paper-identity-and-authority-software-agents

Implication:
- agent control is moving from niche research into enterprise standards and procurement language
- our evidence, authority and recovery boundaries should map cleanly to emerging standards without claiming conformance prematurely

### OWASP: failures now map directly to our benchmark assumptions

The OWASP Top 10 for Agentic Applications and related guidance explicitly call out:
- goal hijacking
- tool misuse
- identity / privilege abuse
- memory / context poisoning
- insecure inter-agent communication
- cascading failures
- rogue agents

Sources:
- https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/
- https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html
- https://genai.owasp.org/2026/09/01/owasp-genai-security-project-unveils-2026-top-10-for-llm-applications-new-agent-control-standard-and-sponsors-as-community-tops-30000-members/

Implication:
- our multi-agent cascade, memory poisoning, tool misuse and authority-resurrection tests are aligned with recognized real risks
- avoid building generic prevention controls already covered by a large ecosystem
- use these categories as external vocabulary for assessment findings and benchmark mapping

## Direct recovery competitors

### Rubrik Agent Cloud / Agent Rewind

Rubrik now positions Agent Cloud around visibility, governance and the ability to undo unwanted/destructive agent changes. Agent Rewind markets immutable audit trails, causal visibility and selective rollback of files, data, configurations and code.

Sources:
- https://www.rubrik.com/products/agent-rewind
- https://www.rubrik.com/products/rubrik-agent-cloud

Threat level: **very high adjacent/direct**.

Do not fight Rubrik on:
- enterprise backup
- snapshot infrastructure
- generic selective rollback
- distribution into existing large accounts

Our required differentiation:
- framework-neutral recovery above storage boundaries
- explicit external side-effect classes and compensation
- cross-agent shared-state causality
- recovery-path integrity
- replay / regression before restoration
- exact authority restoration rather than merely restoring data

### Toffoli

Toffoli describes itself as the recovery half the industry skipped. It classifies actions as reversible / compensable / irreversible, creates restitution plans, escalates irreversibility and keeps a deterministic-first boundary around LLM assistance.

Sources:
- https://github.com/theo-ai-lab/toffoli
- https://github.com/theo-ai-lab/toffoli/blob/main/README.md

Threat level: **high conceptual / open-source**.

Important lesson:
- reversibility taxonomy is not our moat
- deterministic-first recovery is table stakes
- Toffoli's public framing validates recovery as a distinct product category

Defensible space for us:
- cross-agent / shared-state recovery
- stronger restoration semantics
- recovery-path security under adversarial conditions
- incident-to-regression and replay-bound restoration

### KavachIQ Agentic Incident Recovery

KavachIQ is explicitly positioning an agent incident recovery layer for Microsoft 365, with attribution, blast-radius mapping, operator-approved dependency-ordered reversal and validation.

Sources:
- https://agents.kavachiq.com/
- https://github.com/gpatwa/autonomous-assurance

Threat level: **high vertical proof that the niche is real**.

Implication:
- do not race into Microsoft 365 as our first vertical
- vertical specialization can be a distribution strategy later, but our current advantage should remain cross-system and framework-neutral

### Moholo Agent Rewind

Public project positioning: flight recorder + undo button, MCP interception proxy, journal, snapshots, policy gate, kill switch and rewind.

Source:
- https://github.com/moholo-founder/agent-rewind

Threat level: **medium-high open-source / MCP**.

Implication:
- MCP interception is useful as an adapter, not a category
- do not spend product identity on building another proxy / journal / kill switch

### AgentOptics Rewind

AgentOptics Rewind focuses on time-travel debugging, trace import, fork/replay, diff, evaluation, regression testing and proving code/prompt fixes without replaying the entire prior chain.

Source:
- https://github.com/agentoptics/rewind

Threat level: **medium adjacent developer tool**.

Implication:
- its trace import and OTel/Langfuse interoperability is a pattern worth learning from
- our product should interoperate with observability and debugging tools rather than rebuilding them
- our value begins where model/debug replay ends and real side effects, compensation, containment and authority restoration begin

## Runtime / governance competitors

### HiddenLayer

HiddenLayer is expanding Agentic Runtime Security around visibility, investigation/threat hunting and detection/enforcement and announced a $100M Series B in September 2026.

Sources:
- https://www.hiddenlayer.com/news/hiddenlayer-unveils-new-agentic-runtime-security-capabilities-for-securing-autonomous-ai-execution
- https://www.hiddenlayer.com/news/hiddenlayer-100m-series-b-ai-security

### Geordie AI

Geordie markets a security/governance platform for enterprise AI agents and announced a $30M Series A in May 2026.

Source:
- https://www.geordie.ai/resources/geordie-raises-30m-to-help-enterprises-securely-adopt-agentic-ai-at-scale/

### NeuralTrust

NeuralTrust announced a $20M seed round focused on securing AI agents as enterprise adoption grows.

Source:
- https://neuraltrust.ai/news/neuraltrust-raises-20m

### Zenity

Zenity offers agent security/governance with runtime inline protection and policy enforcement, including Microsoft Foundry agents.

Sources:
- https://zenity.io/platform
- https://zenity.io/company-overview/newsroom/company-news/zenity-announces-availability-of-inline-agent-runtime-security-for-agents-built-on-microsoft

### Astrix

Astrix focuses on discovery/governance, agent/non-human identity lifecycle, access controls and threat detection/response.

Source:
- https://astrix.security/product/secure-ai-agents/

### AIR

AIR emerged from stealth with $50M raised to discover agents and continuously vet the skills, plug-ins, MCP servers and add-ons they use.

Source:
- https://techcrunch.com/2026/09/01/air-raises-50m-to-help-companies-vet-the-skills-and-add-ons-ai-agents-use/

Implication across this group:
- discovery, identity, runtime policy, supply-chain vetting and prevention are becoming well-funded crowded layers
- do not broaden sideways into their category
- integrate their alerts and evidence later as incident triggers
- own what happens after a harmful action crosses the preventive boundary

## Major platform direction

### AWS AgentCore

AgentCore is adding increasingly complete IAM, resource policy, identity and harness primitives. This strengthens the case for treating cloud authorization as an integration layer rather than our proprietary identity product.

Sources:
- https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/security_iam_service-with-iam.html
- https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-security.html

### Salesforce

Salesforce has announced an Enterprise AI Harness / AI Control Plane direction covering agent discovery, policy, monitoring, governance and cost control across enterprise systems.

Implication:
- broad control planes will be native platform features
- independent products need a specialized hard outcome, not generic agent governance

## Strategic white space

### 1. Recovery Readiness as a developer and services wedge

A Recovery Contract / CI check can answer whether a write-capable action has a real recovery path before production.

This is close enough to the core engine to be cheap to build, supports paid assessments and can create product adoption before a customer experiences an incident.

Do not turn it into a general agent vulnerability scanner.

### 2. Cross-system recovery above backup boundaries

A database snapshot cannot unsend a message, revoke an external entitlement, unwind a SaaS workflow, compensate a payment, clean poisoned memory and reason about delegated authority in one incident.

The product should model these as explicit side effects and obligations rather than pretending one rollback primitive solves them.

### 3. Incident-to-regression as a differentiated output

The market is filling with detection and undo. A stronger answer is:

> every accepted incident becomes a deterministic regression and restoration proof.

This makes recovery improve the system rather than only repair one incident.

### 4. Verified restoration as a separate security boundary

Stopping or recovering an agent does not prove it should regain authority.

Keep restoration separate and evidence-bound:
- exact incident
- exact scope
- current recovery generation
- current contract versions
- residual-risk state
- replay/regression evidence
- explicit human policy where required

This is one of the most defensible parts of the existing architecture and should remain first-class.

## What not to build now

- generic agent discovery
- generic MCP scanner
- broad runtime policy engine
- generic kill switch
- generic trace viewer
- backup/snapshot engine
- enterprise IAM
- broad compliance dashboard
- dozens of connectors
- LLM-only autonomous recovery

## Commercial conclusion

**GO, with discipline.**

The project is in a promising market at the right time, but the window will not stay empty. We already have stronger security/recovery semantics than a normal hackathon prototype; the next advantage must come from productization, one realistic integration, measurable recoverability and buyer evidence.

The recommended bet is not to add a flashy adjacent feature. It is to turn the existing hard recovery core into a product lifecycle competitors cannot trivially copy as one checkbox:

**Recovery Readiness -> Runtime Evidence -> Verified Recovery -> Incident-to-Regression -> Selective Restoration.**
