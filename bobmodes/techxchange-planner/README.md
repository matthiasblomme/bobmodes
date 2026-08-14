# TechXchange Planner (`techxchange-planner`)

Plans a personalized **IBM TechXchange** conference agenda end-to-end: scrapes the event data (session catalog via the RainFocus API, agenda/experience and FAQ pages), discovers your interest profile, and builds a slot-budgeted day-by-day schedule with ranked alternates. Re-run it when the session times publish and it diffs the catalog and clash-checks your picks. Works for any IBM event with a `reg.tools.ibm.com` session catalog, not just TechXchange.

## What it does

- **Scrape.** `scripts/fetch_catalog.py` pulls the full catalog and filter attributes through the RainFocus JSON API - no login, just two public widget tokens (TechXchange 2026 defaults baked in, overridable per event/year; discovery steps in `references/rainfocus-api.md`). `parse_faq.py` converts any IBM accordion page (FAQ, experience) to markdown - the collapsed panels are server-rendered, so no browser is needed. `build_catalog_notes.py` generates a browsable catalog note plus per-product focus notes with abstracts and speakers. Test/dummy catalog entries are filtered out.
- **Profile.** `mine_history.py` mines local AI-chat history for product mentions, using the catalog's own filter vocabulary as the term list so it stays current each year. Falls back to asking who you are and what you work with, then to short multiple-choice rounds for what history cannot tell (aspirations vs. current work).
- **Plan.** Clusters the catalog around the profile (product tags primary, topics/text secondary), budgets slots from real session lengths (lab 90 / breakout 45 / talk 20 min), asks only at genuine forks, and writes the personalized agenda: day tables, track tallies, ranked alternates with swap reasons, and a to-do whose first item is the refresh instruction.
- **Refresh.** Re-scrape into the same data dir, diff against the previous run, and - when `times_published` flips true - map picks and alternates to real slots and resolve clashes. The personalized agenda is updated in place (it contains user decisions), never silently regenerated.
- **Status lines.** Long steps report playful but truthful progress ("Sweet-talking the RainFocus API… 400/822 sessions so far"); numbers are always real, and errors drop the humor.

## The champion-schedule file

`assets/champion-schedule.md` ships as a **placeholder**. IBM Champions receive the real file separately (champions-only - it is never published with the skill); drop it over the placeholder or next to your conference notes, and the planner treats its per-day entries as fixed anchors that outrank regular sessions, without asking. While the `PLACEHOLDER` marker is present the file is ignored and champions are simply asked for their commitments instead.

## When to use

"Scrape the TechXchange agenda", "which sessions should I attend", "build my conference schedule", "update my plan - the session times are out", or any IBM event with a `reg.tools.ibm.com` session catalog.

## Dependencies

Python 3 (scripts are stdlib-only, except the FAQ parser which needs `beautifulsoup4`), network access to `ibm.com` / `events.tools.ibm.com` / `reg.tools.ibm.com`. A browser tool is only needed to discover the widget tokens of a new event/year.

## Layout

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

Claude Code skill only - there is no `.bobmodes` mode definition; the workflow leans on scripting and (optionally) browser tooling rather than a Bob persona.
