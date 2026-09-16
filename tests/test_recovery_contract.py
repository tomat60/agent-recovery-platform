import pytest

from agent_recovery.recovery_contract import (
    RecoveryClass,
    RecoveryContractError,
    parse_recovery_contract,
)


def contract(**overrides):
    value = {
        "version": "1",
        "tool_id": "crm.contacts",
        "action_id": "contact.update",
        "recovery_class": "reversible",
        "recovery_operation": "contact.restore",
        "verification_operation": "contact.read",
        "parameter_binding": "sha256:parameters",
        "context_binding": "sha256:authority-scope",
    }
    value.update(overrides)
    return value


def test_reversible_contract_declares_recovery_and_verification():
    parsed = parse_recovery_contract(contract())
    assert parsed.recovery_class is RecoveryClass.REVERSIBLE
    assert parsed.recovery_operation == "contact.restore"
    assert parsed.verification_operation == "contact.read"


def test_compensatable_contract_requires_compensation_operation():
    parsed = parse_recovery_contract(
        contract(recovery_class="compensatable", recovery_operation="payment.refund")
    )
    assert parsed.recovery_class is RecoveryClass.COMPENSATABLE


def test_irreversible_contract_keeps_residual_truth_explicit():
    parsed = parse_recovery_contract(
        contract(recovery_class="irreversible", recovery_operation=None)
    )
    assert parsed.recovery_class is RecoveryClass.IRREVERSIBLE
    assert parsed.recovery_operation is None


@pytest.mark.parametrize(
    "overrides",
    [
        {"version": "2"},
        {"tool_id": ""},
        {"action_id": None},
        {"verification_operation": ""},
        {"parameter_binding": ""},
        {"context_binding": ""},
        {"recovery_class": "reversible", "recovery_operation": None},
        {"recovery_class": "compensatable", "recovery_operation": None},
        {"recovery_class": "irreversible", "recovery_operation": "pretend.undo"},
        {"recovery_class": "unknown"},
    ],
)
def test_contract_validation_fails_closed(overrides):
    with pytest.raises(RecoveryContractError):
        parse_recovery_contract(contract(**overrides))
