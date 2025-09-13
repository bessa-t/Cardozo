import os
import matplotlib.pyplot as plt
import numpy as np
from geometry_builder import GeometryBuilder
from dxf_parser import DXFParser
from materials import concrete, steel

parser = DXFParser("/home/tarso/projects/biaxal_bending/Biaxial-Bending-Diagram/dxf_files/section 7.dxf")
builder = GeometryBuilder()
section= builder.build_section(parser.parse(),concrete,steel)

#testando

bb_res =section.biaxial_bending_diagram(n_points=24, progress_bar=False)

bb_res.plot_diagram(eng=True)

plt.show()