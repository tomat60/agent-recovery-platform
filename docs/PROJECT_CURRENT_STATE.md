# Project Current State

Date: 2026-09-30

## Status

Agent Recovery Platform is a **commercial-product-first cybersecurity company/project**. Funding is a permanent parallel workstream, not the product goal.

Engineering state accepted through PR #209 / commit `22980344...`. Draft PR #210 is the active implementation front.

Latest accepted commercial signals:

- PR #167 / commit `2f48091e...` records the first meaningful n8n routing signal: the Recoverability Assessment was understood correctly and routed to a named human contact for continuation. This is qualification/routing evidence, not yet a pilot or buyer commitment.
- Kyvvu co-founder & CEO Jeroen Ghijsen completed a short discovery call with Paweł on 2026-09-30. He found the recovery problem sensible and the products potentially complementary, but said Kyvvu does not currently have customers asking for this recovery capability. He offered a soft reciprocal referral path: Kyvvu may refer a future recovery need, and Agent Recovery may refer customers needing pre-action controls. This is useful partner validation, but it is not a formal partnership, pilot, customer signal or current distribution channel.

Latest accepted product/security and funding movement:

- PR #172 / commit `4e7f8758...` adds a buyer-readable owned-pilot evidence summary and fail-closed restart-continuity validation.
- PRs #178 to #189 mature the buyer-facing Agent Recoverability Assessment into a delivery-grade evidence package with deterministic source identity, separate detection/recovery/replay dimensions, contradiction checks, buyer-readable output, bound delivery manifest, authority-free verification and trusted manifest pinning.
- PRs #191 to #196 productize standard OTLP JSON as a real evidence handoff path. The platform can ingest canonical OTLP action spans, export provenance-bound recovery evidence artifacts, verify received artifacts fail closed, pin OTLP evidence to an out-of-band digest, and pin supplied assessment evidence to a trusted source identity.
- PR #202 adds a bounded OCSF runtime-evidence adapter for security-runtime sources such as NVIDIA OpenShell. OCSF policy outcomes remain non-authorizing evidence, source identity is preserved, duplicate source events fail closed, and promotion into canonical recovery evidence requires explicit recovery identity.
- PR #204 adds deterministic OCSF evidence export and receiver verification, including raw-event binding, fail-closed provenance checks and an optional out-of-band exact-artifact SHA-256 pin.
- PR #205 adds an exact one-to-one recovery-mapping manifest with independent source-evidence and mapping digests so runtime policy evidence can enter a pilot workflow without becoming authority.
- PR #206 adds a deterministic CLI handoff from a verified, optionally out-of-band-pinned OCSF evidence artifact plus exact recovery mappings to a non-authorizing promotion artifact.
- PR #208 adds receiver-side fail-closed verification and optional exact-artifact pinning for that promotion handoff.
- PR #209 packages the exact OCSF evidence and promotion artifacts behind one fail-closed delivery manifest with optional out-of-band manifest pinning.
- Draft PR #210 reduces pilot setup to one deterministic command that stages, packages and self-verifies the complete OCSF handoff without overwriting prior evidence.
- PR #170 / commit `fffe3119...` makes funding a permanent parallel workstream, corrects the ECCC call identifiers to the 2027 call family, adds the live funding tracker and prepares the Warsaw matchmaking pack.
- Issue #194 is a bounded research intake for Cloudflare Agents. Evaluate BORROW / ADAPT / REJECT and one small provider-free proof only if it can delete work or strengthen a real integration target. No migration or spend is authorized.

Core lifecycle remains:

**incident -> containment -> evidence -> recovery / compensation -> replay / regression -> verified restoration**

Current wedge remains:

> **Verified recovery for autonomous AI-agent side effects across multiple tools and systems.**

Do not broaden into generic SIEM, IAM, EDR, prompt firewall or a general AI-security platform merely to fit funding language.

## Product truth now accepted

The accepted product foundation includes:

