# Narrative spine

Two essays, one corpus. `scripts/build-clips.py` reads this file, so the section
ids below are the controlled vocabulary for every clip's `section:` field. A clip
pointing at a section that is not listed here is a build error, not a silent miss.

Format is fixed and parsed:

- `## Essay N — Title` opens an essay
- `N. ` + backticked id + ` — ` + title names a section
- the indented line under it says what that section has to do

Reorder the numbers to reorder an essay. Section ids are prefixed `e1-` / `e2-`
so a clip always declares which essay it belongs to.

---

## Essay 1 — Psychosis: first episode and predisposing factors

The core essay. No AI, no internet: this one has to stand as a piece of clinical
writing about psychosis itself. Essay 2 depends on it, so anything Essay 2 needs
the reader to already understand belongs here.

1. `e1-what` — What psychosis is, and how a delusion is defined
   Fix the terms before using them. Definition first, with its source named.

2. `e1-continuum` — Psychosis on a transdiagnostic continuum
   The model that lets risk be discussed below the diagnostic threshold.

3. `e1-prodrome` — The prodrome and the first episode
   The window in which onset happens, and what subthreshold symptoms predict.

4. `e1-predispose` — Predisposing factors
   What raises risk: neurodevelopmental, behavioural, environmental. The essay's
   title promises this section, so it carries the most weight.

5. `e1-assess` — Assessing risk, and what the instruments cannot say
   PQ-B and its kind. A screening threshold is not a clinical determination.

6. `e1-treat` — Treatment, and why CBTp underperforms for delusions
   Guideline-recommended, small-to-moderate effect. Say why.

7. `e1-coping` — Coping as the active ingredient
   The mechanism the treatment section implies: coping mediates exacerbation.

---

## Essay 2 — Vignette: internet and AI use as a predicating factor

Built on Essay 1. Leads with a vignette and argues from it. The thesis hinge is
`e2-history`: technology shapes the content of psychosis rather than causing it,
so the claim is predication and pathoplasticity, never causation.

1. `e2-vignette` — The vignette
   The case the essay argues from. Published cases sit here as models and as
   corroboration, not as the vignette itself.

2. `e2-scale` — The scale of exposure
   Establish a population-level exposure, with real adoption data.

3. `e2-history` — This is not new: pathoplastic, not pathogenic
   The intellectual core. Influencing machines since 1810; technology has shaped
   delusional content for two centuries. Concede this before claiming anything.

4. `e2-definition` — Naming it: AI-related psychosis, and its contested status
   Define the term, say whose definition it is, and that it is descriptive rather
   than diagnostic.

5. `e2-mechanism` — Why this technology invites it
   What is actually different this time: a fluent, agreeable, second-person
   interlocutor. Mindless social response, sycophancy, misread referentiality,
   and the documented failures that stop this being theoretical.

6. `e2-evidence` — What the evidence actually shows
   The empirical core, with the cross-sectional limit stated in the authors' own
   words. Survey base rates, then the clinical tail.

7. `e2-window` — First episode and the developmental window
   Where the two essays meet: peak adoption age meets peak onset age, and the
   clinical data points the same way.

8. `e2-benefit` — The other side
   Access, waitlists, companionship, changing attitudes. Held after the risk so
   the essay is not a one-sided alarm.

9. `e2-practice` — Assessment and practice implications
   Digital-use history, technological literacy, screening, early intervention.
