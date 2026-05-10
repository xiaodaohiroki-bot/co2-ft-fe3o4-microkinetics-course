import unittest

from src.microkinetics.reactions import Reaction, Species


SPECIES = {
    "*": Species("*", {}, sites=1),
    "CO2": Species("CO2", {"C": 1, "O": 2}, sites=0),
    "CO2*": Species("CO2*", {"C": 1, "O": 2}, sites=1),
    "H2": Species("H2", {"H": 2}, sites=0),
    "H*": Species("H*", {"H": 1}, sites=1),
    "COOH*": Species("COOH*", {"C": 1, "O": 2, "H": 1}, sites=1),
    "CO*": Species("CO*", {"C": 1, "O": 1}, sites=1),
    "OH*": Species("OH*", {"O": 1, "H": 1}, sites=1),
    "H2O": Species("H2O", {"H": 2, "O": 1}, sites=0),
    "CO": Species("CO", {"C": 1, "O": 1}, sites=0),
}


REACTIONS = [
    Reaction("CO2 adsorption", {"CO2": -1, "*": -1, "CO2*": 1}),
    Reaction("H2 dissociation", {"H2": -1, "*": -2, "H*": 2}),
    Reaction("COOH formation", {"CO2*": -1, "H*": -1, "COOH*": 1, "*": 1}),
    Reaction("COOH cleavage", {"COOH*": -1, "*": -1, "CO*": 1, "OH*": 1}),
    Reaction("water formation", {"OH*": -1, "H*": -1, "H2O": 1, "*": 2}),
    Reaction("CO desorption", {"CO*": -1, "CO": 1, "*": 1}),
]


class SiteBalanceTest(unittest.TestCase):
    def test_minimal_rwgs_network_conserves_sites(self):
        for reaction in REACTIONS:
            with self.subTest(reaction=reaction.label):
                self.assertEqual(reaction.net_site_count(SPECIES), 0)