- framework-neutral action evidence ingestion and OTel-compatible normalization;
- durable evidence/provenance and persistent incident/containment/recovery state across restart;
- versioned Recovery Contracts separated from trusted runtime bindings;
- deterministic Recovery Readiness / CI coverage;
- read-only operator API and commercial console over canonical persisted incident state;
- one repeatable owned multi-surface pilot with recovery, replay and restoration evidence;
- deterministic Agent Recoverability Assessment with evidence identity, residual truth and evidence-derived remediation priorities;
- a source-verified ranked design-partner/channel pipeline;
- representative Composio and synthetic n8n pilot mappings;
- a compact technical diligence pack and first-wave outreach package;
- an ECCC partner one-pager, live funding opportunity tracker and Warsaw matchmaking pack.

Evidence discipline remains strict: synthetic benchmarks, owned sandbox results, external pilots and production evidence are different classes and must never be conflated.

## Current execution fronts

The project now runs five permanent parallel fronts:

1. **Product / CTO** - ship only product work that improves pilotability, buyer proof, security correctness, integration effort or verified restoration.
2. **Security** - preserve fail-closed authorization, evidence integrity, exact recovery binding and claim discipline.
3. **Commercialization** - continue qualified outreach, buyer discovery, design-partner/pilot conversion and channel/strategic partnerships.
4. **Funding / grants** - continuously research, qualify and prepare non-dilutive and accelerator opportunities without deforming the product.
5. **Company readiness** - monitor the point at which a legal entity, IP chain, insurance, contracts or financing structure becomes necessary.

Issue #128 remains the commercialization umbrella. Issue #144 remains the design-partner packaging/pipeline gate. Issue #169 is the active ECCC/funding execution gate.

## Commercial proof gates

Before broad SaaS expansion, seek:

- roughly 10 qualified buyer/partner conversations;
- at least 2 concrete pilot/assessment interests;
- at least 1 MSSP/AppSec/cloud-security/AI consultancy partner signal;
- one realistic pilot-ready external integration path;
- evidence about whether buyers value pre-incident Recoverability Assurance, post-incident Verified Recovery, or the combined proposition.

Commercial outreach is authorized when it is low-volume, qualified, personalized and evidence-based. Do not wait for per-message approval.

For founder-facing synchronous discovery, prefer the lowest-friction format that still advances the deal: async/email or the already-planned in-person TechEx meeting by default; use a short pre-event call only where a concrete high-value counterpart requests or materially benefits from it. Keep any such call tightly scripted around qualification and a concrete next step.

## Funding strategy - active truth

Funding must accelerate the commercial product and must not become a separate grant-only roadmap.

### Priority 1 - DIGITAL / ECCC 2027 call

Official current call family:

`DIGITAL-ECCC-2027-DEPLOY-CYBER-11`

Primary topic:

`DIGITAL-ECCC-2027-DEPLOY-CYBER-11-AI4SME`

Secondary topic:

`DIGITAL-ECCC-2027-DEPLOY-CYBER-11-CYBERAI`

Deadline: **2027-01-14, 17:00 CET**.

Preferred role: **technology provider + owner of a concrete recovery work package**, not coordinator of the first large EU consortium.

Immediate consortium targets:

- experienced EU cybersecurity coordinator / proposal lead;
- 2-4 SME end users operating write-capable AI/automation;
- MSSP/AppSec/cloud-security/AI-security implementation partner;
- optional independent research/test partner where it closes a real evaluation gap.

### Warsaw workshop status

The German-Polish Cybersecurity Matchmaking & Proposal Writing Workshop in Warsaw on 1-2 October 2026 is closed as an attendance path for us.

NCC confirmed on 2026-09-25 that no places remain.

Do not ask organizers or companies for a ticket. If a high-fit company is independently confirmed to be in Warsaw for the event, an outside-programme meeting nearby can be proposed without implying attendance or asking for event access.

Replacement consortium search channels:
- DEP4ALL matchmaking;
- KPK DEP Partner Search Form;
- EU Funding & Tenders partner search;
- direct qualified outreach to coordinators, SME end users, MSSP/AppSec/cloud-security partners and research/test partners.

