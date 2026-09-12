# Submission Execution Plan - 2026-09-12

Status: working plan on a separate submission-prep branch. Do not merge into the audited remediation branch before the targeted GPT-6 re-audit completes.

## Competition facts that drive the plan

Agents for Humans is judged in two stages. Stage One is pass/fail for theme/tool fit. Stage Two uses five equally weighted criteria:

1. Technical Implementation
2. Design
3. Potential Impact
4. Creativity & Originality
5. Presentation

Official submission requirements include:

- text description
- public repository with all source/assets/setup instructions
- MIT or Apache license visible in repository metadata/About
- README
- architecture diagram
- public demo video no longer than 5 minutes
- AWS Builder ID
- optional live demo link

A live demo and/or AgentCore deployment strengthens Technical Implementation. A public builder.aws.com build-story post can add up to 0.6 bonus points in Stage Two, 0.2 per eligible post.

Submission deadline: September 14, 2026 at 5:00 PM PDT.

Official sources:
- https://agentsforhumans.devpost.com/
- https://agentsforhumans.devpost.com/rules
- https://agentsforhumans.devpost.com/details/faqs

## AWS account runway confirmed 2026-09-12

The owner successfully activated a new AWS Free account plan.

Observed account state:
- USD 100.00 initial credits available
- 182 days remaining in the free-plan exploration period
- USD 0.00 current-month cost at activation
- no paid-plan upgrade required for the current competition plan

Current AWS documentation lists both Amazon Bedrock and Amazon Bedrock AgentCore among services supported in the new free-plan experience. New customers can earn up to an additional USD 100 through five guided activities, USD 20 each:
- AWS Budgets
- Amazon Bedrock playground
- AWS Lambda web app
- Amazon EC2 instance
- Amazon RDS database

Cost-control order:
1. complete the AWS Budgets activity first and set conservative alerts
2. complete the Bedrock playground activity second because it directly supports the competition path
3. do not launch EC2/RDS merely for credits until the core submission is secure
4. test AgentCore only with a bounded experiment tied to the actual demo/architecture claim
5. remain on Free plan before submission unless a verified blocker requires otherwise

Do not expose account identifiers, credentials, access keys or billing details in the repository or submission evidence.

## Current project position against the rubric

### Technical Implementation

Strengths:
- non-trivial Strands-based multi-agent reasoning layer
- deterministic safety boundary separated from model output
- incident -> containment -> evidence -> recovery -> replay -> restoration lifecycle
- adversarial benchmark suite B01-B10
- exact-head CI on Python 3.10 and 3.12
- credential-free reproduction path
- GPT-6 red-team findings converted into regression tests

Remaining gate:
- targeted GPT-6 re-audit of Draft PR #67
- no merge until any Critical/High blocker is closed

### Design

Current weakness:
- the repository has a judge console data model, but no polished visual product surface
- current experience risks reading as an advanced technical proof of concept rather than a complete product

Decision:
- build a minimal Judge Incident Recovery Console after the security re-audit
- do not build a broad production UI
- the UI must be artifact-driven, deterministic, read-only, and truthful to represented evidence

### Potential Impact

Primary user:
- teams operating write-capable autonomous agents in professional workflows
- security/platform/AI infrastructure engineers responsible for recovery after agent failures

Message:
- prevention is not enough once agents can change state
- existing kill-switch/monitoring approaches stop future actions but do not reconstruct, repair, replay, and selectively restore authority

Evidence boundary:
- all measured claims remain bounded to synthetic deterministic fixtures
- no production effectiveness claim without separate evidence

### Creativity & Originality

Core differentiator:
- recovery-first control plane after prevention fails
- cross-agent causal recovery plus explicit residual truth
- replay-bound selective authority restoration
- model agents investigate and propose, deterministic controls authorize

### Presentation

Current gap:
- no final visual narrative/video package yet

Decision:
- demo one incident end-to-end, not many features
- show the failure, propagation, containment, recovery, residuals, replay, and selective restoration visually
- use the audit itself as credibility evidence near the end, not as the main story

## Critical execution sequence

### Gate A - Security re-audit

Frozen target:
- Draft PR #67
- head `9251510b94e8da42e59b7878b0826d5c519b7e0e`
- baseline `de835c3b571261e2398c0dbb619647fa1c2860fa`

Do not modify this PR until GPT-6 targeted re-audit completes.

### Gate B - Remediation and merge

If GPT-6 finds a confirmed Critical/High:
1. reproduce it independently
2. patch smallest safe surface
3. add regression
4. rerun full CI on exact head
5. repeat targeted verification if needed

