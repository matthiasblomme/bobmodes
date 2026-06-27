# Bob modes - per-mode documentation

What each mode does, how to use it, and its layout. For prerequisites and installation, see the [root README](../README.md).

---

## ACE Support Case (`ace-support-case`)

The ACE Support Case mode turns the assistant into a **senior ACE support specialist**. When you hit a problem with IBM App Connect Enterprise and need to open an IBM support case (PMR / ticket), the mode walks you through the entire diagnostic-collection process so that IBM Support gets everything it needs the first time - no back-and-forth, no missing pieces.

### What it does

It follows a structured, phase-by-phase workflow:

1. **Triage** - a conversational set of questions to understand the symptom, timing, scope, and recent changes, then classify the problem (crash/abend, performance, functional, deployment, database/ODBC, SSL/TLS/GSKit, or general).
2. **Runtime access check** - either run the collection commands directly on the server, or generate a ready-to-run script for someone who has access.
3. **Baseline collection** - `mqsiservice -v` plus **aceDataCollector**, the single most complete automated diagnostic tool.
4. **Problem-specific diagnostics** - a decision tree of exactly what to gather for each problem type (event-log windows, user/service trace, ODBC trace, abend/dump files, GSKit library-ordering checks, and more).
5. **Analysis and case generation** - self-assessment of the collected data, an optional `ACELogAnalyser` run, and a ready-to-paste IBM case submission block (title, product, version, severity, business impact, structured description), with the bundle compressed and ready to attach.

The mode is distilled from IBM's ACE 13 "Troubleshooting and support" documentation. The operational detail it actually loads lives in `references/workflow.md` and `references/diagnostics_guide.md`; `references/manifest.csv` lists the relevant IBM doc pages by URL so you can go to the source.

The diagnostic commands it suggests (`mqsiservice`, `aceDataCollector`, `mqsireportproperties`, etc.) must be run from an **ACE Console** on Windows, or after sourcing `mqsiprofile` on Linux/UNIX. The mode only runs the assistant through the workflow and generates the commands / scripts - you run the actual ACE diagnostic commands against your own environment.

### How to use it

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

### Custom rules (optional)

The mode reads `custom-rules/rules.md`. Out of the box it is effectively empty (template comments only) and the mode runs exactly as described above. Add your organisation's own rules to that file - the kind of thing the generic workflow cannot know - and the mode applies them on top of its default steps:

- **House trace / data-collection procedure** - your own scripts, flags, and steps where they differ from the default `aceDataCollector` / trace instructions.
- **Where your logs actually live** - custom work-dir, container/volume paths, or a log aggregator (Splunk / ELK) instead of the local error log.
- **Data handling** - what to redact before anything goes to IBM, and the approved upload channel (portal attachment vs ECuRep, encryption, no production data).
- **Entitlement** - IBM Customer Number (ICN), site ID, support tier, named callers.
- **Internal governance** - required incident/change ticket, internal-to-IBM severity mapping, where the bundle must be stored.

When a custom rule conflicts with a default step, the custom rule wins - the mode follows it and tells you it is doing so.

### Mode layout

```
ace-support-case/
├── .bobmodes                # Bob mode definition (slug: ace-support-case)
├── SKILL.md                 # Claude Code entry point (workflow + rules)
├── ace_support_case.md      # original working notes
├── custom-rules/
│   └── rules.md             # drop organisation-specific rules here (empty by default)
└── references/
    ├── workflow.md          # authoritative phase-by-phase workflow
    ├── diagnostics_guide.md # command / path / tool reference
    └── manifest.csv / .json # links to the relevant IBM doc pages (by URL)
```

---

## Disclaimers

- **Review and validate everything the modes produce.** They use AI assistance and can make mistakes, misread requirements, or miss edge cases. You remain responsible for testing and for compliance with your organisation's standards.
- **Never commit credentials or sensitive data** into mode configurations or collected diagnostics. Scrub diagnostic bundles before sharing.

## License

No license is specified. IBM App Connect Enterprise documentation is referenced by link (see `references/manifest.csv`), not redistributed here, and remains the property of IBM.
