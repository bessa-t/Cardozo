import os
from geometry_builder import GeometryBuilder
from dxf_parser import DXFParser

parser = DXFParser("/home/tarso/projects/biaxal_bending/Biaxial-Bending-Diagram/dxf_files/section 7.dxf")

builder = GeometryBuilder()
print("===================================================")
builder.concrete_section(parser.parse())
print("===================================================")
#print(test2.concrete_section(dxf_parser.test))