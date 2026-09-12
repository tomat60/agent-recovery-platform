# Builder AWS Post Draft

Status: private working draft for final fact-check after the security re-audit and exact-head merge. Do not publish until all metrics and claims are synchronized to the submitted head.

## Proposed title

Agents for Humans: What a Green Test Suite Missed in an AI Agent Recovery System

## Subtitle

How an adversarial architecture audit changed the way I think about recovery, replay, and authority restoration for write-capable AI agents.

## Draft

I started this hackathon with a simple question:

What happens after an autonomous AI agent has already done the wrong thing?

A lot of agent security work focuses on prevention. Prompt injection filters, tool policies, permissions, approval gates, monitoring, and kill switches are all important. But once an agent can write to shared memory, customer records, permissions, configuration, or communication systems, prevention is only half of the operational problem.

If the failure already happened, a team still needs to answer:

- What changed?
- Which later actions depended on the compromised state?
- What can actually be reversed?
- What requires compensation?
- What is irreversible?
- When is it safe to restore authority?

That became Agent Recovery Platform, my project for the Agents for Humans Hackathon.

The recovery lifecycle is:

`incident -> containment -> evidence -> recovery -> replay -> verified restoration`

The project uses Strands Agents for evidence-bound investigation, recovery planning, and skeptical review. But there is an important design constraint: model output is advisory only. It cannot authorize recovery execution or restore authority.

Those boundaries belong to deterministic controls.

## The first architecture

The system grew around a few core ideas:

1. Every consequential tool action has a Recovery Contract describing side effects, recovery class, verification, compensation, and approval requirements.
2. A tamper-evident local action ledger records represented effects and causal relationships independently from the agent's narration.
3. Containment limits affected authority while the incident is investigated.
4. Recovery reconstructs represented dependencies and shared-state hazards before changing state.
5. An isolated Replay Lab reruns a represented attack path after recovery.
6. Authority restoration is separate from recovery and requires deterministic evidence.

The Strands layer consists of three evidence-only roles:

- Investigator: reconstructs likely root cause and blast radius.
- Recovery Planner: proposes an ordered candidate recovery plan.
- Skeptic/Verifier: challenges unsupported assumptions and unsafe recovery claims.

The model can propose. The control plane decides.

That separation became the most important architectural principle in the project.

## Then the tests all passed

Before submission, the project had a large deterministic test suite and a benchmark covering ten adversarial classes, including indirect prompt injection, tool-output poisoning, memory poisoning, approval bypass, privilege escalation, cascading multi-agent failure, partial compensation failure, irreversible external effects, runaway loops, and attacks on the recovery path itself.

The suite was green.

That felt good, but it was not proof.

So instead of using the final days only for presentation polish, I ran an adversarial architecture audit whose job was to falsify the safety thesis.

The instruction was deliberately hostile: find a concrete sequence where individually reasonable components compose into an unsafe lifecycle, even if all existing tests continue to pass.

It did.

## The dangerous bugs were between the components

The most useful findings were not simple syntax bugs or missing branches. They were composition failures.

The audit found cases such as:

- restoration could be authorized without proving all represented recovery obligations were complete,
- replay evidence could be too weakly bound to the exact source action and current recovery state,
- containment state could be lost when reconstructing a controller from retained evidence,
- a one-shot approval could be reused across pre-existing controllers sharing the same ledger,
- recovering an earlier write could destroy a later legitimate shared-state write,
- recovery verification could trust a target value selected by the compensator itself,
- exported evidence could accidentally share mutable nested objects with retained ledger state,
- ambiguous executor failures could leave side effects outside recovery accounting.

Every one of these bugs taught the same lesson:

A safe transition is not automatically a safe lifecycle.

Containment can be correct in isolation. Recovery can be correct in isolation. Replay can be correct in isolation. Restoration can be correct in isolation. The system can still fail if the evidence connecting those stages is stale, incomplete, cross-incident, or insufficiently bound.

## Turning the audit into architecture

I treated the findings as submission blockers, not as documentation notes.

The hardened design now focuses on stronger lifecycle invariants:

