#!/usr/bin/env python3
"""Download an IBM AEM event page (FAQ, experience, ...) and extract its
accordion content (cmp-accordion__item) to markdown.

IBM event pages are server-rendered: collapsed accordion panels ARE in the
HTML, so no browser is needed. Requires beautifulsoup4 (pip install beautifulsoup4).

Emits markdown to --out: one "### question" + answer per accordion item, in
document order. Frontmatter is intentionally minimal - the caller adds
environment-specific conventions.
"""
import argparse
import datetime
import io
import re
import sys
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: beautifulsoup4 not installed (pip install beautifulsoup4)", file=sys.stderr)
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="https://www.ibm.com/events/techxchange/faq")
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default=None, help="note title; defaults to the page <title>")
    args = ap.parse_args()

    req = urllib.request.Request(args.url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=120) as r:
        html = r.read().decode("utf-8", errors="replace")

    soup = BeautifulSoup(html, "html.parser")
    title = args.title or (soup.title.get_text(strip=True) if soup.title else args.url)

    def txt(el):
        t = el.get_text("\n", strip=True)
        return re.sub(r"\n{2,}", "\n", t).strip()

    entries = []
    for el in soup.find_all(class_=re.compile(r"cmp-accordion__item")):
        if el.name == "button":
            continue
        qel = el.find(class_=re.compile(r"cmp-accordion__title|cmp-accordion__header"))
        pel = el.find(class_=re.compile(r"cmp-accordion__panel"))
        q = txt(qel) if qel else "?"
        a = txt(pel) if pel else ""
        entries.append((q, a))

    today = datetime.date.today().isoformat()
    lines = ["---", f"date: {today}", f'title: "{title}"', "source: manual", f"url: {args.url}", "---", "",
             f"# {title}", "", f"Scraped from {args.url} on {today}. {len(entries)} items.", ""]
    for q, a in entries:
        lines += [f"### {q}", "", a or "*(no answer text)*", ""]

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"wrote {args.out}: {len(entries)} accordion items")


if __name__ == "__main__":
    main()
