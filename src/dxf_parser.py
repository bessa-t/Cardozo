# src/dxf_parser.py
# OOP implementation of a DXF parser with built-in normalization.

import ezdxf
from sectionproperties.pre.geometry import Geometry
from concreteproperties import SteelBar
from typing import List

class DXFParser:
    """
    Parses a DXF file to extract and normalize geometry for structural analysis.
    """
    def __init__(self, dxf_filepath: str):
        """Initializes the parser, loads the doc, and finds the geometry offset."""
        self.doc = ezdxf.readfile(dxf_filepath)
        self.modelspace = self.doc.modelspace()
        self.offset = (0, 0) # Will be calculated by _find_global_offset
        self.all_polylines = []
        self.all_circles = []
        self._find_global_offset() # Calculate offset upon initialization
        print(f"DXF loaded. Geometry offset found: ({self.offset[0]:.2f}, {self.offset[1]:.2f})")

    def _find_global_offset(self):
        """
        Private method to find the bottom-left corner of all entities
        in the DXF to determine the global offset.
        """
        all_points = []
        
        # Gather points from all polylines
        self.all_polylines = list(self.modelspace.query('LWPOLYLINE'))
        for poly in self.all_polylines:
            all_points.extend(list(poly.points()))
            
        # Gather bounding box points from all circles
        self.all_circles = list(self.modelspace.query('CIRCLE'))
        for circle in self.all_circles:
            center = circle.dxf.center
            radius = circle.dxf.radius
            all_points.append((center.x - radius, center.y - radius))
            all_points.append((center.x + radius, center.y + radius))

        if not all_points:
            return

        min_x = min(p[0] for p in all_points)
        min_y = min(p[1] for p in all_points)
        self.offset = (min_x, min_y)

    def get_concrete_geometry(self, layer: str, material) -> Geometry:
        """
        Extracts, normalizes, and returns the concrete geometry with holes.
        """
        concrete_polys_vertices = [
            list(poly.points()) for poly in self.all_polylines if poly.dxf.layer == layer
        ]
        
        # Normalize the vertices using the pre-calculated offset
        normalized_polys = [
            [(p[0] - self.offset[0], p[1] - self.offset[1]) for p in poly]
            for poly in concrete_polys_vertices
        ]

        # Logic to find exterior and holes from normalized polygons
        exterior_points = max(normalized_polys, key=lambda p: Geometry.from_points(p).area)
        holes_points_list = [p for p in normalized_polys if p is not exterior_points]
        
        return Geometry(exterior=exterior_points, holes=holes_points_list, material=material)

    def get_steel_bars(self, layer: str, steel_material) -> List[SteelBar]:
        """
        Extracts, normalizes, and returns a list of SteelBar objects.
        """
        steel_bars = []
        rebar_circles = [c for c in self.all_circles if c.dxf.layer == layer]

        for circle in rebar_circles:
            center = circle.dxf.center
            radius = circle.dxf.radius
            
            # Normalize the center coordinates
            norm_x = center.x - self.offset[0]
            norm_y = center.y - self.offset[1]
            
            steel_bars.append(
                SteelBar(area=3.14159 * radius**2, material=steel_material, x=norm_x, y=norm_y)
            )
        return steel_bars