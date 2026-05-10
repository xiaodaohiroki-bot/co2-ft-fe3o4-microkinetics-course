"""Thermodynamic helper placeholders for future lessons."""

from __future__ import annotations

R_GAS_CONSTANT = 8.31446261815324


def arrhenius_rate(prefactor: float, activation_energy_j_mol: float, temperature_k: float) -> float:
    """Return an Arrhenius rate constant."""

    if temperature_k <= 0:
        raise ValueError("Temperature must be positive.")
    exponent = -activation_energy_j_mol / (R_GAS_CONSTANT * temperature_k)
    return prefactor * __import__("math").exp(exponent)