### EIC path

- **EIC Pre-Accelerator 2027** is the preferred EIC readiness path if traction and TRL continue to improve.
- Poland is eligible as a widening country.
- Single SME; minimum TRL 4.
- EUR 500k-1m grant, 70% funding.
- Opens 2027-05-05; deadline 2027-11-18.

Do not rush an EIC Accelerator 2026 full proposal. Current EIC Accelerator is targeted at TRL 6-8; the 2026 final full-proposal batching date is 2026-11-04, but a short proposal GO is required first and EIC recommends substantial lead time. Preserve application attempts until customer/TRL evidence is stronger.

### NATO / dual-use

DIANA 2027 challenge applications are already closed. Monitor the next annual call, expected around June/July 2027. Do not distort the roadmap toward defence unless a future challenge naturally matches resilient autonomous systems, recovery after compromise or cyber resilience.

### Polish programmes

PARP Start-ups Are Us - Cybersecurity 2026 is closed. Monitor future editions; do not spend time attempting a closed call.

## Funding evidence to build through normal product work

Prefer evidence that helps both customers and grant evaluators:

- recovery-path coverage;
- time to containment;
- time to verified recovery;
- false restoration attempts rejected;
- irreversible residuals surfaced;
- integration effort;
- deterministic benchmark reproducibility;
- operator usability;
- external design-partner/pilot evidence;
- independent security review;
- clear IP/open-source chain.

## Company / legal-entity trigger

Do not create a company only because funding exists.

Prepare a legal entity when one of these becomes real:

- a design partner is ready to sign/pay;
- an ECCC consortium needs us as an applicant/beneficiary;
- an accelerator/investor requires the entity;
- liability/IP separation becomes materially useful.

Before choosing structure, compare Polish sp. z o.o./PSA and any genuinely relevant alternative with legal/tax input. Minimize founder liability and avoid unnecessary personal guarantees/co-financing risk.

## Owner-only gates

Stop only for:

- legally binding terms/contracts/NDA where substantive obligations arise;
- payment or new spend;
- company formation / ownership changes;
- IP transfer or exclusive licensing;
- material co-financing or budget commitments;
- customer production credentials/data or destructive actions;
- binding final grant/investment submission requiring declarations/signature.

Autonomous actions include research, qualified outreach, partner search, branch/PR/CI work, grant/application drafting, consortium concepts, budget drafts, work packages, trackers, one-pagers and non-binding event/program inquiries.

## Immediate next actions

1. Keep product engineering focused on external pilotability and buyer proof. The current assessment plus OTLP and OCSF evidence handoffs are now strong enough to support real design-partner conversations without inflating evidence claims.
2. Shift commercial emphasis from event-led partner discovery toward continuous direct buyer validation. Kyvvu validated that the problem is understandable and complementary, but not that current partner customers are demanding it. Prioritize teams already operating write-capable agents and ask for one concrete workflow, failure mode and recovery gap.
3. Keep Kyvvu warm as a reciprocal referral and future integration relationship. Do not count it as a formal partnership or pilot. A concise post-call follow-up was sent on 2026-09-30.
4. TechEx outreach remains open, but Amsterdam travel is deferred unless new evidence creates a clear reason to go, such as multiple high-value meetings, a concrete pilot discussion or a strong partner invitation. Do not spend on travel merely for general networking.
5. Continue low-volume event follow-up where fit is strong, but expand the main pipeline beyond events. Target direct buyers, agent platforms, workflow vendors, AI consultancies, runtime-security vendors and assurance ecosystems.
6. Continue ECCC AI4SME consortium search through direct channels now that the Warsaw workshop is closed.
7. Evaluate Cloudflare Agents only where it can remove infrastructure work or become a realistic recovery integration target. Do not let research displace commercial execution.
8. Maintain strict evidence class separation and fail-closed delivery verification. Synthetic, owned-pilot, external-pilot and production evidence remain distinct.