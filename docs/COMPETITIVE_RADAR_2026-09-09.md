# Competitive Radar - 2026-09-09

This is a bounded refresh of the recovery / replay / agent-integrity landscape. It supplements `docs/COMPETITIVE_LANDSCAPE.md`; it does not replace the product thesis.

## Decision

Keep the current wedge:

**distributed multi-agent incident recovery + recovery-path security + adversarial replay + verified restoration**

Do not pivot into generic agent observability, generic self-healing, generic runtime guardrails, or a single-agent rewind debugger.

The refresh strengthens three requirements:

1. make incident-to-regression a first-class product primitive;
2. cryptographically bind provenance/topology/evidence to the recovery proof where practical;
3. measure the advisory AI layer against adversarial multi-turn and ambiguous-evidence cases, not just clean fixtures.

## Existing direct references - progress check

### Toffoli

Repository: https://github.com/theo-ai-lab/toffoli

Latest substantive activity observed in the refresh is dominated by supply-chain hardening and ship-gate evidence rather than a new multi-agent recovery architecture. The project reports strong engineering discipline, including dependency-age policy, package-audit checks, mutation gates, measured irreversible-action recall and explicit limitations.

What to learn:
- release evidence should be treated as a security artifact, not a CI checkbox;
- dependency provenance / package-age policy can become relevant before production pilots;
- mutation testing is a useful way to prove that safety gates fail when deliberately weakened.

Do not copy code or test fixtures. Use the engineering standard as a quality benchmark.

### Moholo Agent Rewind

Repository: https://github.com/moholo-founder/agent-rewind

Recent published work remains focused on interception, snapshots, STOP/kill-switch behavior, outbound connectors and honest connector-local reversibility. It has strong crash/concurrency and intent-before-effect journaling lessons.

What to learn:
- persist the intent before the side effect whenever possible;
- make recovery/rewind sets immutable once previewed so concurrent changes cannot silently alter the operation;
- external effects need connector-specific truth, never generic "undo" claims;
- secrets should not flow through the same argument/evidence surface as tool actions.

Our differentiation remains cross-agent causal recovery and verified restoration, not connector count.

## Newly important adjacent projects

### Agentegrity

Repository: https://github.com/Cogensec/agentegrity
License: Apache-2.0

Agentegrity is now a serious adjacent reference. It frames agent security as three measurable capabilities: self-defense, self-stability and self-recovery. It also ships signed/hash-chained decision provenance and explicit multi-agent topology evidence across many agent frameworks.

Important strengths:
- signed decision provenance;
- hash-chained evidence;
- multi-agent topology committed into evidence;
- role-drift / peer-authority / cascade concepts;
- explicit published weak benchmark numbers instead of hiding limitations;
- framework-neutral instrumentation.

Important gap relative to our target:
- it is primarily integrity measurement/verification and checkpoint-style self-recovery;
- it does not replace a distributed side-effect recovery engine that reconstructs causal blast radius, compensates cross-system effects, replays the source attack and gates restoration of authority.

Action for our design:
- add topology/provenance binding to the evidence contract before claiming a strong multi-agent proof;
- keep cross-framework neutrality in the longer-term commercial architecture;
- distinguish "agent says it recovered" from "external state and authority restoration were independently verified".

### AgentOptics Rewind

Repository: https://github.com/agentoptics/rewind
License: MIT

A mature time-travel debugger for LLM agents. It records exact model/tool boundaries, supports fork/replay/diff, imports production traces, performs regression testing and can apply an AI-suggested fix before replaying it.

Important strengths:
- timeline ancestry and fork semantics are treated as real data-integrity problems;
- replay separates the source/read timeline from the new write/fork timeline;
- production trace import and local replay are excellent product UX;
- every production failure can become a regression baseline;
- explicit replay savings provide an immediate ROI story.

Gap relative to our target:
- its primary problem is debugging/reproducibility of agent behavior;
- our primary problem is security incident containment, side-effect recovery, residual truth and authority restoration after compromise.

Action for our design:
- keep source evidence lineage separate from recovered/forked state lineage;
- make incident-to-regression one command / one artifact eventually;
- include recovery-time / avoided-reexecution / prevented-downtime metrics in the commercial assessment without inventing unsupported monetary savings.

### AgentReplay

Repository: https://github.com/anzal1/agentreplay

