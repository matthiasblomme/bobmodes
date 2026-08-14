# bobmodes

Custom **Bob modes** for IBM App Connect Enterprise (ACE) and prompting work. Every mode also ships as a Claude Code skill (`SKILL.md`), but Bob is the primary target.

A Bob mode is a persona with its own instructions, tools, and triggers. These ones bake in the workflows I would otherwise run from memory and a pile of bookmarked doc pages.

## Modes

- **ACE Support Case** (`ace-support-case`) - walks you through collecting a complete diagnostic bundle for an IBM ACE support case, then writes a ready-to-paste IBM case submission. [Details](bobmodes/README.md).
- **IBM Champion Report** (`ibm-champion-report`) - assembles an IBM Champion act-of-advocacy submission for the Activity Report form: pulls your identity from a private `.env`, drafts the description, and produces a proven prefilled-form URL plus a copy-paste sheet (never auto-submits). [Details](bobmodes/README.md).
- **Prompt Forge** (`prompt-forge`) - turns a rough idea or brain dump into a clean prompt tuned for a specific target model (Fable 5 / Opus 4.8 / Sonnet 5 / Haiku 4.5). Its deliverable is the prompt, not the task's output. [Details](bobmodes/README.md).
- **CVE Analysis** (`cve-analysis`) - practical exploitability assessment of CVEs and IBM security bulletins for ACE and MQ. Answers the question the advisory never does: affected is an inventory fact, but is it actually reachable in *this* environment, and how urgent is the patch? [Details](bobmodes/README.md).
- **TechXchange Planner** (`techxchange-planner`) - scrapes an IBM event's session catalog (RainFocus API), agenda and FAQ pages, profiles your interests from chat history or guided questions, and builds a slot-budgeted personal conference agenda with ranked alternates; re-run it when session times publish and it clash-checks your picks. Claude Code skill only - no Bob mode. [Details](bobmodes/README.md).

You can tailor the ACE Support Case and CVE Analysis modes to your organisation by adding rules to their `custom-rules/rules.md` - see the [per-mode docs](bobmodes/README.md).

**Naming rule:** a mode's folder name, its `SKILL.md` `name:`, its `.bobmodes` `slug:` and the name you invoke it by are all the same string. Claude Code takes the invocable identifier from the folder name under `~/.claude/skills/`, so a folder that disagrees with its frontmatter means typing one name while the docs describe another.

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

Reload your VS Code window (`Ctrl + Shift + P` -> `Reload Window`) and the modes appear in Bob's mode selector, with `/ace-support-case`, `/ibm-champion-report`, `/prompt-forge` and `/cve-analysis` slash commands.

### As a Claude Code skill (optional)

Every mode also ships as a Claude Code skill, discovered from `~/.claude/skills/`.

On Windows, install them all with:

```powershell
.\scripts\Install-Skills.ps1 -WhatIf    # preview, changes nothing
.\scripts\Install-Skills.ps1            # install / refresh
```

It creates a junction per skill, so a `git pull` updates the installed skills with no copying. It skips skills from other sources, backs up (never deletes) anything it replaces, and refuses to install at all if a folder name and its declared `name:` disagree.

If you would rather copy, or you are on macOS / Linux:

```bash
cp -r ./bobmodes/ace-support-case      ~/.claude/skills/ace-support-case
cp -r ./bobmodes/ibm-champion-report   ~/.claude/skills/ibm-champion-report
cp -r ./bobmodes/prompt-forge          ~/.claude/skills/prompt-forge
cp -r ./bobmodes/cve-analysis          ~/.claude/skills/cve-analysis
cp -r ./bobmodes/techxchange-planner   ~/.claude/skills/techxchange-planner
```

The destination folder name must match the mode's `name:` - that is the name you invoke it by.

IBM Champion Report reads your identity from a private `.env` in its folder, and CVE Analysis reads your estate baseline (ACE/MQ versions, install method, HA topology) from one of its own. Copy `.env.sample` to `.env` in the installed skill and fill it in once - the file is gitignored and never leaves your machine. If you installed with `Install-Skills.ps1`, edit it in the repo folder; the junction means it is the same file.

Start a new Claude Code session afterwards so the skill is picked up.

## Per-mode documentation

What each mode does, how to use it, and its layout live in **[bobmodes/README.md](bobmodes/README.md)**.

## Repository layout

```
bobmodes/
├── README.md                 # you are here
├── scripts/
│   ├── Import-BobModes.ps1    # imports modes into a project's .bob/custom_modes.yaml
│   └── Install-Skills.ps1     # installs the modes as Claude Code skills
└── bobmodes/
    ├── README.md             # per-mode documentation
    ├── ace-support-case/     # the mode (.bobmodes + SKILL.md + references + custom-rules)
    ├── ibm-champion-report/  # the mode (.bobmodes + SKILL.md + .env.sample + references)
    ├── prompt-forge/         # the mode (.bobmodes + SKILL.md + references)
    ├── cve-analysis/         # the mode (.bobmodes + SKILL.md + references + custom-rules)
    └── techxchange-planner/  # skill only (SKILL.md + scripts + references + assets)
```

## Support

If these modes save you time, you can support their upkeep via
[GitHub Sponsors](https://github.com/sponsors/matthiasblomme).
