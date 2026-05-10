"""Rate expressions for the minimal seven-step Fe3O4-RWGS model."""

from __future__ import annotations

from collections.abc import Callable, Mapping

SURFACE_SPECIES = ("*", "CO2*", "H*", "CO*", "O*", "OH*", "H2O*")
ADSORBED_SPECIES = SURFACE_SPECIES[1:]
GAS_SPECIES = ("CO2", "H2", "CO", "H2O")
REACTION_IDS = tuple(f"R{idx}" for idx in range(1, 8))
RATE_CONSTANT_NAMES = tuple(
    f"R{idx}{direction}" for idx in range(1, 8) for direction in ("f", "r")
)

RateValue = float | Callable[[float], float]


def reaction_rates(
    temperature: float,
    partial_pressures: Mapping[str, float],
    rate_constants: Mapping[str, RateValue],
    coverages: Mapping[str, float],
) -> dict[str, float]:
    """Return net rates for R1-R7 using mass-action kinetics."""

    _validate_temperature(temperature)
    p = validate_partial_pressures(partial_pressures)
    theta = normalize_coverages(coverages)
    k = {name: rate_constant(rate_constants, name, temperature) for name in RATE_CONSTANT_NAMES}

    return {
        "R1": k["R1f"] * p["CO2"] * theta["*"] - k["R1r"] * theta["CO2*"],
        "R2": k["R2f"] * p["H2"] * theta["*"] ** 2 - k["R2r"] * theta["H*"] ** 2,
        "R3": k["R3f"] * theta["CO2*"] * theta["*"] - k["R3r"] * theta["CO*"] * theta["O*"],
        "R4": k["R4f"] * theta["CO*"] - k["R4r"] * p["CO"] * theta["*"],
        "R5": k["R5f"] * theta["O*"] * theta["H*"] - k["R5r"] * theta["OH*"] * theta["*"],
        "R6": k["R6f"] * theta["OH*"] * theta["H*"] - k["R6r"] * theta["H2O*"] * theta["*"],
        "R7": k["R7f"] * theta["H2O*"] - k["R7r"] * p["H2O"] * theta["*"],
    }


def coverage_residuals(rates: Mapping[str, float]) -> dict[str, float]:
    """Return dtheta/dt residuals for the six non-empty surface species."""

    return {
        "CO2*": rates["R1"] - rates["R3"],
        "H*": 2.0 * rates["R2"] - rates["R5"] - rates["R6"],
        "CO*": rates["R3"] - rates["R4"],
        "O*": rates["R3"] - rates["R5"],
        "OH*": rates["R5"] - rates["R6"],
        "H2O*": rates["R6"] - rates["R7"],
    }


def net_production_rates(rates: Mapping[str, float]) -> dict[str, float]:
    """Return net gas-phase production rates from the surface mechanism."""

    return {
        "CO2": -rates["R1"],
        "H2": -rates["R2"],
        "CO": rates["R4"],
        "H2O": rates["R7"],
    }


def co_production_rate_from_rates(rates: Mapping[str, float]) -> float:
    """Return the gas-phase CO production rate from reaction R4."""

    return float(rates["R4"])


def site_balance(coverages: Mapping[str, float]) -> float:
    """Return the sum of the surface coverages."""

    return sum(float(coverages.get(name, 0.0)) for name in SURFACE_SPECIES)


def normalize_coverages(coverages: Mapping[str, float]) -> dict[str, float]:
    """Normalize supported surface coverages so they sum to one."""

    validate_coverage_values(coverages)
    total = site_balance(coverages)
    if total <= 0:
        raise ValueError("Coverage total must be positive.")
    return {name: float(coverages.get(name, 0.0)) / total for name in SURFACE_SPECIES}


def validate_partial_pressures(partial_pressures: Mapping[str, float]) -> dict[str, float]:
    """Validate and copy required gas partial pressures."""

    missing = [name for name in GAS_SPECIES if name not in partial_pressures]
    if missing:
        raise KeyError(f"Missing partial pressure(s): {', '.join(missing)}")

    pressures: dict[str, float] = {}
    for name in GAS_SPECIES:
        value = float(partial_pressures[name])
        if value < 0:
            raise ValueError(f"Partial pressure for {name} must be non-negative.")
        pressures[name] = value
    return pressures


def validate_coverage_values(coverages: Mapping[str, float]) -> None:
    for name in SURFACE_SPECIES:
        value = float(coverages.get(name, 0.0))
        if value < 0:
            raise ValueError(f"Coverage for {name} must be non-negative.")


def rate_constant(rate_constants: Mapping[str, RateValue], name: str, temperature: float) -> float:
    """Evaluate one rate constant from a scalar or temperature callable."""

    try:
        value = rate_constants[name]
    except KeyError as exc:
        raise KeyError(f"Missing rate constant: {name}") from exc

    evaluated = value(temperature) if callable(value) else value
    evaluated = float(evaluated)
    if evaluated < 0:
        raise ValueError(f"Rate constant {name} must be non-negative.")
    return evaluated


def _validate_temperature(temperature: float) -> None:
    if temperature <= 0:
        raise ValueError("Temperature must be positive.")
