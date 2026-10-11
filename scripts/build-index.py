#!/usr/bin/env python3
"""Aggregate notes/ into BIBLIOGRAPHY.md and COVERAGE.md.

Reads the YAML-ish frontmatter of every note and produces:
  BIBLIOGRAPHY.md — all sources, grouped by design, Warwick Harvard ordering
  COVERAGE.md     — what the corpus is made of, and where it is thin

Deliberately dependency-free: parses only the flat frontmatter it defines, so it
runs anywhere with a bare python3 and never breaks on a missing package.

Usage: python3 scripts/build-index.py
"""
import pathlib, re, sys, datetime
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
NOTES, APPR = ROOT / "notes", ROOT / "appraisals"

def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    out = {}
    for line in m.group(1).splitlines():
        line = line.split(" #")[0].rstrip()
        if not line or line.lstrip().startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip().strip('"')
        if v in ("[]", ""):
            v = []
        elif v.startswith("[") and v.endswith("]"):
            v = [x.strip().strip('"') for x in v[1:-1].split(",") if x.strip()]
        out[k.strip()] = v
    return out

def main():
    notes = []
    for f in sorted(NOTES.glob("*.md")):
        if f.name == "TEMPLATE.md":
            continue
        fm = parse_frontmatter(f.read_text())
        if not fm:
            print(f"  skipped (no frontmatter): {f.name}", file=sys.stderr)
            continue
        fm["_file"] = f.name
        # Trust the filesystem over the flag: a note can claim appraised: false
        # while an appraisal exists, and the file is the fact.
        fm["_appraised"] = (APPR / f.name).exists()
        notes.append(fm)

    today = datetime.date.today().isoformat()

    # --- BIBLIOGRAPHY ---
    by_design = defaultdict(list)
    for n in notes:
        by_design[n.get("design", "unclassified")].append(n)
    b = [f"# Bibliography\n", f"Generated {today} from `notes/`. Do not hand-edit —",
         "run `python3 scripts/build-index.py`.\n",
         f"**{len(notes)} sources.**\n"]
    for design in sorted(by_design):
        rows = sorted(by_design[design], key=lambda x: (str(x.get("authors", "")), str(x.get("year", ""))))
        b.append(f"\n## {design} ({len(rows)})\n")
        for n in rows:
            cite = f"{n.get('authors','?')} ({n.get('year','?')}) *{n.get('title','?')}*"
            extra = [str(n.get("source", "")), f"n={n['n']}" if n.get("n") else "",
                     "appraised" if n["_appraised"] else ""]
            b.append(f"- {cite}  \n  `{n['_file']}` — {', '.join(x for x in extra if x)}")
    (ROOT / "BIBLIOGRAPHY.md").write_text("\n".join(b) + "\n")

    # --- COVERAGE ---
    designs, sources = Counter(n.get("design", "?") for n in notes), Counter(n.get("source", "?") for n in notes)
    themes = Counter(t for n in notes for t in (n.get("themes") or []))
    appraised = sum(1 for n in notes if n["_appraised"])
    unthemed = [n["_file"] for n in notes if not n.get("themes")]

    c = [f"# Coverage\n", f"Generated {today}. What the corpus is made of, and where it is thin.\n",
         f"- **{len(notes)}** sources with notes",
         f"- **{appraised}** appraised ({(100*appraised//len(notes)) if notes else 0}%)",
         f"- **{len(themes)}** distinct themes assigned\n",
         "## By design\n"]
    for d, k in designs.most_common():
        c.append(f"- {d}: {k}")
    c.append("\n## By source\n")
    for s, k in sources.most_common():
        c.append(f"- {s}: {k}")
    c.append("\n## Themes\n")
    if themes:
        for t, k in themes.most_common():
            flag = "  — **thin**, fewer than three sources" if k < 3 else ""
            c.append(f"- {t}: {k}{flag}")
    else:
        c.append("_None assigned yet._")
    c.append("\n## Gaps\n")
    if unthemed:
        c.append(f"- {len(unthemed)} note(s) with no theme assigned:")
        c += [f"  - `{f}`" for f in unthemed[:20]]
    if appraised < len(notes):
        c.append(f"- {len(notes)-appraised} note(s) without an appraisal.")
    if len(designs) == 1 and notes:
        c.append(f"- Single design ({next(iter(designs))}) across the whole corpus — "
                 "a limitation of the evidence base to state explicitly.")
    if len(sources) == 1 and notes:
        c.append(f"- All sources from one database ({next(iter(sources))}) — search "
                 "strategy may be too narrow to defend.")
    (ROOT / "COVERAGE.md").write_text("\n".join(c) + "\n")

    print(f"wrote BIBLIOGRAPHY.md and COVERAGE.md — {len(notes)} notes, {appraised} appraised")

if __name__ == "__main__":
    main()
