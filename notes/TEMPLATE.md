---
# Machine-readable header. scripts/build-index.py aggregates over these fields,
# so spelling and vocabulary matter more than prose does.
key: author-year-keyword          # matches the filename, without .md
authors: "Surname, A. & Surname, B."
year: 2024
title: "Exact title as published."
source: ScienceDirect             # ScienceDirect | PubMed | Lancet | Cochrane | Google Scholar | other
doi: 10.xxxx/xxxxx                # or: not reported
url: ""                           # where a human can actually READ it: a PMC link, a
                                  # guideline page, a repository copy. Not the DOI, which
                                  # the board links separately. Leave empty if there is none.
design: RCT                       # RCT | single-arm-trial | cohort | case-control | cross-sectional | systematic-review | meta-analysis | qualitative | narrative-review | case-report | guideline
n: 240                            # participants, or studies for a review; or: not reported
population: "who, where"
themes: []                        # assigned later, by literature-synthesis-coach

# --- evidence-scout fields. Independence is judged from these, so code them
# from the paper itself, never from where the authors work. Leave a field EMPTY
# rather than guessing: triangulation_check.py reports "uncoded", which is a
# true statement, whereas a guess silently changes a section's status.
serves: []                        # section ids this source COULD feed, from outline.md.
                                  # A suggestion, not a placement: it puts the source on
                                  # the board's shelf against those sections until a clip
                                  # is actually made. Leave EMPTY where the fit is poor —
                                  # an honest blank beats an invitation to misuse it.
harvard: ""                       # full Warwick Harvard reference, one line
team: []                          # short labels for the lead group(s)
affiliations: []
countries: []                     # where PARTICIPANTS were recruited
weird: ""                         # true | false | partial
perspective: ""                   # "discipline / method"
dataset: ""                       # named cohort or database, if any
strength: ""                      # strong | moderate | indicative | weak | not-citable
strength_why: ""                  # 2-4 sentences: what it can and cannot establish
strength_basis: ""                # design-only | publication-status | full-appraisal
appraised: false                  # true once appraisals/<key>.md exists
read: 2026-09-06
---

# Author (Year) — short title

**Citation:** Full Warwick Harvard reference.

## Question
What the paper set out to answer, in one sentence.

## Design
Design, sample size, population, setting, follow-up length.

## Measures
Instruments used, and whether validated for this population.

## Findings
Numbers copied exactly — direction, magnitude, intervals. Never paraphrased.

## Authors' conclusion
What they claim it means. Kept separate from Findings on purpose.

## Limitations
The ones that constrain the claim, not the ritual paragraph.

## Quotables
> "Exact wording." (Author, Year:Page)

## Reader's note
Your own thinking, explicitly marked as yours so it never leaks into a citation.

## Not reported
Fields the paper did not supply. Meaningful in aggregate.
