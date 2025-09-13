# src/geometry_builder.py
# OOP implementation of a geometry builder that constructs section objects from raw data.
import math
from shapely import Polygon
from sectionproperties.pre.geometry import Geometry
from sectionproperties.analysis import Section
from concreteproperties import (
    Concrete, 
    Steel, 
    SteelBar,
    ConcreteSection,
    add_bar
)


class GeometryBuilder:
    """
    Builds geometry objects from raw data for structural analysis.
    """
    def __init__(self):
        pass
    def _build_concrete_section(self,raw_data:dict):

        concrete_data = raw_data.get("concrete_data")

        if not concrete_data:
            raise ValueError("Concrete section data is missing.")
        
        """Finding Exterior and Interior sections"""

        exterior_section = None
        max_area = 0.0
        sections = []
        for section in concrete_data:
            poly = Polygon(section)
            if poly.area > max_area:
                max_area = poly.area
                exterior_section = poly
            sections.append(poly)

        holes_list = [sec for sec in sections if sec is not exterior_section]
        
       
                
        concrete_section = {"main-section" : exterior_section, 
                           "hole-sections": holes_list
          }     
        
        return concrete_section 
    
    def build_section(self,raw_data:dict,concrete_material:Concrete,steel_material:SteelBar):
        #Steel Bars
        steel_bars_data = raw_data.get("steel_bars_data",[])
        if not steel_bars_data:
            raise ValueError("Steel bars data is missing.")
        steel_bars_list = raw_data.get("steel_bars_data")

        #Concrete Section
        concrete_section = self._build_concrete_section(raw_data)
        outer = Geometry(concrete_section["main-section"], material=concrete_material)
        geom = outer
        for hole in concrete_section["hole-sections"]:
            geom = geom - Geometry(hole)


        #Adding Steel Bars
        final_concrete_geometry = geom
        composite_geometry = final_concrete_geometry

        for bar in steel_bars_list:
            x,y = bar["center"]
            area = math.pi * bar["radius"]**2

            composite_geometry = add_bar(
                geometry= composite_geometry,
                area=area,
                material=steel_material,
                x=x,
                y=y,
                n =16)
        final_reinforced_section = ConcreteSection(geometry=composite_geometry)
        return final_reinforced_section
        

        

    

    