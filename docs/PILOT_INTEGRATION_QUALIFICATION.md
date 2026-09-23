# Pilot Integration Qualification

Date: 2026-09-24

Purpose: turn the first design-partner targets into bounded, evidence-driven pilot shapes without credentials, customer data, production access, or claims beyond the accepted product boundary. These are qualification maps, not vendor commitments or implemented connectors.

## Decision rule

Prefer a pilot only when it can expose consequential writes at a stable tool boundary, identify mutable resources, capture before/after evidence, declare a Recovery Contract, execute or explicitly refuse compensation, replay the repaired path, and make restoration depend on current verification evidence. A successful retry is not recovery proof.

## Composio: representative cross-app write chain

### Hypothesis

An agent uses a managed tool boundary to update a CRM-like record and then create a task/message in a second application. The second write fails or is later judged unsafe after the first write has committed. The assessment asks whether the already-completed effect can be reconstructed, compensated, verified, and replayed before authority is restored.

### Synthetic surfaces

- `crm.contact.update`: mutable contact record; compensatable by restoring the captured prior field values when current state still matches the incident lineage.
- `tasks.task.create`: created external object; reversible when deletion/cancellation is supported and independently verified.

No Composio credentials or live third-party APIs are required for the first qualification run. The existing owned multi-surface pilot remains the execution substrate; this map tests whether its evidence model matches the likely integration boundary.

### Recovery Contract mapping

| Contract field | CRM update | Task create |
| --- | --- | --- |
| `tool_id` | `composio.crm` | `composio.tasks` |
| `action_type` | `contact.update` | `task.create` |
| `risk_level` | medium/high by changed field | medium |
| `recovery_class` | compensatable | reversible |
| `verifier` | read current contact and compare incident-bound fields/version | read task identity/state |
| `recovery_executor` | restore captured prior values | delete/cancel exact created task |
| `recovery_params_builder` | incident-bound resource id + prior values + expected current lineage | incident-bound created object id |
| `resource_key_builder` | canonical CRM contact identity | canonical task identity plus parent/project when shared state matters |
| `approval_before_recovery` | true when compensation overwrites post-incident legitimate changes | false for isolated synthetic task; qualify for real pilot |
| `containment_scopes` | tool, session, affected resource/authority | tool, session, affected resource/authority |

### Evidence needed

1. normalized action evidence for both writes with one causal incident identity;
2. durable before/after evidence for the CRM mutation and created-object identity for the task;
3. resource keys proving whether another writer touched either resource after the incident;
4. compensation outcome plus independent verifier output for every recoverable effect;
5. explicit residual if current state makes safe compensation impossible;
6. repaired replay result;
7. restoration decision limited to the verified-safe scope.

### Disqualifying discovery

Do not build a Composio-specific connector if qualification shows that the tool boundary cannot expose stable action/resource identity or enough post-write evidence to bind verification. Prefer a thin adapter to framework-neutral ingestion if those fields are available. Do not duplicate managed auth or observability.

## n8n: synthetic two-surface workflow

### Hypothesis

An AI-agent workflow updates a customer/order-like record, then emits a downstream ticket/message. A later node failure or policy correction must not be treated as solved merely because n8n can retry the workflow. The assessment distinguishes workflow execution status from verified external-effect recovery.

### Synthetic nodes

1. `record.update` writes shared structured state.
2. `ticket.create` creates a second-surface side effect.
3. injected failure occurs after both writes or between verification and downstream completion.
4. incident containment blocks further consequential writes for the affected workflow authority.
5. recovery planner orders compensation using causal dependencies and shared-resource keys.
6. verifiers establish actual post-recovery state.
7. repaired replay runs only after compensation/residual classification.
8. restoration remains fail-closed unless current recovery and replay evidence covers the exact scope.

### Recovery Contract mapping

Use two contracts with the same primitives as the Composio qualification: a compensatable shared-record update and a reversible created-object action. The n8n adapter, if later justified, should emit framework-neutral action evidence and runtime bindings; it must not embed a second recovery policy engine in workflow-specific code.

### Acceptance evidence for a real pilot path

- deterministic fixture or owned sandbox reproduces partial completion;
- persisted incident survives restart;
- causal graph preserves ordering and shared-resource hazards;
- recovery candidate is rejected when evidence is stale or another writer invalidates compensation assumptions;
- successful compensation is independently verified;
- irreversible/unrecoverable effects remain residual rather than being labeled restored;
- replay/regression is incident-derived;
- operator API/console shows evidence separately from advisory reasoning;
- exact restoration scope is evidence-derived.

## Product-gap decision

Current accepted primitives are sufficient to model both qualification workflows. No new backend feature is justified yet. The first implementation trigger is concrete evidence that a target cannot supply one of the minimum integration fields needed by the existing framework-neutral boundary: stable action identity, causal/trace identity, resource identity, post-write outcome, or a trusted runtime binding for verification/recovery. If that happens, implement the smallest adapter/schema extension and add a deterministic contract test before broad connector work.

## Buyer questions this mapping should answer

- Can your write-capable agent/tool boundary expose stable action and resource identities after a write commits?
- Which actions have native inverse operations, compensating operations, or no safe recovery path?
- Can a verifier read the authoritative external state independently of the model that requested the action?
- What happens when another actor legitimately changes the same resource before recovery?
- Is retry currently being used as a proxy for recovery, and can you prove what happened to already-completed side effects?
- Which exact authority should remain contained until compensation and replay evidence is current?
