---
name: techxchange-planner
description: >
  Plan a personalized IBM TechXchange (or any RainFocus-based IBM event)
  conference agenda end-to-end: scrape the session catalog via the RainFocus
  API, scrape the event agenda/experiences/FAQ pages, discover the user's
  interest profile (from local AI-chat history, their self-description, or
  guided questions), and build a slot-budgeted personal schedule with
  alternates. Use this whenever the user mentions TechXchange, planning or
  updating an IBM conference agenda, scraping an IBM event session catalog,
  "which sessions should I attend", re-checking a conference plan because
  session times were published, or building a colleague's conference schedule
  — even if they only say "scrape the agenda", "update my TechXchange plan",
  or name another IBM event with a reg.tools.ibm.com catalog.
---

# TechXchange Planner

Build (or refresh) a personalized conference agenda for an IBM event in three
phases: **scrape** the event data, **profile** the user's interests, **plan**
the agenda. Each phase produces markdown notes so the work survives the
session and the next run can diff instead of redo.

First decision — is this a first run or a refresh? Look for existing output
notes and a `sessions_raw.json` from a previous run (ask where they live if
not obvious). A refresh reuses the stored profile and decisions; jump to
[Refresh runs](#refresh-runs).

## Status feedback — make waiting fun

Scraping, history mining, and agenda building all take noticeable time. The
user should never stare at silence: before each long step, emit a short
status line — playful in tone, but carrying **real** information (numbers,
filenames, counts). One line per step, not a running commentary. The fun is
in the phrasing, never in the facts: never invent progress, and when
something fails, drop the humor entirely and report plainly.

Examples of the register to aim for:

- "🎪 Sweet-talking the RainFocus API… it's coughing up 50 sessions per page, 400/822 so far."
- "🕵️ Rifling through 1,240 chat transcripts for IBM fingerprints — MQ mentioned in 37 files and counting."
- "🧩 810 sessions, one of you. Cross-referencing interests against product tags…"
- "📋 The FAQ page surrendered 51 answers without a fight."
- After failure, plain: "The catalog API returned 403 — the widget tokens have likely rotated. Re-discovering them via the browser."

## Phase 1 — Scrape the event data

All scripts live in this skill's `scripts/` directory; API details and quirks
in [references/rainfocus-api.md](references/rainfocus-api.md) — read it before
debugging any scrape problem, the quirks are non-obvious.

1. **Session catalog + attributes** (needs Python 3, stdlib only):
   ```
   python scripts/fetch_catalog.py --out <data-dir>
   ```
   Defaults target TechXchange 2026. For another event/year, discover the two
   widget tokens via the browser (steps in the reference) and pass
   `--api-profile` / `--widget`. The summary it prints tells you the real
   session count, type distribution, and — critically — `times_published`.
2. **Event pages** (agenda/experience + FAQ). The FAQ:
   ```
   python scripts/parse_faq.py --url <faq-url> --out <notes-dir>/<slug>-faq.md
   ```
   (needs `beautifulsoup4`). For the experience/agenda page, extract via the
   browser DOM or curl the HTML — collapsed accordions are server-rendered,
   and a visible-text dump misses them. Write the agenda note per
   [references/note-templates.md](references/note-templates.md).
3. **Catalog notes**:
   ```
   python scripts/build_catalog_notes.py --raw <data-dir>/sessions_raw.json \
     --out-dir <notes-dir> [--product "IBM Bob"] [--product "<user's main product>"]
   ```

Keep `sessions_raw.json` and `attributes.json` next to the notes — they are
the diff baseline for refresh runs.

Output location: if the current repo is a notes vault (look for conventions
in its CLAUDE.md), follow its structure and frontmatter rules and cross-link
notes with wikilinks. Otherwise ask once where output should go, or default
to a `techxchange/` folder in the working directory.

## Phase 2 — Discover the interest profile

Goal: enough signal to cluster the catalog around the user. Work down this
cascade, stopping as soon as the profile is solid; report which sources fed
it, because the user should know what their agenda is based on.

1. **Local AI-chat history.** Use the catalog's own vocabulary so the terms
   are always current:
   ```
   python scripts/mine_history.py --attributes <data-dir>/attributes.json \
     --paths <history dirs>
   ```
   Known sources: Claude Code transcripts (`~/.claude/projects`, the default).
   For other assistants (IBM Bob, ChatGPT, …) do not guess storage paths —
   ask the user whether they have local history or an export to point at,
   and pass those directories via `--paths`. Treat `low_confidence` terms
   (product names that are everyday words) with skepticism; a term in 30
   files is a signal, a term in 2 files is noise.
2. **The user's own words.** If history is thin or unavailable, ask them
   directly: who are they professionally, which products do they work with,
   what do they want out of the conference (learning, certification,
   networking, advocacy)? One open question, not a form.
3. **Guided choices.** If it's still fuzzy — or to resolve what history
   can't tell you (aspirations vs. current work) — use structured
   multiple-choice questions (AskUserQuestion): pick focus clusters from
   the event's tech tracks, choose certification targets, set depth per
   cluster. Offer a recommended option first, with the reason in the
   description.

**Champions:** ask whether the user is an IBM Champion (or infer from
history/context and confirm). If yes, look for a champion-schedule file
before asking anything: check `assets/champion-schedule.md` in this skill's
directory, then the output/notes directory for the same filename. That file
is distributed separately, to Champions only. If it exists **and no longer
contains its `PLACEHOLDER` marker**, read it and use its entries as fixed
anchors that outrank regular sessions — do not ask the user to repeat what
the file already says. If the file is absent or still the placeholder, ask
them to list their champion commitments (arrival events, programming blocks,
dinners, feedback sessions) instead. Champion schedule details live in
champions-only communications; never invent or assume them.

## Phase 3 — Build the agenda

Follow the personalized-agenda template in
[references/note-templates.md](references/note-templates.md). The method:

1. **Cluster** the catalog around the profile using product tags (primary)
   and topics/text (secondary). Report cluster sizes — the user should see
   the shape of the overflow.
2. **Budget slots** from the event's week structure and real session lengths
   (from the data, not assumption). A hands-on lab costs two breakout slots;
   general sessions, lunch, and expo time are not free.
3. **Ask at genuine forks only.** When a cluster has more strong candidates
   than slots, when certification attempts are limited, or when two clusters
   compete for the same day — present the choice with a recommendation.
   Everything else: decide, and show the reasoning in the note.
4. **Write the personalized agenda note**: day tables, track tallies,
   ranked alternates (with the swap reason), and a to-do list whose first
   item is the refresh instruction for when the schedule publishes.

If `times_published` was false, say so prominently — the plan is provisional
by construction, and pretending otherwise erodes trust in the whole note.

## Refresh runs

Re-run Phase 1 into the same data dir, then diff against the previous
`sessions_raw.json` (details in the templates reference):

- Report added/removed/changed sessions; flag any that were picks.
- If `times_published` flipped true: map picks + alternates to real slots,
  detect clashes, resolve from the alternates list, rewrite the day tables
  with actual times. This is the moment the alternates list earns its keep.
- Update the personalized agenda **in place** — it contains user decisions;
  list what changed and re-ask only forks the new data actually reopened.

## Dependencies

- Python 3 (scripts are stdlib-only, except `parse_faq.py` → `beautifulsoup4`)
- Browser tool: only needed to discover widget tokens for a new event/year
  or to extract the experience page DOM; the API itself needs no browser
- Network access to `events.tools.ibm.com`, `ibm.com`, `reg.tools.ibm.com`
