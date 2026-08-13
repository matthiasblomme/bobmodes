#!/usr/bin/env python3
"""Turn sessions_raw.json (from fetch_catalog.py) into markdown notes:

  1. A full session-catalog note: summary tables (activity type, tech track,
     top products) + a compact per-type listing of every real session.
  2. Optional per-product focus notes (--product, repeatable): every session
     tagged with that product, WITH abstracts and speakers.

Test/dummy sessions are filtered out. Frontmatter is minimal and generic -
adapt tags/links to the environment after generation if needed.
"""
import argparse
import collections
import datetime
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TYPE_ORDER = ["Technology Breakout", "Hands-on Lab", "Tech Talk", "Certification", "Workshop"]


def attr_vals(s, name):
    return [v["value"] for v in s.get("attributevalues", []) if v.get("attribute") == name]


def clean(txt):
    return re.sub(r"\s+", " ", str(txt or "")).strip()


def esc(txt):
    return clean(txt).replace("|", "/")


def speakers(s):
    out = []
    for p in s.get("participants", []):
        nm = p.get("fullName") or f"{p.get('firstName', '')} {p.get('lastName', '')}".strip()
        bits = [b for b in [p.get("jobTitle"), p.get("companyName")] if b]
        out.append(f"{nm} ({', '.join(bits)})" if bits else nm)
    return out


def type_sorted(sessions):
    return sorted(sessions, key=lambda s: (
        TYPE_ORDER.index(s["type"]) if s.get("type") in TYPE_ORDER else 9, s.get("code", "")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True, help="sessions_raw.json path")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--event", default="IBM TechXchange 2026")
    ap.add_argument("--catalog-url",
                    default="https://reg.tools.ibm.com/flow/ibm/techxchange26/sessioncatalog/page/sessioncatalog")
    ap.add_argument("--slug", default="techxchange-2026", help="filename prefix")
    ap.add_argument("--product", action="append", default=[],
                    help="product tag to build a detailed focus note for (repeatable)")
    args = ap.parse_args()

    items = json.load(open(args.raw, encoding="utf-8"))
    items = [s for s in items if not s.get("title", "").startswith("TEST Session")
             and "Yes" not in attr_vals(s, "Dummy session")]
    today = datetime.date.today().isoformat()
    os.makedirs(args.out_dir, exist_ok=True)

    for s in items:
        s["_tracks"] = attr_vals(s, "Tech Track")
        s["_level"] = ", ".join(attr_vals(s, "Technical Level")).replace(" Level", "")
        s["_topics"] = attr_vals(s, "Session Topic")
        s["_products"] = attr_vals(s, "IBM TechXchange Conference Products")
        s["_champ"] = bool(attr_vals(s, "IBM Champion Led"))

    # --- catalog note ---
    L = ["---", f"date: {today}", f'title: "{args.event} — Session Catalog"',
         "tags: [conference, sessions, catalog]", "source: manual", f"url: {args.catalog_url}",
         "---", "", f"# {args.event} — Session Catalog", "",
         f"Scraped from the [session catalog]({args.catalog_url}) (RainFocus API) on {today}. "
         f"{len(items)} activities (test sessions filtered out).", "", "## Summary", ""]

    tc = collections.Counter(s.get("type", "?") for s in items)
    L += ["| Activity type | Count |", "|---|---|"]
    L += [f"| {t} | {c} |" for t, c in tc.most_common()]
    L.append("")
    trc = collections.Counter(t for s in items for t in s["_tracks"])
    L += ["| Tech track | Sessions |", "|---|---|"]
    L += [f"| {t} | {c} |" for t, c in trc.most_common()]
    L.append("")
    pc = collections.Counter(p for s in items for p in s["_products"])
    L += ["Top products by session count (sessions can carry several tags):", "",
          "| Product | Sessions |", "|---|---|"]
    L += [f"| {p} | {c} |" for p, c in pc.most_common(25)]
    L.append("")

    for t in TYPE_ORDER + [t for t in tc if t not in TYPE_ORDER]:
        group = sorted((s for s in items if s.get("type") == t), key=lambda s: s.get("code", ""))
        if not group:
            continue
        L += [f"## {t} ({len(group)})", "", "| Code | Title | Track | Level |", "|---|---|---|---|"]
        for s in group:
            L.append(f"| {s.get('code', '?')} | {esc(s.get('title'))} | "
                     f"{esc(', '.join(s['_tracks'])) or '-'} | {esc(s['_level']) or '-'} |")
        L.append("")

    cat_path = os.path.join(args.out_dir, f"{args.slug}-session-catalog.md")
    with open(cat_path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print(f"wrote {cat_path}: {len(items)} sessions")

    # --- product focus notes ---
    for prod in args.product:
        sel = type_sorted([s for s in items if prod in s["_products"]])
        pslug = re.sub(r"[^a-z0-9]+", "-", prod.lower()).strip("-")
        B = ["---", f"date: {today}", f'title: "{args.event} — {prod} Sessions"',
             "tags: [conference, sessions]", "source: manual", f"url: {args.catalog_url}",
             "---", "", f"# {args.event} — {prod} Sessions", "",
             f"All {len(sel)} catalog activities tagged with product **{prod}**, scraped {today}.", ""]
        cur = None
        for s in sel:
            if s.get("type") != cur:
                cur = s.get("type")
                B += [f"## {cur}", ""]
            B += [f"### {clean(s.get('title'))} [{s.get('code', '?')}]", ""]
            meta = []
            if s["_tracks"]:
                meta.append("**Track:** " + ", ".join(s["_tracks"]))
            if s["_topics"]:
                meta.append("**Topic:** " + ", ".join(s["_topics"]))
            if s["_level"]:
                meta.append("**Level:** " + s["_level"])
            if s.get("length"):
                meta.append(f"**Length:** {int(s['length'])} min")
            others = [p for p in s["_products"] if p != prod]
            if others:
                meta.append("**Also tagged:** " + ", ".join(others))
            if s["_champ"]:
                meta.append("**IBM Champion led**")
            B += ["  \n".join(meta), ""]
            ab = clean(s.get("abstract"))
            if ab:
                B += [ab, ""]
            sp = speakers(s)
            if sp:
                B += ["*Speakers:* " + "; ".join(sp), ""]
        ppath = os.path.join(args.out_dir, f"{args.slug}-{pslug}-sessions.md")
        with open(ppath, "w", encoding="utf-8") as f:
            f.write("\n".join(B))
        print(f"wrote {ppath}: {len(sel)} sessions")


if __name__ == "__main__":
    main()
