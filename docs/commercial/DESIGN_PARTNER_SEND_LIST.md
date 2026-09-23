# Qualified Design-Partner Send List

Date: 2026-09-23
Status: owner-reviewable research; **no external outreach authorized**

This list promotes only candidates with current primary-source evidence of consequential agent/tool execution and a plausible bounded sandbox path. It is intentionally short rather than padding the pipeline with weak leads.

## Ranking rubric

Score 0–2 each for: write-capable execution, multi-system side effects, platform/security owner, visible recoverability pain, practical sandbox/design-partner path. Promotion threshold: 7/10.

## 1. n8n — 10/10 — design partner

**Evidence.** n8n currently positions production AI agents/workflows with 500+ integrations, multi-agent support, human-in-the-loop controls, execution inspection, replay/mock data, isolated environments and governance. Its official MCP product explicitly lets AI clients create/update workflows, validate them, execute tests, inspect failures and fix workflows. Public examples include CRM updates and account creation, making consequential writes concrete rather than hypothetical.

**Likely buyer roles.** VP/Head of Product for AI, Head of Platform/Engineering, Security/AI Governance lead, enterprise platform engineering.

**Pain hypothesis.** n8n can observe, validate, retry and govern workflow execution, but customers operating autonomous cross-system writes still need evidence that a failed action chain has a valid recovery/compensation path and that only verified-safe authority is restored after an incident. Our wedge must complement n8n's existing replay/debug/governance rather than claim those features are missing.

**Why now.** n8n is actively expanding MCP-driven AI creation and execution, increasing the number of agents able to mutate workflows and business systems.

**Personalized opening line.** “Your MCP flow can already let an agent build, validate, run and repair n8n workflows; I’m working on the adjacent question of proving that the business-side effects those workflows create are recoverable before authority is restored.”

**Sandbox path.** Self-hosted/owned n8n instance with synthetic CRM/ticketing targets; no customer credentials or production data required.

**Disqualifier to test early.** If n8n already has an internal product roadmap for dependency-aware cross-system compensation plus independently verified restoration, partner differentiation may be too narrow.

**Primary sources verified 2026-09-23.** `https://n8n.io/`, `https://n8n.io/ai-agents/`, `https://n8n.io/mcp/`.

## 2. Composio — 9/10 — strategic integration / design partner

**Evidence.** Composio currently offers agents execution/auth infrastructure across 1,500+ apps and an enterprise MCP gateway that centralizes policy, credentials, governance, observability and audit trails for agent tool calls. Its developer material explicitly describes agents discovering and executing app tools at runtime.

**Likely buyer roles.** CTO, Head of Product/Platform, enterprise/security product lead, agent infrastructure engineering.

**Pain hypothesis.** Composio is positioned at the exact tool boundary where consequential side effects occur. Governance and audit can establish who called what; our complementary value is declaring recovery contracts for those writes, tracking causal dependencies across calls, verifying compensation outcomes and refusing restoration when current recovery evidence is insufficient.

**Why now.** Centralized MCP/tool execution creates a high-leverage integration point: one evidence adapter could cover many downstream applications without building dozens of connectors.

**Personalized opening line.** “Composio already gives agents a governed execution boundary across 1,500+ apps; I’m building the recovery layer for what happens after a permitted tool call creates the wrong real-world side effect.”

**Sandbox path.** Synthetic Composio-connected accounts or mocked tool boundary with two reversible/compensatable app writes; avoid production credentials.

**Disqualifier to test early.** If Composio is already shipping verified compensation semantics and restoration gating—not merely policy/audit—the partnership wedge needs re-evaluation.

**Primary sources verified 2026-09-23.** `https://composio.dev/for-you`, `https://composio.dev/mcp-gateway`, `https://docs.composio.dev/docs/quickstart`.

## Recommended outreach order

Start with n8n for a direct design-partner conversation and Composio for a strategic integration/design-partner conversation. Do not send yet. The next research slice should qualify additional candidates to at least the same evidence standard before expanding this file toward the target top-10 and five channel/strategic partners.

## Claim discipline

Do not say either company lacks recovery. Say their public product evidence strongly establishes consequential agent execution and adjacent governance/observability, while our proposed assessment tests a narrower property: validated recovery paths, compensation evidence, residual truth and scope-bound restoration eligibility. Any statement about internal roadmaps remains unknown until a conversation occurs.
