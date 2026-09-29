#!/usr/bin/env python3
"""Check a personalized agenda note against the catalog it was built from.

Two checks over the day tables (the '|' rows under a '## <Weekday>' heading):

1. Times. Every row that names a session in its own code cell and carries a
   clock time in its first cell must start at times[0].dayTimeSort of that
   session in sessions_raw.json. Rows for sessions with an empty times[] must
   say TBD.
2. Overlaps. No two rows of the same day may overlap. A row's span is the
   session's catalog start and end (times[0]) when it names a session, else the
   range written in its first cell ("12:30 PM - 1:00 PM", "8:00-9:45 AM").
   A row with a single time ("6:00 PM | Dinner") is a fixed start: anything
   still running at that minute overlaps it. Remark rows, whose activity cell
   starts with "(" ("5:00 PM | *(MUP-4811 still running)*"), and rows without a
   time ("Evening") are skipped. Rows that only touch (one ends 11:00, the next
   starts 11:00) do not overlap.

Codes mentioned inside prose cells (clash remarks) are ignored; a code cell may
start with an emoji or markdown bold; catalog codes with a stray space
("GEN- 5572") are normalised.

  python scripts/check_agenda_times.py --raw <data-dir>/sessions_raw.json \
      --agenda <notes-dir>/<slug>-my-agenda.md

Prints one line per problem and exits 1 if there is any; exits 0 when every
timed row matches the catalog and nothing overlaps. Run it before handing the
note over: on 2026-09-28 a run that read times[] correctly still placed 2 of 35
timed picks at times that exist nowhere in the catalog, and on 2026-09-29 one
run kept two picks that overlap by five minutes because "speakers usually finish
early", and another kept a lab running until 6:15 PM next to a 6:00 PM dinner
("arrive ~15 min late").
"""
import argparse
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CODE_RE = re.compile(r"\b((?:TEC|LAB|TLK|GEN|MUP|MTE|CRT|DEM)-\s?\d{4})\b")
CLOCK_RE = re.compile(r"(\d{1,2}):(\d\d)\s*(AM|PM)?", re.I)


def norm(code):
    return (code or "").replace(" ", "")


def to_minutes(h, m, ampm):
    h, m = int(h), int(m)
    ampm = (ampm or "").upper()
    if ampm == "PM" and h != 12:
        h += 12
    if ampm == "AM" and h == 12:
        h = 0
    return h * 60 + m


def fmt(minutes):
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def catalog_span(session):
    times = session.get("times") or []
    if not times:
        return None
    m = re.search(r"t(\d\d)(\d\d)$", times[0].get("dayTimeSort", ""))
    if not m:
        return None
    start = int(m.group(1)) * 60 + int(m.group(2))
    e = CLOCK_RE.search(times[0].get("endTimeFormatted", ""))
    end = to_minutes(*e.groups()) if e else start + int(float(session.get("length") or 0))
    return start, end


def cell_start(first_cell):
    # a range like "1:00-1:20 PM" gives its start the end's AM/PM, so read it as a span
    span = cell_span(first_cell)
    if span is not None:
        return span[0]
    m = CLOCK_RE.match(first_cell.strip("* "))
    return to_minutes(*m.groups()) if m else None


def cell_span(first_cell):
    """Parse 'H:MM [AM|PM] <dash> H:MM [AM|PM]'; a missing AM/PM on the start is
    taken from the end, and flipped to AM if that would put the start after the end."""
    clocks = CLOCK_RE.findall(first_cell)
    if len(clocks) < 2:
        return None
    (h1, m1, a1), (h2, m2, a2) = clocks[0], clocks[1]
    end = to_minutes(h2, m2, a2)
    start = to_minutes(h1, m1, a1 or a2)
    if not a1 and start > end:
        start = to_minutes(h1, m1, "AM")
    return start, end


def bare_cell(cell):
    # drop leading whitespace, markdown bold/code marks and emoji, nothing else: a
    # remark like "*(MUP-4811 still running)*" keeps its "(" and never counts as a pick
    return re.sub(r"^[\s*`\u0080-\U0010FFFF]+", "", cell).replace("**", "").replace("`", "").strip()


def is_remark(cell):
    return bare_cell(cell).startswith("(")


def primary_code(cells):
    # a cell that IS a code wins; else a cell that STARTS with one ("**TEC-4200: title",
    # "<emoji> **MUP-4811** ..."); a code inside prose or a remark never counts
    for c in cells:
        m = CODE_RE.fullmatch(bare_cell(c))
        if m:
            return norm(m.group(1))
    for c in cells:
        m = CODE_RE.match(bare_cell(c))
        if m:
            return norm(m.group(1))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True, help="sessions_raw.json the agenda was built from")
    ap.add_argument("--agenda", required=True, help="the personalized agenda note")
    args = ap.parse_args()

    with open(args.raw, encoding="utf-8") as f:
        by_code = {norm(s.get("code")): s for s in json.load(f)}
    with open(args.agenda, encoding="utf-8") as f:
        lines = f.read().splitlines()

    mismatches, overlaps = [], []
    compared, coded_rows, spans_checked = 0, 0, 0
    day, day_spans = None, []

    def close_day():
        nonlocal spans_checked
        spans_checked += len(day_spans)
        for i in range(len(day_spans)):
            for j in range(i + 1, len(day_spans)):
                (s1, e1, l1), (s2, e2, l2) = day_spans[i], day_spans[j]
                if s1 < e2 and s2 < e1:
                    overlaps.append(f"{day}: {fmt(s1)}-{fmt(e1)} {l1} overlaps {fmt(s2)}-{fmt(e2)} {l2}")

    for line in lines:
        if line.startswith("## "):
            close_day()
            m = re.match(r"^## (\w+day)", line)
            day, day_spans = (m.group(1) if m else None), []
            continue
        if day is None or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or set(cells[0]) <= set("-: "):
            continue
        code = primary_code(cells[1:])
        label = code or re.sub(r"[*`]", "", cells[1])[:40].strip()
        span = None
        if code is not None:
            coded_rows += 1
            session = by_code.get(code)
            if session is None:
                mismatches.append(f"{code}: not in the catalog | {line[:90]}")
            else:
                span = catalog_span(session)
                when = cell_start(cells[0])
                if span is None:
                    if when is not None and not re.search(r"\bTBD\b", line):
                        mismatches.append(f"{code}: note says {fmt(when)}, catalog has no time yet (mark TBD) | {line[:90]}")
                elif when is not None:
                    compared += 1
                    if when != span[0]:
                        mismatches.append(f"{code}: note {fmt(when)}, catalog {fmt(span[0])} | {line[:90]}")
        if span is None:
            span = cell_span(cells[0])
        if span is None and not is_remark(cells[1]):
            start = cell_start(cells[0])
            if start is not None:
                span = (start, start + 1)  # a fixed start with no end written
        if span is not None and span[1] > span[0]:
            day_spans.append((span[0], span[1], label))
    close_day()

    print(f"rows with a session code: {coded_rows}; timed rows compared: {compared}; "
          f"mismatches: {len(mismatches)}; rows with a span: {spans_checked}; overlaps: {len(overlaps)}")
    for m in mismatches:
        print(" - time:", m)
    for o in overlaps:
        print(" - overlap:", o)
    sys.exit(1 if mismatches or overlaps else 0)


if __name__ == "__main__":
    main()
