---
# Machine-readable header. scripts/build-index.py aggregates over these fields,
# so spelling and vocabulary matter more than prose does.
key: author-year-keyword          # matches the filename, without .md
authors: "Surname, A. & Surname, B."
year: 2024
title: "Exact title as published."
source: ScienceDirect             # ScienceDirect | PubMed | Lancet | Cochrane | Google Scholar | other
doi: 10.xxxx/xxxxx                # or: not reported
design: RCT                       # RCT | single-arm-trial | cohort | case-control | cross-sectional | systematic-review | meta-analysis | qualitative | narrative-review | case-report
n: 240                            # participants, or studies for a review; or: not reported
population: "who, where"
themes: []                        # assigned later, by literature-synthesis-coach
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
