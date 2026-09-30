from pathlib import Path


PROJECT_STATE = (
    Path(__file__).resolve().parents[1] / "docs" / "PROJECT_CURRENT_STATE.md"
)


def test_project_state_does_not_encode_markdown_newlines_as_text() -> None:
    content = PROJECT_STATE.read_text(encoding="utf-8")

    assert r"\n-" not in content
