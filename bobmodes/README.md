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
├── custom-rules/
│   └── rules.md             # drop organisation-specific rules here (empty by default)
└── references/
    ├── workflow.md          # authoritative phase-by-phase workflow
    ├── diagnostics_guide.md # command / path / tool reference
    └── manifest.csv / .json # links to the relevant IBM doc pages (by URL)
```

---

## IBM Champion Report (`ibm-champion-report`)

The IBM Champion Report mode helps you report an IBM Champion (or Rising Champion) **act of advocacy** on the IBM Champion Program Activity Report form (the Airtable form behind `ibm.biz/champ-report`). It assembles every value, polishes the free-text description to the 250-word limit, and produces a **proven prefilled-form URL** plus a copy-paste field sheet. It never ticks the consent checkbox and never submits - you do the final review, consent, and click.

### What it does

1. **Load identity** - reads your stable identity (Champion Program ID, name, emails) from a private, gitignored `.env` (copy `.env.sample` once).
2. **Gather the activity** - one act at a time: what you did, the Act-of-Advocacy type, the product(s), a link (effectively mandatory), the date, and whether IBM may amplify it.
3. **Write the description** - drafts each "Description of this Activity" for a reviewer who has not seen the work, factual and within 250 words, and reports the word count.
4. **Confirm the dropdowns** - the Act-of-Advocacy (40) and Product(s) (516) option lists are verified verbatim from the live form; the mode picks the exact entry and confirms it with you.
5. **Produce the output** - a prefilled URL that lands 8 fields (identity, Act of Advocacy, Product(s), Date) via verified field-ID / name params, plus a copy-paste sheet for the fields that cannot be prefilled (Description, Link, Amplify, How-many-more, PRIVACY). If a browser MCP is available it can fill the form in place and verify, but never submits.

The authoritative field spec - the field-ID prefill map, date format, word limits, and the full verified option lists - lives in `references/form_fields.md`.

### How to use it

Once installed, describe the activity you want to report. The mode triggers when you:

- want to report or register an IBM Champion activity / act of advocacy,
- ask to "fill in the champ-report form" or mention `ibm.biz/champ-report`,
- want to log a blog, talk, video, idea, or code contribution for a Champion badge.

Example prompts:

```
Report my IBM Champion activity: I published a blog on community.ibm.com about MCP in ACE.

Log this idea I submitted on the IBM Ideas portal as an act of advocacy: https://ideas.ibm.com/ideas/APPC-I-1249

Fill in the champ-report form for a conference talk I gave last month.
```

The mode pulls your identity from `.env`, gathers the activity, drafts the description, and hands back the prefilled URL plus the copy-paste sheet.

### One-time setup (`.env`)

Copy `.env.sample` to `.env` in the mode folder and fill in your real values once:

```
CHAMPION_PROGRAM_ID=...
FIRST_NAME=...
LAST_NAME=...
PRIMARY_EMAIL=...
ALTERNATE_EMAIL=...
```

`.env` is gitignored and stays private; only `.env.sample` (placeholders) is committed.

### Mode layout

```
ibm-champion-report/
├── .bobmodes                # Bob mode definition (slug: ibm-champion-report)
├── SKILL.md                 # Claude Code entry point (workflow + rules)
├── .env.sample              # copy to .env and fill once (.env itself is gitignored)
└── references/
    └── form_fields.md       # verified field spec + prefill map + full option lists
```

---

## Prompt Forge (`prompt-forge`)

Prompt Forge turns a rough idea or brain dump into a clean, model-tuned prompt you can paste into a fresh Claude session. Its deliverable is **the prompt, not the task's output** - if you want the work done, just ask for the work.

### What it does

It runs a five-stage spine - capture, clarify, structure, tune, iterate - that pins down the five things a model cannot guess: goal, context, inputs, output shape, and success criteria. Clarification is gated and batched, so it asks one short round of questions that would actually change the prompt rather than interrogating you.

The tuning stage is the differentiator. The same task spec becomes a different prompt depending on which model will run it, because **capability and steering trade off**: a capable model wants the outcome specified and latitude on the how, while a smaller one wants the steps, the format, and the examples spelled out. Getting that backwards is the most common prompting mistake - step-by-step babysitting makes a frontier model worse, and a trust-the-model one-liner makes a small one flail. One parameterised stage covers the whole roster rather than a separate mode per model.

Optional passes run only when the material calls for them: a voice pass (baking a concrete "write in this voice" instruction into the prompt), an anti-AI de-slop pass, a next-chat handoff document, and bottling a prompt you reuse into a skill.

### How to use it

Describe what you want a prompt for, in whatever shape it is currently in. The mode triggers when you:

- ask for a prompt ("write me a prompt for X", "turn this into a prompt"),
- want an existing prompt cleaned up or tuned for a specific model,
- ask to be questioned until the prompt is clear, or
- paste a messy task description and want it shaped rather than executed.

Example prompts:

```
Write me a prompt that reviews our release notes for missing breaking-change callouts.

