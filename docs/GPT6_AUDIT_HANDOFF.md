# GPT-6 Adversarial Architecture Audit Handoff

Status: owner-gated external review package. Run in ChatGPT Work only when the owner explicitly chooses to spend the available GPT-6 allowance.

## Goal

Try to falsify the safety architecture before final competition submission. Do not optimize for encouragement, feature ideation or code style. Optimize for finding a concrete architecture-level counterexample where the current implementation can pass its existing tests yet violate a stated safety invariant.

## Repository

Public repository: `https://github.com/tomat60/agent-recovery-platform`

Audit the exact current `main` head at the time of the Work run. Record that commit SHA in the output.

## Required reading order

1. `README.md`
2. `AGENTS.md`
3. `docs/PROJECT_CURRENT_STATE.md`
4. `docs/THREAT_MODEL.md`
5. `docs/ARCHITECTURE.md`
6. `docs/RECOVERY_CONTRACT_SPEC.md`
7. `docs/RECOVERY_INTEGRITY_MODEL.md`
8. `docs/BENCHMARK.md`
9. `docs/FINAL_PACKAGE_ACCEPTANCE.md`
10. `docs/JUDGE_EVIDENCE_INDEX.md`
11. all files under `src/agent_recovery/`
12. all relevant tests under `tests/`
13. `.github/workflows/ci.yml`

Treat documentation as claims, not truth. Trust executable behavior and evidence more than prose.

## Non-negotiable safety invariants to attack

- Model output is never authorization.
- Missing or malformed Recovery Contract fails consequential writes closed.
- Approval must be bound to the exact intended action and parameters.
- Evidence must be preserved before recovery mutation.
- Recovery actions receive equal or stronger controls than original actions.
- A compromised source agent cannot erase evidence, alter its governing contract, mark itself recovered or restore its own authority.
- Recovery evidence must remain bound to the correct incident and current recovery generation.
- Stale, replayed, forged, cross-incident or tampered proof must not restore authority.
- Dependency-aware recovery must not corrupt valid concurrent state.
- Irreversible external effects must never be represented as undone.
- Failed compensation must remain visible as residual risk.
- Replay must be able to invalidate a false recovery claim.
- Restoration requires independent state verification plus a fresh valid replay result.

## Attack the recovery system itself

Prioritize finding counterexamples in these classes:

1. Causal graph confusion or missing cross-agent edge.
2. Shared-state race conditions and concurrent writers.
3. ABA/version-reuse style state problems.
4. TOCTOU between evidence validation and recovery execution.
5. Recovery-contract version mismatch or downgrade.
6. Approval confusion, parameter substitution or scope widening.
7. Incident-ID, action-ID, evidence-ID or generation confusion.
8. Hash-chain integrity that detects mutation but not omission, fork or alternate valid history.
9. Replay proof generated from the wrong state, wrong topology or incomplete environment.
10. Authority resurrection after runtime reconstruction/restart.
11. Partial recovery that accidentally re-enables a still-compromised dependent agent.
12. Residual side effect hidden by local state convergence.
13. Idempotency-key reuse across incidents or generations.
14. Recovery action that is itself more privileged than the original operation.
15. Compromised Investigator, Planner or Skeptic output exploiting parser/schema ambiguity.
16. Evidence truncation causing a confident but unsafe plan rather than an `insufficient evidence` result.
17. Denial-of-wallet/runaway behavior that remains harmful even when writes are blocked.
18. Cross-tenant or cross-workflow evidence confusion if the current abstractions could permit it.
19. Serialization/deserialization or type-coercion boundaries that can weaken identity or authority checks.
20. Benchmark gaming: a way for the implementation to score well while remaining materially unsafe.

## Required method

For each suspected weakness:

1. Cite the exact files/functions/tests involved.
2. State the violated invariant.
3. Give a minimal concrete state/action sequence that triggers the issue.
4. Distinguish `confirmed from code`, `plausible but unproven`, and `out of current scope`.
5. Propose the smallest defensible correction.
6. Design a falsification test that fails before the correction and passes after it.
7. Explain whether the current benchmark would detect the issue. If not, propose the smallest benchmark change.
8. Do not recommend broad rewrites unless a local correction cannot defend the invariant.

## Formal reasoning pass

After code review, model the core lifecycle as a state machine or transition system. At minimum include:

- agent authority state,
- incident state,
- evidence generation,
- recovery generation,
- approval consumption,
- recovery execution,
- verification state,
- replay state,
- restoration state.

Identify forbidden transitions and safety properties. Look specifically for transition sequences that are individually valid but globally unsafe.

Where useful, express candidate invariants in a form suitable for property-based testing or model checking.

## Mutation-testing pass

Propose a compact set of deliberate safety mutations that a strong test suite must kill, for example:

- skip incident binding,
- accept stale replay generation,
- ignore one causal dependency,
- treat irreversible as compensatable,
- restore authority without successful replay,
- allow duplicate approval consumption,
- trust model-supplied recovery status,
- skip ledger integrity verification,
- allow recovery contract version mismatch.

Rank mutations by expected value. Prefer mutations that test architecture rather than formatting or ordinary validation.

## Output format

Produce exactly these sections:

### 1. Executive verdict
- SHIP / SHIP WITH BLOCKERS / DO NOT SHIP
- short reason
- exact audited commit SHA

### 2. Critical findings
For each: severity, confidence, violated invariant, exact code references, counterexample sequence, fix, falsification test.

### 3. High and medium findings
Same structure, concise.

### 4. Benchmark blind spots
List cases that can pass current metrics while violating the product thesis.

### 5. Formal safety model
State variables, allowed transitions, forbidden transitions and candidate invariants.

### 6. Mutation plan
Top 10 mutations in priority order and which current/new test should kill each one.

### 7. Competition claim audit
Flag any README/submission claim that is stronger than executable evidence.

### 8. Smallest pre-submission patch set
Maximum 10 items, ordered by risk reduction per implementation effort.

### 9. Post-competition research backlog
Important issues that should not destabilize the competition build now.

## Stop conditions

- Do not attack or interact with third-party systems.
- Use only repository code, synthetic reasoning and owned/local test designs.
- Do not request secrets or credentials.
- Do not change the repository directly during the first audit pass.
- Do not spend time on UI polish, naming or generic startup advice.
- Do not assume that passing tests proves an invariant.

The most valuable result is one reproducible counterexample that the current test suite misses.
