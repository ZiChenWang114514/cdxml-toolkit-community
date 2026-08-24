# Maintenance Guide

This document defines how `cdxml-toolkit-community` tracks upstream, tests
changes, and prepares releases.

## Repository model

- `origin` is `ZiChenWang114514/cdxml-toolkit-community`.
- `upstream` is `leehiufung911/cdxml-toolkit`.
- `main` contains reviewed community changes.
- Feature and repair work uses short-lived branches.
- The compatible import package remains `cdxml_toolkit`.

The project starts from the complete upstream Git history. Upstream version
`0.5.17` was introduced by commit
`0ae1a94275f2c91e2c45a832c33744c22447d24b`; the PyPI source distribution must
still be compared before that commit is declared an exact release snapshot.

## Upstream synchronization

Review upstream commits before merging them into a dedicated branch:

```powershell
git fetch upstream
git log --oneline main..upstream/main
git switch -c sync/upstream-YYYYMMDD
git merge --no-commit upstream/main
```

Resolve changes deliberately, run the complete portable suite, and add native
checks when affected modules use ChemDraw, ChemScript, or Office. Merge the
sync branch through a pull request. Do not force-push `main`.

## Supported environments

| Capability | Maintained environment |
| --- | --- |
| Portable CDXML and RDKit behavior | Windows, Python 3.10-3.13 |
| MCP server | MCP Python SDK 1.x and 2.x |
| ChemDraw COM and ChemScript | Licensed Windows workstation |
| Editable Office objects | Desktop Word and PowerPoint on Windows |
| DECIMER recognition | Optional `decimer` dependency group and local weights |

Hosted CI validates portable behavior. Native software checks must run on a
licensed local or self-hosted Windows machine and must identify skipped
applications explicitly.

## Compatibility policy

- Patch releases repair compatible behavior.
- Minor releases may add APIs and deprecate old behavior.
- Breaking changes require a major release or a clearly marked prerelease.
- MCP tool names and result fields remain compatible throughout a minor series.
- Deprecated public members remain available for at least one minor release.

## Release procedure

1. Update the version in `pyproject.toml` and `cdxml_toolkit/__init__.py`.
2. Run `python -m pytest -m "not network" -q` on Python 3.10-3.13.
3. Run applicable native ChemDraw, ChemScript, and Office checks.
4. Run `python -m build` and `python -m twine check dist/*` in a clean tree.
5. Confirm the bundled JRE is a real LFS object and review its license and hash.
6. Create an annotated `vX.Y.Z` tag and a GitHub Release with compatibility notes.
7. Publish to TestPyPI before any production package index.

The GitHub build workflow creates inspectable wheel and source artifacts. PyPI
publishing remains disabled until the community distribution name is reserved
and Trusted Publishing is configured with an approved GitHub environment.

## Initial maintenance priorities

1. Verify the PyPI `0.5.17` source archive against upstream history.
2. Move the bundled JRE to a verified optional download after licensing review.
3. Define stable, experimental, and internal Python APIs.
4. Add a licensed Windows self-hosted test workflow for native applications.
5. Integrate the hardened MCP 2.x and worker-process behavior from
   `codex-chemdraw-skill` through focused, reviewed changes.
