import customtkinter as ctk
import os
from tkinter import filedialog

# Imports the material dictionaries to populate the dropdowns
# Certifique-se de que seu arquivo de materiais está em src/data/std_materials.py
# ou ajuste o import abaixo para: from data.materials_library import ...
try:
    from data.std_materials import CONCRETE_LIBRARY, STEEL_LIBRARY
except ImportError:
    # Fallback caso o arquivo ainda não esteja criado corretamente, para não travar a janela
    CONCRETE_LIBRARY = {"C25 (Demo)": None}
    STEEL_LIBRARY = {"CA-50 (Demo)": None}

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Window Setup
        self.title("Hyperion - Biaxial Bending Analysis")
        self.geometry("1100x650")
        
        # Define grid layout (2 columns: Sidebar | Main Content)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 2. UI Initialization
        self.create_sidebar()
        self.create_main_area()

    def create_sidebar(self):
        """Creates the left sidebar with controls."""
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1) # Pushes footer to bottom

        # --- Header ---
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="HYPERION", 
                                       font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # --- Section 1: Material Selection ---
        self.lbl_concrete = ctk.CTkLabel(self.sidebar_frame, text="Concrete Class:", anchor="w")
        self.lbl_concrete.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.concrete_option = ctk.CTkOptionMenu(self.sidebar_frame, 
                                                 values=list(CONCRETE_LIBRARY.keys()))
        self.concrete_option.grid(row=2, column=0, padx=20, pady=5)
        
        self.lbl_steel = ctk.CTkLabel(self.sidebar_frame, text="Steel Grade:", anchor="w")
        self.lbl_steel.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.steel_option = ctk.CTkOptionMenu(self.sidebar_frame, 
                                              values=list(STEEL_LIBRARY.keys()))
        self.steel_option.grid(row=4, column=0, padx=20, pady=5)

        # --- Section 2: File Input ---
        self.lbl_file = ctk.CTkLabel(self.sidebar_frame, text="Geometry (DXF):", anchor="w")
        self.lbl_file.grid(row=5, column=0, padx=20, pady=(20, 0), sticky="w")

        # Entry box to show path
        self.path_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="No file selected")
        self.path_entry.grid(row=6, column=0, padx=20, pady=5)

        # Button to choose file
        self.btn_browse = ctk.CTkButton(self.sidebar_frame, text="Load DXF File", 
                                        command=self.open_dxf_file)
        self.btn_browse.grid(row=7, column=0, padx=20, pady=10, sticky="n")

        # --- Footer: Calculate Button ---
        self.btn_calculate = ctk.CTkButton(self.sidebar_frame, text="CALCULATE", 
                                           fg_color="green", hover_color="darkgreen",
                                           command=self.calculate_event)
        self.btn_calculate.grid(row=8, column=0, padx=20, pady=20)

    def create_main_area(self):
        """Creates the right area with tabs for Geometry and Results."""
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.tab_geometry = self.tab_view.add("Geometry Preview")
        self.tab_results = self.tab_view.add("Interaction Diagram")

        # Placeholder Text
        self.lbl_placeholder = ctk.CTkLabel(self.tab_geometry, 
                                            text="Load a DXF file to view geometry here.")
        self.lbl_placeholder.pack(expand=True)

    # --- Event Handlers (Empty for now) ---
    
    def open_dxf_file(self):
        """Opens file dialog and updates the entry box."""
        filename = filedialog.askopenfilename(title="Select DXF File", 
                                              filetypes=(("DXF Files", "*.dxf"),))
        if filename:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, filename)
            print(f"File Selected: {filename}")

    def calculate_event(self):
        """Connects to Backend (To be implemented)."""
        print("Calculate button clicked!")
        print(f"Material: {self.concrete_option.get()}")
        print(f"File: {self.path_entry.get()}")