- containment must be reconstructable from retained represented evidence,
- approval consumption must be authoritative within the shared bounded ledger runtime,
- recovery approval must be bound to the actual recovery operation and context,
- malformed security metadata must fail before side effects,
- shared-state recovery must protect later legitimate writers,
- recovery verification must compare against trusted preserved state rather than a value chosen by the compensator,
- replay must bind to the represented source action, execution-time source/recovery state, contract versions, and one proposed release scope,
- stale or superseded replay evidence must fail closed,
- restoration requires complete represented recovery obligations and a current applicable replay,
- irreversible or failed-compensation effects remain explicit residual risk.

Just as importantly, the public claims became narrower.

The prototype does not claim authenticated ledger completeness, valid-prefix rollback resistance without external anchoring, distributed consensus, universal causal capture, remote proof-forgery resistance, full production topology equivalence, or production security effectiveness.

A security project becomes less credible when its marketing outruns its evidence.

## Why replay is not just another test

One of the most interesting parts of the design is the Replay Lab.

After recovery, the system reconstructs a bounded isolated environment and reruns the represented attack action. The replay is not allowed to simply say "the current state looks fine." It has to preserve relevant execution identity and prove that the represented unsafe action cannot succeed under the recovery state being evaluated.

Even that required careful hardening.

A replay can be misleading if it blocks the attack using a control that would disappear immediately after authority is restored. It can also be misleading if the replayed tool, parameters, contract version, or environment no longer match the represented source action.

That is why replay provenance and restoration provenance have to be treated as one security boundary, not two loosely connected features.

## Strands is useful precisely because it is not the authority

The hackathon theme is about agents doing real work. For this project, the agentic work is investigation and judgment-heavy planning.

Strands is valuable because it can:

- synthesize evidence into a root-cause hypothesis,
- reconstruct a likely multi-agent story,
- propose ordered recovery actions,
- identify missing evidence,
- challenge a plan from a skeptical perspective.

But the same flexibility that makes an LLM useful for investigation makes it a poor final authorization primitive.

So the architecture intentionally separates:

`agentic reasoning` from `deterministic authority`.

The system benefits from model intelligence without treating model confidence as permission to mutate state.

## The competition demo

The final demo focuses on one synthetic multi-agent cascade rather than a feature tour.

A poisoned input reaches a support agent, compromised shared state affects downstream agents, and the platform reconstructs the represented blast radius. The affected authority is contained. Strands agents investigate and propose a recovery. Deterministic controls decide what can execute. Recoverable state is restored where evidence supports it. Irreversible effects remain visible. The repaired path is replayed, and only the represented downstream authority supported by current evidence is restored.

The compromised root remains contained.

That last detail is important. A recovery system should be willing to say "not yet."

## What I learned

Three lessons changed the project most.

### 1. Recovery is a security boundary

Compensation code is privileged code. Recovery approvals, freshness, provenance, and shared-state ordering deserve the same scrutiny as the original action path.

### 2. Green tests are evidence, not proof

The best audit findings were valid state transitions composed in an unsafe order. Stateful falsification and mutation testing matter more than adding another happy-path fixture.

### 3. Honest residual risk is a feature

An external message that was already delivered is not "rolled back." If compensation fails, the failure is not "recovered." The product should preserve residual truth instead of optimizing for a green dashboard.

## Where this goes next

After the hackathon, the next steps are deliberately more production-oriented:

- authenticated durable evidence storage with externally committed heads,
- stronger causal completeness measurement,
- larger topology and environment binding for replay,
- stateful property/model checking including concurrency and ABA schedules,
- authenticated capability/issuer boundaries for approvals and recovery APIs,
- integration with existing SIEM, identity, and agent-security products.

The long-term goal is not to replace prevention.

It is to make recovery from autonomous-agent incidents a first-class engineering discipline.

The rule I keep coming back to is simple:

`No restored authority without complete represented recovery evidence and a current scope-bound replay.`

## Final publication checklist

Before publishing:
- replace all test-count/CI references with exact submitted-head facts
- verify all security claims against final GPT-6 targeted re-audit
- add architecture diagram or console screenshot if builder.aws supports it
- add public repository link
- add public demo video link when available
- add `#AgentsforHumans` if required by the final live contest rules/UI
