# Ranked Design-Partner Send List

Date: 2026-09-23
Status: owner-reviewable research artifact; no external send is authorized by this file.

This list promotes only candidates with current public evidence of consequential agent/tool execution and a plausible recoverability gap. It is intentionally short rather than a generic lead dump. Scores use the 0–10 rubric in `DESIGN_PARTNER_PIPELINE.md`.

## Ranked design-partner / integration targets

| Rank | Target | Score | Likely buyer / owner | Evidence-backed pain hypothesis | Personalized opening line | Disqualifier / caution | Public evidence |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| 1 | Composio | 10 | Head of Platform / Enterprise Engineering / Partnerships | Composio is explicitly the execution/auth boundary for agents acting across 1,500+ apps. Managed auth, tool execution and audit controls reduce access risk, but they do not by themselves prove dependency-aware compensation, residual truth, replay or verified restoration after a bad cross-app write. This is the cleanest integration surface for Recovery Contracts plus recovery evidence. | “Composio already gives agents a governed execution boundary across 1,500+ apps; we are building the missing evidence layer for what happens after an authorized tool call causes the wrong side effect — compensation, replay and verified restoration.” | They may decide recovery belongs natively in their tool runtime; treat that as both partner opportunity and convergence risk. | https://composio.dev/for-you ; https://docs.composio.dev/docs/composio-connect |
| 2 | n8n | 9 | VP Product / AI Platform / Enterprise Engineering | n8n agents can autonomously update business systems across 500+ integrations, supports multi-agent workflows, HIL, logs and replay/mock tooling. That makes controlled incident/recovery testing unusually realistic. Existing workflow replay/debugging is adjacent, but public positioning does not establish cross-system causal recovery with explicit irreversible residuals and scope-bound restoration. | “n8n is already where AI decisions become real business-system writes; we can test whether those workflows are not only observable and replayable, but actually recoverable after a bad multi-system action.” | Strong workflow history/replay could absorb parts of the wedge; qualify whether recovery/compensation evidence is materially distinct before deep integration work. | https://n8n.io/ ; https://n8n.io/ai-agents/ |
| 3 | LangChain / LangSmith Deployment | 9 | Head of LangSmith / Platform Product / Partnerships | LangSmith Deployment provides durable production agents, HIL, multi-agent coordination, fault tolerance, versioning and instant rollbacks. That proves a mature runtime buyer already values reliability, while creating a sharp boundary: runtime rollback is not the same as compensating external side effects or independently verifying restoration. | “LangSmith can roll an agent runtime back; we are focused on the harder question of proving what happened to external systems before that rollback and which authority can safely be restored afterward.” | Their instant-rollbacks story means generic “undo for agents” messaging will fail. Only pursue the external-side-effect / independent recoverability-assurance wedge. | https://www.langchain.com/langsmith/deployment |
| 4 | CrewAI | 8 | Enterprise Product / Platform Engineering / Security | CrewAI sells governed production agent workflows with SSO, RBAC, workload identity, policies and deployment into customer infrastructure. As customers grant those fleets more write authority, recoverability evidence becomes a credible enterprise-control extension beyond governance alone. | “CrewAI is putting governed agent fleets into enterprise production; we are testing a complementary control: whether every consequential write has a validated recovery path and current restoration evidence.” | Public evidence currently supports governance more strongly than cross-system side-effect complexity. Validate a concrete tool-writing workflow before proposing a pilot. | https://crewai.com/pricing |
| 5 | Dust | 8 | Security / Platform / Product | Dust’s enterprise-agent model connects agents to company tools and workflows with governance/audit controls. The likely gap is incident recovery after a permitted agent action mutates shared state across tools, not prevention or generic audit. | “You already help enterprises govern agents acting across company tools; we are building recoverability assurance for the moment a permitted action is still wrong and the operator needs evidence-backed restoration.” | Re-verify current write/action surfaces and identify one bounded consequential workflow before outreach; do not assume every deployment grants write authority. | Candidate retained from verified pipeline; source refresh required before send. |

## Recommended first wave

1. **Composio** — strongest product-boundary fit and clearest integration primitive.
2. **n8n** — strongest owned/sandbox feasibility for a realistic multi-system recovery proof.
3. **LangChain / LangSmith** — strongest strategic credibility, but messaging must explicitly distinguish external-side-effect recovery from runtime rollback.

CrewAI is the next design-partner candidate after one concrete write-capable workflow is verified. Dust remains high-potential but must not enter a send wave until its current consequential-write surface is source-refreshed.

## Message discipline

Lead with a narrow technical/customer question, not a broad security pitch: **when an authorized agent makes the wrong consequential write, can the operator reconstruct the causal chain, compensate what is reversible, preserve irreversible residual truth, replay the repaired control and restore only the exact safe authority?**

Do not claim universal rollback, prevention, production security effectiveness, complete causal capture, or restoration of irreversible effects. Do not send externally without the current owner gate being satisfied.

## Qualification next actions

- Composio: map one representative cross-app write chain to the current Recovery Contract schema and owned pilot evidence; no credentials or live customer data.
- n8n: identify the smallest synthetic workflow with two consequential surfaces that can demonstrate compensation plus an irreversible residual.
- LangSmith: prepare a one-page boundary diagram showing runtime rollback vs external side-effect recovery / verified restoration.
- CrewAI: verify one current enterprise tool-execution example and buyer role.
- Dust: refresh primary-source evidence for write-capable actions before promotion.

This artifact advances issue #144 toward its success gate; it does not close the issue until the top-10 design-partner list, five channel/strategic partners and ready-to-send package are complete.