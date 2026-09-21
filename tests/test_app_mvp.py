from pathlib import Path

from agent_recovery.app_fixture import build_app_fixture

ROOT = Path(__file__).resolve().parents[1]


def test_app_fixture_is_backend_derived_and_non_authorizing():
    payload = build_app_fixture()

    assert payload["product"] == {
        "name": "Agent Recovery Platform",
        "mode": "read_only_operator_console",
        "authority": "none",
    }
    assert payload["overview"]["recoverability_fraction"] == 0.75
    assert payload["overview"]["verification_status"] == "verified"
    assert payload["overview"]["containment_active"] is True
    assert payload["overview"]["irreversible_residual_count"] == 1
    assert payload["overview"]["restoration_eligible"] is False
    assert payload["incident"]["authority"] == "none"
    assert payload["assessment"]["evidence_identity"]["sha256"]


def test_app_static_assets_keep_security_logic_out_of_frontend():
    html = (ROOT / "app" / "index.html").read_text(encoding="utf-8")
    javascript = (ROOT / "app" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "app" / "styles.css").read_text(encoding="utf-8")

    assert 'data-view="overview"' in html
    assert 'data-view="incident"' in html
    assert 'data-view="assessment"' in html
    assert 'fetch("./data/sample.json"' in javascript
    assert "RecoveryEngine" not in javascript
    assert "authorize(" not in javascript
    assert "approval" not in javascript.lower()
    assert ".metric-grid" in css
    assert "@media" in css