I have a half-formed idea for a prompt - ask me questions until it's clear.

Clean this prompt up and tune it for Haiku.
```

It asks which model the prompt is for. If you do not know, say so and it picks a sensible default and tells you what it assumed.

### Mode layout

```
prompt-forge/
├── .bobmodes                    # Bob mode definition (slug: prompt-forge)
├── SKILL.md                     # Claude Code entry point (the five-stage spine)
└── references/
    ├── model_tuning.md          # per-model steering profiles, roster, prompt anatomy
    └── clarify_and_polish.md    # clarify question bank, task-spec template, voice + de-slop passes
```

---

## CVE Analysis (`cve-analysis`)

The CVE Analysis mode turns the assistant into a **senior IBM middleware security architect** for IBM App Connect Enterprise and IBM MQ, plus everything they bundle (IBM Semeru/Java, XML stacks, Jakarta Mail, embedded Node.js, Liberty in mqweb, GSKit).

The point is not to summarise the advisory. IBM marks a product affected whenever it bundles a vulnerable component, which is an inventory statement rather than a risk statement. This mode answers the question the bulletin never does: is the vulnerable code path actually reachable in *this* environment, and what does that mean for patch urgency?

### What it does

1. **Intake and scope** - checks its decision log first, so a CVE assessed three months ago is answered from the record instead of researched again. Reads an estate baseline from `.env` so it does not re-ask your versions and topology every time.
2. **Source research** - the IBM bulletin for affected versions and fix levels, the upstream advisory (Apache, Eclipse, OpenSSL, GHSA, Oracle CPU) for the technical detail IBM omits, NVD/MITRE for CWE and vector. A bulletin bundling five CVEs is treated as five assessments sharing one fix level, never as one assessment with five ids.
3. **Component usage mapping** - locates the vulnerable component *inside* the products using `references/component-map.md`, a curated map with `[confirmed]`/`[verify]` flags and a "False trails" section for claims that sound right and are not (XMLNSC is ACE's native C++ parser, so Java XML CVEs do not travel through it).
4. **Exposure and exploitability** - places the CVE in one of three classes (direct runtime exposure, indirect/conditional, runtime inheritance) and defends the placement. ACE and MQ are assessed separately; they share almost no architecture.
5. **Estate check (optional)** - greps your actual ACE projects for the vulnerable node type, library, or listener, turning "conditionally exposed" into a hard yes or no.
6. **Report** - a deep-dive per CVE or a triage table for a bulletin sweep, closed with a fixed-order in-chat digest (what it is, applicable, action, notes, related).

Conceptual and defensive throughout: it never produces exploit instructions, payloads, or proof-of-concept code.

### How to use it

Describe the CVE or paste the bulletin. It triggers when you:

- ask "are we affected by CVE-XXXX-NNNNN?",
- paste a CVE id or IBM security bulletin text in an ACE/MQ context,
- want a monthly PSIRT sweep triaged,
- ask whether something is exploitable in your setup or how urgently it needs patching.

Example prompts:

```
Are we affected by CVE-2025-12345? We run ACE 13.0.7.1 on-prem and MQ 9.4.0.21 on the same box.

Triage this month's IBM ACE bulletins for me.

Is this Liberty CVE exploitable if we never enabled mqweb?
```

For collecting diagnostics or opening an IBM case, use `ace-support-case` instead.

### The decision log

The mode keeps a persistent log of every assessment: the verdict, the reasoning, and above all which fixes were **deliberately not applied** and why. Each entry carries a mandatory "revisit when" trigger, the concrete condition that invalidates the decision ("if Designer flows are ever deployed", "when we expose mqweb", "next LTS upgrade").

That log is what makes next quarter's triage cheap. A CVE that resurfaces in the next scanner report is answered from the record rather than researched from scratch, and the same digest comes out whether the assessments ran in one session or across months.

Set a durable location in `custom-rules/rules.md` - a notes vault or wiki checkout that outlives the skill folder. Without one it falls back to `log/cve-decisions.md` inside the mode folder, which is gitignored and does not survive a re-clone.

### One-time setup (`.env`)

Copy `.env.sample` to `.env` and fill in your estate: exact ACE and MQ fix-pack levels, install method (on-prem vs Certified Containers, node-managed vs standalone), co-location, HA topology, and exposure-relevant notes. Many bulletins resolve on form factor alone, so this is what keeps intake short.

The file is gitignored and never leaves your machine. Keep it current: stale versions here mean wrong verdicts, and the mode writes newly confirmed facts back to it as it learns them.

### Custom rules (optional)

`custom-rules/rules.md` ships empty. Add your organisation's policy and the mode applies it on top of its built-in workflow; a custom rule that conflicts with a default step wins. Useful things to put there: patch-urgency thresholds and who signs off, which endpoints sit behind a WAF or gateway, which scanner produces the findings you triage, reporting requirements your security team expects, and the decision-log location.

Facts about the estate go in `.env`; policy about the estate goes here.

### Mode layout

```
cve-analysis/
├── .bobmodes                    # Bob mode definition (slug: cve-analysis)
├── SKILL.md                     # Claude Code entry point (six-phase workflow)
├── .env.sample                  # estate baseline template; copy to .env
├── custom-rules/
│   └── rules.md                 # your organisation's policy (empty by default)
└── references/
    ├── report-template.md       # deep-dive, triage table, and log-entry structures
    └── component-map.md         # where bundled components live inside ACE and MQ
