# Final Demo Video Production Plan

Target runtime: **3:15–3:40**. Hard limit: **under 5:00**.

The video should feel like one coherent product demo, not a slide deck and not a terminal walkthrough. The primary visual is the one-page Judge Incident Recovery Console in `demo/index.html`. The Architecture and Evidence views are built into the same page so the edit can stay visually consistent.

Paweł records voiceover only. The visual capture and edit should be assembled around the prepared narration.

## Visual sources

Use the Judge Console for almost the entire video:

- Incident phases 1–6
- Architecture view
- Evidence view

Optional: one 3–5 second clean crop of the final green GitHub Actions run if it improves credibility. It is not required because the Evidence view already presents the accepted facts in the same visual language.

## Storyboard and voiceover

### 0:00–0:14 — Hook

**Visual**
Judge Console title area, phase 1 selected.

**On-screen text**
`AI agents can change real state. What happens after prevention fails?`

**Voiceover**
AI agents are starting to change real state: customer records, shared memory, access controls and workflows. A kill switch can stop the next action, but it cannot explain what already changed or when authority is safe to restore.

### 0:14–0:34 — Thesis

**Visual**
Move across the six lifecycle buttons, then pause on the strip.

**On-screen text**
`incident → containment → evidence → recovery → replay → verified restoration`

**Voiceover**
Agent Recovery Platform is a recovery-first safety layer. It reconstructs represented side effects, contains affected authority, recovers what is actually recoverable, preserves residual risk, runs bounded replay, and restores only downstream authority supported by current deterministic evidence.

### 0:34–1:02 — Incident and blast radius

**Visual**
Phase 1 → phase 2 → phase 3. Keep the three-agent chain centered.

**On-screen text**
`3 / 3 represented blast actions detected`
`Recall 1.0 • Precision 1.0`

**Voiceover**
In this bounded deterministic fixture, poisoned external content reaches a support agent and contaminates shared state. Downstream workflow and identity authority are affected. The platform reconstructs the represented causal path instead of trusting the compromised agent's narration. All three expected blast actions are detected in this fixture.

### 1:02–1:32 — Trust boundary

**Visual**
Open `Architecture`. Hold long enough to read the two zones.

**On-screen text**
`Strands: investigate, propose, challenge`
`Deterministic control plane: authorize, recover, replay, restore`

**Voiceover**
Strands agents investigate evidence, propose recovery and challenge assumptions, but they never receive execution authority. Deterministic code owns contracts, the ledger, containment, recovery verification, replay admission and restoration. Model output is advisory, not authorization.

### 1:32–2:04 — Recovery integrity

**Visual**
Back to incident. Select phase 4 and hold on the Recovery evidence.

**On-screen text**
`Recovery target = preserved pre-action evidence`
`Failed or irreversible effects remain residual risk`

**Voiceover**
Recovery itself is treated as a security boundary. The expected recovered state comes from preserved pre-action evidence, not from the recovery builder or executor. Shared-state writers can block unsafe rollback, approvals are single-use in the bounded runtime, and failed or irreversible effects remain visible as residual risk instead of being relabeled as recovered.

### 2:04–2:34 — Replay and selective restoration

**Visual**
Phase 5 → phase 6. Let Workflow Agent and Identity Agent switch from Held to Restored while Support Agent stays red and contained.

**On-screen text**
`Replay: exact represented source action`
`2 downstream authorities restored`
`Root remains contained`

**Voiceover**
Recovery is not enough to restore authority. The system replays the exact represented attack action in isolation against repaired state. Replay evidence is bound to the incident, source action, state generation, represented contract versions and release scope. Only then can selected downstream authority return. The compromised root remains contained.

### 2:34–3:08 — Evidence and adversarial hardening

**Visual**
Open `Evidence` view. Hold on the 153 tests / Python / B01–B10 / Judge reproduction cards, then highlight the hardening sequence.

**On-screen text**
`153 deterministic tests`
`Python 3.10 + 3.12`
`B01–B10`
`Credential-free judge reproduction`

**Voiceover**
We deliberately tried to break this architecture before submission. A green 120-test build still had unsafe lifecycle compositions. An adversarial GPT-6 audit found them. A targeted re-audit found more. The final Codex acceptance audit found one additional recovery-target provenance flaw. Each confirmed blocker was fixed and converted into permanent regression coverage. The accepted code now passes 153 deterministic tests on Python 3.10 and 3.12, benchmark smoke and credential-free judge reproduction.

### 3:08–3:28 — Close

**Visual**
Return to phase 6. Fade to product title and invariant.

**On-screen text**
`No restored authority without complete recovery evidence and a current scope-bound replay.`

Small footer:
`Synthetic bounded evidence. No production security-effectiveness claim.`

**Voiceover**
The goal is not to pretend autonomous agents never fail. It is to make failure recoverable, auditable and explicit. No restored authority without complete represented recovery evidence and a current scope-bound replay.

## Voiceover recording instructions

Record the seven sections separately, not as one continuous take.

- Quiet room, phone or decent USB microphone is enough.
- WAV or high-quality M4A preferred.
- Speak naturally, slightly slower than conversation.
- Leave about one second of silence before and after each section.
- If one sentence is difficult, record that sentence again rather than restarting the full section.
- Do not add improvised technical claims beyond the script.

## Capture and edit rules

- 16:9, 1080p or 1440p.
- Keep mouse movement deliberate and slow.
- Keep the browser zoom such that the main console is readable without scrolling during phases 1–6.
- Prefer simple cuts and short crossfades over flashy motion graphics.
- Architecture and Evidence should open from the console itself so the film feels like one product.
- Do not show private tabs, AWS account details, credentials, account IDs or unrelated projects.
- Terminal/code footage should be omitted unless a final edit clearly benefits from a very brief proof insert.
- If the story is clear around 3:20, do not pad toward the five-minute maximum.

## Claim guardrails

Do not claim production security effectiveness, universal attack prevention, arbitrary production rollback, distributed-controller consensus, authenticated ledger completeness, full production replay equivalence, live AWS security effectiveness without evidence, or safe restoration of the compromised source/root agent.

The demonstrated evidence is synthetic, deterministic and bounded to the represented fixtures.
