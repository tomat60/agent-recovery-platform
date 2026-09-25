# Kyvvu discovery call - 2026-09-30 11:30

Purpose: keep the pre-TechEx call light, useful and low-stress. This is a qualification / relationship-building call, not a technical diligence session and not a sales pitch.

## Target outcome

Leave the call with:
- mutual understanding of what each product does;
- one concrete overlap hypothesis worth exploring in Amsterdam;
- confirmation that the TechEx meeting is still useful;
- no commitments beyond a next conversation / in-person discussion.

## 20-minute shape

### 0-3 min - easy opening

- Thank Jeroen for making time while travelling.
- Ask one simple opener about his route / TechEx preparation.
- Keep this conversational; do not start with architecture.

Suggested opening:

> Hi Jeroen, thanks for fitting this in while you're on the road. I’ll keep it light. I mainly wanted to get to know each other a bit before Amsterdam and make sure we’re looking at the overlap in the right way.

### 3-7 min - Kyvvu first

Ask him to explain Kyvvu in his own words:
- What kind of agent workflows are they seeing most often?
- Where does ASK sit in the stack today?
- What problem are customers most worried about before an action executes?

Do not interrupt to prove similarity. Listen for:
- pre-action authorization / policy;
- write-capable agents;
- evidence / telemetry;
- customer incidents or recovery gaps;
- integration surfaces.

### 7-11 min - Agent Recovery in plain language

Use only this level unless Jeroen asks deeper questions:

> Agent Recovery focuses on what happens after an allowed action still produces a bad outcome. We want to know exactly what changed, contain further damage, recover or compensate what can be recovered, keep irreversible effects explicit, replay the failure and only restore authority when the evidence supports it.

Then:

> The interesting overlap for me is that Kyvvu can decide whether an action should be allowed, while Agent Recovery can prove whether that action had a recovery path and whether the system is actually safe to restore after something goes wrong.

Avoid feature dumping. Avoid claiming production effectiveness beyond current evidence.

### 11-16 min - qualify the overlap

Questions:
1. Do Kyvvu customers already ask what happens after an allowed-but-wrong action?
2. Does ASK expose enough action context / policy evidence that a downstream recovery layer could consume it?
3. Would Kyvvu rather integrate with a recovery layer, refer customers to one, or keep that capability in-house?
4. Is there one realistic workflow we could sketch together at TechEx?

If he raises roadmap overlap, answer openly:
- some adjacency is expected;
- the purpose is to identify complementary boundaries early;
- no need to force a partnership if the products converge.

### 16-20 min - close

Aim for:

> This sounds worth exploring properly in Amsterdam. I’ll bring one concrete integration scenario so we can talk about something real rather than a generic partnership.

Confirm:
- likely day / rough meeting window at TechEx if convenient;
- booth T64 as fallback;
- whether he wants anything sent beforehand.

## If technical questions get deep

Use this bridge:

> I can go deeper, but I’d rather not turn this call into a technical review while you’re driving. I can bring the exact evidence flow and recovery boundary to Amsterdam.

## What not to do

- no long pitch;
- no funding discussion unless he raises it;
- no pricing unless he asks;
- no request for commitment;
- no claim that Kyvvu + Agent Recovery is already an integration;
- no unsupported production-security claims;
- no architecture dump while he is driving.

## Current verified facts to remember

- Kyvvu: Jeroen Ghijsen, Co-founder & CEO.
- TechEx Europe: 19-20 Oct 2026, RAI Amsterdam.
- Kyvvu booth: T64.
- Jeroen explicitly proposed this regular phone call before a deeper technical discussion.
- Agent Recovery current wedge: verified recovery for autonomous AI-agent side effects across multiple tools and systems.
- Current product evidence is owned/synthetic/controlled unless explicitly classified otherwise.

## One-sentence fallback if stressed

> We’re building the recovery layer for AI agents: if an allowed action causes a bad outcome, we contain it, prove what changed, recover what can be recovered, and verify the system before restoring authority.
