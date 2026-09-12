# Final Submission Checklist

Status: owner/assistant execution checklist for Agents for Humans.

## A. Security gate — must complete before merge

- [ ] Targeted GPT-6 re-audit executed against Draft PR #67 exact head.
- [ ] Any confirmed Critical/High finding independently reproduced.
- [ ] Submission-blocking findings patched with permanent regressions.
- [ ] Exact-head CI green on Python 3.10 and 3.12.
- [ ] Benchmark B01-B10 green.
- [ ] Judge reproduction and artifact validation green.

## B. Main branch and evidence package

- [ ] Merge hardened PR only after Gate A.
- [ ] Record final `main` SHA.
- [ ] Rerun exact-head CI on final `main`.
- [ ] Regenerate judge evidence package on final `main`.
- [ ] Refresh SHA-256 manifest.
- [ ] Update `docs/FINAL_PACKAGE_ACCEPTANCE.md` to the final accepted head.
- [ ] Refresh all test-count references after final CI.

## C. Judge Console

- [ ] Console renders deterministic artifact truth only.
- [ ] Incident lifecycle visible in one screen.
- [ ] Root agent remains visibly contained.
- [ ] Downstream restoration is visibly selective.
- [ ] Replay and recovery are separate evidence gates.
- [ ] Claim boundary visible on-screen.
- [ ] No credentials or account identifiers embedded.
- [ ] Screenshot at 1440p/1080p captured for Devpost.
- [ ] Optional static deployment verified if used as live demo.

## D. Architecture diagram

- [ ] Two trust zones are explicit: Strands advisory reasoning and deterministic recovery control plane.
- [ ] Investigator, Recovery Planner and Skeptic are shown as advisory only.
- [ ] Recovery Contracts, Ledger, Causal Graph, Recovery Engine, Replay Lab and Restoration Gate are shown.
- [ ] AWS services are marked live/verified only if actually exercised.
- [ ] Use official/current AWS iconography where AWS services are shown.
- [ ] Export high-resolution PNG/SVG for Devpost and video.

## E. AWS / Strands proof

- [x] AWS Builder ID/account available.
- [x] AWS Free Plan active with credits.
- [ ] Cost budget/alert configured before non-trivial cloud testing.
- [ ] Bedrock playground smoke test completed if used in claims.
- [ ] Strands + Bedrock live path captured if used in submission.
- [ ] AgentCore path captured only if actually working and useful; otherwise mark as architecture/future path.
- [ ] No AWS security-effectiveness claim without measured evidence.

## F. Demo video — owner recording/publication

- [ ] Script refreshed with final test count and final SHA.
- [ ] 4:45–4:55 final runtime; never above 5:00.
- [ ] Working product visible, not only slides.
- [ ] Problem, target user and importance are explicit in first minute.
- [ ] One incident shown end-to-end.
- [ ] Trust boundary between model reasoning and deterministic authority is explicit.
- [ ] Residual-risk truth shown.
- [ ] Adversarial audit/hardening shown briefly as credibility proof.
- [ ] No private tabs, credentials, billing identifiers or secrets visible.
- [ ] Upload publicly to YouTube or Vimeo.
- [ ] Verify public playback in logged-out/incognito mode.

## G. Devpost package

Assistant-preparable:
- [ ] Final project title/tagline.
- [ ] Concise description.
- [ ] Problem / target user / why it matters.
- [ ] How Strands is used.
- [ ] Architecture explanation.
- [ ] Measured evidence and claim boundaries.
- [ ] Public repository URL.
- [ ] Architecture image.
- [ ] Judge Console screenshot/live-demo link if available.
- [ ] Demo video URL after owner publishes it.
- [ ] Disclosure of pre-existing work if required.

Owner-only:
- [ ] Log into Devpost.
- [ ] Confirm AWS Builder ID field.
- [ ] Review final public wording and visuals.
- [ ] Accept competition terms.
- [ ] Submit before deadline.
- [ ] Verify submission confirmation page/email.

## H. Repository polish

- [x] Public repository.
- [x] MIT license recognized by GitHub.
- [ ] Repository description populated.
- [ ] Repository topics populated if useful.
- [ ] README hero section reflects final positioning.
- [ ] Architecture diagram visible from README.
- [ ] One-command judge reproduction remains accurate.
- [ ] No stale branch/test-count/accepted-head references in final public docs.

## I. Optional bonus — only after core submission is safe

- [ ] Publish one high-quality builder.aws.com build-story post.
- [ ] Add qualifying competition identifiers/tags required by official rules.
- [ ] Record public URL in Devpost if applicable.
- [ ] Consider a second post only if video, diagram and submission are already complete.

## Stop conditions

Do not spend pre-deadline time on:
- generic SaaS account/authentication UI,
- billing implementation,
- multi-tenant infrastructure,
- unrelated EC2/RDS credit activities,
- extra benchmark families without a discovered blocker,
- visual polish that delays the working demo or final submission.
