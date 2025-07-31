from sectionproperties.pre import Geometry

# the following path is a .dxf file that describes a box section with two holes
dxf_path = "/home/tarso/projects/flexão_composta/dxf_files/teste seção 7.dxf"

# load dxf file into a Geometry object
geom = Geometry.from_dxf(dxf_filepath=dxf_path)
geom.plot_geometry()