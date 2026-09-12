# Judge Incident Recovery Console - Visual Product Spec

Status: competition-facing visual layer specification. Build only on the separate submission-prep path until the GPT-6 re-audit of PR #67 is complete.

## Product decision

Build a small, polished, read-only web console instead of a broad application UI.

Purpose:
- turn deterministic evidence into a coherent product experience for judges
- make the end-to-end recovery story understandable in under 60 seconds of screen time
- provide a strong visual surface for the demo video
- optionally provide a live demo link without introducing write authority or cloud credentials

Non-goals:
- production admin console
- authentication
- live recovery controls
- generic SIEM dashboard
- cloud control plane
- mutable incident editing

## Visual principle

The screen should answer five questions immediately:

1. What happened?
2. What did it affect?
3. What can be safely recovered?
4. What remains risky or irreversible?
5. Why is authority safe to restore?

The primary visual language should borrow from incident-response and security products:
- one authoritative incident timeline
- one attack/causal graph
- clear state/severity/status chips
- fewer, stronger panels rather than a dense monitoring dashboard
- evidence drill-down on demand

Avoid "AI chat app" aesthetics. The product is a recovery control plane, not a chatbot.

## Screen structure

### 1. Header - incident truth

Left:
- Agent Recovery
- Incident `B06 / Multi-agent cascade`
- bounded synthetic fixture badge

Right status chips:
- `CONTAINED`
- `RECOVERY VERIFIED`
- `REPLAY PASSED`
- `2 SCOPES RESTORED`
- `ROOT STILL CONTAINED`

Important: render only statuses present in deterministic evidence.

### 2. Lifecycle rail

A horizontal lifecycle directly below the header:

`Incident -> Containment -> Evidence -> Recovery -> Replay -> Restoration`

Each phase has one of:
- complete
- active
- blocked
- residual
- unrepresented

Clicking a phase scrolls/highlights its corresponding evidence section.

This lifecycle is the visual thesis of the project and should be visible throughout the demo.

### 3. Blast-radius / causal graph

Center-left, largest panel.

Nodes:
- external poisoned input
- support/root agent
- shared memory/tool state
- workflow agent
- identity/downstream authority

States:
- compromised root: red
- affected/contained downstream: amber
- verified recovered state: green
- residual/irreversible external effect: violet or gray warning

Edges:
- causal action
- shared-state dependency
- authority propagation

Graph must come from represented incident evidence only.

For the competition demo, keep the graph small and legible. Five to seven nodes is enough.

### 4. Recovery timeline

Right-side or lower panel using a chronological feed.

Events should show:
- event type
- actor/control plane
- status
- evidence/reference ID
- concise explanation

Key milestones:
- poison observed
- compromised write executed
- blast radius reconstructed
- authority scopes contained
- Investigator hypothesis produced
- Planner plan produced
- Skeptic challenge
- deterministic gate accepted/rejected plan
- recovery executed
- verifier result
- replay run
- restoration decision

AI-generated advisory steps must carry a visible `ADVISORY ONLY` badge.

Deterministic execution steps carry `CONTROL PLANE`.

### 5. Recovery obligations panel

Table or stacked cards:

Columns:
- action/effect
- recovery class
- current state
- verification
- residual risk

Example states:
- `memory.write` -> reversible -> verified recovered
- downstream permission change -> compensatable -> verified recovered
- external message -> irreversible -> residual visible

This panel is critical for truthful semantics. Never turn an irreversible effect green.

### 6. Replay and Restoration Gate panel

This is the hero proof panel.

Show:
- source action identity
- contract version
- source/recovery freshness
- proposed release scope
- replay environment binding
- replay verdict
- latest applicable proof
- restoration decision

The final visual should make selective restoration obvious:
- workflow/identity downstream authority: RESTORED
- compromised root agent: CONTAINED

Do not imply the source/root agent is safe to restore unless the implementation and evidence explicitly support that case.

