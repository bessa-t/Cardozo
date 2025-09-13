import os
import matplotlib.pyplot as plt
import numpy as np
from geometry_builder import GeometryBuilder
from dxf_parser import DXFParser
from materials import concrete, steel

parser = DXFParser("/home/tarso/projects/biaxal_bending/Biaxial-Bending-Diagram/dxf_files/section 7.dxf")
builder = GeometryBuilder()
print("===================================================")
builder.build_section(parser.parse(),concrete,steel)
print("===================================================")
#print(test2.concrete_section(dxf_parser.test))