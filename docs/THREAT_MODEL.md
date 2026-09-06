# Threat Model

## Objective

Protect enterprises from harmful side effects produced by compromised, manipulated, malfunctioning, or over-authorized autonomous agents, with emphasis on containment and verified recovery.

## Protected assets

- production data and configuration
- customer and employee records
- external communications
- agent memory and context
- credentials and delegated identities
- approval records
- recovery contracts and policies
- audit evidence
- downstream systems reachable through agent tools

## Adversaries and failure sources

- malicious user input
- indirect prompt injection through documents, web pages, tickets, email, or retrieved data
- malicious or compromised tool output
- poisoned persistent memory
- compromised MCP/skill/tool dependency
- attacker with access to an over-scoped agent identity
- buggy model or planner
- benign but incorrect agent reasoning
- stale or incorrectly reused human approval
- multi-agent propagation of contaminated context
- operator error during recovery
- malicious instruction embedded in incident evidence attempting to attack the recovery agent

## Primary threats

### T01 Tool abuse

Agent invokes a legitimate write-capable tool outside intended purpose or scope.

### T02 Privilege escalation

Agent or tool reaches resources not intended for the current task, identity, or tenant.

### T03 Data exfiltration

Sensitive information leaves a controlled boundary through a legitimate or malicious channel.

### T04 Memory poisoning

Persistent state influences future reasoning after the original malicious input is gone.

### T05 Approval manipulation

High-impact action executes using missing, stale, forged, broadly scoped, or parameter-mismatched approval.

### T06 Cascading multi-agent failure

A compromised agent causes downstream agents to act outside their trust boundaries.

### T07 Evidence poisoning

Incident data attempts to manipulate the investigator or recovery planner.

### T08 Recovery abuse

The recovery path itself is manipulated into executing a second harmful action.

### T09 Incomplete rollback

The platform reports success after restoring one controlled system while an external side effect remains.

### T10 Audit destruction

Containment or recovery mutates state before preserving enough evidence to understand what happened.

### T11 Runaway execution / denial of wallet

Agent enters recursive or repeated tool/model calls causing cost or operational damage.

### T12 Supply-chain change

A trusted tool, skill, contract, or dependency changes behavior after approval.

## Trust boundaries

### Untrusted

- user and external content
- retrieved documents
- tool-returned natural language
- agent-generated explanations
- model-generated recovery plans before validation
- cross-agent messages unless cryptographically/policy authenticated

### Higher-integrity

- deterministic policy engine
- recovery contract registry
- approval verifier
- action ledger append path
- idempotency store
- benchmark ground truth
- recovery executor

Higher-integrity components should be isolated from the agent's ordinary write authority.

## Core controls

- least-privilege tool access
- separate decision and execution layers
- normalized, parameter-bound approvals
- immutable/versioned contracts
- append-oriented action ledger
- independent read-after-write verification
- policy enforcement outside model prompts
- fail-closed behavior when contract, policy, approval, or evidence logging is unavailable
- containment scopes for tool/session/identity/memory
- resource and retry limits
- isolated replay environment
- independent skeptic/verifier pass
- explicit residual-risk state for irreversible effects

## Recovery-specific threat model

Recovery is treated as a new privileged workflow, not an exception to security controls.

A compromised source agent must not be able to:

- modify its own Recovery Contract
- mark its own incident recovered
- approve its own recovery
- erase action evidence
- bypass independent verification
- restore its own authority

The recovery planner may generate hypotheses and proposed actions, but deterministic policy controls bind every execution step to a known contract and current incident state.

## Safe development boundary

All benchmark incidents run against synthetic or owned environments. No test should require compromising external infrastructure, stealing live credentials, evading third-party detection, or causing real destructive effects.

The benchmark should model attacker effects precisely enough to test defensive controls while keeping the offensive mechanism minimal and contained.

## Residual risks

The platform cannot guarantee recovery from every incident. In particular:

- externally observed information cannot be made unseen
- copied secrets may remain compromised even after rotation
- third-party systems may not expose compensation APIs
- delayed side effects may occur after containment
- forensic evidence may be incomplete if integrations were not instrumented before the incident
- the verifier model can be wrong

The product must expose these residual risks instead of collapsing them into a single green status.
