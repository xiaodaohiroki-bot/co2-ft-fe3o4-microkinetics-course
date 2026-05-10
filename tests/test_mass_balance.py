from collections import Counter

from tests.test_site_balance import REACTIONS, SPECIES


def _composition_sum(names):
    total = Counter()
    for name in names:
        total.update(SPECIES[name].composition)
    return dict(total)


def test_elementary_steps_conserve_elements():
    for reaction in REACTIONS:
        imbalance = reaction.net_element_count(SPECIES)
        assert imbalance == {}, (
            f"{reaction.label} does not conserve elemental mass: {imbalance}."
        )


def test_overall_rwgs_carbon_oxygen_hydrogen_balance_closes():
    reactants = _composition_sum(["CO2", "H2"])
    products = _composition_sum(["CO", "H2O"])

    assert reactants == products == {"C": 1, "O": 2, "H": 2}, (
        f"Overall RWGS mass balance mismatch: reactants={reactants}, products={products}."
    )


def test_gas_phase_net_production_is_consistent_with_rwgs_stoichiometry():
    net_stoichiometry = {
        "CO2": -1,
        "H2": -1,
        "CO": 1,
        "H2O": 1,
    }
    element_balance = Counter()
    for species, coefficient in net_stoichiometry.items():
        for element, count in SPECIES[species].composition.items():
            element_balance[element] += coefficient * count

    assert dict(element_balance) == {"C": 0, "O": 0, "H": 0}, (
        f"Gas-phase RWGS stoichiometry is not mass balanced: {dict(element_balance)}."
    )
