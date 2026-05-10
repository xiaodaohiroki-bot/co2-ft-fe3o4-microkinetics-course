from pathlib import Path

from src.microkinetics import Reaction, Species, load_mechanism_yaml


MECHANISM_PATH = Path("mechanisms/fe3o4_rwgs_minimal.yaml")
EXPECTED_GAS_SPECIES = ["CO2", "H2", "CO", "H2O"]
EXPECTED_SURFACE_SPECIES = ["*", "CO2*", "H*", "CO*", "O*", "OH*", "H2O*"]
EXPECTED_REACTIONS = [
    ("R1", "CO2 + * <=> CO2*"),
    ("R2", "H2 + 2* <=> 2H*"),
    ("R3", "CO2* + * <=> CO* + O*"),
    ("R4", "CO* <=> CO + *"),
    ("R5", "O* + H* <=> OH* + *"),
    ("R6", "OH* + H* <=> H2O* + *"),
    ("R7", "H2O* <=> H2O + *"),
]


def test_loads_r1_to_r7_from_yaml():
    mechanism = load_mechanism_yaml(MECHANISM_PATH)

    assert [(reaction.id, reaction.equation) for reaction in mechanism.reactions] == EXPECTED_REACTIONS


def test_distinguishes_gas_and_surface_species():
    mechanism = load_mechanism_yaml(MECHANISM_PATH)

    assert list(mechanism.gas_species) == EXPECTED_GAS_SPECIES
    assert list(mechanism.surface_species) == EXPECTED_SURFACE_SPECIES
    assert all(species.is_gas for species in mechanism.gas_species.values())
    assert all(species.is_surface for species in mechanism.surface_species.values())


def test_each_reaction_has_required_metadata():
    mechanism = load_mechanism_yaml(MECHANISM_PATH)

    for reaction in mechanism.reactions:
        assert reaction.id
        assert reaction.equation
        assert reaction.type
        assert reaction.reversible is True


def test_species_names_match_lesson_mechanism():
    mechanism = load_mechanism_yaml(MECHANISM_PATH)

    assert set(mechanism.species) == set(EXPECTED_GAS_SPECIES + EXPECTED_SURFACE_SPECIES)
    assert mechanism.species["CO2"].phase == "gas"
    assert mechanism.species["CO2*"].phase == "surface"


def test_reaction_stoichiometry_is_parsed():
    reaction = Reaction(id="R3", equation="CO2* + * <=> CO* + O*", type="surface_reaction")

    assert reaction.stoichiometry == {"CO2*": -1, "*": -1, "CO*": 1, "O*": 1}


def test_species_dataclass_supports_phase_flags():
    gas = Species(name="CO2", phase="gas", composition={"C": 1, "O": 2})
    surface = Species(name="CO2*", phase="surface", composition={"C": 1, "O": 2}, sites=1)

    assert gas.is_gas
    assert not gas.is_surface
    assert surface.is_surface
    assert not surface.is_gas
