# Market intelligence - 2026-09-29

## Executive read

The AI agent security market is accelerating and consolidating around prevention, identity, governance, runtime controls, red teaming and assurance.

This makes the Agent Recovery wedge more valuable, not less, if we stay disciplined.

Do not reposition as a general agent security platform.

Own the narrower category:

**verified recovery and recoverability assurance after consequential AI-agent side effects**

## Market signals

### NVIDIA Open Agent Safety Platform

NVIDIA announced Open Agent Safety Platform on 2026-09-28.

Primary sources:
- https://nvidianews.nvidia.com/news/open-agent-safety-platform
- https://www.nvidia.com/en-us/ai/openshell/
- https://docs.nvidia.com/openshell/observability/ocsf-json-export

What it does:
- secure runtime boundary;
- sandboxing;
- deny-by-default policy;
- runtime governance outside the agent process;
- out-of-band watchdog through Sentry;
- OCSF JSON security telemetry.

Strategic implication:
- prevention and containment are becoming infrastructure;
- do not compete with sandboxing or action policy;
- integrate with OpenShell evidence and treat it as an upstream control;
- recovery remains necessary for allowed actions that create wrong external state.

### Zenity

Sources:
- https://zenity.io/blog/zenity-raises-125-million-secure-era-autonomous-ai
- https://zenity.io/blog/august-2026-product-updates
- https://zenity.io/company/newsroom

Current direction:
- broad enterprise agent security;
- continuous contextual security;
- Guardian Agents;
- runtime enforcement;
- broad agent coverage;
- OTel and gen_ai span connectivity;
- $125M Series C announced in August 2026.

Strategic implication:
- generic visibility, posture and runtime security are becoming crowded;
- OTel is becoming a practical interoperability surface;
- our OTLP path was the right decision;
- do not chase Zenity feature breadth.

### Noma Security

Sources:
- https://noma.security/blog/noma-brings-agent-security-to-every-employee-endpoint
- https://noma.security/solutions/agent-control-plane
- https://noma.security/blog/noma-partners-with-kong-to-secure-the-agentic-ai-era

Current direction:
- unified agent control plane;
- discovery;
- access control;
- runtime enforcement;
- endpoint, SaaS and homegrown agent coverage;
- states that more than 2.6M agents are secured across customers;
- ecosystem partnerships such as Kong.

Strategic implication:
- identity and governance will be dominated by well-funded horizontal platforms;
- our product should consume their decisions and telemetry as evidence rather than reproduce them.

### Outerlimit

Sources:
- https://www.outerlimit.com/company-news/outerlimit-launch
- https://www.outerlimit.com/

Current direction:
- emerged from stealth in September 2026;
- $16M pre-seed;
- deterministic authorization at the agent action layer;
- zero trust for tool execution;
- partner program for technology vendors and channels.

Strategic implication:
- this is another strong proof that pre-action authorization is becoming its own market layer;
- Outerlimit is a potential integration or strategic-partner target similar to Kyvvu;
- our boundary should be explicit: authorization before execution, verified recovery after harmful side effects.

### Eve Security

Sources:
- https://eve.security/
- https://www.prnewswire.com/news-releases/eve-security-extends-seed-round-to-7-5-million-as-rogue-ai-agents-turn-runtime-security-into-an-enterprise-imperative-302878598.html

Current direction:
- runtime security;
- behavior monitoring;
- intervention during execution;
- seed extension to $7.5M total in September 2026.

Strategic implication:
- detection and intervention do not automatically repair completed external side effects;
- Eve is a potential integration partner, not only a competitor.

### Check Point AI Security

Sources:
- https://docs.lakera.ai/docs/agent-security
- https://docs.lakera.ai/changelog/2026-06-01

Current direction:
- agent discovery;
- posture and risk assessment;
- runtime tool-call defense;
- connectors for Bedrock, Copilot Studio, Agentforce, n8n and others.

Strategic implication:
- discovery and pre-action / runtime controls are commoditizing;
- recoverability should become a separate measurable control plane rather than another risk score.

### Pillar Security

Sources:
- https://www.pillar.security/blog/introducing-pillar-for-agentic-ci-cd
- https://www.pillar.security/blog/from-ai-discovery-to-attack-surface-mapping-announcing-the-wiz-pillar-partnership
- https://www.pillar.security/blog/pillar-security-named-a-pioneer-in-the-2026-gartner-r-emerging-market-quadrant-for-ai-application-security