If no submission blocker remains:
1. finalize PR #67
2. merge to main
3. rerun exact-head CI on main
4. regenerate final judge package on merged head

### Gate C - Visual product layer

Build only after the security target is stable.

Target deliverable:
- one static/read-only web console generated from deterministic judge artifacts
- deployable as GitHub Pages or another free static host if time permits
- no cloud credentials required
- no live write/recovery authority exposed

See `docs/JUDGE_UI_VISUAL_SPEC.md`.

### Gate D - Architecture diagram

Produce one competition-facing diagram with two visible trust zones:

1. Agentic reasoning layer
   - user/system incident input
   - Investigator
   - Recovery Planner
   - Skeptic/Verifier
   - Strands Agents SDK

2. Deterministic recovery control plane
   - Recovery Contracts
   - tamper-evident Action Ledger
   - containment
   - causal graph
   - controlled recovery/reconciliation
   - Replay Lab
   - Restoration Gate
   - Judge Evidence/Console

Optional AWS path must be visually marked according to verified state:
- Amazon Bedrock
- AgentCore Gateway/Policy
- CloudWatch/trace evidence

Use current official AWS Architecture Icons.

### Gate E - Demo video

Target duration: 4:30 to 4:50, never above 5:00.

Storyboard:

0:00-0:25 - Problem
- write-capable agents can leave real state changes after compromise
- kill switches stop future actions but do not recover what already happened

0:25-0:45 - Product thesis
- "Verified recovery for compromised autonomous AI agents"
- show lifecycle strip: incident -> containment -> evidence -> recovery -> replay -> verified restoration

0:45-1:50 - Working incident demo
- poisoned external input
- root support agent writes compromised shared memory
- downstream workflow/identity authority becomes affected
- show blast-radius graph and active containment

1:50-2:50 - Agentic reasoning
- Investigator evidence-bound root-cause hypothesis
- Recovery Planner candidate plan
- Skeptic rejects unsupported steps
- explicitly show "proposal only - no authority"

2:50-3:45 - Deterministic recovery
- recovery obligations
- safe/compensatable vs irreversible effects
- verification and explicit residual risk

3:45-4:20 - Replay and selective restoration
- isolated replay of exact represented attack action
- current scope-bound verdict
- downstream authority restored only after gate passes
- compromised root remains contained

4:20-4:45 - Proof
- CI 3.10/3.12
- benchmark B01-B10
- adversarial GPT-6 red-team audit and permanent regressions
- reproducible without paid model calls or credentials

4:45-4:55 - Close
- "No restored authority without complete recovery evidence and a current scope-bound replay."

### Gate F - Devpost submission

Required owner actions:
- AWS Builder ID
- final Devpost account/submission access
- public YouTube/Vimeo upload
- terms acceptance
- final submit

Prepare before owner actions:
- title and tagline
- concise text description
- public repo URL
- architecture diagram image
- demo video
- optional live demo URL
- setup/testing instructions
- disclosure of any pre-existing non-standard work if applicable

## Bonus strategy

High-value, low-risk bonus:
- publish at least one builder.aws.com post before deadline

Recommended post 1:
- title theme: "Agents for Humans: What a green test suite missed in an AI agent recovery system"
- story: build -> adversarial audit -> lifecycle counterexamples -> deterministic hardening -> lessons about model authority boundaries
- strong because it is specific, technical, and authentic to the project

Optional post 2 if time allows:
- architecture-focused story about separating Strands reasoning from deterministic authorization

Do not attempt three posts until code, video, diagram, and submission are secure.

## Scope control

Do now:
- security re-audit
- one polished judge-facing UI
- one architecture diagram
- one excellent 5-minute video
- one bonus build-story post
- exact-head package acceptance

Do not do before deadline unless required by a blocker:
- broad SaaS dashboard
- authentication/accounts
- production AWS multi-tenant deployment
- billing
- generic analytics suite
- new benchmark categories beyond existing safety needs
- large branding exercise

## Definition of done

The project is submission-ready only when:

- targeted re-audit has no unresolved submission-blocking Critical/High finding
- merged main has fresh exact-head CI
- final judge reproduction package is regenerated on merged head
- visual console displays only represented evidence
- architecture diagram matches actual implementation and claim boundaries
- demo video shows a real working end-to-end path
- Devpost description does not exceed executable evidence
- public repo has visible MIT license, README, setup, assets, and architecture diagram
- AWS Builder ID is ready
- owner approves and submits before the deadline
