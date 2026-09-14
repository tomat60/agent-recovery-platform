# Final Judge Video Storyboard

Status: production storyboard for owner voiceover. Target runtime: **3:25–3:40**. No face camera required.

The video should feel like a concise product demonstration, not a narrated README. The Judge Console is the hero surface. Architecture and evidence appear only when they explain a decision the viewer just saw.

## Core message

**Prevention failed. The agent already changed shared state. Agent Recovery Platform determines what changed, what can actually be recovered, and what authority is safe to return.**

The memorable product loop is:

`contain -> reconstruct causality -> recover -> verify -> replay -> selectively restore`

The live Strands layer helps investigate, plan and challenge. It never owns execution authority.

## Recording rules

- 16:9, preferably 1920x1080.
- Dark Judge Console fills almost the whole frame.
- Avoid terminal footage except for a very short proof cut.
- Mouse movement should be slow and purposeful.
- No long scrolling through source code.
- On-screen captions should be short, 3–8 words where possible.
- Do not show the unsupported `Alex Rivera` detail from the raw model output.
- If the live Bedrock artifact is shown, show only sanitized ledger-backed fields, model ID, `authorization_effect: none`, Skeptic verdict and SHA-256 proof.
- Background music, if used at all, stays quiet and neutral. Voice must dominate.

## Shot-by-shot plan

### 0:00–0:11 — Cold open

**Picture:** Black/dark background. Product title fades in, then immediately cuts to the Judge Console showing the incident state.

**On-screen text:**

`When prevention fails, recovery must be provable.`

**Voiceover 01:**

> AI agents are starting to change real systems, not just generate text. When one of those actions goes wrong, stopping the agent is only the beginning.

### 0:11–0:31 — The problem

**Picture:** Incident card. Show poisoned support input flowing into the Support Agent, then downstream agents. Red/amber state appears.

**On-screen text:**

`Bad answer -> state-changing incident`

then

`What changed? What propagated? What is safe to restore?`

**Voiceover 02:**

> Agent Recovery Platform is built for the moment after prevention has already failed. It reconstructs the represented blast radius across agents and shared state, then contains affected authority before recovery begins.

### 0:31–0:58 — Causality and containment

**Picture:** Advance Judge Console through Incident, Containment and Evidence. Highlight the causal chain and three represented actions. Root remains red. Downstream authority remains held.

**On-screen text:**

`Blast radius: 3 / 3 represented actions`

`Root: contained`

**Voiceover 03:**

> In this bounded scenario, poisoned external input reaches shared memory, changes a CRM record, and propagates into identity authority. The ledger records that path independently from the agents' own narration, and containment follows the represented dependencies.

### 0:58–1:23 — Live Strands proof

**Picture:** Switch to a dedicated advisory panel or architecture view. Show three cards: Investigator, Recovery Planner, Skeptic. Add a small LIVE AWS badge and the model ID. Briefly flash the terminal PASS capture or a sanitized evidence card, not raw prose.

**On-screen text:**

`LIVE: Strands + Amazon Bedrock`

`Claude Haiku 4.5 • EU inference`

`NO EXECUTION AUTHORITY`

**Voiceover 04:**

> The advisory layer is real Strands running on Amazon Bedrock. Investigator reconstructs the incident, Recovery Planner proposes candidate steps and residual risks, and Skeptic challenges unsupported claims. These agents have no tools and no execution authority.

### 1:23–1:42 — Why the boundary matters

**Picture:** Architecture split-screen: advisory reasoning on left, deterministic control plane on right. Make the divider visually strong.

**On-screen text:**

`Model advice != recovery proof`

**Voiceover 05:**

> That separation is deliberate. A model can reason well and still add an unsupported detail. So no model output can make its own recovery claim true. Authority stays behind deterministic gates.

### 1:42–2:10 — Recovery integrity

