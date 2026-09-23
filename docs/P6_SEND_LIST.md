# P6 Ranked Send List

Date: 2026-09-23
Status: owner-reviewable research artifact; **no outreach has been sent**.

This list promotes candidates only when current public product evidence shows consequential agent/tool execution and a plausible recoverability gap. Ranking is for outreach sequencing, not a claim that any organization has expressed interest.

## Tier 1 — design / integration conversations

### 1. Pipedream — strategic integration / design partner
- **Public evidence:** Pipedream currently positions itself as the integration layer for AI agents, with managed auth, 10,000+ tools across 3,000+ APIs, actions that write to APIs, per-user connected accounts, access policies and audit trails.
- **Likely buyer / sponsor:** product leader for Connect/Conduit, agent infrastructure lead, security/product engineering leader.
- **Pain hypothesis:** a platform sitting between agents and thousands of external APIs has unusually high exposure to consequential cross-system writes. Auth, policy and auditability help before/during execution, but independent evidence of whether an incident can be compensated, replayed and safely restored is a different control.
- **Why Agent Recovery can complement rather than replace it:** use tool-call evidence as provenance input and attach Recovery Contracts/verification to consequential actions; do not compete on auth, MCP connectivity or generic audit logging.
- **Opening line:** “You already sit at the highest-leverage boundary between agents and real APIs; we’re testing whether that same boundary can expose verified recovery contracts and post-incident restoration evidence instead of stopping at auth and audit.”
- **Disqualifier:** deprioritize if Pipedream already has a first-class, evidence-backed compensation/replay/restoration layer for arbitrary cross-app side effects.
- **Source:** https://pipedream.com/ and https://pipedream.com/conduit (verified 2026-09-23).

### 2. n8n — design partner / sandbox candidate
- **Public evidence:** n8n markets AI agents and workflows with 500+ integrations, multi-agent systems, MCP connectivity, human-in-the-loop controls, execution logs, workflow history and governance. Its MCP product can let AI create, edit, validate and fix live workflows.
- **Likely buyer / sponsor:** AI product lead, enterprise platform/security product leader, developer platform lead.
- **Pain hypothesis:** agents and AI-assisted workflow changes can create effects across many connected systems. Existing observability, approvals and rollback of workflow definitions do not by themselves prove compensation of already-executed external effects or safe selective restoration after an incident.
- **Why Agent Recovery can complement rather than replace it:** use n8n as a bounded high-signal workflow environment for recovery contracts, causal side-effect evidence, compensation verification and incident-to-regression replay.
- **Opening line:** “n8n already makes agent actions inspectable and controllable; we’re building the missing post-incident proof layer for what happened across connected systems, what was actually compensated, and what authority is safe to restore.”
- **Disqualifier:** deprioritize if n8n can already verify cross-system compensation and scope-bound restoration after consequential agent actions, not merely workflow-version rollback or reruns.
- **Source:** https://n8n.io/, https://n8n.io/ai-agents/, https://n8n.io/mcp/ (verified 2026-09-23).

### 3. Composio — strategic integration / design partner
- **Public evidence:** Composio exposes agent tool execution across 1,500+ applications and 20,000+ tools, with managed authentication, access policies, execution logs and an enterprise MCP gateway/audit layer. Its own product material explicitly positions agents as taking actions across connected apps.
- **Likely buyer / sponsor:** MCP Gateway or developer-platform product leader, agent infrastructure lead, security product leader.
- **Pain hypothesis:** a governed tool gateway can constrain and record actions, but cross-application writes still leave a post-incident question: which effects are reversible or compensatable, which recovery actually succeeded, and which authority is safe to restore.
- **Why Agent Recovery can complement rather than replace it:** consume gateway/tool execution evidence and bind Recovery Contracts plus compensation/replay verification to consequential actions; do not compete on auth, tool discovery, policy enforcement or audit logging.
- **Opening line:** “Composio already governs the boundary where agents act across thousands of tools; we’re testing the recovery contract and verification layer for what happens after one of those permitted actions causes a cross-system incident.”
- **Disqualifier:** deprioritize if Composio already verifies dependency-aware compensation of executed cross-app effects and gates restoration on fresh recovery/replay evidence.
- **Sources:** https://composio.dev/mcp-gateway and https://composio.dev/for-you (verified 2026-09-23).

