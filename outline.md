# Narrative spine

Two essays, 2,000 words each. `scripts/build-clips.py` reads this file, so the
section ids below are the controlled vocabulary for every clip's `section:`
field. A clip pointing at a section that is not listed here is a build error.

Format is fixed and parsed:

- `## Essay N — Title` opens an essay
- `N. ` + backticked id + ` — ` + title + ` · <words> words` names a section
- the indented line under it says what that section has to do

The word budget is parsed and reported against the clip count, because a section
budgeted at 300 words cannot use eleven clips. Budgets are placeholders until the
argument decides which sections grow and which get cut.

**Both gates are governed by `claims.md`.** No section is researched until it
carries a claim in Natalie's own words.

---

## Essay 1 — Psychosis: first episode and predisposing factors

2,000 words. Treatment has moved to Essay 2, so this essay does only what its
title promises: what psychosis is, when it first appears, and what raises the
risk of it appearing. Essay 2 depends on this one, so anything Essay 2 needs the
reader to already understand belongs here.

1. `e1-intro` — Introduction · 200 words
   The argument in two sentences, and the scope of the essay.

2. `e1-what` — What psychosis is, and the continuum · 300 words
   Definition first, with its source named, then the transdiagnostic continuum
   that lets risk be discussed below the diagnostic threshold. Merged, because
   separately they were two descriptive sections.

3. `e1-prodrome` — The prodrome and the first episode · 250 words
   The window in which onset happens, and what subthreshold symptoms predict.

4. `e1-predispose` — Predisposing factors · 600 words
   Neurodevelopmental, behavioural and environmental. The title promises this
   section, so it carries the most weight and the largest budget.

5. `e1-assess` — Assessing risk, and what the instruments cannot say · 300 words
   The PQ-B and its kind. A screening threshold is not a clinical determination.

6. `e1-limits` — Limitations · 200 words
   What this evidence base cannot establish. Mostly design: no longitudinal data.

7. `e1-conclusion` — Conclusion · 150 words
   What follows, and the handover to Essay 2.

---

## Essay 2 — Vignette: internet and AI use as a precipitating factor

2,000 words. A vignette asks for a formulation of a particular person, and a
formulation leads to a plan for that person — so treatment lives here, absorbed
into the formulation rather than sitting beside it.

The thesis hinge is `e2-history`: technology has shaped the *content* of
psychosis since at least 1810, so the claim is precipitation and pathoplasticity,
never causation.

1. `e2-intro` — Introduction · 150 words
   The argument in two sentences.

2. `e2-vignette` — The vignette · 150 words
   The case the essay argues from. Composite, and labelled as such.

3. `e2-naming` — Naming it, and the scale of exposure · 250 words
   Define the term, say whose definition it is and that it is descriptive rather
   than diagnostic; establish the exposure is population-level. Merged.

4. `e2-history` — This is not new: pathoplastic, not pathogenic · 200 words
   The intellectual core. Influencing machines since 1810. Concede this before
   claiming anything, then ask whether this technology differs.

5. `e2-mechanism` — Why this technology invites it · 300 words
   What is actually different: a fluent, agreeable, second-person interlocutor.

6. `e2-evidence` — What the evidence actually shows · 300 words
   Survey base rates, then the clinical tail, with the cross-sectional limit in
   the authors' own words.

7. `e2-plan` — Formulation and holistic treatment plan · 500 words
   The 5Ps formulation of the vignette, with each factor meeting the intervention
   that targets it: predisposing, precipitating, perpetuating, protective and
   presenting. Absorbs assessment and the digital-use history as its opening
   step, CBTp and coping as its interventions, and the access-and-companionship
   evidence as protective factors where the evidence supports reading it that
   way. "Holistic" is testable here: does the plan touch every P?

8. `e2-conclusion` — Conclusion · 150 words
   What the evidence can and cannot support, and what would settle it.
