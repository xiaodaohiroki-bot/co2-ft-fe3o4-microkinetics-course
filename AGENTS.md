# AGENTS.md

Guidance for Codex and other coding agents working in this repository.

## Project Intent

This is a research-course repository for CO2 Fischer-Tropsch chemistry on Fe3O4-related catalysts and microkinetic modeling. Treat files as learning materials that may later become research notes, executable examples, or teaching content.

## Working Style

- Prefer small, traceable changes.
- Keep scientific assumptions explicit.
- Preserve units in every parameter table.
- Separate literature evidence, model assumptions, and interpretation.
- Do not invent citations. Mark missing sources with `TODO: citation needed`.

## Documentation Conventions

- Use Markdown for course notes.
- Keep equations readable in plain Markdown where possible.
- Use clear section names and short paragraphs.
- When adding Japanese explanations, preserve important English technical terms such as `microkinetic model`, `RWGS`, `coverage`, and `degree of rate control`.

## Code Conventions

- Prefer simple, readable Python for modeling examples unless the repository later adopts another stack.
- Keep example scripts runnable from the repository root.
- Avoid adding heavy dependencies unless they clearly improve the course.
- Include a short usage note whenever adding a runnable script.

## Verification

Before committing changes:

- Check `git status --short`.
- Run relevant tests or scripts if code exists.
- For documentation-only edits, at least review Markdown structure and links.
