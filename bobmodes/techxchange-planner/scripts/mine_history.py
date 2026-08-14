#!/usr/bin/env python3
"""Mine local AI-chat history for IBM product/topic mentions, using the
event catalog's own filter vocabulary (attributes.json from fetch_catalog.py)
as the term list - so the vocabulary stays current with each event.

Scans .jsonl / .md / .txt / .json files under the given paths (default:
Claude Code transcripts in ~/.claude/projects). Counts, per term, how many
files mention it and total occurrences. Substring matching, case-insensitive.

Terms that are also common English words (Scale, Verify, Concert, Fusion, ...)
are flagged low_confidence - treat their counts with skepticism.

Output: JSON to stdout. Interpretation (turning counts into an interest
profile) is the caller's job, not this script's.
"""
import argparse
import collections
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

EXTS = {".jsonl", ".md", ".txt", ".json"}
# product names that collide with everyday English - counts are unreliable
NOISY = {"scale", "verify", "concert", "fusion", "instana", "maximo", "not on this list",
         "z/os", "ibm i", "confluent"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--attributes", required=True, help="attributes.json from fetch_catalog.py")
    ap.add_argument("--paths", nargs="+", default=[os.path.expanduser("~/.claude/projects")])
    ap.add_argument("--extra-terms", nargs="*", default=[],
                    help="additional terms to count (e.g. company or project names)")
    ap.add_argument("--max-file-mb", type=float, default=25.0)
    ap.add_argument("--top", type=int, default=40)
    args = ap.parse_args()

    attrs = json.load(open(args.attributes, encoding="utf-8"))
    vocab = set(args.extra_terms)
    for a in attrs.get("attributes", []):
        if a.get("id") in ("ibmtechxchangeconferenceproducts", "sessiontopic", "techtrack"):
            vocab.update(v["name"] for v in a.get("values", []))
    terms = sorted({t.strip() for t in vocab if t and len(t.strip()) >= 3})

    files_scanned, files_skipped = 0, 0
    file_hits = collections.Counter()   # term -> nr of files containing it
    total_hits = collections.Counter()  # term -> total occurrences
    lower_terms = [(t, t.lower()) for t in terms]

    for root_path in args.paths:
        if not os.path.isdir(root_path):
            print(f"warn: not a directory, skipping: {root_path}", file=sys.stderr)
            continue
        for dirpath, _dirnames, filenames in os.walk(root_path):
            for fn in filenames:
                if os.path.splitext(fn)[1].lower() not in EXTS:
                    continue
                full = os.path.join(dirpath, fn)
                try:
                    if os.path.getsize(full) > args.max_file_mb * 1024 * 1024:
                        files_skipped += 1
                        continue
                    with open(full, encoding="utf-8", errors="replace") as f:
                        text = f.read().lower()
                except OSError:
                    files_skipped += 1
                    continue
                files_scanned += 1
                for term, lt in lower_terms:
                    n = text.count(lt)
                    if n:
                        file_hits[term] += 1
                        total_hits[term] += n

    ranked = [{"term": t, "files": file_hits[t], "hits": total_hits[t],
               "low_confidence": t.lower() in NOISY}
              for t, _ in file_hits.most_common(args.top)]

    print(json.dumps({
        "files_scanned": files_scanned,
        "files_skipped": files_skipped,
        "vocabulary_size": len(terms),
        "matches": ranked,
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
