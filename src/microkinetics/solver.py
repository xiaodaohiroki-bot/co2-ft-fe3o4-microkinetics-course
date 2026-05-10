"""Steady-state solver for a minimal Fe3O4-RWGS surface mechanism."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np
from scipy.optimize import root

from .rates import (
    ADSORBED_SPECIES,
    GAS_SPECIES,
    RATE_CONSTANT_NAMES,
    SURFACE_SPECIES,
    RateValue,
    co_production_rate_from_rates,
    coverage_residuals,
    net_production_rates,
    normalize_coverages,
    reaction_rates,
    site_balance,
    validate_coverage_values,
    validate_partial_pressures,
)


@dataclass(frozen=True)
class SteadyStateResult:
    """Result from solving the surface steady state."""

    coverages: dict[str, float]
    reaction_rates: dict[str, float]
    net_production_rates: dict[str, float]
    success: bool
    message: str
    residuals: dict[str, float]

    @property
    def rates(self) -> dict[str, float]:
        """Compatibility alias for earlier callers."""

        return self.reaction_rates


def solve_steady_state(
    temperature: float,
    partial_pressures: Mapping[str, float],
    rate_constants: Mapping[str, RateValue],
    initial_coverages: Mapping[str, float] | None = None,
) -> SteadyStateResult:
    """Solve steady-state coverages for the minimal seven-step Fe3O4-RWGS model.

    The seven elementary steps are:

    R1: CO2 + * <=> CO2*
    R2: H2 + 2* <=> 2H*
    R3: CO2* + * <=> CO* + O*
    R4: CO* <=> CO + *
    R5: O* + H* <=> OH* + *
    R6: OH* + H* <=> H2O* + *
    R7: H2O* <=> H2O + *

    Coverages are parameterized with logits and converted through a softmax.
    This keeps every coverage positive and makes the site balance exactly one.
    """

    _validate_temperature(temperature)
    pressures = validate_partial_pressures(partial_pressures)
    y0 = _initial_logits(initial_coverages)

    solution = root(
        lambda y: _steady_state_residual_vector(y, temperature, pressures, rate_constants),
        y0,
        method="hybr",
    )

    coverages = _coverages_from_logits(solution.x)
    rates = reaction_rates(temperature, pressures, rate_constants, coverages)
    residual_values = coverage_residuals(rates)
    return SteadyStateResult(
        coverages=coverages,
        reaction_rates=rates,
        net_production_rates=net_production_rates(rates),
        success=bool(solution.success),
        message=str(solution.message),
        residuals=residual_values,
    )


def co_production_rate(
    temperature: float,
    partial_pressures: Mapping[str, float],
    rate_constants: Mapping[str, RateValue],
    coverages: Mapping[str, float],
) -> float:
    """Return the net gas-phase CO production rate from R4."""

    return co_production_rate_from_rates(
        reaction_rates(temperature, partial_pressures, rate_constants, coverages)
    )


def co_production_rate_from_result(result: SteadyStateResult) -> float:
    """Return the CO production rate stored in a steady-state result."""

    return co_production_rate_from_rates(result.reaction_rates)


def _steady_state_residual_vector(
    logits: np.ndarray,
    temperature: float,
    partial_pressures: Mapping[str, float],
    rate_constants: Mapping[str, RateValue],
) -> np.ndarray:
    coverages = _coverages_from_logits(logits)
    rates = reaction_rates(temperature, partial_pressures, rate_constants, coverages)
    residuals = coverage_residuals(rates)
    return np.array([residuals[name] for name in ADSORBED_SPECIES], dtype=float)


def _coverages_from_logits(logits: np.ndarray) -> dict[str, float]:
    if len(logits) != len(ADSORBED_SPECIES):
        raise ValueError(f"Expected {len(ADSORBED_SPECIES)} coverage logits.")
    raw = np.array([0.0, *logits], dtype=float)
    raw = raw - np.max(raw)
    weights = np.exp(raw)
    fractions = weights / np.sum(weights)
    return {name: float(value) for name, value in zip(SURFACE_SPECIES, fractions, strict=True)}


def _initial_logits(initial_coverages: Mapping[str, float] | None) -> np.ndarray:
    if initial_coverages is None:
        coverages = {name: 1.0 / len(SURFACE_SPECIES) for name in SURFACE_SPECIES}
    else:
        coverages = normalize_coverages(initial_coverages)

    floor = 1e-30
    empty_site = max(coverages["*"], floor)
    return np.array(
        [np.log(max(coverages[name], floor) / empty_site) for name in ADSORBED_SPECIES],
        dtype=float,
    )


def _validate_temperature(temperature: float) -> None:
    if temperature <= 0:
        raise ValueError("Temperature must be positive.")
