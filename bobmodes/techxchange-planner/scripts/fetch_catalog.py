#!/usr/bin/env python3
"""Fetch the full session catalog + filter attributes of a RainFocus-based
IBM event (TechXchange, Think, ...) and save them as JSON.

Defaults target IBM TechXchange 2026. For another event/year, discover the
tokens as described in references/rainfocus-api.md and pass them as args.

Output files in --out:
  sessions_raw.json  - every catalog item, unfiltered (test sessions included)
  attributes.json    - filter attribute definitions (products, tracks, topics...)

Prints a JSON summary to stdout, including whether session day/times are
published yet - the signal that a re-run should do clash checking.
"""
import argparse
import collections
import io
import json
import sys
import urllib.parse
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DEFAULT_BASE = "https://events.tools.ibm.com/api"
# IBM TechXchange 2026 (event techxchange26) - public widget tokens, no login needed
DEFAULT_API_PROFILE = "HkAL70o02Smvj2jmwmYgs7v3n6fMYzK1"
DEFAULT_WIDGET = "ChglfSDiz1jlTR8V97Qf6kYzs773nQuF"


def post(base, headers, path, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(f"{base}/{path}", data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--api-profile", default=DEFAULT_API_PROFILE, help="rfApiProfileId header")
    ap.add_argument("--widget", default=DEFAULT_WIDGET, help="rfWidgetId header")
    ap.add_argument("--search", default="", help="optional free-text server-side search")
    args = ap.parse_args()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "rfApiProfileId": args.api_profile,
        "rfWidgetId": args.widget,
    }

    import os
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

    def attr_vals(s, name):
        return [v["value"] for v in s.get("attributevalues", []) if v.get("attribute") == name]

    def is_test(s):
        return s.get("title", "").startswith("TEST Session") or "Yes" in attr_vals(s, "Dummy session")

    real = [s for s in items if not is_test(s)]
    types = collections.Counter(s.get("type", "?") for s in real)
    products = collections.Counter(p for s in real for p in attr_vals(s, "IBM TechXchange Conference Products"))
    timed = [s for s in real if attr_vals(s, "Day") or attr_vals(s, "Day Time")]

    print(json.dumps({
        "total_fetched": len(items),
        "test_or_dummy": len(items) - len(real),
        "real_sessions": len(real),
        "types": dict(types),
        "times_published": len(timed) > 0,
        "sessions_with_times": len(timed),
        "top_products": products.most_common(15),
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
