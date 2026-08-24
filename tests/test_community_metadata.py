"""Community distribution metadata checks."""

from __future__ import annotations

from pathlib import Path
import re

import cdxml_toolkit


ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = (ROOT / "pyproject.toml").read_text(encoding="utf-8")


def _project_value(name: str) -> str:
    match = re.search(rf'^{re.escape(name)}\s*=\s*"([^"]+)"$', PYPROJECT, re.MULTILINE)
    assert match is not None, f"Missing project value: {name}"
    return match.group(1)


def test_distribution_uses_community_name() -> None:
    assert _project_value("name") == "cdxml-toolkit-community"


def test_runtime_and_distribution_versions_match() -> None:
    assert cdxml_toolkit.__version__ == _project_value("version")


def test_community_repository_urls_are_present() -> None:
    assert "ZiChenWang114514/cdxml-toolkit-community" in PYPROJECT
    assert "leehiufung911/cdxml-toolkit" in PYPROJECT

