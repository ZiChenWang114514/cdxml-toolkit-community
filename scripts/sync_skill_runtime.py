"""Export lightweight compatibility files from the package into a ChemDraw Skill."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil


RUNTIME_MODULES = {
    "artifact_safety": "artifact_safety",
    "chemistry_compare": "chemistry_compare",
    "chemscript_sdk": "chemscript_sdk",
    "chemscript_sdk_runtime": "chemscript_sdk_runtime",
    "decimer_api": "decimer_api",
    "extended_tools": "extended_tools",
    "install_decimer_models": "install_decimer_models",
    "mcp_compat": "mcp_compat",
    "mcp_server": "mcp_server",
    "native_io": "native_io",
    "native_renderer": "native_renderer",
    "office_objects": "office_objects",
    "official_overrides": "official_overrides",
    "process_control": "process_control",
    "remote_tools": "remote_tools",
    "resource_lock": "resource_lock",
    "runtime_diagnostics": "runtime_diagnostics",
    "runtime_discovery": "runtime_discovery",
    "structure_fidelity": "structure_fidelity",
    "telemetry": "telemetry",
    "tool_registry": "tool_registry",
    "tool_worker": "tool_worker",
    "generate_tool_reference": "generate_reference",
}

RUNTIME_TESTS = {
    "test_artifact_safety.py",
    "test_chemistry_compare.py",
    "test_chemscript_sdk.py",
    "test_decimer_api.py",
    "test_extended_tools.py",
    "test_generate_reference.py",
    "test_http_transport.py",
    "test_install_decimer_models.py",
    "test_mcp_compat.py",
    "test_mcp_stdio.py",
    "test_native_io.py",
    "test_native_renderer.py",
    "test_office_objects.py",
    "test_process_control.py",
    "test_runtime_diagnostics.py",
    "test_structure_fidelity.py",
    "test_worker_runtime.py",
}


def _wrapper_source(module_name: str) -> str:
    return f'''"""Compatibility proxy for cdxml_toolkit.mcp_runtime.{module_name}."""

from __future__ import annotations

from importlib import import_module as _import_module
import sys as _sys

_runtime = _import_module("cdxml_toolkit.mcp_runtime.{module_name}")

if __name__ == "__main__":
    _main = getattr(_runtime, "main", None)
    if _main is None:
        raise SystemExit("This compatibility module has no command-line interface.")
    raise SystemExit(_main())
else:
    _sys.modules[__name__] = _runtime
'''


def export_skill(repo_root: Path, skill_root: Path) -> None:
    scripts = skill_root / "scripts"
    references = skill_root / "references"
    runtime_tests = repo_root / "tests" / "runtime"
    scripts.mkdir(parents=True, exist_ok=True)
    references.mkdir(parents=True, exist_ok=True)

    for skill_name, package_name in sorted(RUNTIME_MODULES.items()):
        (scripts / f"{skill_name}.py").write_text(
            _wrapper_source(package_name), encoding="utf-8", newline="\n"
        )

    for filename in sorted(RUNTIME_TESTS):
        shutil.copyfile(runtime_tests / filename, scripts / filename)

    shutil.copyfile(repo_root / "docs" / "mcp-tools.md", references / "mcp-signatures.md")
    shutil.copyfile(repo_root / "docs" / "mcp-schema.json", references / "mcp-schema.json")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_root", type=Path)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args()
    export_skill(args.repo_root.resolve(), args.skill_root.resolve())


if __name__ == "__main__":
    main()
