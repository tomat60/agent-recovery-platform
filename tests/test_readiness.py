from __future__ import annotations

from agent_recovery.contracts import RecoveryClass, RecoveryContract, RiskLevel
from agent_recovery.readiness import evaluate_recovery_readiness


def _contract(
    tool_id: str,
    recovery_class: RecoveryClass,
    *,
    version: str = "1",
    approval: bool = False,
) -> RecoveryContract:
    recoverable = recovery_class is not RecoveryClass.IRREVERSIBLE
    return RecoveryContract(
        tool_id=tool_id,
        action_type="write",
        risk_level=RiskLevel.MEDIUM,
        recovery_class=recovery_class,
        executor=lambda state, params: None,
        verifier=lambda state, params: None,
        recovery_executor=(lambda state, params: None) if recoverable else None,
        recovery_params_builder=(lambda result, observed, params: params) if recoverable else None,
        approval_before_action=approval,
        contract_version=version,
    )


def test_readiness_reports_coverage_and_missing_runtime_binding():
    reversible = _contract("store.write", RecoveryClass.REVERSIBLE)
    compensatable = _contract("mail.send", RecoveryClass.COMPENSATABLE, approval=True)
    irreversible = _contract("external.publish", RecoveryClass.IRREVERSIBLE)

    report = evaluate_recovery_readiness(
        (reversible, compensatable, irreversible),
        runtime_bindings={"store.write": reversible, "external.publish": irreversible},
    )

    assert report.total_actions == 3
    assert report.structurally_recoverable == 2
    assert report.recoverability_fraction == 2 / 3
    assert report.reversible == 1
    assert report.compensatable == 1
    assert report.irreversible == 1
    assert report.human_approval_required == 1
    assert report.missing_runtime_bindings == ("mail.send@1",)
    assert report.blockers == ("missing_runtime_binding:mail.send@1",)


def test_readiness_fails_binding_evidence_closed_on_version_mismatch():
    declared = _contract("store.write", RecoveryClass.REVERSIBLE, version="1")
    stale_runtime = _contract("store.write", RecoveryClass.REVERSIBLE, version="2")

    report = evaluate_recovery_readiness(
        (declared,),
        runtime_bindings={"store.write": stale_runtime},
    )

    assert report.missing_runtime_bindings == ("store.write@1",)
    assert report.blockers == ("runtime_binding_mismatch:store.write@1",)