```

If a documentation or knowledge-base MCP is available, the mode uses it to ground component-usage claims in the product documentation and to recall prior assessments. Without one it falls back to web research and the bundled component map.

---

## TechXchange Planner (`techxchange-planner`)

The TechXchange Planner builds a **personalized IBM conference agenda** end-to-end: it scrapes the event data (session catalog through the RainFocus API, agenda/experience and FAQ pages), discovers your interest profile, and produces a slot-budgeted day-by-day schedule with ranked alternates. It is re-runnable by design: when the session timetable publishes, a refresh run diffs the catalog and clash-checks your picks against the real times. It works for any IBM event with a `reg.tools.ibm.com` session catalog, not just TechXchange.

Claude Code skill only - there is no `.bobmodes` mode definition; the workflow leans on scripting and (optionally) browser tooling rather than a Bob persona.

### What it does

1. **Scrape** - bundled Python scripts pull the full session catalog and filter attributes through the RainFocus JSON API (no login; public widget tokens with TechXchange 2026 defaults, overridable per event/year - discovery steps in `references/rainfocus-api.md`), convert the FAQ and other accordion pages to markdown, and generate a browsable catalog note plus per-product focus notes with abstracts and speakers. Test/dummy catalog entries are filtered out.
2. **Profile** - mines local AI-chat history for product mentions using the catalog's own filter vocabulary as the term list (so it stays current each year), falls back to asking who you are and what you work with, then to short multiple-choice rounds for genuine forks.
3. **Plan** - clusters the catalog around the profile, budgets slots from real session lengths (lab 90 / breakout 45 / tech talk 20 min), and writes the personalized agenda: day tables, track tallies, ranked alternates with swap reasons, and a to-do whose first item is the refresh instruction.

Long steps report playful but truthful status lines ("Sweet-talking the RainFocus API… 400/822 sessions so far") - the numbers are always real, and errors drop the humor.

### How to use it

Once installed, describe your conference-planning need. The skill triggers when you:

- want the TechXchange (or another IBM event) agenda or session catalog scraped,
- ask "which sessions should I attend?" or want a personal conference schedule,
- want your existing plan re-checked because session times were published.

Example prompts:

```
Scrape the TechXchange agenda and session catalog for me.

I'm going to TechXchange - I work with ACE and MQ daily. Build me a personalized agenda.

The session times are out. Update my TechXchange plan and check for clashes.
```

### The champion-schedule file

`assets/champion-schedule.md` ships as a **placeholder**. IBM Champions receive the real schedule file separately (champions-only - it is never published with the skill); drop it over the placeholder or next to your conference notes and the planner treats its per-day entries as fixed anchors that outrank regular sessions, without asking. While the `PLACEHOLDER` marker is present the file is ignored and champions are simply asked for their commitments instead.

### Mode layout

```
techxchange-planner/
├── SKILL.md                     # Claude Code entry point (scrape → profile → plan, refresh mode)
├── scripts/
│   ├── fetch_catalog.py          # RainFocus API: full catalog + attributes → JSON
│   ├── parse_faq.py              # any IBM accordion page → markdown note
│   ├── build_catalog_notes.py    # catalog note + per-product focus notes
│   └── mine_history.py           # chat-history interest mining (catalog vocabulary)
├── references/
│   ├── rainfocus-api.md          # API endpoints, token discovery, pagination quirks
│   └── note-templates.md         # output note structures + slot-budget rules
└── assets/
    └── champion-schedule.md      # placeholder; champions get the real file separately
```

Requires Python 3 (stdlib-only scripts, except the FAQ parser which needs `beautifulsoup4`) and network access to `ibm.com` / `events.tools.ibm.com` / `reg.tools.ibm.com`.

---

## Disclaimers

- **Review and validate everything the modes produce.** They use AI assistance and can make mistakes, misread requirements, or miss edge cases. You remain responsible for testing and for compliance with your organisation's standards.
- **Never commit credentials or sensitive data** into mode configurations or collected diagnostics. Scrub diagnostic bundles before sharing.

## License

No license is specified. IBM App Connect Enterprise documentation is referenced by link (see `references/manifest.csv`), not redistributed here, and remains the property of IBM.
