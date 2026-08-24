# cdxml-toolkit-community

[![Validate](https://github.com/ZiChenWang114514/cdxml-toolkit-community/actions/workflows/validate.yml/badge.svg)](https://github.com/ZiChenWang114514/cdxml-toolkit-community/actions/workflows/validate.yml)
[![Python 3.10-3.13](https://img.shields.io/badge/Python-3.10--3.13-3776AB)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-2f855a.svg)](LICENSE)

Community-maintained continuation of
[`leehiufung911/cdxml-toolkit`](https://github.com/leehiufung911/cdxml-toolkit).
The distribution name is `cdxml-toolkit-community`; the compatible Python
import remains `cdxml_toolkit`.

Chemistry office automation toolkit with MCP (Model Context Protocol) server. Lets LLM agents draw reaction schemes, parse ELN exports, analyze LCMS data, and produce publication-ready ChemDraw (CDXML) output.

The community runtime exposes 15 compatible core tools plus 20 hardened and
extended tools for layout, Office, analysis, ChemScript, remote recognition,
diagnostics, and capability discovery. Tool execution is isolated in bounded
worker processes; native ChemDraw calls share a serialized resource queue.

> Original project statement: Built and tested with Claude Code (Opus 4.6).
> The original design and implementation were directed by Hiu Fung Kevin Lee,
> a PhD organic chemist.

![Agent builds a 3-step reaction scheme from an image and natural language instructions](docs/images/showcase-example.webp)

*The user pastes an image of a Boc deprotection, asks for a modified version with a different scaffold plus two extra reaction steps. The agent resolves all building blocks, applies transformations with structural diffs, and renders a .cdxml native 3-step scheme — all via MCP tool calls, no hand-written SMILES.*

## Installation

**Prerequisites:** 64-bit Python 3.10–3.13. Native rendering, ChemScript, and
editable Office objects additionally require Windows and an activated desktop
ChemDraw installation. Python 3.14 is not yet supported.

```bash
# 1. Create a conda environment and clone the community project
conda create -n cdxml python=3.12 pip -y
conda activate cdxml
git clone https://github.com/ZiChenWang114514/cdxml-toolkit-community.git
cd cdxml-toolkit-community

# Remove the legacy distribution if it was installed previously. Both
# distributions provide the same cdxml_toolkit Python import directory.
pip uninstall -y cdxml-toolkit

# Complete community runtime
pip install -e ".[all]"

# 2. Run the doctor to check your setup
cdxml-doctor --no-tests
```

The core installation includes CDXML utilities, RDKit, and MCP. Optional groups
are `windows`, `office`, `chemscript`, `analysis`, `image`, `decimer`, `opsin`,
`http`, `all`, and `dev`.

`cdxml-doctor --no-tests` is read-only. Use `cdxml-doctor --json` for a
machine-readable capability report. It never configures ChemScript unless
`--configure-chemscript` is supplied.

The wheel does not contain a JRE. OPSIN first uses `JAVA_HOME` or `java` on
`PATH`. When Java is absent it can download Temurin from Adoptium, or install a
pre-approved local archive:

```powershell
$env:CDXML_TOOLKIT_JRE_ZIP = "C:\installers\temurin-jre.zip"
$env:CDXML_TOOLKIT_JRE_SHA256 = "approved sha256"
cdxml-doctor --no-tests
```

JRE installation verifies SHA-256 when supplied, limits archive and extracted
sizes, rejects unsafe ZIP paths, and records an installation manifest.

To configure ChemScript explicitly, run:

```powershell
cdxml-doctor --no-tests --configure-chemscript
```

The command detects the ChemDraw installation and presents the planned setup:

```
=== ChemScript setup ===

  Found ChemScript DLLs:
    Managed:  C:\...\CambridgeSoft.ChemScript16.dll (32-bit)
    Native:   C:\...\ChemScript160.dll (32-bit)

  32-bit ChemScript requires a 32-bit Python environment.
  The doctor will run the following commands:

    set CONDA_SUBDIR=win-32 && conda create -n chemscript32 python=3.10 pip -y
    C:\Users\YOU\miniconda3\envs\chemscript32\python.exe -m pip install pythonnet

  Proceed? [y/N] y

  Creating chemscript32 conda env...
  chemscript32 env created.
  Installing pythonnet in chemscript32...
  pythonnet installed.
  Saving config...
  ChemScript configured. Run cdxml-doctor again to verify.
```

Run `cdxml-doctor --json` afterward to confirm ChemScript status.

ChemScript is optional — without it, OPSIN handles IUPAC name resolution as an offline fallback. ChemScript adds bidirectional name-to-structure conversion and aligned naming.

To install the latest community development version directly from GitHub:

```bash
pip install "cdxml-toolkit-community[all] @ git+https://github.com/ZiChenWang114514/cdxml-toolkit-community.git@main"
```

## MCP server (Claude Desktop)

The primary interface is the MCP server. Connect it to Claude Desktop and chat naturally: "Draw deucravacitinib", "Help me complete my lab book", "Extract structures from this image".

Open `%APPDATA%\Claude\claude_desktop_config.json`. It will look something like this:

```json
{
  "preferences": {
    ...
  }
}
```

Add an `"mcpServers"` key at the top level, next to `"preferences"` (change `YOUR_USERNAME` to your Windows username):

```json
{
  "mcpServers": {
    "cdxml-toolkit": {
      "command": "C:\\Users\\YOUR_USERNAME\\miniconda3\\envs\\cdxml\\python.exe",
      "args": ["-m", "cdxml_toolkit.mcp_runtime", "--profile", "codex"]
    }
  },
  "preferences": {
    ...
  }
}
```

Restart Claude Desktop. Verify by asking:

```
> Resolve "aspirin", then draw it.
```

Expected: 2 tool calls (resolve_name, draw_molecule), produces an aspirin CDXML file.

The same config pattern works with other MCP-compatible agents (Claude Code, opencode, qwen-agent, etc.).

### Agent instructions file

Copy `CLAUDE.md` from the repository root into your agent's working directory. This file contains critical rules that prevent the agent from hallucinating chemistry:

- **Never write SMILES from built-in knowledge or vision.** Every molecule must come from a tool (`resolve_name`, `modify_molecule`, `extract_structures_from_image`, etc.).
- **Never use vision to identify molecular structures.** Image reading can recognize that "this is a reaction scheme" but cannot reliably determine exact atom connectivity. Always use `extract_structures_from_image` for that — it runs DECIMER neural network OCR and returns validated SMILES.
- **Never edit SMILES directly.** Use `modify_molecule` which provides an MCS diff to verify the change.

For Claude Code, name it `CLAUDE.md`. For other agents, use `agents.md` or whatever your framework reads as system instructions.

## MCP tools

The default `codex` profile contains 35 tools. Smaller profiles reduce tool
selection noise while preserving the 15 compatible core tools and
`get_toolkit_capabilities`:

| Profile | Tools | Additional focus |
|---------|------:|------------------|
| `core` | 16 | Core tools plus capability discovery |
| `office` | 21 | Office inspection, replacement, templates, and batch embedding |
| `analysis` | 20 | Experiment discovery, LCMS series, lab books, and SciFinder RDF |
| `chemscript` | 20 | Molecule comparison and controlled ChemScript SDK access |
| `codex` | 35 | Complete local and remote tool collection |

The exact generated signatures are in [docs/mcp-tools.md](docs/mcp-tools.md),
with a machine-readable counterpart in
[docs/mcp-schema.json](docs/mcp-schema.json).

### Compatible core tools (15)

### Chemistry resolution
| Tool | Description |
|------|-------------|
| `resolve_name` | Name/abbreviation/CAS/formula to rich molecule JSON (5-tier: reagent DB, condensed formula, ChemScript, OPSIN, PubChem) |
| `modify_molecule` | 6 operations: analyze, name_surgery, smarts, set_smiles, set_name, reaction. 162 named reaction templates. Returns MCS-based structural diffs. |

### Structure rendering
| Tool | Description |
|------|-------------|
| `draw_molecule` | Single molecule to CDXML |
| `render_scheme` | YAML/compact text/reaction JSON to publication-ready CDXML. Forgiving parser handles common LLM YAML mistakes. |

### Perception (reading existing chemistry)
| Tool | Description |
|------|-------------|
| `parse_reaction` | ELN exports (CDXML/CDX/CSV/RXN) to semantic JSON with species, roles, SMILES, equivalents |
| `summarize_reaction` | Context-efficient view of reaction JSON (select only the fields you need) |
| `extract_structures_from_image` | Image to SMILES + confidence scores via DECIMER neural network |
| `parse_scheme` | CDXML scheme to structured species/steps/topology JSON |

### Analysis
| Tool | Description |
|------|-------------|
| `parse_analysis_file` | LCMS (Waters/manual) or NMR (MestReNova) PDF to structured peak data |
| `format_lab_entry` | Structured entry dicts to formatted lab book text. Re-reads LCMS PDFs for exact numbers. |

### Office integration
| Tool | Description |
|------|-------------|
| `extract_cdxml_from_office` | Pull embedded ChemDraw OLE objects from PPTX/DOCX |
| `embed_cdxml_in_office` | Inject CDXML as editable ChemDraw OLE into PPTX/DOCX |
| `convert_cdx_cdxml` | Bidirectional CDX/CDXML conversion |
| `search_compound` | Find a molecule across experiment directories by SMILES similarity |
| `render_to_png` | CDXML to PNG via ChemDraw COM |

## Design principles

**Never trust LLM-generated SMILES.** The agent always goes through `resolve_name` to get grounded SMILES from databases. Direct SMILES generation is the #1 source of chemistry hallucination.

**Verify every transformation.** `modify_molecule` returns aligned IUPAC name diffs and MCS-based molecular diffs after every edit. The agent can confirm the transformation is correct.

**Never flood the agent.** Large outputs (CDXML, JSON) always write to files and return `{ok: true, output_path: "...", size: 23456}`. The agent never gets 30KB of XML in its context window.

**Forgiving inputs.** The YAML parser accepts 9+ common LLM mistakes (inline structures, `substrates` as alias for `structures`, text as string not list, bare SMILES, `above_arrow` as list/string). Input parameters accept bare SMILES strings, stringified JSON arrays, and fuzzy operation names.

**Actionable errors.** Every error tells the agent what to do instead: "Did you mean: BOC_deprotection?", not "KeyError".

**Progressive discovery.** Start with `get_toolkit_capabilities`, then expose a
smaller profile when the complete collection is unnecessary. Exact signatures
come from the live registry and are checked in CI.

## Streamable HTTP

Stdio remains the default. To make an activated Windows workstation available
to another trusted computer, install the `http` extra and provide an API key:

```powershell
$env:CHEMDRAW_MCP_HTTP_API_KEY = "generate-a-long-random-value"
cdxml-mcp --transport streamable-http --host 0.0.0.0 --port 8029 `
  --allowed-host chemdraw-host.example:8029 `
  --allowed-origin https://trusted-client.example
```

Remote binding is refused without an API key and explicit allowed hosts.
`/health` contains no molecule data. `/metrics` records counts, duration,
timeouts, worker failures, and ChemDraw queue length without recording tool
arguments or molecular content.

## CLI tools

All tools are also available as command-line scripts:

| Command | Description |
|---------|-------------|
| `cdxml-mcp` | Complete hardened MCP runtime (35 tools by default) |
| `cdxml-mcp-core` | Compatible 15-tool core server |
| `cdxml-mcp-docs` | Regenerate MCP Markdown and JSON references |
| `cdxml-parse` | Parse reaction files to JSON |
| `cdxml-render` | Render JSON/YAML/compact text to CDXML |
| `cdxml-convert` | CDX/CDXML bidirectional conversion |
| `cdxml-image` | CDXML to PNG/SVG (ChemDraw COM) |
| `cdxml-merge` | Merge multiple reaction schemes |
| `cdxml-layout` | Clean up reaction layout (pure Python) |
| `cdxml-ole` | Embed CDXML as editable OLE in PPTX/DOCX |
| `cdxml-lcms` | Parse LCMS PDF reports |
| `cdxml-nmr` | Extract NMR data from MestReNova PDFs |
| `cdxml-format-entry` | Format lab book entries |
| `cdxml-discover` | Discover experiment files in a directory |
| `cdxml-doctor` | Diagnostics, test runner, and ChemScript setup guide |

## Scheme DSL

The renderer accepts three input formats:

**YAML** (what agents typically write):
```yaml
layout: sequential
structures:
  SM:
    smiles: "Brc1ncnc2sccc12"
  Product:
    smiles: "c1nc(N2CCOCC2)c2ccsc2n1"
steps:
  - substrates: [SM]
    products: [Product]
    above_arrow:
      structures: [Morph]
    below_arrow:
      text: ["Pd2(dba)3", "BINAP", "Cs2CO3", "Dioxane, 105 C"]
```

**Compact text** ("Mermaid for reactions"):
```
SM: {Brc1ncnc2sccc12}
SM --> Product{c1nc(N2CCOCC2)c2ccsc2n1}
  above: Morph{C1COCCN1}
  below: "Pd2(dba)3", "BINAP", "Cs2CO3"
```

**Reaction JSON** (from parse_reaction):
```bash
cdxml-render --from-json reaction.json -o scheme.cdxml
```

## Running tests

```bash
# Using cdxml-doctor (recommended — also prints diagnostics)
cdxml-doctor

# Or directly with pytest
pytest -m "not network" -v

# Build and inspect distribution artifacts
python -m build
python -m twine check dist/*
```

See the [maintenance guide](docs/maintenance.md),
[contribution guide](.github/contributing.md), and
[security policy](.github/SECURITY.md) before proposing or releasing changes.

## License

[MIT](LICENSE)

## Attribution

See [NOTICE.md](NOTICE.md) for third-party data attribution (ChemScanner, RDKit).

## Maintainers and upstream

- Community maintainer: [ZiChenWang114514](https://github.com/ZiChenWang114514)
- Original author: Hiu Fung Kevin Lee ([@leehiufung911](https://github.com/leehiufung911))
- Upstream project: [`leehiufung911/cdxml-toolkit`](https://github.com/leehiufung911/cdxml-toolkit)
