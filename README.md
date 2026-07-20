# bobmodes

Custom **Bob modes** for IBM App Connect Enterprise (ACE) work. Both modes also ship as a Claude Code skill (`SKILL.md`), but Bob is the primary target.

A Bob mode is a persona with its own instructions, tools, and triggers. These ones bake in the ACE workflows I would otherwise run from memory and a pile of bookmarked doc pages.

## Modes

- **ACE Support Case** (`ace-support-case`) - walks you through collecting a complete diagnostic bundle for an IBM ACE support case, then writes a ready-to-paste IBM case submission. [Details](bobmodes/README.md).
- **IBM Champion Report** (`ibm-champion-report`) - assembles an IBM Champion act-of-advocacy submission for the Activity Report form: pulls your identity from a private `.env`, drafts the description, and produces a proven prefilled-form URL plus a copy-paste sheet (never auto-submits). [Details](bobmodes/README.md).

You can tailor the ACE Support Case mode to your organisation by adding rules to its `custom-rules/rules.md` - see the [per-mode docs](bobmodes/README.md).

## Prerequisites

- **Bob** in VS Code (modes live in `.bob/custom_modes.yaml`). The modes also work as **[Claude Code](https://claude.com/claude-code)** skills if you prefer that (skills are discovered from `~/.claude/skills/`).
- **Windows + PowerShell** to run `Import-BobModes.ps1`. On macOS/Linux, install manually (see below).
- **IBM App Connect Enterprise** on the machine you are diagnosing. The ACE Support Case workflow assumes ACE v11.0.0.8 or later for the bundled `aceDataCollector`; v12 and v13 are fully supported.

## Installation

### Into a Bob (VS Code) project with `Import-BobModes.ps1` (recommended)

`scripts/Import-BobModes.ps1` scans a source path for `.bobmodes` files and merges their mode definitions into a target project's `.bob/custom_modes.yaml`, skipping any whose slug already exists.

```powershell
git clone https://github.com/matthiasblomme/bobmodes.git
cd bobmodes
.\scripts\Import-BobModes.ps1 -SourcePath ".\bobmodes" -TargetProjectPath "D:\Projects\YourProject"
```

To refresh modes you already imported, add `-Replace` - without it, existing slugs are left untouched:

```powershell
.\scripts\Import-BobModes.ps1 -SourcePath ".\bobmodes" -TargetProjectPath "D:\Projects\YourProject" -Replace
```

Reload your VS Code window (`Ctrl + Shift + P` -> `Reload Window`) and both modes appear in Bob's mode selector - **ACE Support Case** and **IBM Champion Report** - with `/ace-support-case` and `/ibm-champion-report` slash commands.

### As a Claude Code skill (optional)

Both modes ship as Claude Code skills. Skills are discovered from `~/.claude/skills/`, so copy the mode folder there:

```powershell
# Windows / PowerShell
Copy-Item -Recurse -Force .\bobmodes\ace-support-case "$HOME\.claude\skills\ace-support-case"
Copy-Item -Recurse -Force .\bobmodes\ibm-champion-report "$HOME\.claude\skills\ibm-champion-report"
```

```bash
# macOS / Linux
cp -r ./bobmodes/ace-support-case ~/.claude/skills/ace-support-case
cp -r ./bobmodes/ibm-champion-report ~/.claude/skills/ibm-champion-report
```

IBM Champion Report reads your identity from a private `.env` in its folder. Copy `.env.sample` to `.env` in the installed skill and fill it in once - the file is gitignored and never leaves your machine.

Start a new Claude Code session afterwards so the skill is picked up.

## Per-mode documentation

What each mode does, how to use it, and its layout live in **[bobmodes/README.md](bobmodes/README.md)**.

## Repository layout

```
bobmodes/
├── README.md                 # you are here
├── scripts/
│   └── Import-BobModes.ps1    # imports modes into a project's .bob/custom_modes.yaml
└── bobmodes/
    ├── README.md             # per-mode documentation
    ├── ace-support-case/     # the mode (.bobmodes + SKILL.md + references + custom-rules)
    └── ibm-champion-report/  # the mode (.bobmodes + SKILL.md + .env.sample + references)
```

## Support

If these modes save you time, you can support their upkeep via
[GitHub Sponsors](https://github.com/sponsors/matthiasblomme).
