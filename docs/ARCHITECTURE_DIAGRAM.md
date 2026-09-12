# Agent Recovery Platform Architecture Diagram

This diagram is intended for the Agents for Humans submission and matches the implemented trust boundary.

```mermaid
flowchart TD
    EXT[External content / user task / tool output] --> SRC[Source AI Agent]
    SRC --> REQ[Governed tool request]

    subgraph CONTROL[Recovery Control Plane]
        CONTRACT[Recovery Contract Registry]
        GATE[Deterministic Action Gate]
        APPROVAL[Parameter-bound Approval Verifier]
        ADAPTER[Governed Tool Adapter]
        LEDGER[Tamper-evident Action + Side-Effect Ledger]
        CONTAIN[Containment Plane]

        CONTRACT --> GATE
        APPROVAL --> GATE
        GATE --> ADAPTER
        ADAPTER --> LEDGER
        CONTAIN --> LEDGER
    end

    REQ --> GATE
    ADAPTER --> SYSTEMS[Synthetic / Owned Enterprise Systems]
    SYSTEMS --> LEDGER

    LEDGER --> EVIDENCE[Integrity-verified incident evidence]
    EVIDENCE --> INVESTIGATOR[Strands Investigator - read-only]
    INVESTIGATOR --> CAUSAL[Causal graph + blast radius]
    CAUSAL --> PLANNER[Strands Recovery Planner]
    PLANNER --> SKEPTIC[Independent Skeptic / Verifier]
    SKEPTIC --> CANDIDATE[Candidate recovery plan]

    CANDIDATE --> RGATE[Deterministic Recovery Gate]
    CONTRACT --> RGATE
    LEDGER --> RGATE
    RGATE --> EXEC[Recovery / Compensation Executors]
    EXEC --> VERIFY[Independent State Verification]
    VERIFY --> REPLAY[Isolated Replay Lab]
    REPLAY --> RESULT{Replay and state proof}

    RESULT -->|verified| RESTORE[Selective authority restoration gate]
    RESULT -->|failed / stale / incomplete| HOLD[Remain contained]
    RESULT -->|irreversible effect| RESIDUAL[Explicit residual risk]

    RESTORE --> HUMAN[Human restoration decision]
    HOLD --> HUMAN
    RESIDUAL --> HUMAN

    POLICY[Optional AWS live path:\nBedrock + AgentCore Gateway / Policy / Observability] -. external policy and evidence .-> CONTROL
```

## Trust boundary

- Strands agents may investigate, hypothesize, challenge and propose.
- Model output never grants approval, executes recovery or restores authority.
- Deterministic gates bind actions to contracts, incident evidence, approvals, dependency order and freshness.
- Irreversible external effects remain visible as residual risk.
- Restoration requires independent state verification plus a fresh replay proof.

## Judge story

`attack -> cross-agent propagation -> blast radius -> scoped containment -> investigation -> recovery planning -> skeptic challenge -> deterministic recovery gate -> dependency-safe recovery -> residual truth -> adversarial replay -> verified selective restoration`
