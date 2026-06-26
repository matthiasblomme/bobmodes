# bobmodes

Custom **Bob modes** for IBM App Connect Enterprise (ACE) work. Each mode also ships as a Claude Code skill (`SKILL.md`), but Bob is the primary target.

A Bob mode is a persona with its own instructions, tools, and triggers. These ones bake in the ACE workflows I would otherwise run from memory and a pile of bookmarked doc pages.

## Modes

### ACE Support Case (`ace-support-case`)

Turns the assistant into a senior ACE support specialist. When something breaks and you need to open an IBM support case (PMR / ticket), it walks you through gathering a complete diagnostic bundle so IBM Support gets everything the first time, then writes a ready-to-paste case submission.

It works in five phases:

1. **Triage** - pin down the symptom, timing, and scope, then classify the problem.
2. **Runtime access check** - run the commands directly, or hand you a script if you have no shell on the server.
3. **Baseline collection** - `mqsiservice -v` plus `aceDataCollector`.
4. **Problem-specific diagnostics** - the right traces, logs, and dumps for the problem type.
5. **Analysis and case generation** - an organised bundle plus a structured IBM case submission.

It is grounded in the IBM ACE 13 "Troubleshooting and support" documentation, which is bundled into the mode.

## Install (quick start)

```powershell
git clone https://github.com/matthiasblomme/bobmodes.git
cd bobmodes
.\scripts\Import-BobModes.ps1 -SourcePath ".\bobmodes" -TargetProjectPath "D:\Projects\YourProject"
```

Reload VS Code and pick **ACE Support Case** from Bob's mode selector. (It also installs as a Claude Code skill - see the detailed docs.)

## More

Full details - prerequisites, the Claude Code option, usage examples, and mode layout - are in **[bobmodes/README.md](bobmodes/README.md)**.

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
