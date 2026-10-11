#!/usr/bin/env python3
"""Push an arrangement made on the board back into clips/ frontmatter.

The files are the source of truth; the board is a view you can rearrange. This
script is the one direction that writes back, so the two never silently drift:
it rewrites only `section:` and `order:` in each clip, touching nothing else.

  1. On the board, press "Export arrangement" — it downloads arrangement.json
  2. python3 scripts/apply-arrangement.py ~/Downloads/arrangement.json
  3. python3 scripts/build-clips.py

Pass --dry-run to see what would change without writing.

Expected input: {"clips": [{"id": "...", "section": "...", "order": 10}, ...]}
"""
import pathlib, re, sys, json

ROOT = pathlib.Path(__file__).resolve().parent.parent
CLIPS = ROOT / "clips"

def main(argv):
    args = [a for a in argv if not a.startswith("-")]
    dry = "--dry-run" in argv
    if len(args) != 1:
        sys.exit(__doc__)
    data = json.loads(pathlib.Path(args[0]).read_text())
    rows = data.get("clips", data if isinstance(data, list) else [])

    valid = {s for s in re.findall(r"^\s*\d+\.\s+`([a-z0-9-]+)`", (ROOT / "outline.md").read_text(), re.M)}
    changed = unchanged = 0
    for r in rows:
        cid, sec, order = r.get("id"), r.get("section"), r.get("order")
        f = CLIPS / f"{cid}.md"
        if not f.exists():
            print(f"  ! no such clip: {cid}", file=sys.stderr); continue
        if sec not in valid:
            print(f"  ! {cid}: section '{sec}' is not in outline.md — skipped", file=sys.stderr); continue
        t = old = f.read_text()
        t = re.sub(r"^section:.*$", f"section: {sec}", t, count=1, flags=re.M)
        t = re.sub(r"^order:.*$", f"order: {int(order)}", t, count=1, flags=re.M)
        if t == old:
            unchanged += 1; continue
        changed += 1
        print(f"  {'would move' if dry else 'moved'} {cid} -> {sec} / {order}")
        if not dry:
            f.write_text(t)
    print(f"\n{changed} changed, {unchanged} already in place"
          + ("  (dry run — nothing written)" if dry else "\nNow run: python3 scripts/build-clips.py"))

if __name__ == "__main__":
    main(sys.argv[1:])
