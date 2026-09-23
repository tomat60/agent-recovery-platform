# Design Partner Pipeline

Date: 2026-09-23

This is an active research/outreach pipeline. External sending remains owner-gated. Legal commitments, spend, production access/data and binding terms remain gated.

## Qualification rubric

Score 0–2 on each:
- real write-capable agent/tool execution;
- multi-system side effects;
- platform/security budget and owner;
- recoverability pain is visible now;
- practical sandbox/design-partner path.

10/10 is strongest. 7+ is worth immediate qualification.

## Ranked design-partner send list

Every promoted target below has current public evidence of consequential agent/tool execution or production-agent infrastructure. Ranking reflects fit for a bounded Agent Recoverability Assessment, not inferred buying intent.

| Rank | Organization | Score | Current evidence | Likely buyer role | Pain hypothesis | Personalized opening line | Disqualifier |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| 1 | Composio | 10 | Managed auth and agent tool execution across 1,500+ apps creates a high-density write boundary. | Platform / security / partnerships lead | A failed cross-app agent action can leave several external systems in inconsistent state even when auth and execution are well controlled. | You already own the tool-execution boundary; we are testing whether Recovery Contracts plus verified compensation can make that boundary measurably recoverable after consequential writes. | Native verified cross-system compensation/replay already covers the same lifecycle. |
| 2 | n8n | 10 | AI-agent workflows can execute multi-step business automations across connected services. | Product security / AI platform / partnerships lead | Workflow retries and node-level error handling do not by themselves prove that already-completed side effects were safely compensated and replayed. | We want to test a two-surface n8n workflow where recovery evidence, not a successful rerun, decides whether authority can be restored. | Existing product already provides dependency-aware verified compensation and residual-risk truth for agent writes. |
| 3 | LangChain / LangSmith | 9 | Production agent deployment emphasizes durable execution, rollbacks, human-in-the-loop and governance. | LangSmith product / platform / partnerships lead | Runtime durability and trace visibility can show what happened without independently proving external side effects were compensated and safe scope restored. | LangSmith already has the trace/runtime context; our question is whether that evidence can drive independent recoverability assurance and verified restoration. | Roadmap already owns full external-effect recovery verification as a first-class control plane. |
| 4 | Pipedream | 9 | Connect exposes 10,000+ tools across 3,000+ APIs with managed auth; Conduit adds policy, audit and OTel export at the agent/tool boundary. | Connect/Conduit product or security lead | Centralized auth, policy and audit increase control but also make the boundary an ideal place to declare and verify recovery contracts for consequential writes. | Your gateway can see and authorize the tool call; we are testing the missing post-incident question: which external effects were actually recovered, which remain residual, and what exact authority is safe to restore? | Conduit/Connect already verifies cross-API compensation outcomes and scope-bound restoration. |
| 5 | Dust | 8 | Enterprise agents connect to company tools and act across governed workflows. | Security / platform / enterprise product lead | Enterprise governance can contain an agent but may not prove downstream shared-state recovery after a bad action sequence. | We are looking for one bounded enterprise-agent workflow where containment is only the first step and restoration requires current recovery evidence. | No consequential write-capable workflows or no sandboxable design-partner path. |
| 6 | Braintrust | 8 | Production traces can be converted directly into eval datasets and regression tests; platform is framework-agnostic. | Product / agent platform / partnerships lead | Incident-to-regression is strong, but regression success does not prove external side effects from the original incident were compensated before authority returns. | Braintrust already turns failures into regression assets; we want to connect that loop to verified recovery evidence and selective restoration. | Product scope intentionally excludes runtime/write-boundary integrations and customers show no recovery need. |
| 7 | Arize | 8 | Agent observability traces actions/tool use on OpenInference/OpenTelemetry and supports production eval/debug workflows. | Product / integrations / AI platform lead | Rich causal traces are valuable recovery evidence, but observability alone does not execute or verify compensation and restoration. | OpenInference gives us a standards-aligned evidence source; we want to test whether it can feed a recovery assessment without duplicating observability. | Recovery/compensation is already a productized Arize capability or no interest beyond observability. |
| 8 | CrewAI | 8 | Enterprise agent runtime/governance makes coordinated production agent workflows a natural shared-state recovery surface. | Enterprise platform / security / partnerships lead | Multi-agent coordination increases causal ambiguity when several agents touch shared state or external systems. | We want to test recoverability at the fleet boundary: reconstruct the causal chain, compensate what can be compensated, and restore only verified-safe scope. | Enterprise workflows are primarily read-only or lack a bounded sandbox path. |
| 9 | Langfuse | 7 | Framework-neutral tracing/evals cover tool invocation and production agent behavior. | Product / integrations / partnerships lead | Trace evidence can seed causal reconstruction and replay, while verified compensation remains outside the observability layer. | We would keep Langfuse as the evidence source and test a narrow recoverability layer above it rather than competing on tracing. | Users have little consequential-write exposure or partnership would require duplicating tracing. |
| 10 | LlamaIndex | 7 | LlamaIndex supports end-to-end document agents and enterprise agent pipelines that can reason and act. | Platform / enterprise product lead | Document-agent workflows can produce downstream writes whose recovery requirements are not captured by document parsing or retrieval quality. | We want to qualify one write-capable document-agent workflow for recovery-contract coverage and controlled incident replay. | Current commercial workflows are overwhelmingly parse/read-only or no consequential action boundary is available. |

