import pytest

from src.microkinetics.rates import RATE_CONSTANT_NAMES, SURFACE_SPECIES
from src.microkinetics.solver import co_production_rate_from_result, solve_steady_state


def example_partial_pressures():
    return {"CO2": 0.25, "H2": 0.75, "CO": 1e-6, "H2O": 1e-6}


def example_rate_constants():
    return {name: 1.0 for name in RATE_CONSTANT_NAMES}


def test_solve_steady_state_returns_coverages_rates_and_production_rates():
    result = solve_steady_state(
        temperature=523.15,
        partial_pressures=example_partial_pressures(),
        rate_constants=example_rate_constants(),
    )

    assert result.success, result.message
    assert set(result.coverages) == set(SURFACE_SPECIES)
    assert set(result.reaction_rates) == {f"R{i}" for i in range(1, 8)}
    assert set(result.net_production_rates) == {"CO2", "H2", "CO", "H2O"}


def test_coverages_sum_to_one_and_are_non_negative():
    result = solve_steady_state(
        temperature=523.15,
        partial_pressures=example_partial_pressures(),
        rate_constants=example_rate_constants(),
    )

    assert sum(result.coverages.values()) == pytest.approx(1.0, abs=1e-12)
    assert all(value >= 0.0 for value in result.coverages.values())


def test_co_production_rate_is_numeric():
    result = solve_steady_state(
        temperature=523.15,
        partial_pressures=example_partial_pressures(),
        rate_constants=example_rate_constants(),
    )

    assert isinstance(result.net_production_rates["CO"], float)
    assert co_production_rate_from_result(result) == result.net_production_rates["CO"]


def test_missing_partial_pressure_raises_clear_error():
    pressures = example_partial_pressures()
    pressures.pop("H2O")

    with pytest.raises(KeyError, match="Missing partial pressure"):
        solve_steady_state(
            temperature=523.15,
            partial_pressures=pressures,
            rate_constants=example_rate_constants(),
        )
