import ezdxf
import os
# Getting dxf file path across different directories.
script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
project_root = os.path.dirname(script_dir)

filename = "teste seção 7.dxf"
dxf_folder = "dxf_files"
dxf_path = os.path.join(project_root,dxf_folder,filename)
print(dxf_path)
#