# Owner Gate - Final Submission Day

This file is for the project owner. It contains only actions that genuinely require the owner or a final public-release decision.

## What the owner does not need to do again

- No more AWS Bedrock setup.
- No more CloudShell work for the live Strands proof.
- No manual code editing.
- No security re-audit unless runtime/security code changes again.
- No face-camera recording is required for the planned demo video.

## Owner action 1 - Record voiceover

Use `docs/VIDEO_FINAL_STORYBOARD.md`.

Record the 10 numbered voiceover blocks as separate files. Natural English delivery is more important than speed. Leave roughly half a second of silence before and after each take.

Do not try to synchronize while recording. The edit will be synchronized to the finished Judge Console capture.

Preferred audio priority:

1. quiet room,
2. phone or microphone close enough to avoid room echo,
3. no noise reduction or aggressive processing while recording,
4. WAV, M4A or high-quality MP3 is acceptable.

## Owner action 2 - Review the final video once

Owner review should answer only these questions:

- Is the narration understandable?
- Is any on-screen claim stronger than what the evidence proves?
- Is the product understandable without reading the repository?
- Does the video stay concise and feel like a product rather than a slide deck?
- Are there any visual glitches, private data, browser tabs or accidental notifications visible?

Minor aesthetic preferences should not trigger a last-minute rebuild if the video is otherwise clean.

## Owner action 3 - Public video upload

Only after final review, upload the final video to the competition-accepted public video host and provide the public URL for the Devpost entry.

Do not use an expiring/private share link.

## Owner action 4 - Devpost / competition form

Use `docs/DEVPOST_FINAL_DRAFT.md` as the source copy, but read the actual competition form labels before pasting so sections map correctly.

Before the final submit button, verify:

- project name,
- Professional Agents track,
- public repository URL,
- public demo video URL,
- final repository SHA,
- required AWS / Strands disclosures,
- team / author information,
- terms and eligibility acknowledgements.

The final submitted SHA must be read from `main` after all presentation-only merges and the last exact-head CI run.

## Owner action 5 - Final submit

This is the explicit owner gate. Do not submit the competition entry until the owner approves the final public package.

After submission, capture screenshots of the confirmation page and any submission ID / URL.

## Project-side work before those gates

The project lane should complete, in this order:

1. Judge Console live-proof integration and 1920x1080 browser QA.
2. Final claim pass against deterministic evidence and live artifact.
3. Merge presentation-only PR after green CI.
4. Exact-head post-merge CI.
5. Final video screen capture and edit against the locked storyboard.
6. Fill final SHA and video URL placeholders.
7. Public owner gate.

## Non-negotiable claim rules

Do not claim:

- production-proven security,
- universal agent attack detection,
- arbitrary production rollback,
- AgentCore deployment unless separately completed and verified,
- that the LLM authorizes or verifies recovery,
- that the compromised root agent is restored,
- first / only in the world.

Strong supported claim:

> Agent Recovery Platform provides a bounded, evidence-gated incident recovery control plane for represented write-capable agent workflows, with a real Strands + Amazon Bedrock advisory path and a credential-free deterministic recovery path.
