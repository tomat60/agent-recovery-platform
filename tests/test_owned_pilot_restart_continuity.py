from __future__ import annotations

from agent_recovery.evidence_store import JsonlEvidenceStore
from agent_recovery.operator_api import incident_operator_detail
from agent_recovery.persisted_operator_api import persisted_incident_detail
from agent_recovery.pilot_sandbox import run_multisurface_recovery_sandbox


def test_owned_pilot_operator_detail_survives_restart(tmp_path, monkeypatch):
    """The buyer-visible pilot must survive controller restart on canonical evidence."""

    evidence_path = tmp_path / "pilot-ledger.jsonl"
    original_append = JsonlEvidenceStore.append

    def persist_every_event(self, event):
        original_append(self, event)

    # The sandbox remains zero-network. Capture its admitted ledger events at the durable
    # boundary, then reconstruct a fresh controller/read model from disk.
    from agent_recovery import pilot_sandbox

    original_ledger = pilot_sandbox.ActionLedger

    class PersistingLedger(original_ledger):
        def append(self, event):
            chained = super().append(event)
            JsonlEvidenceStore(evidence_path).append(chained)
            return chained

    monkeypatch.setattr(pilot_sandbox, "ActionLedger", PersistingLedger)
    live = run_multisurface_recovery_sandbox()

    restarted = persisted_incident_detail(evidence_path, incident_id=live["incident_id"])
    detail = restarted["incident"]

    assert restarted["authority"] == "none"
    assert detail["authority"] == "none"
    assert detail["incident_id"] == live["incident_id"]
    assert detail["status"] == live["operator_status"]
    assert detail["next_action"] == live["operator_next_action"]
    assert detail["recovery_candidates"] == live["operator_recovery_candidates"]
    assert detail["side_effects"] == live["operator_side_effects"]
    assert detail["active_containment"]
    assert any(residual["irreversible"] is True for residual in detail["residuals"])

    # A second reconstruction proves the read path does not depend on process-local state.
    reloaded_ledger = JsonlEvidenceStore(evidence_path).load_ledger()
    assert incident_operator_detail(reloaded_ledger, incident_id=live["incident_id"]) == detail
