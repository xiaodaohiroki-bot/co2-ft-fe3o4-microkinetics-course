import pytest

from src.microkinetics import load_mechanism_yaml
from src.microkinetics.rates import RATE_CONSTANT_NAMES, REACTION_IDS, SURFACE_SPECIES
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
    assert set(result.coverages) == set(SURFACE_SPECIES), (
        f"Unexpected coverage keys: {result.coverages.keys()}."
    )
    assert set(result.reaction_rates) == set(REACTION_IDS), (
        f"Unexpected reaction-rate keys: {result.reaction_rates.keys()}."
    )
    assert set(result.net_production_rates) == {"CO2", "H2", "CO", "H2O"}, (
        f"Unexpected gas production keys: {result.net_production_rates.keys()}."
    )


def test_coverages_sum_to_one_and_are_non_negative():
    result = solve_steady_state(
        temperature=523.15,
        partial_pressures=example_partial_pressures(),
        rate_constants=example_rate_constants(),
    )

    assert sum(result.coverages.values()) == pytest.approx(1.0, abs=1e-8), (
        f"Coverage sum is not 1.0: {result.coverages}."
    )
    tolerance = -1e-12
    for species, coverage in result.coverages.items():
        assert coverage >= tolerance, (
            f"Coverage for {species} is below tolerance {tolerance}: {coverage}."
        )


def test_co_production_rate_is_numeric():
    result = solve_steady_state(
        temperature=523.15,
        partial_pressures=example_partial_pressures(),
        rate_constants=example_rate_constants(),
    )

    assert isinstance(result.net_production_rates["CO"], float), (
        "CO production rate should be returned as a float."
    )
    assert co_production_rate_from_result(result) == result.net_production_rates["CO"], (
        "CO production helper should return the same value as net_production_rates['CO']."
    )


def test_missing_partial_pressure_raises_clear_error():
    pressures = example_partial_pressures()
    pressures.pop("H2O")

    with pytest.raises(KeyError, match="Missing partial pressure"):
        solve_steady_state(
            temperature=523.15,
            partial_pressures=pressures,
            rate_constants=example_rate_constants(),
        )


def test_negative_partial_pressure_raises_clear_error():
    pressures = example_partial_pressures()
    pressures["CO2"] = -0.1

    with pytest.raises(ValueError, match="CO2.*non-negative"):
        solve_steady_state(
            temperature=523.15,
            partial_pressures=pressures,
            rate_constants=example_rate_constants(),
        )


def test_reaction_ids_and_equations_match_mechanism_file():
    mechanism = load_mechanism_yaml("mechanisms/fe3o4_rwgs_minimal.yaml")
    expected = [
        ("R1", "CO2 + * <=> CO2*"),
        ("R2", "H2 + 2* <=> 2H*"),
        ("R3", "CO2* + * <=> CO* + O*"),
        ("R4", "CO* <=> CO + *"),
        ("R5", "O* + H* <=> OH* + *"),
        ("R6", "OH* + H* <=> H2O* + *"),
        ("R7", "H2O* <=> H2O + *"),
    ]
    actual = [(reaction.id, reaction.equation) for reaction in mechanism.reactions]

    assert actual == expected, (
        f"Mechanism R1-R7 definitions differ from the lesson mechanism: {actual}."
    )
