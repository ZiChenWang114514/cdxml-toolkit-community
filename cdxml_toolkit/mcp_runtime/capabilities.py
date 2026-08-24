"""Content-free runtime identity and capability reporting."""

from __future__ import annotations

import hashlib
import importlib.metadata
import inspect
import json
import os
from pathlib import Path
import sys
from typing import Any


def _distribution(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def get_toolkit_capabilities() -> dict[str, Any]:
    """Return versions, profile, tool schema digest, and local capability status."""
    from .runtime_diagnostics import diagnose_runtime
    from .tool_registry import build_registry

    profile = os.environ.get("CHEMDRAW_MCP_PROFILE", "codex")
    registry = build_registry(profile=profile)
    schema = [
        {
            "name": name,
            "signature": str(inspect.signature(spec.function)),
            "group": spec.group,
            "resource_class": spec.resource_class,
        }
        for name, spec in sorted(registry.items())
    ]
    digest = hashlib.sha256(
        json.dumps(schema, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    diagnostics = diagnose_runtime()
    distributions = {
        "cdxml-toolkit-community": _distribution("cdxml-toolkit-community"),
        "cdxml-toolkit": _distribution("cdxml-toolkit"),
        "mcp": _distribution("mcp"),
    }
    installed_toolkits = [
        name
        for name, version in distributions.items()
        if version and name != "mcp"
    ]
    warnings = []
    if len(installed_toolkits) > 1:
        warnings.append(
            "Both cdxml-toolkit-community and cdxml-toolkit are installed; remove the legacy distribution."
        )
    return {
        "ok": True,
        "outputs": {
            "profile": profile,
            "tool_count": len(registry),
            "tool_schema_sha256": digest,
            "tools": schema,
            "distributions": distributions,
            "python": {
                "path": str(Path(sys.executable).resolve()),
                "version": sys.version.split()[0],
                "bits": 64 if sys.maxsize > 2**32 else 32,
            },
            "capabilities": diagnostics.get("capabilities", {}),
        },
        "warnings": warnings,
        "metadata": {"content_free": True},
    }


SYSTEM_TOOLS = {"get_toolkit_capabilities": get_toolkit_capabilities}