### 7. Evidence drawer

Collapsed by default.

Contains:
- incident ID
- action event IDs
- contract versions
- ledger head/hash
- replay fingerprint
- recovery fingerprint
- artifact schema version
- exact CI/run metadata when available

This makes the UI credible to technical judges without overwhelming the main story.

## Visual style

Direction:
- dark neutral security/operations surface
- high contrast
- restrained use of red/amber/green
- monospace only for IDs/hashes/code-like evidence
- normal sans-serif for narrative text
- no neon cyberpunk aesthetic
- no excessive gradients or glassmorphism

Reference patterns:
- incident.io / Rootly: chronological incident timeline and lifecycle clarity
- Wiz / CrowdStrike: attack-path graph and contextual relationships
- AWS architecture diagrams: clear trust boundaries and official service icons

Do not imitate any proprietary UI exactly. Borrow interaction patterns, not branding.

## Information hierarchy

First 5 seconds:
- incident status
- lifecycle rail
- causal graph

Next 15 seconds:
- containment and recovery obligations

Next 15 seconds:
- replay proof and selective restoration

Technical drill-down:
- evidence drawer and exact references

This order matches the demo narrative and keeps judges from starting with raw logs.

## Implementation strategy

Preferred minimum implementation:
- static HTML/CSS/JavaScript or a similarly lightweight frontend
- consumes generated deterministic JSON artifacts
- no write APIs
- no secrets
- no model calls required to render
- no dependency on AWS credentials

Hosting priority:
1. GitHub Pages if safe and quick
2. another free static host only if already available and low-risk
3. local screen recording if hosting would threaten submission stability

A static read-only live demo still adds product polish and provides a judge-accessible surface. Do not overstate it as a production deployment.

## Architecture diagram visual plan

Use a left-to-right flow with explicit trust boundaries.

### Input and agentic reasoning
- Incident/evidence input
- Strands Investigator
- Strands Recovery Planner
- Strands Skeptic/Verifier

Place these in a clearly labeled `Advisory reasoning - no execution authority` zone.

### Deterministic control plane
- Recovery Contract Registry
- Action Ledger
- Incident Graph
- Containment
- Recovery/Reconciliation Engine
- Replay Lab
- Restoration Gate

Place these in `Deterministic authorization and verification` zone.

### Output
- Judge Evidence Package
- Judge Incident Recovery Console
- Regression Test

Optional AWS services, if not live-verified, must be separated with a dashed `Optional verified-live path` boundary and wording that does not imply current production use.

Use official AWS Architecture Icons for any AWS services shown.

## Video capture plan

Record at 1440p or 1080p with browser chrome minimized.

Recommended shots:
1. full console with incident graph
2. zoom to poisoned root and downstream propagation
3. containment status transition
4. advisory panel showing Investigator/Planner/Skeptic separation
5. recovery obligations with one residual effect remaining visible
6. replay gate passing for downstream scope
7. root remains contained while downstream scope becomes restored
8. final proof card with exact tests/benchmark/audit evidence

Do not spend video time scrolling raw repository files unless needed for one credibility shot.

## Copy rules

Preferred language:
- represented
- bounded
- verified
- contained
- residual
- current replay
- deterministic evidence

Avoid unqualified:
- safe
- secure
- production-ready
- guaranteed
- complete causal graph
- fully recovered

Use one memorable line consistently:

`No restored authority without complete represented recovery evidence and a current scope-bound replay.`

## Acceptance criteria for the visual layer

The UI is acceptable only if:
- every displayed fact is backed by the generated artifact
- no UI state grants execution authority
- unavailable evidence renders as unrepresented, not favorable
- residual irreversible effects remain visible
- the compromised root remains visually distinguishable from restored downstream authority
- the page can be understood without reading repository code
- the main incident story can be demonstrated in under 2 minutes
- the page works reliably enough to screen-record and, if hosted, to be judged without credentials
