# Product Strategy

## Executive decision

The product should be comprehensive around **recovery**, but narrow around **category ownership**.

We should not build a general AI-security suite. That market already contains large cloud vendors, security incumbents, and well-funded startups covering discovery, prompt-injection defense, identity, policy, red teaming, and observability.

The wedge is:

> **Verified recovery for autonomous agent side effects across multiple tools and systems.**

The product begins before an action by requiring a declared recovery path, becomes most valuable during an incident by preserving evidence and containing authority, and finishes only when remediation has been independently replayed and verified.

## Why this wedge

Enterprise agents increasingly act through APIs, tools, memory, and identities. Prevention cannot guarantee zero incidents. Recovery is hard because agent workflows cross system boundaries and traditional database rollback does not cover external side effects such as messages, permissions, tickets, deployments, CRM updates, or workflow triggers.

A high-value recovery layer must answer five questions:

1. What did the agent actually change?
2. What is still capable of causing damage?
3. Which effects are reversible, compensatable, or irreversible?
4. What recovery sequence is safe to execute?
5. Can we prove that the same failure no longer succeeds?

## Product promise

Do not promise "zero loss" or perfect reversal.

Promise:

> **Minimize blast radius. Recover what is recoverable. Prove what was repaired. Know exactly what remains.**

## Product surface

### 1. Recovery Readiness

Before production or before a high-risk action:

- inventory write-capable tools
- require Recovery Contracts
- identify actions with no compensation path
- score recovery coverage
- flag overbroad identities and approval gaps that directly affect recovery
- produce concrete remediation tasks

This becomes the first commercial assessment product.

### 2. Runtime Recovery Control

During normal operation:

- record action intent, normalized parameters, identity, policy version, approval, and observed result
- assign recovery class and recovery deadline
- maintain causal links between actions
- expose containment controls

### 3. Incident Recovery

When compromise or harmful behavior is suspected:

- freeze relevant authority
- preserve evidence
- reconstruct causal graph and blast radius
- isolate contaminated memory/context where possible
- produce ordered recovery plan
- require approval for consequential recovery steps
- execute allowed compensation actions

### 4. Verified Restoration

After recovery:

- query source systems to verify side effects
- replay the incident in a controlled environment
- run a skeptical independent verification pass
- identify residual irreversible effects
- create permanent regression tests
- restore authority only after policy conditions are met

## What we intentionally do not build

- a general SIEM
- EDR or endpoint malware detection
- broad identity governance
- a generic prompt firewall
- vulnerability scanning for all software
- autonomous offensive counterattack
- generic compliance workflow software

These are integrations and evidence sources, not our category.

## Initial customer

Best first ICP:

- 20-500 employees
- AI-native SaaS, devtools, fintech, or security vendor
- agents already have write permissions to internal or customer-facing systems
- small security/platform team
- visible concern about agent autonomy but no mature recovery program
- CTO, CISO, Head of Platform, or Head of AI can approve a bounded pilot

Avoid major regulated enterprises as first customers because trust, procurement, insurance, and compliance requirements are too costly before credibility exists.

## Initial paid offer

### Agent Recoverability Assessment

Scope one production-like agent workflow.

Deliverables:

- tool and authority map
- Recovery Contract coverage report
- controlled incident suite
- containment test results
- blast-radius reconstruction
- recovery and compensation test
- replay verification
- residual-risk register
- prioritized remediation plan

Commercial hypothesis to validate, not a committed price:

- design-partner assessment: low thousands of EUR
- later premium assessment: higher four to low five figures EUR depending on scope and risk
- platform subscription only after repeated assessment demand proves recurring value

## Partner strategy

Security buying is trust-heavy. A strong route is to sell through or alongside:

- MSSPs
- penetration-testing firms
- AI consultancies
- cloud security consultancies
- agent-platform implementers

They already possess customer relationships and procurement access. We provide a differentiated agent-recovery capability they can package into existing assessments.

## Defensibility

The moat should not be the model or UI.

Build a **Recovery Intelligence Dataset** containing:

- tool and action type
- declared side effect
- observed side effect
- failure or attack pattern
- causal chain
- containment strategy
- recovery strategy
- verification result
- replay result
- residual effect

Over time this can answer which remediation actually works for which classes of agent actions.

## Competition strategy

For hackathons, show one unforgettable end-to-end incident rather than a broad dashboard:

1. benign-looking external content causes an unsafe agent trajectory in a synthetic enterprise environment
2. harmful write is attempted or a controlled side effect occurs
3. recovery platform freezes authority
4. investigator reconstructs causal chain
5. recovery planner proposes compensation
6. skeptic finds an incomplete hypothesis or unsafe recovery step
7. plan is corrected
8. recovery executes in the synthetic environment
9. the same incident is replayed
10. replay is blocked and residual effects are explicitly reported
11. human authorizes restoration

The benchmark numbers shown in the demo must come from automated tests, never hand-authored claims.

## 30-day validation gate after competition

Continue aggressively only if evidence supports it.

Minimum target signals:

- 10 qualified buyer or partner conversations
- at least 2 parties willing to explore a concrete pilot or assessment
- at least 1 MSSP/security/AI consultancy interested in a partner motion
- benchmark demonstrates meaningful improvement over a baseline recovery approach
- technical reviewers do not identify a fatal architecture flaw

If buyers consistently say recovery is interesting but not budgeted, pivot the offer before investing in enterprise platform complexity.

## Hiring strategy

No employee hiring is required for MVP, benchmark, competition build, or customer discovery.

Before a serious external pilot, obtain a limited independent review from a senior AppSec/cloud/AI-security practitioner. Pay from pilot revenue, grant money, prize money, or use a narrow advisory/revenue-share structure if necessary.

Before regulated production, expect to need stronger security engineering, legal/compliance review, insurance, and formal controls. Do not pretend the founding team alone can responsibly secure high-consequence infrastructure at scale.
