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

## Qualification state

Pipedream and n8n are promoted from research candidates because current first-party evidence confirms real tool execution and multi-system side effects. Other candidates in `DESIGN_PARTNER_PIPELINE.md` remain research-only until the same source-verification standard is met.

## Owner gate

Do not send these messages, submit partner forms, accept terms, or make customer commitments without Paweł’s explicit external-action approval. Next autonomous step is to verify additional candidates and expand this into the requested top-10 design-partner + top-5 strategic/channel shortlist while keeping each entry source-backed and disqualifiable.
