from __future__ import annotations

from agent_recovery.contracts import RecoveryClass as RuntimeRecoveryClass
from agent_recovery.contracts import RecoveryContract as RuntimeRecoveryContract
from agent_recovery.contracts import RiskLevel
from agent_recovery.readiness import evaluate_recovery_readiness
from agent_recovery.recovery_contract import parse_recovery_contract


def _declaration(
    tool_id: str,
    recovery_class: str,
    *,
    action_id: str = "write",
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
        }
    )


def _runtime(
    tool_id: str,
    recovery_class: RuntimeRecoveryClass,
    *,
    action_type: str = "write",
    version: str = "1",
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
        contract_version=version,
    )


def test_readiness_reports_declarative_coverage_and_missing_runtime_binding():
    reversible = _declaration("store.write", "reversible")
    compensatable = _declaration("mail.send", "compensatable")
    irreversible = _declaration("external.publish", "irreversible")

    report = evaluate_recovery_readiness(
        (reversible, compensatable, irreversible),
        runtime_bindings={
            "store.write": _runtime("store.write", RuntimeRecoveryClass.REVERSIBLE),
            "external.publish": _runtime(
                "external.publish", RuntimeRecoveryClass.IRREVERSIBLE
            ),
        },
    )

    assert report.total_actions == 3
    assert report.structurally_recoverable == 2
    assert report.recoverability_fraction == 2 / 3
    assert report.reversible == 1
    assert report.compensatable == 1
    assert report.irreversible == 1
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
        runtime_bindings={"store.write": stale_runtime},
    )

    assert report.missing_runtime_bindings == ("store.write:contact.update@1",)
    assert report.blockers == ("runtime_binding_mismatch:store.write:contact.update@1",)


def test_declarative_report_never_supplies_executable_authority():
    declared = _declaration("store.write", "reversible")

    report = evaluate_recovery_readiness((declared,), runtime_bindings={})

    assert report.structurally_recoverable == 1
    assert report.missing_runtime_bindings == ("store.write:write@1",)
    assert report.blockers == ("missing_runtime_binding:store.write:write@1",)
