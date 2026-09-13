# Final Demo Video Production Plan

Target runtime: **3:20–3:50**. Hard limit: **under 5:00**.

The video should feel like a product demo, not a slide deck and not a terminal walkthrough. The main visual is the one-page Judge Incident Recovery Console in `demo/index.html`, with short inserts of the architecture diagram and GitHub Actions evidence.

## Production approach

Use three visual sources only:

1. **Judge Console** — full-screen browser capture at 1440p or 1080p, 16:9.
2. **Architecture diagram** — `docs/assets/architecture-competition.svg`, shown full-screen for the trust-boundary explanation.
3. **GitHub evidence** — a clean crop of the final green Actions run and repository headline facts. No unrelated tabs, account data, billing, secrets or browser chrome if avoidable.

Paweł records voiceover only. The visual edit can be assembled independently around that audio.

## Storyboard and voiceover

### 0:00–0:15 — Hook

**Visual:** Judge Console title area. Start on phase 1, Incident.

**On-screen text:**
`AI agents can change real state. What happens after prevention fails?`

**Voiceover:**
AI agents are starting to change real state: customer records, shared memory, access controls and workflows. A kill switch can stop the next action, but it cannot explain what already changed or when authority is safe to restore.

### 0:15–0:35 — Thesis

**Visual:** Click through the six lifecycle buttons quickly, then pause on the full strip.

**On-screen text:**
`incident → containment → evidence → recovery → replay → verified restoration`

**Voiceover:**
Agent Recovery Platform is a recovery-first safety layer. It reconstructs represented side effects, contains affected authority, recovers what is actually recoverable, preserves residual risk, runs bounded replay, and restores only downstream authority supported by current deterministic evidence.

### 0:35–1:05 — Incident and blast radius

**Visual:** Phase 1 → phase 2 → phase 3. Keep the three-agent chain centered.

**On-screen text:**
`3 / 3 represented blast actions detected`
`Recall 1.0 • Precision 1.0`

**Voiceover:**
In this bounded deterministic fixture, poisoned external content reaches a support agent and contaminates shared state. Downstream workflow and identity authority are affected. The platform reconstructs the represented causal path instead of trusting the compromised agent's narration. All three expected blast actions are detected in this fixture.

### 1:05–1:35 — Trust boundary

**Visual:** Open the Architecture view. Hold for the full explanation.

**On-screen text:**
`Strands: investigate, propose, challenge`
`Deterministic control plane: authorize, recover, replay, restore`

**Voiceover:**
Strands agents investigate evidence, propose recovery and challenge assumptions, but they never receive execution authority. Deterministic code owns contracts, the ledger, containment, recovery verification, replay admission and restoration. Model output is advisory, not authorization.

### 1:35–2:10 — Recovery integrity

**Visual:** Return to incident and move to phase 4. Highlight Recovery proof card.

**On-screen text:**
`Recovery target = preserved pre-action evidence`
`Failed or irreversible effects remain residual risk`

**Voiceover:**
Recovery itself is treated as a security boundary. The expected recovered state comes from preserved pre-action evidence, not from the recovery builder or executor. Shared-state writers can block unsafe rollback, approvals are single-use in the bounded runtime, and failed or irreversible effects remain visible as residual risk rather than being relabeled as recovered.

### 2:10–2:40 — Replay and selective restoration

**Visual:** Phase 5, then phase 6. Let Workflow Agent and Identity Agent change from Held to Restored while Support Agent stays red and contained.

**On-screen text:**
`Replay: exact represented source action`
`2 downstream authorities restored`
`Root remains contained`

**Voiceover:**
Recovery is not enough to restore authority. The system replays the exact represented attack action in isolation against repaired state. Replay evidence is bound to the incident, source action, state generation, represented contract versions and release scope. Only then can selected downstream authority return. The compromised root remains contained.

### 2:40–3:12 — Adversarial hardening and proof

**Visual:** Clean GitHub Actions crop. Show Python 3.10, Python 3.12, green run, then a compact overlay: `120 tests → adversarial audit → 139 → re-audit → 152 → Codex acceptance audit → 153`.

**On-screen text:**
`153 deterministic tests`
`Python 3.10 + 3.12`
`B01–B10`
`Credential-free judge reproduction`

**Voiceover:**
We deliberately tried to break this architecture before submission. A green 120-test build still had unsafe lifecycle compositions. An adversarial GPT-6 audit found them. A targeted re-audit found more. The final Codex acceptance audit found one additional recovery-target provenance flaw. Each confirmed blocker was fixed and converted into regression coverage. The accepted code now passes 153 deterministic tests on Python 3.10 and 3.12, benchmark smoke and credential-free judge reproduction.

### 3:12–3:30 — Close

**Visual:** Return to Judge Console phase 6. Fade to product mark and invariant.

**On-screen text:**
`No restored authority without complete recovery evidence and a current scope-bound replay.`

Small footer:
`Synthetic bounded evidence. No production security-effectiveness claim.`

**Voiceover:**
The goal is not to pretend autonomous agents never fail. It is to make failure recoverable, auditable and explicit. No restored authority without complete represented recovery evidence and a current scope-bound replay.

## Voiceover recording instructions

Paweł should record the seven sections separately, not as one continuous take. This makes timing and editing easier.

- Quiet room, phone or decent USB microphone is enough.
- Record WAV or high-quality M4A if available.
- Speak naturally, slightly slower than conversation.
- Leave about one second of silence before and after each section.
- Do not read headings or on-screen text verbatim unless it is already in the spoken script.
- If one sentence is difficult, record it again as a separate take instead of restarting the full section.

## Capture rules

- 16:9, 1080p or 1440p.
- Keep the mouse movement deliberate and slow.
- Browser zoom should keep the entire console readable without scrolling during the main incident sequence.
- Do not show private browser tabs, AWS account details, credentials, account IDs or unrelated projects.
- Terminal/code footage should be omitted unless a final edit needs a very short texture shot.
- The video should end under 4 minutes if the story is already clear; do not pad toward the 5-minute maximum.

## Claim guardrails

Do not claim production security effectiveness, universal attack prevention, arbitrary production rollback, distributed-controller consensus, authenticated ledger completeness, full production replay equivalence, or safe restoration of the compromised source/root agent. The demonstrated evidence is synthetic, deterministic and bounded to the represented fixtures.
