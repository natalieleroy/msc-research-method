#!/usr/bin/env python3
"""Generate a public, quotation-free copy of this project.

The private repo holds verbatim excerpts from copyrighted papers, publisher PDFs,
and material from a manuscript under confidential peer review. None of that can
be published. But the method and the analysis can, and they are the interesting
part, so this script builds a separate tree containing:

  - the pipeline: outline.md, the scripts, the templates, the board's source
  - public/README.md, which is the public repository's front page
  - one file per source: its citation, design, strength grade and the reason
  - one file per clip: where it sits in the argument, its locator, and the
    commentary written about it -- but NEVER the quoted text

The public form is BUILT FROM THE STRUCTURED DATA, not by editing prose. The
`text` field is simply never read into the output, so a quotation cannot survive
by being missed. A verification pass then proves it: every clip's text is reduced
to word shingles and every output file is checked against them. Any hit fails the
export.

Excluded entirely, by key: anything whose note carries `status: unpublished-manuscript`.

Usage: python3 scripts/export-public.py [target-dir]
       default target: ../msc-research-method
"""
import json, pathlib, re, shutil, sys, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
TARGET = pathlib.Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 \
    else ROOT.parent / "msc-research-method"
WITHHELD = "[quotation withheld — see README]"
REDACTED = "[quoted wording withheld]"
SHINGLE = 8   # consecutive words; long enough to avoid false positives
QUOTED = re.compile(r'[\"\u201c]([^\"\u201c\u201d]{25,})[\"\u201d]')

def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}, text
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

def redact_quotes(s):
    """Blank out quoted wording inside commentary.

    A clip's note is our own writing, but it sometimes quotes the source in order
    to correct or compare it. Those spans are the source's words, so they go.
    Only runs of 6+ words are redacted: shorter quoted fragments are terms of
    art ("amplifier", "first episode") rather than reproduced expression.
    """
    def sub(m):
        inner = m.group(1)
        return REDACTED if len(inner.split()) >= 6 else m.group(0)
    return QUOTED.sub(sub, s)

def shingles(s):
    w = re.findall(r"[a-z0-9]+", s.lower())
    out = set()
    for i in range(max(0, len(w) - SHINGLE + 1)):
        run = w[i:i + SHINGLE]
        # Fewer than three alphabetic tokens means this is a number string --
        # an odds ratio, a confidence interval, a sample size. Facts are not
        # protectable expression and must not be mangled to satisfy a checker.
        if sum(1 for x in run if x.isalpha()) < 3:
            continue
        out.add(" ".join(run))
    return out

