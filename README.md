# Agent Recovery Platform

A recovery-first safety layer for autonomous AI agents.

## Thesis

Most agent security products focus on prevention, monitoring, permissions or detection. Those controls matter, but incidents still happen. The hard question becomes: what exactly changed, what can be reversed, what requires compensation, what remains irrecoverable, and what evidence is sufficient before authority is restored?

This project is built around two rules:

> No autonomous write without a recovery path.
>
> No restored authority without complete recovery evidence and a current scope-bound replay.

The platform records consequential agent actions, classifies recoverability, contains compromised authority, reconstructs blast radius, builds recovery candidates, executes only deterministic policy-approved recovery actions in owned or synthetic environments, verifies resulting state independently, and uses bounded replay evidence before represented downstream authority can be restored.

The competition path intentionally keeps the compromised replay source/root agent contained rather than claiming that its own replay proves it safe to restore.

## Product boundary

This is not a SIEM, IAM, EDR, generic prompt-injection firewall or broad AI-governance suite. It integrates with prevention, detection and identity systems and owns a narrower outcome:

**incident -> containment -> evidence -> recovery -> replay -> verified restoration**

Irreversible external effects are never represented as undone. Failed compensation remains visible as residual risk.

## Core capabilities

1. **Recovery Contract Registry**
   - Every write-capable tool declares side effects, risk, reversibility, compensation path, verification method and approval requirements.
2. **Action + Side-Effect Ledger**
   - Records intended and observed effects independently from agent narration, detaches exported evidence from stored payloads and protects the retained local history with chained integrity checks. The prototype does not claim authenticated completeness or valid-prefix rollback resistance without external anchoring.
3. **Containment Plane**
   - Freezes represented agent/tool authority without destroying evidence. Controllers sharing one in-memory ledger observe the same represented active holds, and independent incidents can retain separate holds on the same scope.
4. **Investigation and Blast Radius**
   - Reconstructs causal chains across prompts, tool calls, memory, approvals, identities and downstream actions represented in the ledger.
5. **Recovery Planner + Deterministic Gate**
   - Strands can propose recovery steps; deterministic controls rebind proposals to incident evidence and decide whether a candidate is executable. Model output is not authorization.
6. **Skeptic / Verifier**
   - Independently challenges root-cause and recovery hypotheses. Model output never authorizes execution or restoration.
7. **Recovery Executor + State Verification**
   - Applies bounded reversible or compensating actions in synthetic/owned state and compares an independent read to a target derived from preserved pre-action evidence. Recovery builders and executors cannot define the success target. Direct recovery adapter failures remain explicit as failure/residual evidence.
8. **Replay Lab**
   - Replays an exact represented attack action in an isolated synthetic runtime, binds the run to source/recovery state, source contract versions and one proposed release scope, and can invalidate a false restoration claim. The competition path rejects positive replay admission that would restore that replay's own source agent. This is not a claim of complete production-environment replay equivalence.
9. **Fresh Scoped Restoration**
   - Applies an authorized downstream restoration only while the decision is current and only to one exact active incident hold. Intervening work or reuse makes the decision stale.
10. **Incident-to-Regression Loop**
   - Converts confirmed incident evidence and adversarial counterexamples into permanent regression contracts.

## Competition build

The 2026 Agents for Humans build has a fully credential-free deterministic judge path. It covers B01-B10 adversarial fixture classes, full incident evidence, authority-free judge rendering, canonical JSON packaging with SHA-256 manifests, one-command incident reproduction and an exact-head package acceptance gate.

Strands Agents SDK is used for evidence-only investigation, recovery planning and skeptical review. Deterministic modules retain authority over contracts, approvals, recovery execution, verification and scoring.

Amazon Bedrock and AgentCore remain optional live-path integrations. They are not required to reproduce the deterministic evidence and no live AWS security-effectiveness claim is made without separate evidence and owner-approved access/cost.

## Accepted technical evidence

Accepted security code anchor before presentation-only packaging:

`b997384addd8781e0dac153d92adabcf9cc11757`

GitHub Actions run `34762391263` passed on that exact code state with:

- Python 3.10: PASS
- Python 3.12: PASS
- Ruff: PASS
- 153 deterministic tests: PASS
- adversarial benchmark contract B01-B10: PASS
- B06 blast-radius recall: 1.0 in the bounded fixture
- B06 blast-radius precision: 1.0 in the bounded fixture
- B06 verified recoveries: 3
- B06 restored downstream authorities: 2
- B06 compromised root remains contained: true
- measured authority-resurrection successes: 0
- credential-free judge reproduction: PASS
- canonical incident evidence validation and round trip: PASS
- SHA-256 manifest verification: PASS
- authority-free judge reproduction manifest: PASS

