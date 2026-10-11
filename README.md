# A clip repository for writing from sources

A file-based method for snipping excerpts from research papers, grading how much
weight each source can bear, arranging the excerpts into the shape of an
argument, and seeing where that argument is still unevidenced.

Built for two MSc essays on psychosis, but the structure does not assume the
topic. This is the **public copy**: the method and the analysis, with every
quotation withheld. See [What is not here](#what-is-not-here).

## The problem it solves

Reading for an essay produces two things that usually live in different places: a
record of what each paper says, and a growing sense of the order the argument
should go in. Notes capture the first and lose the second. Outlines capture the
second and lose the citations. So the argument gets assembled at the end, from
memory, under time pressure — which is when quotations drift from their sources
and weak evidence gets quietly promoted.

Here the two are separate files that know about each other:

```
outline.md          the spine: two essays, their ordered sections
notes/<key>.md      one record per source: what it says, how good it is
clips/<key>-NN.md   one excerpt per file: the quote, its locator, why it is here
```

A **clip** is one excerpt pulled out of a note so it can be moved around the
argument without dragging its paper behind it. It names the source it came from,
the section it belongs to, and its position within that section. Move the clip,
and the argument changes. Nothing else has to.

## The pipeline

```
find a paper   →  sources/<author-year-keyword>.pdf      (private)
read it        →  notes/<author-year-keyword>.md
judge it       →  appraisals/<author-year-keyword>.md
snip it        →  clips/<author-year-keyword>-NN.md
arrange it     →  outline.md + the board
write it       →  NARRATIVE.md, in argument order
```

`scripts/build-clips.py` validates every clip against `outline.md` and `notes/`,
joins each clip to its source's authors, year, design, sample size and strength
grade, and generates the narrative and the board's data.

**It fails the build rather than dropping a clip.** A clip pointing at a section
that does not exist, two clips claiming the same position, a clip whose source
has no note, an unparseable order — each stops the build and names the file. The
alternative is a clip that silently vanishes from the narrative and is noticed
after submission. Running it in CI means a broken clip cannot reach the written
draft.

## Two fields carry the weight

Everything else is bookkeeping. These two are the point:

**`verified`** is true only when the wording has been checked against the source
text — not against a summary, an abstract, or whatever was pasted into a working
document. The build lists every unverified clip as a warning on every run. In
this project that check caught a misquotation in the opening line of an essay and
two places where a paper's abstract overstated its own results.

**`locator`** is a page number, or a section name for e-numbered journals that
have none. `not reported` is an honest value. An invented page number is a
fabrication that survives into submitted work, so the schema makes the absence
visible instead of letting it be filled in later from memory.

## Grading sources instead of counting them

Each source carries a `strength` grade — `strong`, `moderate`, `indicative`,
`weak`, `not-citable` — with a `strength_why` that states the reason and a
`strength_basis` recording whether the grade came from study design alone or from
a full appraisal.

Grades are derived, never invented. A single-arm pilot with ten completers is
`weak` because of its design, not because of its conclusions. An unpublished
manuscript is `not-citable` because of its status, whatever it says. The board
colours every card by this grade, so an argument resting entirely on weak sources
looks wrong before it reads wrong.

This is also where the method earns its keep: a corpus of twenty sources is not
twenty units of evidence, and a tool that counts rather than weighs will tell you
the opposite.

## Seeing it

`board/index.html` is the source of a private web board. Each clip is a card
carrying its authors, year, theme, study design, sample size and strength grade,
grouped into its essay's sections. Cards drag between sections and between
essays; a narrative view reads the same data as continuous prose with citations.

Two panels exist to make weaknesses visible early rather than at the end: sources
ranked by how much weight they bear with the reason stated, and a count of
unevidenced sections, unverified clips, missing locators, un-citable sources, and
clips moved on the board but not yet written back to the files.

**The files are the source of truth and the board is a view of them.** Moves made
on the board live in the board's own store until applied:

```
# on the board: "Export arrangement"
python3 scripts/apply-arrangement.py ~/Downloads/arrangement.json
python3 scripts/build-clips.py
```

`apply-arrangement.py` rewrites only `section:` and `order:`, so a rearrangement
can never touch a quotation, a locator or a verification flag.

Note that `index.html` is written for a host that supplies the document skeleton,
so it is the source of a deployed page rather than a file to open directly.

## What is not here

This repository is public, so three things are withheld.

**Quotations.** Every clip's excerpt is replaced with a placeholder. The
positions, locators, verification status and commentary remain, so the argument's
structure is fully visible — but the papers' words are the papers' own.

**PDFs.** `sources/` is absent and `.gitignore` refuses `*.pdf`. The private
working copy holds publisher material under a no-redistribution constraint.

**One source entirely.** The corpus contains a manuscript that arrived stamped
for peer review, with no DOI, volume or pages. It is excluded from this
repository by `scripts/export-public.py`, which drops any source whose note
carries `status: unpublished-manuscript`. Material circulated for peer review is
given in confidence, and that is a stronger reason than copyright.

`scripts/export-public.py` builds this tree from structured data rather than by
editing prose: the quotation field is never read into the output, so a quote
cannot survive by being overlooked. It then proves it — every excerpt is reduced
to eight-word sequences and every output file is checked against all of them.
Any hit fails the export. Quoted wording inside commentary is redacted
separately, and the one appraisal published here was rewritten by hand to make
its argument without reproducing the paper's phrasing.

## The two essays

`outline.md` carries both spines. Section ids are prefixed, so a clip declares
its essay through the section it sits in.

1. **Psychosis: first episode and predisposing factors** — the core essay.
2. **Vignette: internet and AI use as a predicating factor** — built on the first.

The second essay's thesis is the distinction between *pathoplastic* and
*pathogenic*: technology has shaped the content of psychosis since at least 1810,
so the defensible claim concerns predication rather than causation. The corpus
contains no longitudinal study of AI use and psychosis, and several of its own
sources say so, which is a fact about the evidence that the writing has to carry
rather than a gap to be papered over.

## Running it

Python 3, no dependencies. The frontmatter parser handles only the flat format
this project defines, so a bare `python3` is enough and a missing package can
never break the build.

```
python3 scripts/build-clips.py     # validate, then write the narrative and board data
python3 scripts/build-index.py     # bibliography and coverage, from notes/
python3 scripts/export-public.py   # regenerate this public copy
```
