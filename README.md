# bobmodes

Custom **Bob modes** for IBM App Connect Enterprise (ACE) work. Each mode also ships as a Claude Code skill (`SKILL.md`), but Bob is the primary target.

## Modes

- **ACE Support Case** (`ace-support-case`) - walks you through collecting a complete, well-organised diagnostic bundle for an IBM ACE support case, and generates a ready-to-paste IBM case submission.

## Install (quick start)

```powershell
git clone https://github.com/matthiasblomme/bobmodes.git
cd bobmodes
.\scripts\Import-BobModes.ps1 -SourcePath ".\bobmodes" -TargetProjectPath "D:\Projects\YourProject"
```

Reload VS Code and pick **ACE Support Case** from Bob's mode selector.

For full details - what the mode does, prerequisites, usage, and the Claude Code option - see **[bobmodes/README.md](bobmodes/README.md)**.
