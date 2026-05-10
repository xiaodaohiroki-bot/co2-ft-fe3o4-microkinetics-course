"""Minimal solver placeholders for lesson examples."""

from __future__ import annotations


def site_balance(coverages: dict[str, float]) -> float:
    """Return the sum of surface coverages."""

    return sum(coverages.values())


def normalize_coverages(coverages: dict[str, float]) -> dict[str, float]:
    """Normalize coverages so they sum to one."""

    total = site_balance(coverages)
    if total <= 0:
        raise ValueError("Coverage total must be positive.")
    return {name: value / total for name, value in coverages.items()}
