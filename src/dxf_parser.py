# src/dxf_parser.py
# OOP implementation of a DXF parser with built-in normalization.

import ezdxf
from typing import List

class DXFParser:
    """
    Parses a DXF file to extract and normalize geometry for structural analysis.
    """
    def __init__(self, dxf_filepath: str):
        """Initializes the parser, loads the doc, and finds the geometry offset."""
        try:
            self.doc = ezdxf.readfile(dxf_filepath)
        except:
            raise ValueError(f"Could not read DXF file: {dxf_filepath}!")
        else:
            print(f"DXF file '{dxf_filepath}' loaded successfully.")

        self.msp = self.doc.modelspace()

        self.polylines = [] 
        self.circles = [] 
        self.concrete = []
        self.steel_bars = []

    def parse(self):
        """Extracts and normalizes geometry from the DXF file."""
        # Query entities by layer names
        polyline_query = self.msp.query('LWPOLYLINE')
        circle_query = self.msp.query('CIRCLE')

        for polyline in polyline_query:
            layer = polyline.dxf.layer.lower()
            if not polyline.is_closed:
                raise ValueError("All polylines must be closed.")
            
            if layer == "concrete":
                raw_vertices = list(polyline.get_points())
                cleaned_vertices = [(float(vertex[0]), float(vertex[1])) for vertex in raw_vertices]
                self.concrete.append(cleaned_vertices)

            if layer == "steel bars":
                raise ValueError("Steel bars should be represented as circles, not polylines.")
            if  layer != "concrete" and layer != "steel bars":
                raise ValueError("Invalid layer found. Required layers are 'concrete' or 'steel bars'.")
            
        for circle in circle_query:
            layer = circle.dxf.layer.lower()

            if layer != "concrete" and layer != "steel bars":
                raise ValueError("Invalid layer found. Required layers are 'concrete' or 'steel bars'.")
            circle_data = {
                'center': (circle.dxf.center.x, circle.dxf.center.y),
                'radius': circle.dxf.radius
            }
        
            if layer == "steel bars":
                self.steel_bars.append(circle_data)

            if layer == "concrete":
                self.concrete.append(circle_data)
        print("=======================================================")
        print(self.concrete)
        print(len(self.concrete))
test = DXFParser("/home/tarso/projects/biaxal_bending/Biaxial-Bending-Diagram/dxf_files/section 7.dxf")
test.parse()
