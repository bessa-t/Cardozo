# src/backend/dxf_parser.py

import ezdxf
from dataclasses import dataclass
from typing import List, Tuple, Dict

# --- DTO Definition (Data Transfer Object) --
@dataclass
class ParsedSteelBar:
    """
    Represents the geometric data of a steel bar extracted from the DXF.
    
    Attributes:
        center (Tuple[float, float]): The (x, y) coordinates of the bar's center.
        radius (float): The radius of the bar in the same units as the DXF file.
    """
    center: Tuple[float, float]
    radius: float

@dataclass
class ParsedGeometry:
    """
    Strictly defines the data structure returned by the parser.
    Used for type-checking and autocompletion in the main application.
    """
    concrete_polygons: List[List[Tuple[float, float]]]
    steel_bars: List[ParsedSteelBar]

# --- Main Parser Class ---
class DXFParser:
    """
    Parses a DXF file to extract and normalize geometry for structural analysis.
    Implements a filtering mechanism to ignore non-structural layers.
    """
    # Constants for layer names (Avoids Magic Strings)
    LAYER_CONCRETE = "concrete"
    LAYER_STEEL = "steel bars"

    def __init__(self, dxf_filepath: str):
        """
        Initializes the DXF parser.
        
        Args:
            dxf_filepath: Absolute or relative path to the .dxf file.
        """
        try: 
            self.doc = ezdxf.readfile(dxf_filepath)
        except IOError:
             # IOError covers FileNotFoundError and permission issues
            raise FileNotFoundError(f"File not found or not accessible: {dxf_filepath}")
        except ezdxf.DXFError as e:
            raise ValueError(f"Corrupted or invalid DXF file: {e}")
            
        self.msp = self.doc.modelspace()

    def parse(self) -> ParsedGeometry:
        """
        Iterates over DXF entities and extracts structural geometry.
        
        Returns:
            ParsedGeometry: An object containing clean lists of concrete and steel elements.
        """
        concrete_polygons = []
        steel_bars = []

        # 1. Process Polylines (Expected: Concrete Boundaries)
        for polyline in self.msp.query('LWPOLYLINE'):
            layer = polyline.dxf.layer.lower()

            if layer == self.LAYER_CONCRETE:
                if not polyline.is_closed:
                    raise ValueError(f"Geometry Error: Concrete polyline on layer '{layer}' must be CLOSED.")
                
                # Extract X, Y points and cast to float
                points = [(float(v[0]), float(v[1])) for v in polyline.get_points()]
                concrete_polygons.append(points)

            elif layer == self.LAYER_STEEL:
                raise ValueError(f"Validation Error: Found Polyline on '{self.LAYER_STEEL}'. Steel bars must be CIRCLES.")
            
            # Note: Other layers are implicitly ignored.

        # 2. Process Circles (Expected: Steel Bars)
        for circle in self.msp.query('CIRCLE'):
            layer = circle.dxf.layer.lower()

            if layer == self.LAYER_STEEL:
                c_x = float(circle.dxf.center.x)
                c_y = float(circle.dxf.center.y)
                r   = float(circle.dxf.radius)

                new_bar = ParsedSteelBar(center=(c_x, c_y), radius=r)
                steel_bars.append(new_bar)

            elif layer == self.LAYER_CONCRETE:
                raise ValueError(f"Validation Error: Found Circle on '{self.LAYER_CONCRETE}'. Concrete must be POLYLINES.")

        # 3. Post-Parsing Validation
        if not concrete_polygons:
            raise ValueError(f"Input Error: No geometry found on layer '{self.LAYER_CONCRETE}'.")
        
        if len(concrete_polygons) > 2:
            raise ValueError("Topology Error: More than 2 concrete polygons found. Only single or hollow sections supported.")

        return ParsedGeometry(
            concrete_polygons=concrete_polygons,
            steel_bars=steel_bars
        )
    

# Future improvements:
# - Cases with multiple holes
# - Section doesnt have to be pre-normalized
# - More robust error handling and reporting