**Picture:** Return to Judge Console. Advance to Recovery. Show pre-action evidence, verified recovery chips, residual-risk indicator. Prefer visual before/after state rather than text-heavy output.

**On-screen text:**

`Recovery target = preserved pre-action evidence`

`Verified recoveries: 3`

**Voiceover 06:**

> Recovery targets come from preserved pre-action evidence, not from the code performing recovery. Reversible effects are restored, compensatable effects are checked, and anything irreversible or unverified remains explicit as residual risk.

### 2:10–2:34 — Replay

**Picture:** Advance to Replay. Show attack-path replay entering an isolated box, then PASS. Keep root still contained.

**On-screen text:**

`Replay the represented attack`

`Fresh • scope-bound • single-use`

**Voiceover 07:**

> Then the platform replays the represented attack path against repaired state. Replay evidence is bound to the incident, source action, current state, contract versions and proposed release scope. Stale or mismatched evidence fails closed.

### 2:34–2:55 — Selective restoration

**Picture:** Advance to Restoration. Downstream nodes transition amber -> green. Root stays red.

**On-screen text:**

`Restore only what current evidence supports`

`Compromised root remains contained`

**Voiceover 08:**

> Only after recovery and replay pass can authority return. In this fixture, two downstream authorities are restored. The compromised root agent intentionally stays contained.

### 2:55–3:17 — Evidence, not marketing claims

**Picture:** Evidence view. Animate the proof chips one at a time: 153 tests, Python 3.10/3.12, B01–B10, judge reproduction, adversarial audits, live Bedrock proof.

**On-screen text:**

`153 deterministic tests`

`B01–B10 benchmark`

`Adversarially audited`

`Live Bedrock advisory proof`

**Voiceover 09:**

> The competition build is backed by 153 deterministic tests, the B01 through B10 adversarial benchmark, exact-head CI, repeated adversarial audits, and a separate live Strands plus Bedrock proof. The strongest security claims remain reproducible without cloud credentials.

### 3:17–3:36 — Product / impact close

**Picture:** Pull back to clean architecture/product hero. End on product name and one sentence.

**On-screen text:**

`AI Agent Incident Recovery`

`Know what can safely come back.`

Small footer:

`github.com/tomat60/agent-recovery-platform`

**Voiceover 10:**

> The goal is not an undo button. It is an incident recovery control plane for write-capable AI agents: contain the failure, prove the recovery, and restore only what is safe to bring back.

## Voiceover package for owner

Record the 10 numbered voiceover blocks as **separate audio files**, not one long take. Natural pace is better than racing. Leave about half a second of silence before and after every clip.

Suggested filenames:

- `VO01_cold_open.wav`
- `VO02_problem.wav`
- `VO03_causality.wav`
- `VO04_live_strands.wav`
- `VO05_boundary.wav`
- `VO06_recovery.wav`
- `VO07_replay.wav`
- `VO08_restoration.wav`
- `VO09_evidence.wav`
- `VO10_close.wav`

If one block is difficult to record cleanly, split it at a sentence boundary. Do not rerecord the entire narration.

## Edit priorities

If the video runs long, cut pauses and visual dwell time first. Do **not** remove the following four moments:

1. incident propagation,
2. live Strands + Bedrock proof with `NO EXECUTION AUTHORITY`,
3. deterministic recovery/replay/restoration sequence,
4. final evidence panel.

If runtime must be reduced below 3:20, compress the architecture explanation before cutting any of those four.

## Claims that must not appear

Do not say or imply:

- first / only agent recovery system,
- production-proven security,
- arbitrary rollback of external systems,
- live AgentCore deployment unless separately completed and verified,
- that the LLM itself verifies or authorizes recovery,
- that the compromised root agent is restored,
- that all agent failures are recoverable.

## Final capture gate

Do not record the final screen capture until the Judge Console contains the live-proof panel and has passed a browser QA pass at 1920x1080. The voiceovers can be recorded before that because the timing and narrative above are intentionally UI-layout-independent.