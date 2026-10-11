#!/usr/bin/env python3
"""Validate clips/ against outline.md and notes/, then generate NARRATIVE.md and
board/clips.json.

  NARRATIVE.md      the clips arranged in the spine order, ready to write over
  board/clips.json  the same data for the board, with source metadata joined on

Dependency-free on purpose, matching scripts/build-index.py: it parses only the
flat frontmatter this repo defines, so a bare python3 is enough.

Exits non-zero on a validation error, so a broken clip fails the build rather
than quietly vanishing from the narrative.

Usage: python3 scripts/build-clips.py
"""
import pathlib, re, sys, json, datetime
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
CLIPS, NOTES, BOARD = ROOT / "clips", ROOT / "notes", ROOT / "board"
KINDS = {"quote", "paraphrase", "datum", "mine"}
STRENGTHS = ["strong", "moderate", "indicative", "weak", "not-citable"]

def parse_frontmatter(text):
    """Same flat parser as build-index.py. Quoted values keep their inner colons."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, text
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
    return out, text[m.end():]

def read_outline():
    """Returns ([(essay_no, essay_title, [(id, title, intent)])], flat_sections).

    outline.md carries two essays, so sections are grouped under the `## Essay N`
    heading they sit below and the flat list preserves overall spine order.
    """
    txt = (ROOT / "outline.md").read_text()
    essays, flat = [], []
    # Split on the essay headings, keeping each heading with the block below it.
    parts = re.split(r"^##\s+Essay\s+(\d+)\s*[—-]\s*(.+?)\s*$", txt, flags=re.M)
    # parts[0] is the preamble; then repeating (no, title, body)
    for i in range(1, len(parts) - 2, 3):
        no, title, body = parts[i], parts[i + 1], parts[i + 2]
        secs = []
        for m in re.finditer(r"^\s*(\d+)\.\s+`([a-z0-9-]+)`\s+[—-]\s+(.+?)\s*$\n"
                             r"((?:^[ \t]+\S.*$\n?)*)", body, re.M):
            sec = (m.group(2), m.group(3), " ".join(m.group(4).split()))
            secs.append(sec); flat.append(sec)
        essays.append((no, title, secs))
    return essays, flat

def main():
    errors, warnings = [], []
    essays, sections = read_outline()
    if not sections:
        sys.exit("outline.md: no sections parsed — check the `## Essay N` and "
                 "`N. \\`id\\` — Title` formats")
    order_of = {sid: i for i, (sid, _, _) in enumerate(sections)}
    # Which essay each section belongs to, so a clip inherits it from its section.
    essay_of = {sid: no for no, _, secs in essays for sid, _, _ in secs}

    # --- sources, from the notes the clips point at ---
    srcs = {}
    for f in sorted(NOTES.glob("*.md")):
        if f.name == "TEMPLATE.md":
            continue
        fm, _ = parse_frontmatter(f.read_text())
        if fm:
            srcs[fm.get("key", f.stem)] = fm

    # --- clips ---
    clips = []
    for f in sorted(CLIPS.glob("*.md")):
        if f.name == "TEMPLATE.md":
            continue
        fm, body = parse_frontmatter(f.read_text())
        if not fm:
            errors.append(f"{f.name}: no frontmatter")
            continue
        cid = fm.get("id", "")
        if cid != f.stem:
            errors.append(f"{f.name}: id '{cid}' does not match filename")
        if fm.get("section") not in order_of:
            errors.append(f"{f.name}: section '{fm.get('section')}' is not in outline.md")
        if fm.get("key") not in srcs:
            errors.append(f"{f.name}: key '{fm.get('key')}' has no note in notes/")
        if fm.get("kind") not in KINDS:
            errors.append(f"{f.name}: kind '{fm.get('kind')}' not one of {sorted(KINDS)}")

        quote = "\n".join(l[1:].strip() for l in body.splitlines() if l.startswith(">")).strip()
        nm = re.search(r"^\*\*Note:\*\*\s*(.*?)(?=\n\n|\Z)", body, re.S | re.M)
        note = " ".join(nm.group(1).split()) if nm else ""
        if not quote:
            errors.append(f"{f.name}: no quoted text (lines starting with '>')")

        src = srcs.get(fm.get("key"), {})
        if str(fm.get("verified", "")).lower() != "true":
            warnings.append(f"{f.stem}: unverified against the source text")
        if fm.get("locator") in ("not reported", "", None):
            warnings.append(f"{f.stem}: no page locator")

        try:
            o = int(fm.get("order", 0))
        except ValueError:
            errors.append(f"{f.name}: order '{fm.get('order')}' is not a number")
            o = 0

        clips.append(dict(
            id=cid, key=fm.get("key"), section=fm.get("section"), order=o,
            essay=essay_of.get(fm.get("section"), "?"),
            kind=fm.get("kind"), locator=fm.get("locator"), tags=fm.get("tags") or [],
            verified=str(fm.get("verified", "")).lower() == "true",
            text=quote, note=note,
            # joined from the note so the board can show it on the card
            authors=src.get("authors", "?"), year=str(src.get("year", "?")),
            title=src.get("title", "?"), doi=src.get("doi", ""),
            design=src.get("design", "?"), n=str(src.get("n", "")),
            themes=src.get("themes") or [],
            strength=src.get("strength", "ungraded"),
            strength_why=src.get("strength_why", ""),
            strength_basis=src.get("strength_basis", ""),
            appraised=(ROOT / "appraisals" / f"{fm.get('key')}.md").exists(),
        ))

    # duplicate positions make the narrative order non-deterministic
    seen = defaultdict(list)
    for c in clips:
        seen[(c["section"], c["order"])].append(c["id"])
    for (sec, o), ids in sorted(seen.items()):
        if len(ids) > 1:
            errors.append(f"section '{sec}' order {o} used by {', '.join(ids)}")

    if errors:
        print("BUILD FAILED\n" + "\n".join("  ! " + e for e in errors), file=sys.stderr)
        sys.exit(1)

    clips.sort(key=lambda c: (order_of[c["section"]], c["order"]))
    today = datetime.date.today().isoformat()

    # --- NARRATIVE.md ---
    out = [f"# Narrative\n",
           f"Generated {today} from `outline.md` + `clips/`. Do not hand-edit — run",
           "`python3 scripts/build-clips.py`. To change the order, edit the clips'",
           "`section:`/`order:` or rearrange on the board and run",
           "`scripts/apply-arrangement.py`.\n",
           f"**{len(clips)} clips across {len(sections)} sections in "
           f"{len(essays)} essays.** "
           f"{sum(1 for c in clips if c['verified'])} verified against source text, "
           f"{sum(1 for c in clips if not c['verified'])} not.\n"]
    for no, etitle, secs in essays:
        ec = [c for c in clips if c["essay"] == no]
        out.append(f"\n---\n\n# Essay {no} — {etitle}\n")
        out.append(f"*{len(ec)} clips across {len(secs)} sections.*\n")
        for si, (sid, title, intent) in enumerate(secs, 1):
            rows = [c for c in clips if c["section"] == sid]
            out.append(f"\n## {no}.{si} {title}\n")
            out.append(f"*{intent}*\n")
            if not rows:
                out.append("> **No clips yet.** This section of the argument is "
                           "unevidenced.\n")
            for c in rows:
                flag = "" if c["verified"] else "  ⚠ UNVERIFIED"
                nd = f", n={c['n']}" if c["n"] and c["n"] != "not reported" else ""
                out.append(f"\n**{c['authors']} ({c['year']})** · {c['design']}{nd}"
                           f" · strength: {c['strength']} · `{c['id']}`{flag}\n")
                out.append("\n".join("> " + l for l in c["text"].split("\n")))
                src = "mine — from " if c["kind"] == "mine" else ""
                out.append(f"\n— {src}{c['authors']} ({c['year']}:{c['locator']})\n")
                if c["note"]:
                    out.append(f"*Note: {c['note']}*\n")
    (ROOT / "NARRATIVE.md").write_text("\n".join(out) + "\n")

    # --- board/clips.json ---
    BOARD.mkdir(exist_ok=True)
    (BOARD / "clips.json").write_text(json.dumps(dict(
        generated=today,
        essays=[dict(no=no, title=et,
                     sections=[dict(id=s, title=t2, intent=i) for s, t2, i in secs])
                for no, et, secs in essays],
        sections=[dict(id=s, title=t2, intent=i) for s, t2, i in sections],
        strengths=STRENGTHS,
        sources=[dict(key=k, authors=v.get("authors"), year=str(v.get("year")),
                      title=v.get("title"), doi=v.get("doi"), design=v.get("design"),
                      n=str(v.get("n", "")), strength=v.get("strength", "ungraded"),
                      strength_why=v.get("strength_why", ""),
                      strength_basis=v.get("strength_basis", ""),
                      themes=v.get("themes") or [],
                      appraised=(ROOT / "appraisals" / f"{k}.md").exists())
                 for k, v in sorted(srcs.items())],
        clips=clips,
    ), indent=1) + "\n")

    print(f"NARRATIVE.md      {len(clips)} clips, {len(sections)} sections, "
          f"{len(essays)} essays")
    for no, et, secs in essays:
        print(f"  essay {no}  {sum(1 for c in clips if c['essay'] == no):>3} clips  {et}")
    print(f"board/clips.json  {len(srcs)} sources")
    empty = [t for s, t, _ in sections if not any(c["section"] == s for c in clips)]
    if empty:
        print(f"\n  sections with no clips: {', '.join(empty)}")
    if warnings:
        print(f"\n  {len(warnings)} warnings:")
        for w in warnings:
            print("   - " + w)

if __name__ == "__main__":
    main()