### 4. LangChain / LangSmith — runtime / strategic partner
- **Public evidence:** LangSmith Deployment runs production agents on a durable runtime with fault tolerance, human-in-the-loop, multi-agent coordination, centralized versioning and instant agent rollbacks. LangChain also describes checkpointed durable execution and resume-from-exact-point behavior for agent runs.
- **Likely buyer / sponsor:** LangSmith Deployment product leader, runtime/platform engineering leader, enterprise security/product leader.
- **Pain hypothesis:** runtime durability and agent-version rollback solve execution continuity and software rollback, but they do not obviously prove compensation of external side effects already committed across tools or scope-bound restoration after a security/reliability incident.
- **Why Agent Recovery can complement rather than replace it:** use runtime traces/checkpoints as evidence inputs while independently modeling side-effect recovery contracts, residuals, replay/regression and restoration eligibility.
- **Opening line:** “LangSmith already makes agent execution durable and rollback-friendly; we’re focused on the harder boundary after a tool call commits externally—proving what was compensated, what remains residual, and what authority can safely come back.”
- **Disqualifier:** deprioritize if LangSmith already provides evidence-backed cross-system compensation and selective authority restoration for committed external effects, beyond agent/runtime rollback and resumption.
- **Source:** https://www.langchain.com/langsmith/deployment and https://www.langchain.com/blog/runtime-behind-production-deep-agents (verified 2026-09-23).

### 5. CrewAI — enterprise runtime / design partner
- **Public evidence:** CrewAI positions its platform for production multi-agent workflows that autonomously interact with enterprise applications and tools, with tracing, controls, RBAC, audit trails, human-in-the-loop checkpoints, policies and enterprise governance.
- **Likely buyer / sponsor:** enterprise platform/product leader, agent runtime leader, security/governance product leader.
- **Pain hypothesis:** governance, tracing and checkpoints reduce execution risk, while persistent state helps resume interrupted workflows; neither by itself establishes that already-executed external effects were compensated or that only the recovered authority scope is safe to restore.
- **Why Agent Recovery can complement rather than replace it:** attach recoverability readiness and Recovery Contracts to governed tool actions, then turn incident evidence into verified compensation, replay/regression and restoration decisions.
- **Opening line:** “CrewAI already gives enterprises governance and durable agent workflows; we’re testing the complementary incident-recovery proof layer for external side effects that survive a workflow checkpoint or restart.”
- **Disqualifier:** deprioritize if CrewAI already verifies external compensation outcomes and fail-closed selective authority restoration across enterprise tool calls.
- **Sources:** https://crewai.com/agent-management-platform and https://crewai.com/pricing (verified 2026-09-23).

### 6. Zapier — design / integration partner
- **Public evidence:** Zapier MCP lets AI clients take real actions across 9,000+ apps and tens of thousands of actions, including writes such as sending messages and updating records. Zapier provides scoped app/action access and logs actions in History; Zapier Agents can also be triggered from apps, schedules, Zaps and MCP.
- **Likely buyer / sponsor:** MCP/Agents product leader, AI platform product leader, enterprise security/product engineering leader.
- **Pain hypothesis:** scoped authorization and action history constrain and record agent writes, but after a permitted multi-app action chain causes an incident there is still a distinct need to establish causal effects, verify compensation outcomes, preserve irreversible residuals and decide exactly which authority can safely return.
- **Why Agent Recovery can complement rather than replace it:** treat Zapier action history and tool-call evidence as provenance inputs and bind Recovery Contracts plus post-incident verification to consequential writes; do not compete on integrations, credentials, workflow automation or access governance.
- **Opening line:** “Zapier already gives AI agents governed hands across thousands of apps; we’re testing the complementary recovery proof layer for when a permitted action chain goes wrong—what was actually compensated, what remains residual, and what scope is safe to restore.”
- **Disqualifier:** deprioritize if Zapier already provides evidence-backed dependency-aware compensation of committed cross-app effects plus replay-gated selective restoration, rather than action history, retries or workflow rollback alone.
- **Sources:** https://zapier.com/mcp, https://zapier.com/mcp/agents and https://help.zapier.com/hc/en-us/articles/48308034391821-What-is-Zapier-MCP (verified 2026-09-23).

