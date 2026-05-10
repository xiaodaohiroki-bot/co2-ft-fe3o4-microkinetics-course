"""Species data structures for Fe3O4-RWGS mechanisms."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

SpeciesPhase = Literal["gas", "surface"]


@dataclass(frozen=True, init=False)
class Species:
    """A gas or surface species used in a microkinetic mechanism."""

    name: str
    phase: SpeciesPhase
    composition: dict[str, int] = field(default_factory=dict)
    sites: int = 0

    def __init__(
        self,
        name: str,
        phase: SpeciesPhase | dict[str, int] = "gas",
        composition: dict[str, int] | None = None,
        sites: int = 0,
    ) -> None:
        # Backward-compatible form: Species("CO2", {"C": 1, "O": 2}, sites=0)
        if isinstance(phase, dict):
            inferred_phase: SpeciesPhase = "surface" if name.endswith("*") or name == "*" else "gas"
            composition_value = phase
        else:
            inferred_phase = phase
            composition_value = composition or {}

        object.__setattr__(self, "name", name)
        object.__setattr__(self, "phase", inferred_phase)
        object.__setattr__(self, "composition", dict(composition_value))
        object.__setattr__(self, "sites", int(sites))

    @property
    def is_gas(self) -> bool:
        return self.phase == "gas"

    @property
    def is_surface(self) -> bool:
        return self.phase == "surface"


DEFAULT_COMPOSITIONS: dict[str, dict[str, int]] = {
    "*": {},
    "CO2": {"C": 1, "O": 2},
    "H2": {"H": 2},
    "CO": {"C": 1, "O": 1},
    "H2O": {"H": 2, "O": 1},
    "CO2*": {"C": 1, "O": 2},
    "H*": {"H": 1},
    "CO*": {"C": 1, "O": 1},
    "O*": {"O": 1},
    "OH*": {"O": 1, "H": 1},
    "H2O*": {"H": 2, "O": 1},
}


def make_species(name: str, phase: SpeciesPhase) -> Species:
    """Create a Species with known default composition and site count."""

    sites = 1 if phase == "surface" else 0
    return Species(
        name=name,
        phase=phase,
        composition=dict(DEFAULT_COMPOSITIONS.get(name, {})),
        sites=sites,
    )
