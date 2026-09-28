#!/usr/bin/env python3
"""Check a personalized agenda note against the catalog it was built from.

For every day-table row (a '|' row under a '## <Weekday>' heading) that names a
session in its own code cell and carries a clock time in its first cell, compare
that time with times[0].dayTimeSort of the session in sessions_raw.json. Rows for
sessions with an empty times[] must say TBD. Codes mentioned inside prose cells
(clash remarks) are ignored; catalog codes with a stray space ("GEN- 5572") are
normalised.

  python scripts/check_agenda_times.py --raw <data-dir>/sessions_raw.json \
      --agenda <notes-dir>/<slug>-my-agenda.md

Prints one line per mismatch and exits 1 if there is any; exits 0 when every
timed row matches. Run it before handing the note over: on 2026-09-28 a run
that read times[] correctly still placed 2 of 35 timed picks at times that
exist nowhere in the catalog.
"""
import argparse
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CODE_RE = re.compile(r"\b((?:TEC|LAB|TLK|GEN|MUP|MTE|CRT|DEM)-\s?\d{4})\b")


def norm(code):
    return (code or "").replace(" ", "")


def real_start(session):
    times = session.get("times") or []
    if not times:
        return None
    m = re.search(r"t(\d\d)(\d\d)$", times[0].get("dayTimeSort", ""))
    return f"{m.group(1)}:{m.group(2)}" if m else None


def row_time(first_cell):
    m = re.match(r"\s*\**(\d{1,2}):(\d\d)\s*(AM|PM)?", first_cell)
    if not m:
        return None
    h, mi, ap = int(m.group(1)), m.group(2), m.group(3)
    if ap == "PM" and h != 12:
        h += 12
    if ap == "AM" and h == 12:
        h = 0
    return f"{h:02d}:{mi}"


def primary_code(cells):
    # a cell that IS a code (allowing ** and backticks) wins; else a cell that starts
    # with one ("**TEC-4200: title"); a code inside prose never counts
    for c in cells:
        m = CODE_RE.fullmatch(c.strip("*` "))
        if m:
            return norm(m.group(1))
    for c in cells:
        m = CODE_RE.match(c.strip("*` "))
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

    mismatches, compared, rows = [], 0, 0
    in_day = False
    for line in lines:
        if line.startswith("## "):
            in_day = bool(re.match(r"^## \w+day", line))
            continue
        if not in_day or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or set(cells[0]) <= set("-: "):
            continue
        code = primary_code(cells[1:])
        if code is None:
            continue
        rows += 1
        when = row_time(cells[0])
        session = by_code.get(code)
        if session is None:
            mismatches.append(f"{code}: not in the catalog | {line[:90]}")
            continue
        start = real_start(session)
        if start is None:
            if when and not re.search(r"\bTBD\b", line):
                mismatches.append(f"{code}: note says {when}, catalog has no time yet (mark TBD) | {line[:90]}")
            continue
        if when is None:
            continue
        compared += 1
        if when != start:
            mismatches.append(f"{code}: note {when}, catalog {start} | {line[:90]}")

    print(f"rows with a session code: {rows}; timed rows compared: {compared}; mismatches: {len(mismatches)}")
    for m in mismatches:
        print(" -", m)
    sys.exit(1 if mismatches else 0)


if __name__ == "__main__":
    main()
