from src.microkinetics.reactions import Reaction, Species
from src.microkinetics.rates import SURFACE_SPECIES, site_balance
from src.microkinetics.solver import solve_steady_state


SPECIES = {
    "*": Species("*", {}, sites=1),
    "CO2": Species("CO2", {"C": 1, "O": 2}, sites=0),
    "CO2*": Species("CO2*", {"C": 1, "O": 2}, sites=1),
    "H2": Species("H2", {"H": 2}, sites=0),
    "H*": Species("H*", {"H": 1}, sites=1),
    "CO*": Species("CO*", {"C": 1, "O": 1}, sites=1),
    "O*": Species("O*", {"O": 1}, sites=1),
    "OH*": Species("OH*", {"O": 1, "H": 1}, sites=1),
    "H2O*": Species("H2O*", {"H": 2, "O": 1}, sites=1),
    "H2O": Species("H2O", {"H": 2, "O": 1}, sites=0),
    "CO": Species("CO", {"C": 1, "O": 1}, sites=0),
}


REACTIONS = [
    Reaction("R1 CO2 adsorption", {"CO2": -1, "*": -1, "CO2*": 1}),
    Reaction("R2 H2 dissociation", {"H2": -1, "*": -2, "H*": 2}),
    Reaction("R3 CO2 dissociation", {"CO2*": -1, "*": -1, "CO*": 1, "O*": 1}),
    Reaction("R4 CO desorption", {"CO*": -1, "CO": 1, "*": 1}),
    Reaction("R5 OH formation", {"O*": -1, "H*": -1, "OH*": 1, "*": 1}),
    Reaction("R6 H2O formation", {"OH*": -1, "H*": -1, "H2O*": 1, "*": 1}),
    Reaction("R7 H2O desorption", {"H2O*": -1, "H2O": 1, "*": 1}),
]


def _steady_state_result():
    return solve_steady_state(
        temperature=523.15,
        partial_pressures={"CO2": 0.25, "H2": 0.75, "CO": 1e-6, "H2O": 1e-6},
        rate_constants={name: 1.0 for idx in range(1, 8) for name in (f"R{idx}f", f"R{idx}r")},
    )


def test_elementary_steps_conserve_sites():
    for reaction in REACTIONS:
        assert reaction.net_site_count(SPECIES) == 0, (
            f"{reaction.label} does not conserve surface sites."
        )


def test_all_coverages_sum_to_one():
    result = _steady_state_result()

    assert result.success, result.message
    assert tuple(result.coverages) == SURFACE_SPECIES
    total_coverage = site_balance(result.coverages)
    assert abs(total_coverage - 1.0) < 1e-8, (
        f"Site balance should be 1.0, got {total_coverage}."
    )


def test_all_coverages_are_non_negative():
    result = _steady_state_result()

    assert result.success, result.message
    tolerance = -1e-12
    for species, coverage in result.coverages.items():
        assert coverage >= tolerance, (
            f"Coverage for {species} is below the numerical tolerance: {coverage}."
        )