def main():
    data = json.loads((ROOT / "board" / "clips.json").read_text())

    # --- what is excluded, and why, decided from the notes themselves ---
    excluded = {}
    for f in sorted((ROOT / "notes").glob("*.md")):
        if f.name == "TEMPLATE.md":
            continue
        fm, _ = parse_frontmatter(f.read_text())
        if fm.get("status") == "unpublished-manuscript":
            excluded[fm.get("key")] = "manuscript under confidential peer review"
    srcs = [s for s in data["sources"] if s["key"] not in excluded]
    clips = [c for c in data["clips"] if c["key"] not in excluded]

    if TARGET.exists():
        for child in TARGET.iterdir():
            if child.name == ".git":
                continue
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    TARGET.mkdir(parents=True, exist_ok=True)

    # --- the public README lives here, not in the public tree ---
    # The export clears its target, so anything hand-written there is lost on the
    # next run. Keeping the source copy in this repo makes the public repository
    # fully reproducible from this one, which is the point of generating it.
    readme = ROOT / "public" / "README.md"
    if readme.exists():
        shutil.copy2(readme, TARGET / "README.md")
    else:
        print("  ! public/README.md is missing — the public repo will have no README",
              file=sys.stderr)

    # --- pipeline files, copied verbatim: none contain quoted material ---
    (TARGET / "scripts").mkdir()
    for n in ("build-index.py", "build-clips.py", "apply-arrangement.py",
              "export-public.py"):
        shutil.copy2(ROOT / "scripts" / n, TARGET / "scripts" / n)
    shutil.copy2(ROOT / "outline.md", TARGET / "outline.md")
    (TARGET / "notes").mkdir(); (TARGET / "clips").mkdir()
    shutil.copy2(ROOT / "notes" / "TEMPLATE.md", TARGET / "notes" / "TEMPLATE.md")
    shutil.copy2(ROOT / "clips" / "TEMPLATE.md", TARGET / "clips" / "TEMPLATE.md")
    (TARGET / "board").mkdir()
    shutil.copy2(ROOT / "board" / "index.html", TARGET / "board" / "index.html")

    # --- hand-written public appraisals only (`<key>.public.md`) ---
    pub_appr = sorted((ROOT / "appraisals").glob("*.public.md"))
    if pub_appr:
        (TARGET / "appraisals").mkdir()
        for f in pub_appr:
            shutil.copy2(f, TARGET / "appraisals" / f.name.replace(".public.md", ".md"))

    # --- one file per source ---
    for s in srcs:
        mine = [c for c in clips if c["key"] == s["key"]]
        body = [f"---", f"key: {s['key']}", f"authors: \"{s['authors']}\"",
                f"year: {s['year']}", f"title: \"{s['title']}\"",
                f"doi: {s['doi']}", f"design: {s['design']}", f"n: {s['n']}",
                f"strength: {s['strength']}", f"themes: [{', '.join(s['themes'])}]",
                f"appraised: {str(s['appraised']).lower()}", "---", "",
                f"# {s['authors']} ({s['year']})", "",
                f"**{s['title']}**", "",
                f"DOI: {s['doi']}", "",
                f"## How much weight it bears: {s['strength']}", "",
                redact_quotes(s["strength_why"]), "",
                f"*Graded on {s['strength_basis']}.*", "",
                f"## Clips drawn from it ({len(mine)})", ""]
        for c in sorted(mine, key=lambda c: (c["section"], c["order"])):
            body.append(f"- `{c['id']}` → **{c['section']}** · {c['kind']} · "
                        f"{c['locator']} · {'checked' if c['verified'] else 'unchecked'}")
        body += ["", "---", "", "*Quotations from this source are withheld from the "
                 "public repository. See the README.*", ""]
        (TARGET / "notes" / f"{s['key']}.md").write_text("\n".join(body))

    # --- one file per clip: position and commentary, never the quotation ---
    for c in clips:
        (TARGET / "clips" / f"{c['id']}.md").write_text("\n".join([
            "---", f"id: {c['id']}", f"key: {c['key']}", f"essay: {c['essay']}",
            f"section: {c['section']}", f"order: {c['order']}", f"kind: {c['kind']}",
            f"locator: \"{c['locator']}\"", f"verified: {str(c['verified']).lower()}",
            f"tags: [{', '.join(c['tags'])}]", "---", "",
            f"> {WITHHELD}", "",
            f"— {c['authors']} ({c['year']}:{c['locator']})", "",
            f"**Why this clip is here:** {redact_quotes(c['note'])}", "",
        ]))

    # --- board data with the text withheld, so the board still runs ---
    pub = dict(data)
    pub["sources"] = [dict(s, strength_why=redact_quotes(s.get("strength_why", "")))
                      for s in srcs]
    pub["unplaced"] = [dict(s, strength_why=redact_quotes(s.get("strength_why", "")))
                       for s in data.get("unplaced", []) if s["key"] not in excluded]
    pub["clips"] = [dict(c, text=WITHHELD, note=redact_quotes(c["note"]))
                    for c in clips]
    (TARGET / "board" / "clips.json").write_text(json.dumps(pub, indent=1) + "\n")

    (TARGET / ".gitignore").write_text(
        "# No PDFs, ever. This repository is public.\n*.pdf\nsources/\n"
        ".DS_Store\n__pycache__/\n")

    # --- VERIFY: no clip text survives anywhere in the output ---
    # Only guard against other people's words. A `mine` clip is our own
    # analysis, so it may legitimately reappear in an appraisal we also wrote.
    bad, needles = [], {}
    for c in data["clips"]:
        if c["kind"] == "mine":
            continue
        for sh in shingles(c["text"]):
            needles[sh] = c["id"]
    for f in sorted(TARGET.rglob("*")):
        if not f.is_file() or ".git/" in str(f):
            continue
        try:
            hay = shingles(f.read_text())
        except (UnicodeDecodeError, OSError):
            continue
        for sh in hay & needles.keys():
            bad.append(f"{f.relative_to(TARGET)}: text from {needles[sh]}")
    if bad:
        print("EXPORT FAILED — quoted text leaked:", file=sys.stderr)
        for b in sorted(set(bad))[:40]:
            print("  ! " + b, file=sys.stderr)
        sys.exit(1)

    print(f"exported to {TARGET}")
    print(f"  {len(srcs)} sources, {len(clips)} clips, "
          f"{len(pub_appr)} public appraisals")
    for k, why in excluded.items():
        n = sum(1 for c in data["clips"] if c["key"] == k)
        print(f"  excluded {k} ({n} clips) — {why}")
    print(f"  verified: no {SHINGLE}-word sequence from any clip appears in the output")

if __name__ == "__main__":
    main()
