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

Observed lengths: Technology Breakout 45, Tech Talk 20, Hands-on Lab 90,
Workshop 180, Certification exam ~60–90. Re-verify per event from the data.

## Detecting whether the schedule is published

Early in the cycle, sessions have **no** `Day` / `Day Time` attribute values —
the timetable isn't public yet. `fetch_catalog.py` reports
`times_published` and `sessions_with_times` in its summary. When
`times_published` flips to true on a re-run, the personalized agenda must be
re-checked for clashes (that's the main reason re-runs exist).

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
