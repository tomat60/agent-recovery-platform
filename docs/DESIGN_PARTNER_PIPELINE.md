# Design Partner Pipeline

Date: 2026-09-23

This is an active research/outreach pipeline. Paweł has authorized low-volume, evidence-based outreach waves from `hello@paweltomczak.com`. Legal commitments, spend, production access/data and binding terms remain gated.

## Qualification rubric

Score 0–2 on each:
- real write-capable agent/tool execution;
- multi-system side effects;
- platform/security budget and owner;
- recoverability pain is visible now;
- practical sandbox/design-partner path.

10/10 is strongest. 7+ is worth immediate qualification.

## First research candidates

| Organization | Why it is strategically relevant | Likely angle | Status |
| --- | --- | --- | --- |
| Dust | Enterprise agents act across connected company tools; explicit governance/audit positioning | Design-partner discussion around cross-tool recoverability and controlled incident proof | Research |
| LangChain / LangSmith | Production agent deployment, durable runtime, rollbacks, HIL and governance | Partner/integration angle: independent recoverability assurance on top of agent runtime | Research |
| CrewAI | Enterprise agent build/runtime with centrally governed production workflows | Design-partner or platform-partner angle around recovery readiness for governed agent fleets | Research |
| Composio | Agents execute tools across 1,500+ apps with managed auth | High-fit tool-boundary integration / strategic partner: recovery contracts around real side effects | Research |
| Arize | Agent observability/evaluation and open tracing standards | Partner angle: convert traces/evals into recoverability evidence rather than competing on observability | Research |
| Langfuse | Open-source tracing/evals for agent production loops | OTel/evidence integration and incident-to-regression partner angle | Research |
| Braintrust | Agent eval/observability with multi-step tool execution focus | Assessment/eval complement: consequences and recovery verification after failed action sequences | Research |
| LlamaIndex | Agent/data framework used for enterprise agent applications | Recovery Readiness integration candidate | Verify |
| n8n | Workflow automation plus AI-agent execution across business systems | Strong multi-surface sandbox/design-partner candidate | Verify |
| Pipedream | Tool/API execution infrastructure used by AI workflows | Tool-boundary recovery/compensation integration candidate | Verify |

## Warsaw Tech Week / CYBER SECURITY Expo Poland 2026

Paweł visited the event on 2026-09-23. Treat booth presence as a warm contextual signal, not proof of product fit.

| Organization | Role in our strategy | Evidence / rationale | Current action |
| --- | --- | --- | --- |
| Saugumo operacijų centras / SOC Factory (Lithuania) | Channel/design-partner candidate | Small vCISO/SOC provider with 60+ Lithuanian clients, DORA/NIS2 work and technical leadership. Complementary to agent recoverability rather than directly competitive. | Outreach sent 2026-09-23 to info@saugumovadovas.lt asking for technology/partnership owner. |
| Konsorcjum FEN | Polish channel / VAD candidate | Explicit VAD model, presales engineering, co-selling, demos, partner enablement and security portfolio. Could distribute or co-sell a new recoverability capability if pilot proof lands. | Outreach sent 2026-09-23 to Rafał Gałka (Security PM), cc Maciej Cenkier (BD Director). |
| Acronis | Strategic platform / integration candidate and long-term adjacent threat | Strong data/infrastructure recovery, MSP channel and 300+ integration ecosystem. Our wedge is agent-action recoverability above workload/data restore. | Initial TechnologyPartnerProgram email bounced because the group blocks external senders. Routing request sent 2026-09-23 to Eastern Europe PR contact Silviya Petrova asking for the correct Technology Ecosystem / ISV owner. Do not submit the partner-program form yet because it requires agreement to program terms. |
| Cynet | Adjacent competitor / possible integration route | AI-powered XDR/MDR automates threat detection and response across endpoint/identity/cloud/email/SaaS. Not currently the same product category, but could expand toward agent-action recovery. | Monitor before contact; qualify whether partnership beats competitive disclosure risk. |
| FUDO Security | Strategic adjacent vendor / integration candidate | Privileged access/session control is complementary to exact authority containment/restoration. Potential integration: privileged-session evidence feeding containment/restoration decisions while recovery verification remains in Agent Recovery Platform. | Partnership outreach sent 2026-09-23 to partners@fudosecurity.com. |
| REKOWERY / data-recovery vendors | Low-to-medium partner relevance | Traditional recovery can complement our application-level agent recovery but does not validate our wedge alone. | Research selectively |

## Initial channel / strategic partner classes

Prioritize 5 after research:
1. AI-security vendors that detect or govern agents but do not own verified cross-system recovery.
2. AppSec / cloud-security consultancies already selling AI assessments.
3. Agent observability/eval vendors where our recovery evidence complements traces.
4. Tool-integration / MCP infrastructure vendors exposed to consequential writes.
5. Cloud/agent platforms that need a deployment-readiness and recovery assurance layer.

## Evidence required before promotion to top-10

For every target promoted to the send-list, record:
- current product/use case proving write-capable agents or consequential tool execution;
- likely buyer role;
- concrete pain hypothesis;
- why existing product stack does not obviously solve verified recovery;
- one relevant public source;
- one personalized opening line;
- disqualifier if discovered.

## Research anchors verified 2026-09-23

- LangSmith Deployment publicly positions durable production agents with rollbacks, HIL, durable execution and governance.
- CrewAI positions an enterprise build/runtime layer for governed agents.
- Composio exposes managed execution/auth across 1,500+ apps, including cross-platform writes.
- Dust positions enterprise agents that connect to company tools, act across workflows, and use governance/audit controls.
- Arize positions end-to-end agent observability/evaluation around actions and tool use.
- Langfuse positions tracing/evals across agent tool invocation and production behavior.
- Acronis explicitly supports third-party CyberApps/Public API integrations and a large MSP/channel ecosystem; its core recovery remains workload/data/infrastructure oriented.
- SOC Factory publicly offers SOC monitoring, CISO-as-a-service and DORA/NIS2-oriented resilience work, creating a plausible channel-assessment fit.
- FEN publicly describes itself as a Value Added Distributor providing presales engineering, joint customer presentations and partner enablement.

These facts validate fit for further research; they do not imply interest in partnering.


## Outreach response tracking — 2026-09-23

- **FEN:** Maciej Cenkier returned an automatic out-of-office reply through 2026-09-24. Keep the thread warm; no duplicate same-day message. If no human response after return, follow up through the existing thread / security@fen.pl.
- **Acronis:** the published Technology Partner Program mailbox rejected external senders. A routing request was sent to Acronis Eastern Europe PR. The current Technology Ecosystem web sign-up requires agreement to program terms, so registration remains owner-gated.
- **SOC Factory:** awaiting response.
- **FUDO Security:** first partner-team outreach sent; awaiting response.

Next follow-up rule: no same-day chasing. Follow up after a reasonable business interval only if the target remains high-fit and no human response arrived.
