---
name: quarto-lesson-author
description: Create or revise Quarto lesson pages for the CO2-FT / Fe3O4 microkinetics course. Use when adding course chapters, polishing lesson structure, aligning notation across lessons, or preparing Japanese educational material for Fe3O4-RWGS microkinetics.
---

# Quarto Lesson Author

## Workflow

1. Read `AGENTS.md` first.
2. Inspect `_quarto.yml`, nearby `lessons/*.qmd`, and any mechanism or source files relevant to the requested chapter.
3. Follow the existing course style: Japanese prose, precise technical language, LaTeX equations, compact tables, and explicit MVP boundaries.
4. Keep YAML `title` in the header and do not repeat the same title as a body-level `#` heading.
5. Add or revise sidebar entries in `_quarto.yml` when the lesson should be reachable from the website navigation.
6. Run `pytest` and `quarto render` when available. If Quarto or pytest cannot run, report why.

## Course Boundaries

- Treat the current MVP as Fe3O4-RWGS only.
- Preserve the R1-R7 reaction IDs and equations unless the user explicitly asks for a new model scope.
- Do not implement FeCx-FT, C2+ formation, ASF distributions, or dynamic phase transformation inside MVP lessons.
- Do not claim Fe3O4 alone explains C2+ hydrocarbon formation.
- Do not invent references, DFT values, kinetic parameters, or experimental conclusions. Use `[citation needed]` when evidence is missing.

## Lesson Pattern

Use `references/lesson-pattern.md` when creating a new lesson from scratch or when a lesson needs structural cleanup.

For chemistry notation:

- Write surface species as `*`, `CO2*`, `H*`, `CO*`, `O*`, `OH*`, `H2O*`.
- Write coverages as $\theta_*$, $\theta_{\mathrm{CO_2}}$, $\theta_{\mathrm{H}}$, $\theta_{\mathrm{CO}}$, $\theta_{\mathrm{O}}$, $\theta_{\mathrm{OH}}$, $\theta_{\mathrm{H_2O}}$.
- Explain that $\theta_{\mathrm{CO_2}}$ denotes the coverage of `CO2*` when first needed.
- Keep gas species as `CO2`, `H2`, `CO`, and `H2O` for the MVP.

## Validation Checklist

Before finishing:

- Confirm the page starts with a valid Quarto YAML header.
- Confirm no duplicate body `#` title repeats the YAML `title`.
- Confirm R1-R7 are unchanged if referenced.
- Confirm unsupported claims are removed or marked `[citation needed]`.
- Confirm the sidebar includes the lesson if it is part of the course sequence.
- Run `pytest`.
- Run `quarto render`.
