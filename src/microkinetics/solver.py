"""Steady-state solver for a minimal Fe3O4-RWGS surface mechanism."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

import numpy as np
from scipy.optimize import root

SURFACE_SPECIES = ("*", "CO2*", "H*", "CO*", "O*", "OH*", "H2O*")
ADSORBED_SPECIES = SURFACE_SPECIES[1:]
GAS_SPECIES = ("CO2", "H2", "CO", "H2O")

RateValue = float | Callable[[float], float]


@dataclass(frozen=True)
class SteadyStateResult:
    """Result from solving the surface steady state."""

    coverages: dict[str, float]
    rates: dict[str, float]
    success: bool
    message: str
    residuals: dict[str, float]


def site_balance(coverages: Mapping[str, float]) -> float:
    """Return the sum of the surface coverages."""

    return sum(float(coverages.get(name, 0.0)) for name in SURFACE_SPECIES)


def normalize_coverages(coverages: Mapping[str, float]) -> dict[str, float]:
    """Normalize a surface coverage dictionary so the supported species sum to one."""

    _validate_coverage_values(coverages)
    total = site_balance(coverages)
    if total <= 0:
        raise ValueError("Coverage total must be positive.")
    return {name: float(coverages.get(name, 0.0)) / total for name in SURFACE_SPECIES}


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
    pressures = _validate_partial_pressures(partial_pressures)
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
        rates=rates,
        success=bool(solution.success),
        message=str(solution.message),
        residuals=residual_values,
    )


def reaction_rates(
    temperature: float,
    partial_pressures: Mapping[str, float],
    rate_constants: Mapping[str, RateValue],
    coverages: Mapping[str, float],
) -> dict[str, float]:
    """Return net rates for R1-R7 using mass-action kinetics."""

    _validate_temperature(temperature)
    p = _validate_partial_pressures(partial_pressures)
    theta = normalize_coverages(coverages)
    k = {name: _rate_constant(rate_constants, name, temperature) for name in _RATE_CONSTANT_NAMES}

    return {
        "R1": k["R1f"] * p["CO2"] * theta["*"] - k["R1r"] * theta["CO2*"],
        "R2": k["R2f"] * p["H2"] * theta["*"] ** 2 - k["R2r"] * theta["H*"] ** 2,
        "R3": k["R3f"] * theta["CO2*"] * theta["*"] - k["R3r"] * theta["CO*"] * theta["O*"],
        "R4": k["R4f"] * theta["CO*"] - k["R4r"] * p["CO"] * theta["*"],
        "R5": k["R5f"] * theta["O*"] * theta["H*"] - k["R5r"] * theta["OH*"] * theta["*"],
        "R6": k["R6f"] * theta["OH*"] * theta["H*"] - k["R6r"] * theta["H2O*"] * theta["*"],
        "R7": k["R7f"] * theta["H2O*"] - k["R7r"] * p["H2O"] * theta["*"],
    }


def co_production_rate(
    temperature: float,
    partial_pressures: Mapping[str, float],
    rate_constants: Mapping[str, RateValue],
    coverages: Mapping[str, float],
) -> float:
    """Return the net gas-phase CO production rate from R4."""

    return reaction_rates(temperature, partial_pressures, rate_constants, coverages)["R4"]


def coverage_residuals(rates: Mapping[str, float]) -> dict[str, float]:
    """Return dtheta/dt residuals for the six non-empty surface species."""

    r = rates
    return {
        "CO2*": r["R1"] - r["R3"],
        "H*": 2.0 * r["R2"] - r["R5"] - r["R6"],
        "CO*": r["R3"] - r["R4"],
        "O*": r["R3"] - r["R5"],
        "OH*": r["R5"] - r["R6"],
        "H2O*": r["R6"] - r["R7"],
    }


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


def _validate_partial_pressures(partial_pressures: Mapping[str, float]) -> dict[str, float]:
    pressures: dict[str, float] = {}
    for name in GAS_SPECIES:
        value = float(partial_pressures.get(name, 0.0))
        if value < 0:
            raise ValueError(f"Partial pressure for {name} must be non-negative.")
        pressures[name] = value
    return pressures


def _validate_coverage_values(coverages: Mapping[str, float]) -> None:
    for name in SURFACE_SPECIES:
        value = float(coverages.get(name, 0.0))
        if value < 0:
            raise ValueError(f"Coverage for {name} must be non-negative.")


def _rate_constant(rate_constants: Mapping[str, RateValue], name: str, temperature: float) -> float:
    try:
        value = rate_constants[name]
    except KeyError as exc:
        raise KeyError(f"Missing rate constant: {name}") from exc

    evaluated = value(temperature) if callable(value) else value
    evaluated = float(evaluated)
    if evaluated < 0:
        raise ValueError(f"Rate constant {name} must be non-negative.")
    return evaluated


_RATE_CONSTANT_NAMES = tuple(f"R{idx}{direction}" for idx in range(1, 8) for direction in ("f", "r"))