Product promise: turn every failed agent run into a replayable test using a language-neutral trace format.

Why it matters:
- "incident -> regression" is becoming a recognizable product category, so the concept alone will not remain novel;
- our moat must be that the regression is generated from a security incident with causal side-effect evidence and becomes a prerequisite for authority restoration.

Action:
- keep our regression artifact incident-bound, evidence-bound and policy-aware rather than a generic trace replay file.

### IRAS

Repository: https://github.com/krishnashakula/IRAS

Adjacent incident-response agent for infrastructure/SRE rather than compromised AI agents. It performs triage, root-cause analysis, remediation planning, human approval, sequential remediation and rollback; safety invariants are enforced in code.

Why it matters:
- it validates Investigator -> Planner -> human/deterministic gate as an understandable operational UX;
- confidence loops and escalation on insufficient evidence are useful patterns;
- exact rollback commands from an LLM are not a sufficient trust boundary for our product.

Action:
- our Investigator should be allowed to request more evidence when confidence/evidence coverage is insufficient;
- Planner output stays advisory and typed; execution derives from Recovery Contracts, never arbitrary generated commands.

### Small guarded self-healing projects

Examples include `agentic-recovery-and-incident-response` and Airflow-specific self-healing pipelines.

Common pattern:
`detect -> diagnose -> plan -> approve -> remediate -> verify -> learn`

Implication:
- this lifecycle is quickly becoming standard language, so it is not differentiation by itself;
- our differentiated steps are cross-agent causal reconstruction, recovery-path integrity, residual external-effect truth, attack replay and verified authority restoration.

## Research signal: prompt hardening is not enough

Recent multi-agent security research reports that prompt hardening can substantially reduce direct attack success but still leaves large residual failure under multi-turn attacks. The important design implication is not the exact number; it is that stronger prompts cannot be our primary security boundary.

Action:
- add ambiguous/multi-turn advisory fixtures for Investigator/Planner/Skeptic after the deterministic judge path is stable;
- keep runtime state, identity, tool contracts and evidence outside model authority;
- benchmark recovery from successful compromise, not only prevention of compromise.

## Market signal: containment and shutdown are becoming first-class concerns

Recent public reporting around frontier-agent containment failures and automated shutdown work reinforces the urgency of external authority controls. The product should integrate with prevention and kill-switch layers rather than compete with them.

Positioning remains:

**Detection tools tell you something went wrong. Kill switches stop more damage. We determine what was affected, recover what can be recovered, expose what cannot, replay the incident, and prove what authority can safely come back.**

## Concrete changes to our roadmap

### Before competition submission

Do not expand scope into fourteen framework adapters or generic detection. Prioritize:

1. complete judge-facing end-to-end evidence packaging;
2. Strands Investigator / Planner / Skeptic with evidence-cited typed outputs;
3. deterministic advisory validation and explicit "insufficient evidence" escalation;
4. one bounded adversarial/multi-turn advisory scenario if time permits;
5. preserve source-incident lineage through recovery fork and replay evidence;
6. keep competition claims synthetic and reproducible.

### Immediately after competition

Highest-value hardening candidates:

1. signed evidence / optional external anchoring rather than only in-process hash chaining;
2. topology-bound multi-agent evidence;
3. mutation tests for authorization, replay freshness and restoration gates;
4. OTel / framework-neutral evidence ingestion;
5. production-trace-to-isolated-regression workflow;
6. connector-specific Recovery Contracts for one real design-partner workflow;
7. measurable recovery-time and business-continuity evidence.

## Legal/originality boundary

- Study public architecture, published behavior, standards, papers and benchmark methodology.
- Do not copy competitor code, UI, prose, proprietary fixtures or branding into the competition entry.
- Apache-2.0 / MIT artifacts may be reused only when there is a concrete reason, with attribution/license compliance; independent implementation remains preferred for competition-core functionality.
- Source-available / no-license repositories remain research-only unless separately reviewed.

## Strategic conclusion

The category is becoming more crowded, but the refresh does not reveal a project that makes our current wedge obsolete.

The strongest new competitive pressure is around **replay/regression** and **multi-agent integrity evidence**. We should absorb those lessons now.

Our target remains harder and more operational:

**compromise -> causal blast radius -> scoped containment -> evidence-bound recovery -> residual truth -> adversarial replay -> verified selective restoration.**
