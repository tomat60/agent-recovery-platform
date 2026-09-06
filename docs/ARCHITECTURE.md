# Architecture

## Design principle

The LLM may investigate, hypothesize, and propose. Deterministic components govern authorization, evidence, recovery execution, and restoration.

## Logical architecture

```text
External content / user task / tool output
                 |
                 v
        +------------------+
        | Source AI Agent  |
        +------------------+
                 |
                 | governed tool request
                 v
+-----------------------------------------------+
| Recovery Control Plane                        |
|                                               |
|  Recovery Contract Registry                   |
|       |                                       |
|       v                                       |
|  Deterministic Action Gate <---- Approval     |
|       |                         Verifier       |
|       v                                       |
|  Governed Tool Adapter / AgentCore Gateway    |
|       |                                       |
|       +----> Action + Side-Effect Ledger       |
|                                               |
+-----------------------------------------------+
                 |
                 v
        Synthetic / Enterprise Systems

On incident trigger:

Action Ledger + traces + policies + memory evidence
                 |
                 v
       +----------------------+
       | Strands Investigator |
       +----------------------+
                 |
                 v
          Causal / blast graph
                 |
                 v
       +----------------------+
       | Recovery Planner     |
       +----------------------+
                 |
                 +----> Skeptic / Verifier
                 |             |
                 |<------------+
                 v
       Deterministic Recovery Gate
                 |
                 v
       Recovery / Compensation Executors
                 |
                 v
       Independent State Verification
                 |
                 v
             Replay Lab
                 |
                 v
     Verified / Residual / Failed status
                 |
                 v
       Human restoration decision
```

## Components

### Recovery Contract Registry

Versioned high-integrity definitions for write-capable tools. Declares expected side effects, recovery class, verifier, compensation executor, approval semantics, and containment scopes.

### Deterministic Action Gate

Resolves contract, normalizes parameters, checks policy, binds approval, and records intent before allowing consequential execution.

For the AWS competition live path, Amazon Bedrock AgentCore Gateway + Policy is a preferred enforcement boundary because policy evaluation can occur outside the source agent runtime.

### Governed Tool Adapter

Wraps synthetic or real APIs. It exposes a normalized action interface and captures observed post-action state. In production this layer should avoid trusting the source agent's narration of what happened.

### Action + Side-Effect Ledger

Append-oriented record containing:

- event ID and correlation ID
- source agent/session/identity
- tool and normalized parameters
- contract version
- policy decision
- approval binding
- pre-state reference where allowed
- observed side effect
- downstream causal links
- containment event
- recovery action
- verification result
- replay result

The initial implementation may use SQLite. Production design should support a durable append store and tamper-evident integrity controls.

### Incident Trigger

The recovery platform can accept triggers from existing SIEM/EDR/model-security systems or its own policy failures. It does not need to own all detection mechanisms.

### Containment Plane

Can freeze the narrowest effective scope:

- one tool
- one session
- one agent identity
- one memory namespace
- one downstream integration

Containment preserves evidence and should not silently destroy state required for recovery.

### Strands Investigator

Uses read-only evidence tools to reconstruct likely causal chain and blast radius. It never directly executes recovery actions.

### Recovery Planner

Maps affected actions to Recovery Contracts and proposes ordered compensation steps, expected states, and residual effects.

### Skeptic / Verifier

Runs an independent challenge pass. It looks for missing causal links, unsafe compensation, incorrect reversibility claims, incomplete blast radius, and evidence contradictions.

### Deterministic Recovery Gate

Rejects recovery steps that are not bound to contracts, current incident state, valid approvals, dependencies, and idempotency rules.

### Replay Lab

Runs the incident against an isolated clone/simulator after remediation. Verification requires state-based assertions, not merely an LLM saying the fix looks correct.

## Initial synthetic enterprise

The first benchmark should include a small but cross-system environment:

- CRM contacts and notes
- support tickets
- internal messaging
- access/permission service
- deployment/configuration service
- agent memory store

Every system exposes safe deterministic write and read APIs. Some effects are reversible, some compensatable, and some intentionally irreversible.

## AWS competition integration

Preferred sequence:

1. local deterministic benchmark and tests
2. Strands investigator/planner/verifier using a local or mock model path for CI
3. one controlled Bedrock live path
4. AgentCore Gateway + Policy for governed tool calls
5. AgentCore observability / CloudWatch spans as additional evidence
6. optional AgentCore Runtime if it improves the demo without adding instability

Do not make paid AWS resources a dependency for basic development or regression tests.

## Security properties we want to demonstrate

- policy outside the source agent
- recovery contract required before consequential execution
- model cannot self-authorize
- action evidence survives agent failure
- containment can cross agent boundaries
- recovery plan is independently challenged
- irreversible effects remain visible
- replay can invalidate a false recovery claim
- restoration requires an explicit gate

## Future integrations

Potential integrations after validation:

- OpenTelemetry traces
- MCP gateways
- cloud IAM / workload identity
- GitHub / GitLab
- Slack / Teams
- Salesforce / HubSpot
- ticketing systems
- cloud deployment systems
- SIEM/EDR alert ingestion
- secret managers

Integrations should be prioritized by buyer demand and recoverability value, not by logo count.
