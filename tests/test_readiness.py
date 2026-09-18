from __future__ import annotations

from agent_recovery.contracts import RecoveryClass as RuntimeRecoveryClass
from agent_recovery.contracts import RecoveryContract as RuntimeRecoveryContract
from agent_recovery.contracts import RiskLevel
from agent_recovery.readiness import evaluate_recovery_readiness
from agent_recovery.recovery_contract import parse_recovery_contract
from agent_recovery.runtime_binding import TrustedRuntimeBinding


def _declaration(
    tool_id: str,
    recovery_class: str,
    *,
    action_id: str = "write",
    approval: bool = False,
):
    recoverable = recovery_class != "irreversible"
    return parse_recovery_contract(
        {
            "version": "1",
            "tool_id": tool_id,
            "action_id": action_id,
            "recovery_class": recovery_class,
            "recovery_operation": "recover" if recoverable else None,
            "verification_operation": "verify",
            "parameter_binding": "sha256:parameters",
            "context_binding": "sha256:authority-scope",
            "action_approval_required": approval,
            "containment_scopes": ["tool", "session"],
        }
    )


def _runtime(
    tool_id: str,
    recovery_class: RuntimeRecoveryClass,
    *,
    action_type: str = "write",
    version: str = "1",
    approval: bool = False,
) -> RuntimeRecoveryContract:
    recoverable = recovery_class is not RuntimeRecoveryClass.IRREVERSIBLE
    return RuntimeRecoveryContract(
        tool_id=tool_id,
        action_type=action_type,
        risk_level=RiskLevel.MEDIUM,
        recovery_class=recovery_class,
        executor=lambda state, params: None,
        verifier=lambda state, params: None,
        recovery_executor=(lambda state, params: None) if recoverable else None,
        recovery_params_builder=(lambda result, observed, params: params) if recoverable else None,
        approval_before_action=approval,
        containment_scopes=("tool", "session"),
        contract_version=version,
    )


def _binding(runtime: RuntimeRecoveryContract) -> TrustedRuntimeBinding:
    return TrustedRuntimeBinding(
        runtime_contract=runtime,
        verification_operation="verify",
        parameter_binding="sha256:parameters",
        context_binding="sha256:authority-scope",
        recovery_operation=(
            None if runtime.recovery_class is RuntimeRecoveryClass.IRREVERSIBLE else "recover"
        ),
    )


def _key(tool_id: str, action_id: str = "write", version: str = "1"):
    return (tool_id, action_id, version)


def test_readiness_reports_declarative_coverage_and_missing_runtime_binding():
    reversible = _declaration("store.write", "reversible")
    compensatable = _declaration("mail.send", "compensatable", approval=True)
    irreversible = _declaration("external.publish", "irreversible")

    store_runtime = _runtime("store.write", RuntimeRecoveryClass.REVERSIBLE)
    publish_runtime = _runtime("external.publish", RuntimeRecoveryClass.IRREVERSIBLE)
    report = evaluate_recovery_readiness(
        (reversible, compensatable, irreversible),
        runtime_bindings={
            _key("store.write"): _binding(store_runtime),
            _key("external.publish"): _binding(publish_runtime),
        },
    )

    assert report.total_actions == 3
    assert report.structurally_recoverable == 2
    assert report.recoverability_fraction == 2 / 3
    assert report.reversible == 1
    assert report.compensatable == 1
    assert report.irreversible == 1
    assert report.human_approval_required == 1
    assert report.missing_runtime_bindings == ("mail.send:write@1",)
    assert report.blockers == ("missing_runtime_binding:mail.send:write@1",)


def test_readiness_fails_closed_on_runtime_identity_mismatch():
    declared = _declaration("store.write", "reversible", action_id="contact.update")
    stale_runtime = _runtime(
        "store.write",
        RuntimeRecoveryClass.REVERSIBLE,
        action_type="contact.delete",
        version="1",
    )

    report = evaluate_recovery_readiness(
        (declared,),
        runtime_bindings={
            _key("store.write", "contact.update"): _binding(stale_runtime)
        },
    )

    assert report.missing_runtime_bindings == ("store.write:contact.update@1",)
    assert report.blockers == ("runtime_binding_mismatch:store.write:contact.update@1",)


def test_readiness_fails_closed_on_runtime_policy_mismatch():
    declared = _declaration("store.write", "reversible", approval=True)
    runtime = _runtime("store.write", RuntimeRecoveryClass.REVERSIBLE, approval=False)

    report = evaluate_recovery_readiness(
        (declared,),
        runtime_bindings={_key("store.write"): _binding(runtime)},
    )

    assert report.human_approval_required == 1
    assert report.blockers == ("runtime_binding_mismatch:store.write:write@1",)


def test_readiness_supports_multiple_actions_for_one_tool_without_binding_collision():
    update = _declaration("contacts", "reversible", action_id="contact.update")
    delete = _declaration("contacts", "compensatable", action_id="contact.delete")
    update_runtime = _runtime(
        "contacts", RuntimeRecoveryClass.REVERSIBLE, action_type="contact.update"
    )
    delete_runtime = _runtime(
        "contacts", RuntimeRecoveryClass.COMPENSATABLE, action_type="contact.delete"
    )

    report = evaluate_recovery_readiness(
        (update, delete),
        runtime_bindings={
            _key("contacts", "contact.update"): _binding(update_runtime),
            _key("contacts", "contact.delete"): _binding(delete_runtime),
        },
    )

    assert report.structurally_recoverable == 2
    assert report.missing_runtime_bindings == ()
    assert report.blockers == ()


def test_declarative_report_never_supplies_executable_authority():
    declared = _declaration("store.write", "reversible")

    report = evaluate_recovery_readiness((declared,), runtime_bindings={})

    assert report.structurally_recoverable == 1
    assert report.missing_runtime_bindings == ("store.write:write@1",)
    assert report.blockers == ("missing_runtime_binding:store.write:write@1",)
