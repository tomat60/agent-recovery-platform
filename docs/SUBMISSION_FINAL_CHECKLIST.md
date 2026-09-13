# Final Competition Submission Checklist

Status: execution checklist for the final submission window.

## Accepted technical baseline

- Accepted code anchor before presentation-only packaging: `b997384addd8781e0dac153d92adabcf9cc11757`
- Post-merge GitHub Actions: `recovery-ci` run `34762391263` PASS
- Python 3.10: PASS
- Python 3.12: PASS
- Ruff: PASS
- Deterministic tests: **153 passed**
- Benchmark smoke B01-B10: PASS
- Judge reproduction: PASS
- Canonical round trip / semantic validation: PASS
- SHA-256 manifest verification: PASS
- Authority-free reproduction manifest: PASS

Any later presentation/documentation merge must receive its own exact-head CI before final submission. If security/runtime code changes again, reopen the security gate.

## Security acceptance

- Original adversarial GPT-6 architecture audit completed.
- Targeted GPT-6 re-audit completed.
- Final Codex acceptance audit completed.
- Final Codex High finding on recovery-target provenance fixed in PR #70.
- Exact malicious-builder + no-op-executor regression permanently added.
- Compromised source/root restoration remains intentionally unsupported in the competition path.
- Public claims remain bounded to synthetic deterministic evidence.

## Judge-facing package

- [ ] Interactive Judge Console renders correctly at 16:9 desktop size.
- [ ] Architecture view clearly separates Strands advisory reasoning from deterministic authority.
- [ ] Console shows incident -> containment -> evidence -> recovery -> replay -> restoration.
- [ ] Root support agent stays contained after selective downstream restoration.
- [ ] Test/benchmark numbers match final accepted evidence.
- [ ] Architecture SVG exported cleanly for Devpost/media use.
- [ ] README leads a judge from thesis to reproduction in under two minutes.

## Video

Target: **3:20-3:50**, never over 5:00.

- [ ] Visual capture uses Judge Console as primary product surface.
- [ ] Architecture diagram is the only slide-like insert.
- [ ] GitHub Actions evidence is shown briefly and cleanly.
- [ ] No private tabs, credentials, account IDs or billing details appear.
- [ ] Voiceover recorded as separate sections from `docs/VIDEO_PRODUCTION_PLAN.md`.
- [ ] Final audio is intelligible on laptop speakers.
- [ ] Export is 16:9 1080p or 1440p.
- [ ] Final runtime checked after export.
- [ ] Public YouTube or Vimeo URL works without authentication.

## Devpost

- [ ] Project name: Agent Recovery Platform.
- [ ] Track: Professional Agents.
- [ ] Tagline matches final package.
- [ ] Description uses `docs/DEVPOST_FINAL_DRAFT.md` as source.
- [ ] Public GitHub repository link works.
- [ ] Final submitted Git SHA copied from Git after all presentation-only merges.
- [ ] Architecture diagram attached if the form permits it.
- [ ] Public demo video URL added.
- [ ] Optional live demo omitted unless separately verified.
- [ ] Required disclosure of prior/pre-existing work reviewed truthfully.
- [ ] AWS Builder ID entered exactly as required by the form.
- [ ] Terms accepted by owner.
- [ ] Final Submit performed by owner.

## Optional AWS / Builder content

Do not let optional cloud proof delay the core submission.

- [ ] No Paid Plan upgrade.
- [ ] No new AWS spend without explicit owner decision.
- [ ] Claim live Bedrock/AgentCore behavior only if actually executed and captured.
- [ ] Credential-free deterministic path remains the source of truth.
- [ ] Builder article/bonus work happens only after the core Devpost package is safe.

## Final freeze rule

Once the final presentation/docs branch is merged and exact-head CI is green:

1. Record exact `main` SHA.
2. Do not modify security/runtime code unless a concrete blocker appears.
3. Reproduce judge evidence one last time through CI.
4. Confirm video and Devpost numbers match that accepted state.
5. Submit before the deadline with time left for form/upload problems.
