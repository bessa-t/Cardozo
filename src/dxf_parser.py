# src/dxf_parser.py
# OOP implementation of a DXF parser with built-in normalization.

import ezdxf

class DXFParser:
    """
    Parses a DXF file to extract and normalize geometry for structural analysis.
    """
    def __init__(self, dxf_filepath: str):
        """Initializes the parser, loads the doc, and finds the geometry offset."""
        try:
            self.doc = ezdxf.readfile(dxf_filepath)
        except (FileNotFoundError, ezdxf.DXFError) as e:
            raise ValueError(f"Could not read DXF file: {dxf_filepath}!")
        else:
            print(f"DXF file '{dxf_filepath}' loaded successfully.")

        self.msp = self.doc.modelspace()


    def parse(self):
        """Extracts and normalizes geometry from the DXF file."""
        self.concrete = []
        self.steel_bars = []
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
               
        if len(self.concrete) >2:
            raise ValueError("More than two polylines found. Only concrete sections with one hole are allowed.")
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
                raise ValueError("Concrete sections should be represented as polylines, not circles.")
        return self.concrete, self.steel_bars
    
test = DXFParser("/home/tarso/projects/biaxal_bending/Biaxial-Bending-Diagram/dxf_files/section 7.dxf")
print(test.parse())
# Future improvements:
# - Cases with multiple holes
# - Section doesnt have to be pre-normalized
# - More robust error handling and reporting
