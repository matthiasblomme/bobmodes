#!/usr/bin/env python3
"""Download an IBM AEM event page (FAQ, experience, ...) and extract its
accordion content (cmp-accordion__item) to markdown.

IBM event pages are server-rendered: collapsed accordion panels ARE in the
HTML, so no browser is needed. Requires beautifulsoup4 (pip install beautifulsoup4).

Emits markdown to --out: one "### question" + answer per accordion item, in
document order. The script owns date, title, source and url in the frontmatter;
`tags` comes from --tags. When --out already exists, every other frontmatter
field it carries (tags included) is kept as-is: a re-scrape once rewrote the
FAQ note without its tags line, and the weekly vault pass had to restore it.
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


def existing_frontmatter(path, owned):
    """Top-level frontmatter fields of an existing note, minus the ones this script
    owns, as [(key, [lines])] in file order; indented continuation lines stay with
    their key. A missing file or one without frontmatter yields []."""
    try:
        text = open(path, encoding="utf-8").read()
    except FileNotFoundError:
        return []
    m = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", text, flags=re.S)
    if not m:
        return []
    fields = []
    for line in m.group(1).splitlines():
        km = re.match(r"([A-Za-z_][\w-]*):", line)
        if km:
            fields.append((km.group(1), [line]))
        elif fields:
            fields[-1][1].append(line)
    return [(k, block) for k, block in fields if k not in owned]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="https://www.ibm.com/events/techxchange/faq")
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default=None, help="note title; defaults to the page <title>")
    ap.add_argument("--tags", default="techxchange,ibm,conference,faq",
                    help="comma-separated tags for a NEW note; an existing note keeps its own")
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
    kept = existing_frontmatter(args.out, owned={"date", "title", "source", "url"})
    if not any(k == "tags" for k, _ in kept):
        kept.insert(0, ("tags", ["tags: [" + ", ".join(t.strip() for t in args.tags.split(",") if t.strip()) + "]"]))
    front = ["---", f"date: {today}", f'title: "{title}"']
    for _, block in kept:
        front += block
    front += ["source: manual", f"url: {args.url}", "---"]
    lines = front + ["", f"# {title}", "", f"Scraped from {args.url} on {today}. {len(entries)} items.", ""]
    for q, a in entries:
        lines += [f"### {q}", "", a or "*(no answer text)*", ""]

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"wrote {args.out}: {len(entries)} accordion items")


if __name__ == "__main__":
    main()