Current direction:
- discovery;
- red teaming;
- runtime defense;
- agentic CI/CD security;
- ecosystem integration with Wiz.

Strategic implication:
- independent testing and attack-surface validation are becoming standard;
- Agent Recovery should fit after those tests by proving that failure can be contained and repaired.

### Mindgard

Sources:
- https://mindgard.ai/blog/mindgard-raises-30m-series-a
- https://mindgard.ai/blog/mindgard-launches-guardbuster
- https://mindgard.ai/blog/mindgard-ecosystem-anthropic-nvidia-microsoft-google-cloud-aws

Current direction:
- adversarial testing;
- independent guardrail validation;
- continuous AI security;
- $30M Series A announced in August 2026;
- expanded cloud and model-provider ecosystem.

Strategic implication:
- there is buyer appetite for independent evidence that security controls actually work;
- our buyer-facing assessment should emphasize independent, evidence-bound recovery proof.

### AIUC

Sources:
- https://aiuc.com/updates/series-a-announcement
- https://www.aiuc-1.com/
- https://www.aiuc-1.com/accountability/ai-failure-plan-for-security-breaches
- https://www.aiuc-1.com/methodology

Current direction:
- $40M Series A in September 2026, $55M total;
- AIUC-1 certification and insurance;
- 250+ security and risk leaders in the consortium;
- requirements include incident response, reliability, unsafe tool calls and evidence;
- quarterly updates driven by real incidents.

Strategic implication:
- recoverability can become assurance evidence;
- map Agent Recoverability Assessment outputs to AIUC-1 concepts without claiming official compliance;
- explore whether future standard pilots need measurable recovery evidence.

## Market structure decision

The market is splitting into layers:

1. discovery and posture;
2. identity and authorization;
3. runtime prevention and containment;
4. adversarial testing and validation;
5. assurance, certification and insurance;
6. recovery and verified restoration.

Agent Recovery should own layer 6 and integrate aggressively with layers 1 to 5.

## Commercial expansion

Do not tie business development to events.

Run continuous qualified outreach across six target classes:

1. agent platforms and tool layers;
2. workflow and durable-execution platforms;
3. runtime agent-security vendors;
4. MSSP / AppSec / AI-security consultancies;
5. audit, certification and insurance ecosystems;
6. enterprises already operating write-capable agents.

Current expanded outreach includes:
- Composio;
- Temporal;
- Eve Security;
- Browser Use;
- Gumloop;
- AIUC;
- n8n;
- Kyvvu;
- Veeam;
- Datadog;
- EverWorker;
- TechEx-qualified targets.

## Product decisions

### Decision 1
Keep the category narrow.

Do not build generic posture, identity, prompt filtering or agent firewall features.

### Decision 2
Make interoperability a moat.

Priority evidence inputs:
- OTLP / OTel;
- OCSF for security-runtime sources;
- policy and authorization decision IDs;
- tool and workflow execution events.

### Decision 3
Turn the assessment into a repeatable assurance product.

Commercial product ladder:

1. Agent Recoverability Assessment
2. Recovery Readiness Gate for CI / deployment
3. Runtime Recovery Control
4. Verified Restoration Gate after incidents

### Decision 4
Create explicit partner boundaries.

Upstream products may authorize, block, observe or detect.
Agent Recovery does not replace them.

Agent Recovery receives their evidence, handles recovery semantics and emits non-authorizing recovery state.

### Decision 5
Add standards mapping, not standards theater.

Map our evidence to public AIUC-1 incident-response and reliability concepts where factual.
Do not claim certification, official alignment or endorsement without external confirmation.

### Decision 6
Prioritize one external workflow over more internal breadth.

The next major proof should be:
- one real third-party workflow;
- real evidence handoff;
- one controlled bad outcome;
- recovery or compensation;
- verified source-system state;
- replay;
- explicit residuals.

That is more valuable than another broad dashboard feature.

## Watchlist

Continuously monitor:
- NVIDIA OpenShell and Sentry;
- Zenity;
- Noma;
- Outerlimit;
- Eve Security;
- Pillar Security;
- Check Point AI Security;
- Mindgard;
- AIUC;
- major identity vendors moving into agent governance;
- acquisitions that absorb AI-security point products into larger platforms.

The market is moving too quickly for quarterly competitor reviews. Revisit this file when a material product launch, funding event, acquisition, standard change or real customer signal changes our position.