### 7. Workato — enterprise orchestration / strategic partner
- **Public evidence:** Workato Agentic Orchestration positions autonomous agents as executing multi-step business actions across departments and systems, including thousands of actions across finance, sales and operations, while logging and tracing every agent action with enterprise controls.
- **Likely buyer / sponsor:** Agentic product leader, enterprise automation/platform leader, security/governance product leader.
- **Pain hypothesis:** enterprise controls and traceability reduce execution risk, but broad autonomous cross-system action creates a separate recovery problem after an incident: dependency-aware compensation, verified outcomes, residual truth and selective restoration of affected authority.
- **Why Agent Recovery can complement rather than replace it:** consume orchestration/action evidence as causal provenance and add framework-neutral Recovery Contracts, compensation verification and incident-to-regression replay; do not compete on orchestration, integrations, governance or general observability.
- **Opening line:** “Workato already orchestrates governed agents across consequential business systems; we’re focused on the next incident boundary—proving which external effects were recovered or compensated and which exact authority is safe to restore.”
- **Disqualifier:** deprioritize if Workato already verifies dependency-aware compensation of executed cross-system effects and gates selective authority restoration on fresh recovery/replay evidence.
- **Sources:** https://www.workato.com/agentic and https://www.workato.com/agentic/agent-orchestration (verified 2026-09-23).

### 8. Arize AI — observability / strategic integration partner
- **Public evidence:** Arize AX and Phoenix capture agent traces spanning tool activity, handoffs and state changes, support OpenTelemetry/OpenInference, and explicitly recommend verifying consequential task completion in the downstream system. Arize also turns production failures into regression datasets and experiments.
- **Likely buyer / sponsor:** agent observability product leader, OpenInference/platform leader, partnerships/product engineering leader.
- **Pain hypothesis:** rich traces and evaluations can explain what an agent did and whether an intended outcome occurred, but observability alone does not establish dependency-aware compensation of committed external effects, residual truth, or fail-closed restoration of only the recovered authority scope.
- **Why Agent Recovery can complement rather than replace it:** ingest OpenTelemetry/OpenInference traces as causal evidence, then add Recovery Contracts, verified compensation outcomes, incident-to-regression replay and restoration eligibility; feed recovery outcomes back into the regression corpus instead of building a competing tracing stack.
- **Opening line:** “Arize already captures the evidence needed to explain agent incidents; we’re testing the complementary control that turns those traces into verified compensation, residual truth, regression replay and an exact decision about which authority is safe to restore.”
- **Disqualifier:** deprioritize if Arize already provides dependency-aware recovery execution plus evidence-gated selective authority restoration for committed external side effects, rather than tracing, evaluation, sandbox policy and downstream outcome verification.
- **Sources:** https://arize.com/guides/ai-agent-handbook/agent-observability/, https://arize.com/resources/whats-an-agent-observability-platform/ and https://arize.com/resources/agent-reliability/ (verified 2026-09-23).

## Qualification state

Eight candidates are now promoted from research because current first-party evidence confirms real agent/tool execution or high-value causal evidence infrastructure plus a distinct plausible recoverability boundary. Other candidates in `DESIGN_PARTNER_PIPELINE.md` remain research-only until the same source-verification standard is met.

## Owner gate

Do not send these messages, submit partner forms, accept terms, or make customer commitments without Paweł’s explicit external-action approval. Next autonomous step is to verify the remaining strongest candidates and expand this into the requested top-10 design-partner + top-5 strategic/channel shortlist while keeping each entry source-backed and disqualifiable.
