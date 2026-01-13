# src/backend/geometry_builder.py

import math
from typing import Dict, List
from shapely.geometry import Polygon
from sectionproperties.pre.geometry import Geometry
from concreteproperties import (
    Concrete,  
    SteelBar,
    ConcreteSection,
    add_bar
)

# Local import from your data structure definitions
from backend.dxf_parser import ParsedGeometry

class GeometryBuilder:
    """
    Builds engineering geometry objects from parsed raw data for structural analysis.
    Acts as a bridge between the DXF Parser and the Analysis Engine.
    """

    def __init__(self):
        pass

    def _build_concrete_section(self, raw_data: ParsedGeometry) -> Dict[str, any]:
        """
        Internal method to process concrete boundaries.
        Identifies the exterior boundary (largest area) and treats others as voids.
        """
        
        # Accessing data via Attribute (Dot notation) instead of Dictionary Key
        polygons_coords = raw_data.concrete_polygons

        if not polygons_coords:
            raise ValueError("Concrete section data is missing in the parsed object.")
        
        # Convert all coordinate lists to Shapely Polygons first
        # This allows us to access geometric properties like .area immediately
        all_polygons = [Polygon(pts) for pts in polygons_coords]

        # Logic: The exterior section is always the one with the largest area.
        # We use the max() function with a key argument for efficiency and readability.
        exterior_section = max(all_polygons, key=lambda p: p.area)

        # Logic: Any polygon that is not the exterior is considered a hole/void.
        holes_list = [p for p in all_polygons if p is not exterior_section]
                
        return {
            "main-section": exterior_section, 
            "hole-sections": holes_list
        }     
    
    def build_section(self, 
                      raw_data: ParsedGeometry, 
                      concrete_material: Concrete, 
                      steel_material: SteelBar) -> ConcreteSection:
        """
        Main method to construct the final reinforced concrete section.
        Combines concrete geometry (with voids) and steel bars.
        """

        # --- 1. Processing Concrete ---
        concrete_dict = self._build_concrete_section(raw_data)
        
        # Create the main geometry with material properties
        base_geometry = Geometry(concrete_dict["main-section"], material=concrete_material)
        
        # Subtract holes from the main geometry
        final_concrete_geometry = base_geometry
        for hole in concrete_dict["hole-sections"]:
            final_concrete_geometry = final_concrete_geometry - Geometry(hole)

        # --- 2. Processing Steel Bars ---
        # Accessing the list of steel objects from the Data Class
        steel_bars_list = raw_data.steel_bars
        
        if not steel_bars_list:
            raise ValueError("Steel bars data is missing.")

        # Initialize composite geometry
        composite_geometry = final_concrete_geometry

        for bar in steel_bars_list:
            # CRITICAL UPDATE: Using Dot Notation for Object Access
            # Old way (Dict): x, y = bar["center"]
            # New way (Object): We assume the object has a .center attribute (tuple)
            # If your object has .x and .y separately, adjust to: x = bar.x; y = bar.y
            x, y = bar.center 
            
            # Using Dot Notation for radius
            area = math.pi * (bar.radius ** 2)

            composite_geometry = add_bar(
                geometry=composite_geometry,
                area=area,
                material=steel_material,
                x=x,
                y=y,
                n=16  # Discretization for visualization
            )
            
        # --- 3. Final Assembly ---
        final_reinforced_section = ConcreteSection(geometry=composite_geometry)
        
        return final_reinforced_section