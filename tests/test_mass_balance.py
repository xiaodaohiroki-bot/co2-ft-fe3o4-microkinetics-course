import unittest

from tests.test_site_balance import REACTIONS, SPECIES


class MassBalanceTest(unittest.TestCase):
    def test_minimal_rwgs_network_conserves_elements(self):
        for reaction in REACTIONS:
            with self.subTest(reaction=reaction.label):
                self.assertEqual(reaction.net_element_count(SPECIES), {})
