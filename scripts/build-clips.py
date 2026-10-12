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
STANCES = {"supports", "qualifies", "contradicts", ""}
# Fields the evidence-scout skill adds to a source and copies onto its clips.
# Lists are declared so the flat frontmatter parser's [] form round-trips.
INDEP_LIST = ["team", "affiliations", "countries", "serves"]
INDEP_STR = ["harvard", "population", "weird", "perspective", "dataset"]
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

def read_claims():
    """Returns {section_id: (claim, date)} from claims.md.

    claims.md holds Natalie's words and nothing else. This function only reads
    it: no part of the build writes, tidies or normalises a claim. A section
    absent from that file has a closed gate, which is what the evidence-scout
    skill checks before it will search.
    """
    p = ROOT / "claims.md"
    if not p.exists():
        return {}
    out, txt = {}, p.read_text()
    body = txt.split("\n---\n", 1)[-1]
    for m in re.finditer(r"^##\s+([a-z0-9-]+)\s*$\n(?:\*([0-9-]+)\*\s*\n)?(.*?)"
                         r"(?=^##\s|\Z)", body, re.M | re.S):
        sid, date, claim = m.group(1), m.group(2) or "", m.group(3)
        claim = "\n".join(l for l in claim.strip().splitlines()
                           if not l.strip().startswith("<!--")).strip()
        if claim:
            out[sid] = (claim, date)
    return out

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
        for m in re.finditer(r"^\s*(\d+)\.\s+`([a-z0-9-]+)`\s+[—-]\s+(.+?)"
                             r"(?:\s+·\s+(\d+)\s+words)?\s*$\n"
                             r"((?:^[ \t]+\S.*$\n?)*)", body, re.M):
            sec = (m.group(2), m.group(3).strip(), " ".join(m.group(5).split()),
                   int(m.group(4) or 0))
            secs.append(sec); flat.append(sec)
        essays.append((no, title, secs))
    return essays, flat

def section_dict(sid, title, intent, words, claims):
    claim, date = claims.get(sid, ("", ""))
    return dict(id=sid, title=title, intent=intent, words=words, claim=claim,
                claim_by=("natalie" if claim else ""), claim_date=date)

def pdf_for(key):
    """Local PDF for a source, if we hold one. Returns (relative path, bytes)."""
    p = ROOT / "sources" / f"{key}.pdf"
    return (f"sources/{key}.pdf", p.stat().st_size) if p.exists() else ("", 0)

