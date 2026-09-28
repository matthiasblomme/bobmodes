#!/usr/bin/env python3
"""Fetch the full session catalog + filter attributes of a RainFocus-based
IBM event (TechXchange, Think, ...) and save them as JSON.

Defaults target IBM TechXchange 2026. For another event/year, discover the
tokens as described in references/rainfocus-api.md and pass them as args.

Output files in --out:
  sessions_raw.json    - every catalog item, unfiltered (test sessions included)
  attributes.json      - filter attribute definitions (products, tracks, topics...)
  scrape_summary.json  - the summary printed below plus scraped_at, so the next
                         run can decide "re-scrape or reuse?" without re-parsing
                         13 MB of sessions

Prints a JSON summary to stdout, including whether session days/times are
published yet - the signal that a re-run should do clash checking. Clock times
live in each item's times[] array (dayTimeSort / startTimeFormatted), NOT in the
Day Time attribute, which can stay empty after times[] is filled;
sessions_with_clock_times counts the sessions that carry one.

  --from-raw PATH   recompute and print the summary from an existing
                    sessions_raw.json without fetching anything (scraped_at is
                    then that file's modification time)
"""
import argparse
import collections
import datetime
import json
import os
import sys
import urllib.parse
import urllib.request

# cp1252 consoles choke on session titles; reconfigure in place (a TextIOWrapper
# rebind closes the shared buffer on exit)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_BASE = "https://events.tools.ibm.com/api"
# IBM TechXchange 2026 (event techxchange26) - public widget tokens, no login needed
DEFAULT_API_PROFILE = "HkAL70o02Smvj2jmwmYgs7v3n6fMYzK1"
DEFAULT_WIDGET = "ChglfSDiz1jlTR8V97Qf6kYzs773nQuF"


def post(base, headers, path, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(f"{base}/{path}", data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def attr_vals(s, name):
    return [v["value"] for v in s.get("attributevalues", []) if v.get("attribute") == name]


def is_test(s):
    return s.get("title", "").startswith("TEST Session") or "Yes" in attr_vals(s, "Dummy session")


def summarize(items, scraped_at):
    real = [s for s in items if not is_test(s)]
    types = collections.Counter(s.get("type", "?") for s in real)
    products = collections.Counter(p for s in real for p in attr_vals(s, "IBM TechXchange Conference Products"))
    # Clock times live in times[] (dayTimeSort = yyyymmddtHHMM, startTimeFormatted).
    # The Day attribute only names the day; Day Time stayed empty on the whole 2026
    # catalog while times[] was filled. dayTimeHour is the hour bucket, never a start.
    clocked = [s for s in real if s.get("times")]
    timed = [s for s in real if s.get("times") or attr_vals(s, "Day") or attr_vals(s, "Day Time")]
    return {
        "scraped_at": scraped_at,
        "total_fetched": len(items),
        "test_or_dummy": len(items) - len(real),
        "real_sessions": len(real),
        "types": dict(types),
        "times_published": len(timed) > 0,
        "sessions_with_times": len(timed),
        "sessions_with_clock_times": len(clocked),
        "top_products": products.most_common(15),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="output directory (required unless --from-raw)")
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--api-profile", default=DEFAULT_API_PROFILE, help="rfApiProfileId header")
    ap.add_argument("--widget", default=DEFAULT_WIDGET, help="rfWidgetId header")
    ap.add_argument("--search", default="", help="optional free-text server-side search")
    ap.add_argument("--from-raw", help="existing sessions_raw.json: print its summary, fetch nothing")
    args = ap.parse_args()

    if args.from_raw:
        with open(args.from_raw, encoding="utf-8") as f:
            items = json.load(f)
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(args.from_raw), datetime.timezone.utc)
        print(json.dumps(summarize(items, mtime.isoformat(timespec="seconds")), ensure_ascii=False, indent=1))
        return

    if not args.out:
        ap.error("--out is required unless --from-raw is given")

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "rfApiProfileId": args.api_profile,
        "rfWidgetId": args.widget,
    }

    os.makedirs(args.out, exist_ok=True)

    attrs = post(args.base, headers, "attributes", {})
    with open(os.path.join(args.out, "attributes.json"), "w", encoding="utf-8") as f:
        json.dump(attrs, f, ensure_ascii=False, indent=1)

    items = []
    frm, total = 0, None
    while total is None or frm < total:
        data = post(args.base, headers, "sessions",
                    {"search": args.search, "type": "session", "size": 200, "from": frm})
        # first page wraps items in sectionList; subsequent pages are flat
        sec = data["sectionList"][0] if "sectionList" in data else data
        total = sec["total"]
        got = sec["items"]
        items.extend(got)
        print(f"progress: {len(items)}/{total}", file=sys.stderr)
        if not got:
            break
        frm += len(got)

    with open(os.path.join(args.out, "sessions_raw.json"), "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False)

    scraped_at = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    summary = summarize(items, scraped_at)
    with open(os.path.join(args.out, "scrape_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
