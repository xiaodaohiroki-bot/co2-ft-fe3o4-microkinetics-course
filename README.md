# CO2-FT / Fe3O4 Microkinetics Course

This repository contains a Quarto website and Python code for learning microkinetic modeling through a minimal Fe3O4-RWGS model.

The MVP is intentionally limited to RWGS over Fe3O4:

```text
CO2 + H2 <=> CO + H2O
```

Fe3O4 is treated here as an RWGS-active phase. FeCx-FT, C2+ hydrocarbon formation, ASF distributions, and dynamic phase transformation are future extensions only. This repository does not claim that Fe3O4 alone explains C2+ hydrocarbon formation.

## Contents

- `_quarto.yml`: Quarto website configuration
- `index.qmd`: course home page
- `roadmap.qmd`: course development roadmap
- `lessons/`: lesson pages
- `src/microkinetics/`: Python microkinetic-model utilities
- `tests/`: pytest tests for balance checks and solver behavior
- `mechanisms/`: mechanism definitions
- `docs/`: rendered Quarto website output

## Local Setup

Create and activate a Python environment, then install the scientific Python dependencies used by the solver and tests.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install numpy scipy pytest
```

Install Quarto separately from the official site:

<https://quarto.org/docs/get-started/>

Confirm the installation:

```powershell
quarto --version
```

## Render the Quarto Website

From the repository root:

```powershell
quarto render
```

The rendered site is written to `docs/` because `_quarto.yml` sets:

```yaml
project:
  type: website
  output-dir: docs
```

For local preview:

```powershell
quarto preview
```

## Run Tests

```powershell
python -m pytest tests
```

If `pytest` is not installed, install it in the active Python environment:

```powershell
python -m pip install pytest
```

## Modeling Boundary

The first model should remain limited to Fe3O4-RWGS. Future FeCx-FT and C2+ selectivity models should be added only after their species sets, elementary steps, citations, and validation checks are defined. Use `[citation needed]` rather than inventing unsupported references.
