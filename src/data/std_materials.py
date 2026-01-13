# src/data/materials_library.py

"""
Material Definitions Library for Hyperion (Cardozo).

This module contains pre-defined material objects (Concrete and Steel) 
compliant with the Brazilian Standard NBR 6118:2014.

Dependencies:
    - concreteproperties: Used to define constitutive laws (stress-strain).
"""

from concreteproperties import (
    Concrete,
    ConcreteLinear,
    RectangularStressBlock,
    SteelBar,
    SteelElasticPlastic,
)

# ==============================================================================
# 1. CONCRETE DEFINITIONS (NBR 6118:2014)
# ==============================================================================
# Technical Notes:
# - Units: N (Force), mm (Length), MPa (Stress).
# - Density: 2400 kg/m³ -> 2.4e-6 kg/mm³.
# - Aggregate Type: Granite/Gneiss (Alpha_E = 1.0) assumed for E_cs calculation.
# - Constitutive Model: Idealized Parabola-Rectangle for ULS Design.
# - Parameters for Rectangular Block (f_ck <= 50 MPa):
#     - alpha (Rusch effect): 0.85
#     - gamma (Lambda/Depth factor): 0.80
#     - ultimate_strain (Flexure): 0.0035 (3.5 per mil)

# --- C20 (20 MPa) ---
concrete_c20 = Concrete(
    name="Concrete C20 (NBR 6118)",
    density=2.4e-6,
    stress_strain_profile=ConcreteLinear(elastic_modulus=21300),  # E_cs approx.
    ultimate_stress_strain_profile=RectangularStressBlock(
        compressive_strength=20,
        alpha=0.85,
        gamma=0.80,
        ultimate_strain=0.0035,
    ),
    flexural_tensile_strength=2.2,
    colour="lightgrey",
)

# --- C25 (25 MPa) ---
concrete_c25 = Concrete(
    name="Concrete C25 (NBR 6118)",
    density=2.4e-6,
    stress_strain_profile=ConcreteLinear(elastic_modulus=24100),
    ultimate_stress_strain_profile=RectangularStressBlock(
        compressive_strength=25,
        alpha=0.85,
        gamma=0.80,
        ultimate_strain=0.0035,
    ),
    flexural_tensile_strength=2.6,
    colour="lightgrey",
)

# --- C30 (30 MPa) ---
concrete_c30 = Concrete(
    name="Concrete C30 (NBR 6118)",
    density=2.4e-6,
    stress_strain_profile=ConcreteLinear(elastic_modulus=26800),
    ultimate_stress_strain_profile=RectangularStressBlock(
        compressive_strength=30,
        alpha=0.85,
        gamma=0.80,
        ultimate_strain=0.0035,
    ),
    flexural_tensile_strength=2.9,
    colour="grey",
)

# --- C35 (35 MPa) ---
concrete_c35 = Concrete(
    name="Concrete C35 (NBR 6118)",
    density=2.4e-6,
    stress_strain_profile=ConcreteLinear(elastic_modulus=29400),
    ultimate_stress_strain_profile=RectangularStressBlock(
        compressive_strength=35,
        alpha=0.85,
        gamma=0.80,
        ultimate_strain=0.0035,
    ),
    flexural_tensile_strength=3.2,
    colour="grey",
)

# --- C40 (40 MPa) ---
concrete_c40 = Concrete(
    name="Concrete C40 (NBR 6118)",
    density=2.4e-6,
    stress_strain_profile=ConcreteLinear(elastic_modulus=31900),
    ultimate_stress_strain_profile=RectangularStressBlock(
        compressive_strength=40,
        alpha=0.85,
        gamma=0.80,
        ultimate_strain=0.0035,
    ),
    flexural_tensile_strength=3.5,
    colour="darkgrey",
)

# --- C50 (50 MPa) ---
concrete_c50 = Concrete(
    name="Concrete C50 (NBR 6118)",
    density=2.4e-6,
    stress_strain_profile=ConcreteLinear(elastic_modulus=36600),
    ultimate_stress_strain_profile=RectangularStressBlock(
        compressive_strength=50,
        alpha=0.85,
        gamma=0.80,
        ultimate_strain=0.0035,
    ),
    flexural_tensile_strength=4.1,
    colour="darkgrey",
)

# ==============================================================================
# 2. STEEL DEFINITIONS (NBR 6118:2014)
# ==============================================================================
# Technical Notes:
# - Modulus of Elasticity (Es): 210 GPa (210,000 MPa)
# - Behavior: Elastic-Perfectly Plastic (Yield Plateau)
# - Fracture Strain: Limited to 5% (0.05) for safety/ductility in analysis.

# --- CA-50 (500 MPa) ---
steel_ca50 = SteelBar(
    name="Steel CA-50 (NBR 6118)",
    density=7.85e-6,
    stress_strain_profile=SteelElasticPlastic(
        yield_strength=500,
        elastic_modulus=210000,
        fracture_strain=0.05,
    ),
    colour="red",
)

# --- CA-60 (600 MPa) ---
steel_ca60 = SteelBar(
    name="Steel CA-60 (NBR 6118)",
    density=7.85e-6,
    stress_strain_profile=SteelElasticPlastic(
        yield_strength=600,
        elastic_modulus=210000,
        fracture_strain=0.05,
    ),
    colour="orange",
)

# ==============================================================================
# 3. EXPORT LIBRARIES
# ==============================================================================
# These dictionaries are imported by the Frontend (GUI) to populate dropdowns.
# Key (String): The name displayed to the user.
# Value (Object): The actual material object used for calculation.

CONCRETE_LIBRARY = {
    "C20 (NBR 6118)": concrete_c20,
    "C25 (NBR 6118)": concrete_c25,
    "C30 (NBR 6118)": concrete_c30,
    "C35 (NBR 6118)": concrete_c35,
    "C40 (NBR 6118)": concrete_c40,
    "C50 (NBR 6118)": concrete_c50,
}

STEEL_LIBRARY = {
    "CA-50 (500 MPa)": steel_ca50,
    "CA-60 (600 MPa)": steel_ca60,
}