from collections import Counter

from tests.test_site_balance import REACTIONS, SPECIES


def _composition_sum(names):
    total = Counter()
    for name in names:
        total.update(SPECIES[name].composition)
    return dict(total)


def test_elementary_steps_conserve_elements():
    for reaction in REACTIONS:
        assert reaction.net_element_count(SPECIES) == {}, reaction.label


def test_overall_rwgs_carbon_oxygen_hydrogen_balance_closes():
    reactants = _composition_sum(["CO2", "H2"])
    products = _composition_sum(["CO", "H2O"])

    assert reactants == products == {"C": 1, "O": 2, "H": 2}
