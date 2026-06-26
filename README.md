# bobmodes

Custom **Bob modes** for IBM App Connect Enterprise (ACE) work. Each mode also ships as a Claude Code skill (`SKILL.md`) for anyone who wants it, but Bob is the primary target.

This repository currently ships one mode:

- **ACE Support Case** (`ace-support-case`) - guides you through collecting a complete, well-organised diagnostic bundle for an IBM App Connect Enterprise support case.

---

## What the ACE Support Case mode is

The ACE Support Case mode turns the assistant into a **senior ACE support specialist**. When you hit a problem with IBM App Connect Enterprise and need to open an IBM support case (PMR / ticket), the mode walks you through the entire diagnostic-collection process so that IBM Support gets everything it needs the first time - no back-and-forth, no missing pieces.

It follows a structured, phase-by-phase workflow:

1. **Triage** - a conversational set of questions to understand the symptom, timing, scope, and recent changes, then classify the problem (crash/abend, performance, functional, deployment, database/ODBC, SSL/TLS/GSKit, or general).
2. **Runtime access check** - either run the collection commands directly on the server, or generate a ready-to-run script for someone who has access.
3. **Baseline collection** - `mqsiservice -v` plus **aceDataCollector**, the single most complete automated diagnostic tool.
4. **Problem-specific diagnostics** - a decision tree of exactly what to gather for each problem type (event-log windows, user/service trace, ODBC trace, abend/dump files, GSKit library-ordering checks, and more).
5. **Analysis and case generation** - self-assessment of the collected data, an optional `ACELogAnalyser` run, and a ready-to-paste IBM case submission block (title, product, version, severity, business impact, structured description), with the bundle compressed and ready to attach.

The mode is grounded in the full IBM ACE 13 "Troubleshooting and support" documentation set, included under `bobmodes/ace-support-case/references/documentation/` as per-topic PDFs.

---

## Prerequisites

- **Bob** in VS Code (modes live in `.bob/custom_modes.yaml`). The mode also works as a **[Claude Code](https://claude.com/claude-code)** skill if you prefer that (skills are discovered from `~/.claude/skills/`).
- **Windows + PowerShell** to run `Import-BobModes.ps1`. On macOS/Linux, install manually (see below).
- **IBM App Connect Enterprise** on the machine you are diagnosing. The workflow assumes ACE v11.0.0.8 or later for the bundled `aceDataCollector`; v12 and v13 are fully supported.
- The diagnostic commands the mode suggests (`mqsiservice`, `aceDataCollector`, `mqsireportproperties`, etc.) must be run from an **ACE Console** on Windows, or after sourcing `mqsiprofile` on Linux/UNIX.

> The mode only runs the assistant through the workflow and generates the commands / scripts. You run the actual ACE diagnostic commands against your own environment.

---

## Installation

### Into a Bob (VS Code) project with `Import-BobModes.ps1` (recommended)

The included `scripts/Import-BobModes.ps1` is the Bob-mode importer: it scans a source path for `.bobmodes` files and merges their mode definitions into a target project's `.bob/custom_modes.yaml`, avoiding duplicates.

```powershell
git clone https://github.com/matthiasblomme/bobmodes.git
cd bobmodes
.\scripts\Import-BobModes.ps1 -SourcePath ".\bobmodes" -TargetProjectPath "D:\Projects\YourProject"
```

The script will:

- detect every `.bobmodes` file under the source path,
- create or update `.bob/custom_modes.yaml` in the target project,
- merge modes intelligently, skipping any whose slug already exists.

After importing, reload your VS Code window (`Ctrl + Shift + P` -> `Reload Window`) to activate the mode. It appears as **ACE Support Case** in Bob's mode selector.

### As a Claude Code skill (optional)

The same mode also ships as a Claude Code skill (`SKILL.md`). Skills are discovered from `~/.claude/skills/`, so copy the folder there:

```powershell
# Windows / PowerShell
Copy-Item -Recurse -Force .\bobmodes\ace-support-case "$HOME\.claude\skills\ace-support-case"
```

```bash
# macOS / Linux
cp -r ./bobmodes/ace-support-case ~/.claude/skills/ace-support-case
```

Start a new Claude Code session afterwards so the skill is picked up.

---

## How to use the ACE Support Case mode

Once installed, just describe your ACE problem in natural language. The mode triggers when you:

- want to open an IBM support case / PMR / ticket for ACE,
- need to gather diagnostics for IBM,
- reference error codes such as `BIP2111` or `BIP2060`,
- mention an ACE crash or abend files, or
- ask what logs or information IBM needs.

Example prompts:

```
My ACE integration node crashed last night with a BIP2111 - what do I need to collect for an IBM support case?

ACE message throughput dropped off a cliff this morning. Help me gather diagnostics for IBM.

I need to open a PMR for a deployment failure on my standalone integration server.
```

The mode then runs the triage questions, tells you exactly which commands to run (or generates a script if you do not have server access), helps you assemble the bundle into an `ACE_SupportCase_<NodeName>_<YYYYMMDD>/` folder, and produces a ready-to-paste IBM case submission.

---

## Repository layout

```
bobmodes/
├── README.md
├── scripts/
│   └── Import-BobModes.ps1          # imports .bobmodes into a project's .bob/custom_modes.yaml
└── bobmodes/
    └── ace-support-case/
        ├── .bobmodes                # Bob mode definition (slug: ace-support-case)
        ├── SKILL.md                 # mode entry point (workflow + rules)
        ├── ace_support_case.md      # original working notes
        └── references/
            ├── workflow.md          # authoritative phase-by-phase workflow
            ├── diagnostics_guide.md # command / path / tool reference
            ├── manifest.csv / .json # index of the bundled IBM docs
            └── documentation/       # IBM ACE 13 troubleshooting docs (PDF)
```

---

## Disclaimers

- **Review and validate everything the mode produces.** It uses AI assistance and can make mistakes, misread requirements, or miss edge cases. You remain responsible for testing and for compliance with your organisation's standards.
- **Never commit credentials or sensitive data** into mode configurations or collected diagnostics. Scrub diagnostic bundles before sharing.

## License

No license is specified. The bundled PDFs under `bobmodes/ace-support-case/references/documentation/` are IBM App Connect Enterprise product documentation and remain the property of IBM.