def main():
    errors, warnings = [], []
    essays, sections = read_outline()
    claims = read_claims()
    for sid in claims:
        if sid not in {s for s, _, _, _ in sections}:
            errors.append(f"claims.md: '{sid}' is not a section in outline.md")
    if not sections:
        sys.exit("outline.md: no sections parsed — check the `## Essay N` and "
                 "`N. \\`id\\` — Title` formats")
    order_of = {sid: i for i, (sid, _, _, _) in enumerate(sections)}
    # Which essay each section belongs to, so a clip inherits it from its section.
    essay_of = {sid: no for no, _, secs in essays for sid, _, _, _ in secs}

    # --- sources, from the notes the clips point at ---
    srcs = {}
    for f in sorted(NOTES.glob("*.md")):
        if f.name == "TEMPLATE.md":
            continue
        fm, _ = parse_frontmatter(f.read_text())
        if fm:
            for sid in (fm.get("serves") or []):
                if sid not in order_of:
                    errors.append(f"notes/{f.name}: serves '{sid}' is not a section "
                                  f"in outline.md")
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
        stance = fm.get("stance", "")
        if isinstance(stance, list):
            stance = ""
        if stance not in STANCES:
            errors.append(f"{f.name}: stance '{stance}' not one of "
                          f"{sorted(x for x in STANCES if x)}")

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

        indep = {k: (src.get(k) or []) for k in INDEP_LIST}
        indep.update({k: (src.get(k) or "") for k in INDEP_STR})
        if indep.get("weird") in ("true", "True"):
            indep["weird"] = True
        elif indep.get("weird") in ("false", "False"):
            indep["weird"] = False
        clips.append(dict(
            id=cid, key=fm.get("key"), section=fm.get("section"), order=o,
            essay=essay_of.get(fm.get("section"), "?"), stance=stance, **indep,
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
        for si, (sid, title, intent, words) in enumerate(secs, 1):
            rows = [c for c in clips if c["section"] == sid]
            out.append(f"\n## {no}.{si} {title}"
                       + (f" · {words} words" if words else "") + "\n")
            out.append(f"*{intent}*\n")
            if not rows:
                out.append("> **No clips yet.** This section of the argument is "
                           "unevidenced.\n")
            for c in rows:
                flag = "" if c["verified"] else "  ⚠ UNVERIFIED"
                nd = f", n={c['n']}" if c["n"] and c["n"] != "not reported" else ""
                out.append(f"\n**{c['authors']} ({c['year']})** · {c['design']}{nd}"
                           f" · strength: {c['strength']} · `{c['id']}`{flag}  ")
                out.append(f"*{c['title']}*\n")
                out.append("\n".join("> " + l for l in c["text"].split("\n")))
                src = "mine — from " if c["kind"] == "mine" else ""
                doi = f" doi:{c['doi']}" if c.get("doi") and c["doi"] != "not reported" else ""
                out.append(f"\n— {src}{c['authors']} ({c['year']}:{c['locator']}){doi}\n")
                if c["note"]:
                    out.append(f"*Note: {c['note']}*\n")
    (ROOT / "NARRATIVE.md").write_text("\n".join(out) + "\n")

    # --- board/clips.json ---
    BOARD.mkdir(exist_ok=True)
    (BOARD / "clips.json").write_text(json.dumps(dict(
        generated=today,
        essays=[dict(no=no, title=et,
                     sections=[section_dict(s, t2, i, w, claims) for s, t2, i, w in secs])
                for no, et, secs in essays],
        sections=[section_dict(s, t2, i, w, claims) for s, t2, i, w in sections],
        strengths=STRENGTHS,
        sources=[dict(key=k, authors=v.get("authors"), year=str(v.get("year")),
                      pdf=pdf_for(k)[0], pdf_bytes=pdf_for(k)[1],
                      **{f: (v.get(f) or []) for f in INDEP_LIST},
                      **{f: (True if v.get(f) in ("true", "True") else
                             False if v.get(f) in ("false", "False") else
                             (v.get(f) or "")) for f in INDEP_STR},
                      title=v.get("title"), doi=v.get("doi"), design=v.get("design"),
                      n=str(v.get("n", "")), strength=v.get("strength", "ungraded"),
                      strength_why=v.get("strength_why", ""),
                      strength_basis=v.get("strength_basis", ""),
                      themes=v.get("themes") or [],
                      appraised=(ROOT / "appraisals" / f"{k}.md").exists())
                 for k, v in sorted(srcs.items())],
        clips=clips,
        unplaced=[dict(key=k, authors=v.get("authors"), year=str(v.get("year")),
                       pdf=pdf_for(k)[0], pdf_bytes=pdf_for(k)[1],
                       title=v.get("title"), design=v.get("design"),
                       n=str(v.get("n", "")), strength=v.get("strength", "ungraded"),
                       strength_why=v.get("strength_why", ""),
                       strength_basis=v.get("strength_basis", ""),
                       serves=v.get("serves") or [],
                       countries=v.get("countries") or [],
                       weird=(True if v.get("weird") in ("true", "True") else
                              False if v.get("weird") in ("false", "False") else
                              (v.get("weird") or "")),
                       harvard=v.get("harvard", ""), doi=v.get("doi", ""),
                       status=v.get("status", ""))
                 for k, v in sorted(srcs.items())
                 if not any(c["key"] == k for c in clips)],
    ), indent=1) + "\n")

    print(f"NARRATIVE.md      {len(clips)} clips, {len(sections)} sections, "
          f"{len(essays)} essays")
    for no, et, secs in essays:
        print(f"  essay {no}  {sum(1 for c in clips if c['essay'] == no):>3} clips  {et}")
    unplaced = [k for k in srcs if not any(c["key"] == k for c in clips)]
    assigned = [k for k in unplaced if srcs[k].get("serves")]
    held = sum(1 for k in srcs if pdf_for(k)[0])
    print(f"board/clips.json  {len(srcs)} sources, {held} with a local PDF")
    print(f"shelf            {len(unplaced)} sources read but not yet placed in the "
          f"argument, {len(assigned)} of them with a `serves` section named")
    open_gates = [s for s, _, _, _ in sections if s in claims]
    print(f"claims.md        {len(open_gates)} of {len(sections)} section gates open"
          + (f": {', '.join(open_gates)}" if open_gates
             else " — no research can start until a claim is written"))
    empty = [t for s, t, _, _ in sections if not any(c["section"] == s for c in clips)]
    if empty:
        print(f"\n  sections with no clips: {', '.join(empty)}")
    over = []
    for sid, title, _, words in sections:
        n = sum(1 for c in clips if c["section"] == sid)
        if words and n * 45 > words:
            over.append(f"{title[:44]}: {n} clips vs {words} words")
    if over:
        print(f"\n  {len(over)} sections hold more quotation than their budget can"
              f" carry (at ~45 words a clip):")
        for o in over:
            print("   - " + o)
    if warnings:
        print(f"\n  {len(warnings)} warnings:")
        for w in warnings:
            print("   - " + w)

if __name__ == "__main__":
    main()
