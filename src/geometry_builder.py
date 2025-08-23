# src/geometry_builder.py
# OOP implementation of a geometry builder that constructs section objects from raw data.

import math
from shapely import Polygon
from sectionproperties.pre.geometry import Geometry
from concreteproperties import Concrete, Steel, SteelBar

class GeometryBuilder:
    """
    Builds geometry objects from raw data for structural analysis.
    """
    def __init__(self):
        pass
    def concrete_section(self,raw_data:dict):

        concrete_data = raw_data.get("concrete_data")

        if not concrete_data:
            raise ValueError("Concrete section data is missing.")
        
        """Finding Exterior and Interior sections"""

        exterior_section = None
        max_area = 0.0
        sections = []
        for section in concrete_data:
            poly = Polygon(section)
            temp_polygon = Geometry(geom=poly)
            if temp_polygon.area > max_area:
                max_area = temp_polygon.area
                exterior_section = temp_polygon
            sections.append(temp_polygon)
        """Holes are treated as a list of sections for future complex geometries to be implemented"""
        holes_list = [sec for sec in sections if sec is not exterior_section]
        
       
                
        concrete_section = {"main-section" : exterior_section, 
                           "hole-sections": holes_list
          }     
        return concrete_section

