# RainFocus catalog API — mechanics and quirks

IBM event session catalogs (TechXchange, and typically other reg.tools.ibm.com
events) are RainFocus widget apps. The session data is served by a plain JSON
API that needs **no login** — just two widget tokens sent as headers.

## Endpoints

Base: `https://events.tools.ibm.com/api`

| Endpoint | Method | Purpose |
|---|---|---|
| `/sessions` | POST (form-encoded) | Paged session search. Body: `search=&type=session&size=200&from=0` |
| `/attributes` | POST (empty body) | Filter attribute definitions: activity types, tech tracks, session topics, products, levels, days |

Headers on every call:

```
Content-Type: application/x-www-form-urlencoded
rfApiProfileId: <apiProfileToken>
rfWidgetId: <widgetToken>
```

`scripts/fetch_catalog.py` wraps all of this, with the TechXchange 2026 tokens
as defaults.

## Discovering tokens for a new event/year

1. Open the event's session catalog page in the browser tool
   (e.g. `https://reg.tools.ibm.com/flow/ibm/<event>/sessioncatalog/page/sessioncatalog`).
2. Wait for it to render, then evaluate:
   ```js
   window.store.getState().dynamicPages.widgetConf
   ```
   → `{ widgetToken, apiProfileToken, ... }`. Pass these to the script as
   `--widget` / `--api-profile`.
3. Fallback: check `performance.getEntriesByType('resource')` for calls to
   `events.tools.ibm.com/api/*` and read the request headers via the network
   inspector.

## Quirks (all handled by the script — listed so you recognize symptoms)

- **Page size caps at 50** regardless of the `size` you request.
- **Response shape changes after page one**: the first page wraps results in
  `sectionList[0]`, subsequent pages return `{total, items, ...}` flat.
  Parsing only the first shape looks like a crash on page two.
- **Test pollution**: items titled `TEST Session for EventBase ...` and items
  with attribute `Dummy session = Yes` are real catalog rows. Filter both.
- **`search=` is server-side free text** and matches speaker names too — a
  search for a product ("bob") also returns sessions by people named Bob.
  For product filtering, prefer the `IBM TechXchange Conference Products`
  attribute on each session (`attributevalues[]` with `attribute` ==
  `"IBM TechXchange Conference Products"`).

## Session item fields that matter

- `code` (e.g. TEC-2785), `title`, `type`, `abstract`, `length` (minutes)
- `attributevalues[]`: each `{attribute, value}` — Tech Track, Session Topic,
  Technical Level, Industry, products, `IBM Champion Led`, `Day`, `Day Time`
- `participants[]`: `fullName`, `jobTitle`, `companyName`, `roles`
- `times[]`: the schedule, one entry per scheduled occurrence (normally one):
  - `date` - `2026-10-27`
  - `dayTimeSort` - `20261027t1245`: the sortable START time, minute precision
  - `startTimeFormatted` / `endTimeFormatted` - `12:45 PM` / `02:15 PM`
  - `room` - e.g. `Tech Talk Stage for Bob (Bob)`
  - `dayTimeHour` - `20261027t12`: the HOUR BUCKET the site's filter uses. It is
    not the start time; a 12:45 session carries `dayTimeHour` `...t12`. Never
    read it as a clock time.

**Clock times come from `times[0].dayTimeSort` or `startTimeFormatted`, not from
the attributes.** The `Day` attribute (`Tuesday, Oct 27`) only names the day, and
`Day Time` was empty on the whole 2026 catalog while `times[]` was filled for
1,049 of 1,137 sessions. On 2026-09-28 one run read `dayTimeHour` and produced an
agenda with every start cut to the hour and forks around clashes that did not
exist; another trusted the empty `Day Time` and declared the clock times
unpublished. Both notes looked fine. A pick whose `times[]` is empty is `TBD`,
not a guess.

Observed lengths: Technology Breakout 45, Tech Talk 20, Hands-on Lab 90,
Workshop 180, Certification exam ~60–90. Re-verify per event from the data.

## Detecting whether the schedule is published

Early in the cycle `times[]` is empty on every session and the `Day` / `Day Time`
attributes are absent - the timetable isn't public yet. `fetch_catalog.py`
reports `times_published` (any session with a non-empty `times[]` or a `Day`
attribute), `sessions_with_times` and `sessions_with_clock_times` (non-empty
`times[]`, i.e. minute-precision starts) in its summary, and writes the same
summary with a `scraped_at` timestamp to `<out>/scrape_summary.json`;
`--from-raw <path>` reprints it from an existing scrape without fetching. When
`times_published` flips to true on a re-run, the personalized agenda must be
re-checked for clashes (that's the main reason re-runs exist). Days can publish
before clock times, so `sessions_with_clock_times` is the number to watch.

## Related catalogs

The speaker catalog is a sibling widget:
`.../flow/ibm/<event>/SpeakerCatalog/page/SpeakerCatalog` — same API family,
useful if the user wants to follow specific speakers.

## Event pages (non-catalog)

The marketing pages (`ibm.com/events/techxchange/...`) are server-rendered
AEM. Collapsed accordion content (week-at-a-glance days, FAQ answers) **is
present in the raw HTML** (`cmp-accordion__item` / `__title` / `__panel`), so
`curl` + BeautifulSoup works — no browser needed. `scripts/parse_faq.py`
handles any accordion-based page, not just the FAQ. Caveat: a visible-text
dump of such a page misses the collapsed panels; always extract from the DOM
or raw HTML.
