import pytest

from agent_recovery.recovery_contract import (
    RecoveryClass,
    RecoveryContractError,
    RiskLevel,
    parse_recovery_contract,
    parse_recovery_contract_json,
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


def test_full_declarative_contract_round_trip_is_canonical_and_non_executable():
    parsed = parse_recovery_contract(
        contract(
            risk_level="high",
            action_approval_required=True,
            recovery_approval_required=True,
            containment_scopes=["crm:tenant-7", "contact:42"],
            recovery_window_seconds=900,
            reconciliation_operation="contact.reconcile",
            resource_key_operation="contact.resource_key",
            side_effects=["crm_record_write", "search_index_update"],
        )
    )

    canonical = parsed.canonical_json()
    restored = parse_recovery_contract_json(canonical)

    assert restored == parsed
    assert restored.risk_level is RiskLevel.HIGH
    assert restored.containment_scopes == ("crm:tenant-7", "contact:42")
    assert restored.side_effects == ("crm_record_write", "search_index_update")
    assert canonical == restored.canonical_json()
    assert "executor" not in canonical
    assert "callable" not in canonical


def test_high_impact_irreversible_contract_requires_parameter_bound_preapproval():
    with pytest.raises(RecoveryContractError, match="pre-action approval"):
        parse_recovery_contract(
            contract(
                recovery_class="irreversible",
                recovery_operation=None,
                risk_level="critical",
            )
        )

    with pytest.raises(RecoveryContractError, match="parameter-bound"):
        parse_recovery_contract(
            contract(
                recovery_class="irreversible",
                recovery_operation=None,
                risk_level="critical",
                action_approval_required=True,
                parameter_bound_approval_required=False,
            )
        )


def test_external_json_is_data_only_and_rejects_non_object_payload():
    with pytest.raises(RecoveryContractError, match="object"):
        parse_recovery_contract_json('["not", "a", "contract"]')


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
        {"risk_level": "unknown"},
        {"action_approval_required": "yes"},
        {"recovery_approval_required": 1},
        {"parameter_bound_approval_required": None},
        {"containment_scopes": ["scope", "scope"]},
        {"containment_scopes": "scope"},
        {"side_effects": [""]},
        {"recovery_window_seconds": 0},
        {"recovery_window_seconds": True},
        {"reconciliation_operation": ""},
        {"resource_key_operation": 7},
    ],
)
def test_contract_validation_fails_closed(overrides):
    with pytest.raises(RecoveryContractError):
        parse_recovery_contract(contract(**overrides))
