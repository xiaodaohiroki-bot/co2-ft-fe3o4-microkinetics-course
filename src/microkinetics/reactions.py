"""Reaction and species data structures for course examples."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Species:
    """A gas or surface species with elemental composition and site count."""

    name: str
    composition: dict[str, int] = field(default_factory=dict)
    sites: int = 0


@dataclass(frozen=True)
class Reaction:
    """Elementary reaction with stoichiometric coefficients."""

    label: str
    stoichiometry: dict[str, int]
    reversible: bool = True

    def net_site_count(self, species: dict[str, Species]) -> int:
        return sum(coeff * species[name].sites for name, coeff in self.stoichiometry.items())

    def net_element_count(self, species: dict[str, Species]) -> dict[str, int]:
        elements: dict[str, int] = {}
        for name, coeff in self.stoichiometry.items():
            for element, count in species[name].composition.items():
                elements[element] = elements.get(element, 0) + coeff * count
        return {element: count for element, count in elements.items() if count != 0}