These are synthetic deterministic fixture measurements only. They do not establish global or production security effectiveness.

## Adversarial hardening

The project deliberately treated green tests as a hypothesis, not proof.

- A GPT-6 architecture audit attacked a green 120-test baseline and found lifecycle counterexamples.
- A targeted GPT-6 re-audit attacked the hardened 139-test build and found four additional blockers around source-agent restoration, restoration freshness/reuse, shared-ledger containment and independent incident holds.
- After those remediations the suite reached 152 tests.
- A final Codex acceptance audit found one additional High recovery-target provenance flaw. Recovery success could be influenced by recovery-side code. PR #70 fixed that by deriving verification targets from preserved pre-action evidence and added the exact malicious-builder + no-op-executor counterexample as the 153rd regression.

Confirmed issues were fixed rather than hidden or reclassified.

## Judge Console

`demo/index.html` is the competition-facing one-page Incident Recovery Console. It is presentation-only and grants no execution authority.

It visualizes:

- the incident lifecycle,
- the three-agent represented blast radius,
- shared containment,
- independently verified recovery,
- bounded replay,
- selective downstream restoration while the compromised root remains contained,
- the explicit separation between Strands advisory reasoning and deterministic authority.

The architecture diagram used in the submission package is `docs/assets/architecture-competition.svg`.

## Judge reproduction

The default judge path is credential-free and deterministic:

1. reproduce the bounded synthetic incident,
2. validate the represented incident evidence contract and cross-field semantics,
3. render only represented evidence,
4. canonicalize/package evidence and validate SHA-256 manifests,
5. verify recovery/residual truth and bounded replay behavior,
6. run the exact-head final package acceptance gate.

## Repository map

- `demo/index.html` - interactive presentation-only Judge Console
- `docs/VIDEO_PRODUCTION_PLAN.md` - final video storyboard and voiceover script
- `docs/DEVPOST_FINAL_DRAFT.md` - final owner-review submission copy
- `docs/SUBMISSION_FINAL_CHECKLIST.md` - final execution checklist
- `docs/assets/architecture-competition.svg` - competition architecture diagram
- `docs/PRODUCT_STRATEGY.md` - market wedge, scope, buyer, monetization and kill criteria
- `docs/THREAT_MODEL.md` - threats and safety boundaries
- `docs/RECOVERY_CONTRACT_SPEC.md` - contract model for reversible and compensatable actions
- `docs/RECOVERY_INTEGRITY_MODEL.md` - exact integrity guarantees and explicit limits
- `docs/BENCHMARK.md` - benchmark scenarios and metrics
- `docs/ARCHITECTURE.md` - target system architecture
- `docs/PROJECT_CURRENT_STATE.md` - durable execution checkpoint
- `docs/JUDGE_EVIDENCE_INDEX.md` - final judge claim/evidence map
- `src/agent_recovery/` - deterministic recovery/control code
- `tests/` - deterministic safety, benchmark and recovery tests

## Initial buyer

The first target is an AI-native SaaS, fintech, devtools or security company already operating agents with real write permissions but without mature recovery controls.

The first commercial offer is a bounded **Agent Recoverability Assessment** for one workflow, not a large enterprise-platform contract. It maps the workflow, classifies recovery paths, exercises controlled incidents, measures recovery coverage, verifies containment/compensation behavior and produces a remediation report.

## Safety and explicit limits

All adversarial development and demos use owned or synthetic environments. The project is defensive.

The competition build does **not** claim:

- production security effectiveness,
- universal attack prevention,
- arbitrary production rollback,
- reversal of irreversible external effects,
- authenticated ledger completeness or valid-prefix rollback resistance,
- distributed-controller consensus,
- remote proof/approval forgery resistance without an authenticated issuer boundary,
- globally complete causal capture with missing instrumentation,
- full production replay topology/provider/time equivalence,
- demonstrated safe restoration of the compromised source/root agent,
- live Bedrock/AgentCore security effectiveness without separate evidence.

## Current status

Security acceptance is complete for the accepted code anchor above. The final lane is presentation-only packaging: Judge Console, architecture, video, Devpost copy and exact-head verification after the final documentation/demo merge.

Public video upload, AWS Builder ID, competition terms and final Devpost submission remain owner actions.

## License

MIT
