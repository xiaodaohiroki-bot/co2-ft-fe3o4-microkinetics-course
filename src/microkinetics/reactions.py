"""Reaction and mechanism data structures for Fe3O4-RWGS examples."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any, Mapping

import yaml

from .species import Species, make_species


@dataclass(frozen=True, init=False)
class Reaction:
    """Elementary reaction with metadata and stoichiometric coefficients."""

    id: str
    equation: str
    type: str
    reversible: bool
    description: str
    stoichiometry: dict[str, int]

    def __init__(
        self,
        id: str,
        equation: str | Mapping[str, int] | None = None,
        type: str = "surface_reaction",
        reversible: bool = True,
        description: str = "",
        stoichiometry: Mapping[str, int] | None = None,
    ) -> None:
        # Backward-compatible form: Reaction("label", {"A": -1, "B": 1})
        if isinstance(equation, Mapping) and stoichiometry is None:
            stoichiometry = equation
            equation = ""

        equation_text = str(equation or "")
        parsed = parse_stoichiometry(equation_text) if stoichiometry is None and equation_text else {}
        object.__setattr__(self, "id", id)
        object.__setattr__(self, "equation", equation_text)
        object.__setattr__(self, "type", type)
        object.__setattr__(self, "reversible", bool(reversible))
        object.__setattr__(self, "description", description)
        object.__setattr__(self, "stoichiometry", dict(stoichiometry or parsed))

    @property
    def label(self) -> str:
        """Compatibility alias used by earlier tests."""

        return self.id

    def net_site_count(self, species: Mapping[str, Species]) -> int:
        return sum(coeff * species[name].sites for name, coeff in self.stoichiometry.items())

    def net_element_count(self, species: Mapping[str, Species]) -> dict[str, int]:
        elements: dict[str, int] = {}
        for name, coeff in self.stoichiometry.items():
            for element, count in species[name].composition.items():
                elements[element] = elements.get(element, 0) + coeff * count
        return {element: count for element, count in elements.items() if count != 0}


@dataclass(frozen=True)
class Mechanism:
    """A microkinetic mechanism with gas species, surface species, and reactions."""

    name: str
    gas_species: dict[str, Species]
    surface_species: dict[str, Species]
    reactions: list[Reaction] = field(default_factory=list)
    version: str | None = None
    description: str = ""

    @property
    def species(self) -> dict[str, Species]:
        return {**self.gas_species, **self.surface_species}

    def reaction_by_id(self, reaction_id: str) -> Reaction:
        for reaction in self.reactions:
            if reaction.id == reaction_id:
                return reaction
        raise KeyError(f"Unknown reaction id: {reaction_id}")


def load_mechanism_yaml(path: str | Path) -> Mechanism:
    """Load a mechanism YAML file into Python data structures."""

    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return mechanism_from_mapping(data)


def mechanism_from_mapping(data: Mapping[str, Any]) -> Mechanism:
    gas_species = {
        name: make_species(name, "gas")
        for name in _require_list(data, "gas_species")
    }
    surface_species = {
        name: make_species(name, "surface")
        for name in _require_list(data, "surface_species")
    }
    reactions = [
        Reaction(
            id=str(item["id"]),
            equation=str(item["equation"]),
            type=str(item["type"]),
            reversible=bool(item.get("reversible", True)),
            description=str(item.get("description", "")),
        )
        for item in _require_list(data, "reactions")
    ]
    return Mechanism(
        name=str(data["name"]),
        version=str(data["version"]) if data.get("version") is not None else None,
        description=str(data.get("description", "")),
        gas_species=gas_species,
        surface_species=surface_species,
        reactions=reactions,
    )


def parse_stoichiometry(equation: str) -> dict[str, int]:
    """Parse a simple reversible reaction equation into net stoichiometry."""

    if "<=>" in equation:
        left, right = equation.split("<=>", 1)
    elif "->" in equation:
        left, right = equation.split("->", 1)
    else:
        raise ValueError(f"Unsupported reaction equation: {equation}")

    stoichiometry: dict[str, int] = {}
    for species, coeff in _parse_side(left, sign=-1).items():
        stoichiometry[species] = stoichiometry.get(species, 0) + coeff
    for species, coeff in _parse_side(right, sign=1).items():
        stoichiometry[species] = stoichiometry.get(species, 0) + coeff
    return {species: coeff for species, coeff in stoichiometry.items() if coeff != 0}


def _parse_side(side: str, sign: int) -> dict[str, int]:
    terms: dict[str, int] = {}
    for raw_term in side.split("+"):
        term = raw_term.strip()
        if not term:
            continue
        match = re.fullmatch(r"(?:(\d+)\s*)?(.+)", term)
        if match is None:
            raise ValueError(f"Could not parse reaction term: {term}")
        coeff = int(match.group(1) or "1")
        species = match.group(2).strip()
        terms[species] = terms.get(species, 0) + sign * coeff
    return terms


def _require_list(data: Mapping[str, Any], key: str) -> list[Any]:
    value = data.get(key)
    if not isinstance(value, list):
        raise ValueError(f"Expected YAML key '{key}' to contain a list.")
    return value
