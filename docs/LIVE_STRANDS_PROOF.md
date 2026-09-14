# Live Strands + Amazon Bedrock proof

Status: verified live advisory-path evidence for the competition presentation. This document does **not** expand the product's security-effectiveness claims.

## What was executed

On 2026-09-13 the bounded judge incident was executed in AWS CloudShell against the EU Amazon Bedrock inference profile:

`eu.anthropic.claude-haiku-4-5-20251001-v1:0`

The run used the repository's three advisory Strands roles:

1. Investigator
2. Recovery Planner
3. Skeptic

The run completed with:

- `status: PASS`
- `authorization_effect: none`
- incident: `judge-live-strands-proof`
- 10 ledger evidence events
- model calls: 3
- tools exposed to model agents: none
- external production systems touched: none
- recovery / replay / restoration authority granted by the artifact: none

The raw live artifact was downloaded immediately after the successful run. Its SHA-256 is:

`9b9b1fae30faa5d597252d7ea35c9d65bd271a0c5bc2a3c9cdc5ec565a820a8c`

The ledger head recorded inside that artifact is:

`fb869c8dd1ff6b8a120733063d9f36c1b1a371fdb212f8be37e8301afcaf650e`

## What the live model layer demonstrated

The Investigator reconstructed the represented causal path from an untrusted support input through shared memory and CRM state into an identity permission change.

The Recovery Planner proposed an ordered candidate plan and kept residual risks explicit rather than claiming perfect rollback.

The Skeptic supported the incident-causality claim but marked the recovery-plan claim `uncertain`, specifically because recovery classes alone do not prove that rollback, compensation, sequencing or verification will actually restore system integrity.

That result is useful because the product architecture intentionally does not treat model confidence as recovery proof. Deterministic recovery verification, bounded replay and the restoration gate remain separate authority boundaries.

## Important observed limitation

The live Investigator/Planner output introduced the unsupported contact name `Alex Rivera` for contact `c-1`. That name does not exist in the supplied ledger evidence.

This was retained as an honest observation rather than hidden. It demonstrates why advisory LLM output is never allowed to authorize recovery or restoration. Judge-facing UI and claims must use ledger-backed identifiers and deterministic evidence rather than unsupported model-added details.

## Exact code state

The successful live run was produced on branch head:

`0df909b8d823387eef943e29ae24115d1d30bf45`

`recovery-ci` run #257 passed on that exact head.

Before merge, the branch was narrowed so no runtime/security module changed. The final PR #72 merge candidate contained only presentation/support scripts and passed `recovery-ci` #258. PR #72 then merged to `main` as:

`52281e9136ccaf4ed904b9ce1533d5e957635fb1`

Post-merge `recovery-ci` #259 passed on that exact main head.

## Claim boundary

This proves that the project has a real Strands + Amazon Bedrock advisory execution path over the bounded synthetic incident.

It does **not** prove:

- live production rollback,
- production security effectiveness,
- AgentCore deployment,
- universal causal capture,
- safe restoration of a compromised source/root agent,
- that model-generated statements are factual unless supported by the ledger.

The competition's reproducible security claims continue to come from the deterministic credential-free path, tests, benchmark, replay evidence and restoration gates. The live Bedrock path is additive evidence that the advisory reasoning layer actually runs against AWS rather than being a mocked integration.

## Presentation guidance

For the video and Judge Console, present the live result as:

> Live Strands + Amazon Bedrock advisory reasoning. No tools. No execution authority. The deterministic control plane still decides what can be recovered and what authority can return.

Do not present raw model prose as ground truth. Prefer cited ledger events, bounded residual-risk summaries and the Skeptic's `uncertain` verdict for the recovery claim.