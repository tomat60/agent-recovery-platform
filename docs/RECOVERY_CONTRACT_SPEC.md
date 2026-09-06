# Recovery Contract Specification

## Goal

Every write-capable agent tool should declare enough structured information for the recovery layer to decide whether an action can execute, how to observe its side effects, and how to repair those effects if something goes wrong.

A Recovery Contract is not a model prompt. It is machine-readable policy and execution metadata consumed by deterministic code.

## Recovery classes

### REVERSIBLE

The original operation has a supported inverse or version restore that can return the controlled resource to a known previous state.

Examples in synthetic tests:

- update a mutable CRM field with version history
- change a configuration value with a stored previous version
- create a draft object that can be deleted before publication

### COMPENSATABLE

The original operation cannot literally be undone, but a documented compensating action can reduce or repair its effect.

Examples:

- post a corrective message after a wrong message was sent
- revoke a permission after it was temporarily granted
- create an adjusting ledger entry rather than deleting financial history

Compensation must never be described as full reversal unless verification proves equivalent controlled state and no irreversible external effects remain.

### IRREVERSIBLE

No technically honest recovery path can erase the effect.

Examples:

- a secret has been viewed by an external party
- a message has been read
- an irreversible transfer has settled
- a public disclosure has propagated outside controlled systems

The platform may contain further damage and propose mitigation, but must preserve the residual effect in the final incident state.

## Required fields

```yaml
contract_version: "0.1"
tool_id: "crm.update_contact"
action_type: "update"
risk_level: "medium"
recovery_class: "reversible"
side_effects:
  - resource_type: "crm.contact"
    selector_from_input: "contact_id"
    effect: "field_update"
preconditions:
  - "target resource exists"
observation:
  read_after_write: true
  verifier: "crm.get_contact"
recovery:
  strategy: "restore_previous_version"
  executor: "crm.restore_contact"
  recovery_window_seconds: 86400
  idempotency_required: true
approval:
  before_original_action: false
  before_recovery_action: false
  parameter_bound: true
containment:
  scopes:
    - "tool"
    - "session"
evidence:
  retain_input_hash: true
  retain_normalized_parameters: true
  retain_authorization_decision: true
  retain_before_state: true
  retain_after_state: true
```

## Execution requirements

Before a consequential tool call, the execution layer must:

1. resolve the exact tool contract
2. normalize parameters
3. classify risk and recovery class
4. confirm the required observation/verifier path exists
5. confirm approval requirements
6. persist action intent before execution
7. execute through the governed tool boundary
8. query observed post-action state where possible
9. persist the observed side effect independently of model narration

If the contract is missing or malformed, write actions fail closed by default.

## Recovery requirements

A recovery plan step must bind to:

- original action/event identifier
- target resource
- normalized recovery parameters
- contract version
- policy version
- required approval identifier, if any
- idempotency key
- expected post-recovery state

The model may propose these values. Deterministic code validates them against the contract and current state before execution.

## Recovery dependencies

Multi-system recovery often requires ordering.

Each planned recovery step may declare:

```yaml
depends_on:
  - "event_123"
blocks_restoration_until_verified: true
```

The planner can suggest ordering, but a deterministic dependency graph must reject cycles or execution before prerequisites are satisfied.

## Irreversible effects

For `IRREVERSIBLE` actions, a contract should define:

- containment options
- mitigation options
- notification requirements
- evidence required for residual-risk reporting
- whether explicit pre-action human approval is mandatory

A successful mitigation does not change the historical recovery class to reversible.

## Contract quality score

For assessment purposes, each write-capable tool receives coverage indicators:

- contract present
- side effects declared
- independent verifier present
- recovery/compensation executor present
- recovery window known
- idempotency support known
- approval semantics defined
- containment scope defined
- synthetic recovery test passing

This produces a transparent recovery-readiness map rather than a model-generated confidence score.

## Versioning

Contracts are immutable once used by an executed action. Updates create a new version so incident evidence can always reference the exact recovery semantics in force at execution time.

## Security boundary

Recovery contracts are high-integrity configuration. They must not be writable by the same untrusted agent whose actions they govern. Production implementations should protect them with separate authorization and audit controls.