### Source anchors verified 2026-09-23

- Pipedream official product page: managed auth, 10,000+ tools, 3,000+ APIs, tool execution and API proxy for agents; Conduit adds access policy, audit trail and OpenTelemetry export.
- Braintrust official product page: production traces can become eval datasets/regression tests and the platform is framework-agnostic.
- Arize official product page: end-to-end agent observability/evaluation, OpenInference/OpenTelemetry, production tool/action tracing.
- LlamaIndex official product page: end-to-end document agents and enterprise agent pipelines.
- Previously verified anchors remain valid for Composio, LangSmith, CrewAI, Dust and Langfuse.

Public product evidence validates qualification only; it does not imply interest, budget, or consent to contact.

## Warsaw Tech Week / CYBER SECURITY Expo Poland 2026

Paweł visited the event on 2026-09-23. Treat booth presence as a warm contextual signal, not proof of product fit.

| Organization | Role in our strategy | Evidence / rationale | Current action |
| --- | --- | --- | --- |
| Saugumo operacijų centras / SOC Factory (Lithuania) | Channel/design-partner candidate | Small vCISO/SOC provider with DORA/NIS2 work and technical leadership. Complementary to agent recoverability rather than directly competitive. | Existing outreach thread; await response. |
| Konsorcjum FEN | Polish channel / VAD candidate | VAD model, presales engineering, co-selling, demos, partner enablement and security portfolio. | Existing outreach thread; no duplicate same-day message. |
| Acronis | Strategic platform / integration candidate and long-term adjacent threat | Data/infrastructure recovery, MSP channel and integration ecosystem. Our wedge is agent-action recoverability above workload/data restore. | Routing remains owner-gated where terms are required. |
| Cynet | Adjacent competitor / possible integration route | AI-powered XDR/MDR automates threat detection and response. | Monitor before contact; qualify partnership vs disclosure risk. |
| FUDO Security | Strategic adjacent vendor / integration candidate | Privileged access/session control complements exact authority containment/restoration. | Existing outreach thread; await response. |

## Initial channel / strategic partner classes

Prioritize five after research:
1. AI-security vendors that detect or govern agents but do not own verified cross-system recovery.
2. AppSec / cloud-security consultancies already selling AI assessments.
3. Agent observability/eval vendors where our recovery evidence complements traces.
4. Tool-integration / MCP infrastructure vendors exposed to consequential writes.
5. Cloud/agent platforms that need a deployment-readiness and recovery assurance layer.

## Evidence required before promotion

For every target promoted to the send-list, keep:
- current product/use case proving write-capable agents or consequential tool execution;
- likely buyer role;
- concrete pain hypothesis;
- why existing product stack does not obviously solve verified recovery;
- one relevant public source;
- one personalized opening line;
- disqualifier if discovered.

## Outreach response tracking — 2026-09-23

Existing threads: FEN, Acronis routing, SOC Factory, FUDO Security, Composio and LangChain/LangSmith. Do not chase same-day. External sending remains owner-gated under the current steward policy; research and drafts may continue autonomously.
