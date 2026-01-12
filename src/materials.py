# src/materials.py
# OOP implementation of material definitions for structural analysis.

from concreteproperties import (
    Concrete,
    ConcreteLinear,
    RectangularStressBlock,
    SteelBar,
    SteelElasticPlastic,
)


# EXEMPLE MATERIALS PRESENTED BELOW. USER CAN DEFINE OTHER MATERIALS AS NEEDED.
concrete = Concrete(
    name="40 MPa Concrete",
    density=2.4e-6,
    stress_strain_profile=ConcreteLinear(elastic_modulus=32.8e3),
    ultimate_stress_strain_profile=RectangularStressBlock(
        compressive_strength=40,
        alpha=0.79,
        gamma=0.87,
        ultimate_strain=0.003,
    ),
    flexural_tensile_strength=3.8,
    colour="lightgrey",
)

steel = SteelBar(
    name="500 MPa Steel",
    density=7.85e-6,
    stress_strain_profile=SteelElasticPlastic(
        yield_strength=500,
        elastic_modulus=200e3,
        fracture_strain=0.05,
    ),
    colour="grey",
)

# CORRECT USAGE , WILL BE USED IN THE FUTURE
# --- Concrete Materials Library ---

# Concrete C25 (NBR 6118)
