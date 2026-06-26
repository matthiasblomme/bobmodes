# bobmodes

Custom **Bob modes** for IBM App Connect Enterprise (ACE) work. Each mode also ships as a Claude Code skill (`SKILL.md`), but Bob is the primary target.

A Bob mode is a persona with its own instructions, tools, and triggers. These ones bake in the ACE workflows I would otherwise run from memory and a pile of bookmarked doc pages.

## Modes

- **ACE Support Case** (`ace-support-case`) - walks you through collecting a complete diagnostic bundle for an IBM ACE support case, then writes a ready-to-paste IBM case submission.

## Install (quick start)

```powershell
git clone https://github.com/matthiasblomme/bobmodes.git
cd bobmodes
.\scripts\Import-BobModes.ps1 -SourcePath ".\bobmodes" -TargetProjectPath "D:\Projects\YourProject"
```

Reload VS Code and pick **ACE Support Case** from Bob's mode selector. (It also installs as a Claude Code skill - see the detailed docs.)

## More

Full per-mode details - what it does, prerequisites, the Claude Code option, usage examples, and mode layout - are in **[bobmodes/README.md](bobmodes/README.md)**.

## Repository layout

```
bobmodes/
├── README.md                 # you are here
├── scripts/
│   └── Import-BobModes.ps1    # imports modes into a project's .bob/custom_modes.yaml
└── bobmodes/
    ├── README.md             # detailed documentation
    └── ace-support-case/     # the mode (.bobmodes + SKILL.md + references)
```
