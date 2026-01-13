import customtkinter as ctk
from tkinter import filedialog, messagebox
import webbrowser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# --- BACKEND IMPORTS ---
from backend.dxf_parser import DXFParser
from backend.geometry_builder import GeometryBuilder
from data.std_materials import CONCRETE_LIBRARY, STEEL_LIBRARY

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Main Window Setup
        self.title("Hyperion - Biaxial Bending Analysis")
        self.geometry("1200x800") 
        
        # Grid Configuration: Fixed Sidebar (0), Expandable Content (1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Variables to store chart canvases (references for clearing later)
        self.current_results_canvas = None
        self.current_geometry_canvas = None

        # 2. UI Initialization
        self.create_sidebar()
        self.create_main_area()

    def create_sidebar(self):
        """Creates the left sidebar menu with input controls and credits."""
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        # Push footer to the bottom using row weights
        self.sidebar_frame.grid_rowconfigure(13, weight=1) 

        # --- Header ---
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="HYPERION", 
                                       font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 5))
        
        sub_label = ctk.CTkLabel(self.sidebar_frame, text="Structural Analysis v1.0", 
                                       text_color="gray", font=ctk.CTkFont(size=12))
        sub_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        # --- Section 1: Materials ---
        self.lbl_concrete = ctk.CTkLabel(self.sidebar_frame, text="Concrete Class:", anchor="w")
        self.lbl_concrete.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.concrete_option = ctk.CTkOptionMenu(self.sidebar_frame, 
                                                 values=list(CONCRETE_LIBRARY.keys()))
        self.concrete_option.grid(row=3, column=0, padx=20, pady=5)
        
        # Set default value if library is not empty
        if CONCRETE_LIBRARY:
            self.concrete_option.set(list(CONCRETE_LIBRARY.keys())[2]) 
        
        self.lbl_steel = ctk.CTkLabel(self.sidebar_frame, text="Steel Grade:", anchor="w")
        self.lbl_steel.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.steel_option = ctk.CTkOptionMenu(self.sidebar_frame, 
                                              values=list(STEEL_LIBRARY.keys()))
        self.steel_option.grid(row=5, column=0, padx=20, pady=5)

        # --- Section 2: Loading Inputs ---
        self.lbl_n_force = ctk.CTkLabel(self.sidebar_frame, text="Normal Force (kN):", anchor="w")
        self.lbl_n_force.grid(row=6, column=0, padx=20, pady=(20, 0), sticky="w")

        self.entry_n_force = ctk.CTkEntry(self.sidebar_frame, placeholder_text="0.0")
        self.entry_n_force.grid(row=7, column=0, padx=20, pady=5)

        # --- Section 3: File Input with Help Button ---
        # A small frame to align the label and the help button horizontally
        file_label_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        file_label_frame.grid(row=8, column=0, padx=20, pady=(20, 0), sticky="ew")
        
        self.lbl_file = ctk.CTkLabel(file_label_frame, text="Geometry (DXF):", anchor="w")
        self.lbl_file.pack(side="left")

        # Help Button (?)
        self.btn_help = ctk.CTkButton(file_label_frame, text="?", width=20, height=20,
                                      fg_color="gray", hover_color="gray40",
                                      command=self.show_dxf_help)
        self.btn_help.pack(side="right")

        self.path_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Select .dxf file...")
        self.path_entry.grid(row=9, column=0, padx=20, pady=5)

        self.btn_browse = ctk.CTkButton(self.sidebar_frame, text="Browse File", 
                                        fg_color="transparent", border_width=2,
                                        text_color=("gray10", "#DCE4EE"),
                                        command=self.open_dxf_file)
        self.btn_browse.grid(row=10, column=0, padx=20, pady=5, sticky="n")

        # --- Main Action Button ---
        self.btn_calculate = ctk.CTkButton(self.sidebar_frame, text="RUN ANALYSIS", 
                                           height=50,
                                           fg_color="#106A43", hover_color="#148F5C",
                                           font=ctk.CTkFont(size=14, weight="bold"),
                                           command=self.calculate_event)
        self.btn_calculate.grid(row=11, column=0, padx=20, pady=30, sticky="ew")

        # --- Footer: Credits & Support ---
        self.separator = ctk.CTkFrame(self.sidebar_frame, height=2, fg_color="gray30")
        self.separator.grid(row=14, column=0, sticky="ew", padx=20, pady=10)

        self.lbl_credits = ctk.CTkLabel(self.sidebar_frame, 
                                        text="Developed by Tarso Bessa\nbessatarso@gmail.com", 
                                        font=ctk.CTkFont(size=10), text_color="gray60")
        self.lbl_credits.grid(row=15, column=0, padx=20, pady=(0, 5))

        self.btn_support = ctk.CTkButton(self.sidebar_frame, text="☕ Support Me", 
                                         height=25, fg_color="#FFDD00", text_color="black",
                                         hover_color="#E6C200",
                                         command=self.open_support_link)
        self.btn_support.grid(row=16, column=0, padx=20, pady=(0, 20))

    def create_main_area(self):
        """Creates the right main area with Tabs for Geometry and Results."""
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.tab_geometry = self.tab_view.add("Geometry Preview")
        self.tab_results = self.tab_view.add("Interaction Diagram")
        
        # Configure internal grid weights
        self.tab_results.grid_columnconfigure(0, weight=1)
        self.tab_results.grid_rowconfigure(0, weight=1)
        self.tab_geometry.grid_columnconfigure(0, weight=1)
        self.tab_geometry.grid_rowconfigure(0, weight=1)

        # Initial Placeholders
        self.lbl_placeholder_res = ctk.CTkLabel(self.tab_results, 
                                            text="Interaction Diagram will appear here.",
                                            font=ctk.CTkFont(size=16))
        self.lbl_placeholder_res.grid(row=0, column=0)

        self.lbl_placeholder_geo = ctk.CTkLabel(self.tab_geometry, 
                                            text="Geometry Preview will appear here.",
                                            font=ctk.CTkFont(size=16))
        self.lbl_placeholder_geo.grid(row=0, column=0)

    # --- EVENT HANDLERS ---

    def show_dxf_help(self):
        """Displays a popup with DXF instructions."""
        info_text = (
            "DXF FILE REQUIREMENTS:\n\n"
            "1. UNITS: The file must be drawn in millimeters (mm) or meters.\n"
            "   (The software detects coordinates automatically).\n\n"
            "2. CONCRETE LAYER:\n"
            "   - Draw the concrete perimeter as a closed POLYLINE.\n"
            "   - Layer name must contain 'CONCRETE' or 'PILAR'.\n\n"
            "3. STEEL LAYER:\n"
            "   - Draw rebars as CIRCLES.\n"
            "   - Layer name must contain 'STEEL', 'ACO' or 'ARMADURA'.\n\n"
            "4. ORIGIN: Center the section near (0,0) for better visualization."
        )
        messagebox.showinfo("How to prepare your DXF", info_text)

    def open_support_link(self):
        """Opens the support URL in the default browser."""
        # Replace with your actual support link
        url = "https://www.buymeacoffee.com/tarso" 
        webbrowser.open(url)
    
    def open_dxf_file(self):
        """Opens system file dialog to select the DXF."""
        filename = filedialog.askopenfilename(title="Select DXF Geometry", 
                                              filetypes=(("DXF Files", "*.dxf"), ("All Files", "*.*")))
        if filename:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, filename)

    def calculate_event(self):
        """
        Main Event: Connects inputs to backend logic.
        Validates data, builds geometry, and runs analysis.
        """
        # 1. Collect Input Data
        filepath = self.path_entry.get()
        concrete_name = self.concrete_option.get()
        steel_name = self.steel_option.get()
        n_force_str = self.entry_n_force.get()

        if not filepath:
            messagebox.showwarning("Input Error", "Please select a DXF file first.")
            return

        # Handle Normal Force Input (String to Float conversion)
        try:
            if n_force_str.strip() == "":
                n_force_kn = 0.0
            else:
                n_force_kn = float(n_force_str)
        except ValueError:
            messagebox.showerror("Input Error", "Normal Force must be a valid number.")
            return

        # Convert kN to Newtons (Backend requires N)
        n_force_newtons = n_force_kn * 1000.0

        # UI Feedback
        self.btn_calculate.configure(text="Processing...", state="disabled")
        self.update()

        try:
            print(f"--- Starting Analysis ---")
            
            # 2. Instantiate Parser and Builder
            parser = DXFParser(filepath)
            builder = GeometryBuilder()

            # 3. Retrieve Real Material Objects
            mat_concrete = CONCRETE_LIBRARY[concrete_name]
            mat_steel = STEEL_LIBRARY[steel_name]

            # 4. Build Section
            section = builder.build_section(parser.parse(), mat_concrete, mat_steel)

            # --- Plot Geometry (Immediate Feedback) ---
            print("Plotting geometry preview...")
            self.plot_geometry_embedded(section)
            self.update()

            # 5. Execute Heavy Calculation
            print(f"Calculating interaction diagram for N = {n_force_kn} kN...")
            bb_results = section.biaxial_bending_diagram(
                n=n_force_newtons, 
                n_points=24, 
                progress_bar=False
            )

            # 6. Display Results
            self.plot_results_embedded(bb_results, n_force_kn)
            
            # Switch tab to show results
            self.tab_view.set("Interaction Diagram")
            print("Analysis completed successfully.")

        except Exception as e:
            messagebox.showerror("Calculation Error", f"An error occurred during analysis:\n{str(e)}")
            print(f"ERROR: {e}")

        finally:
            # Restore Button State
            self.btn_calculate.configure(text="RUN ANALYSIS", state="normal")

    def plot_geometry_embedded(self, section_obj):
        """Plots the 2D Cross Section in the Geometry Tab."""
        # Clear previous widgets
        if self.lbl_placeholder_geo:
            self.lbl_placeholder_geo.destroy()
            self.lbl_placeholder_geo = None
        
        if self.current_geometry_canvas:
            self.current_geometry_canvas.get_tk_widget().destroy()

        # Setup Matplotlib Figure
        plt.style.use('dark_background')
        fig = plt.Figure(figsize=(5, 5), dpi=100)
        ax = fig.add_subplot(111)

        # Plot Section
        section_obj.plot_section(ax=ax, title="Cross Section View")
        ax.set_aspect('equal') # Ensure circle looks like a circle
        ax.grid(True, linestyle=':', alpha=0.3)

        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.tab_geometry)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        # Add Toolbar
        toolbar_frame = ctk.CTkFrame(self.tab_geometry)
        toolbar_frame.grid(row=1, column=0, sticky="ew")
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()
        
        self.current_geometry_canvas = canvas

    def plot_results_embedded(self, results_obj, n_val):
        """Plots the Interaction Diagram in the Results Tab."""
        # Clear previous widgets
        if self.lbl_placeholder_res:
            self.lbl_placeholder_res.destroy()
            self.lbl_placeholder_res = None

        if self.current_results_canvas:
            self.current_results_canvas.get_tk_widget().destroy()

        # Setup Matplotlib Figure
        plt.style.use('dark_background') 
        fig = plt.Figure(figsize=(5, 5), dpi=100)
        ax = fig.add_subplot(111)

        # Attempt to plot using the library's method
        try:
            results_obj.plot_diagram(ax=ax)
        except TypeError:
            pass # Handle cases where direct plotting might fail

        # Customize Chart
        ax.set_title(f"Interaction Diagram (N = {n_val} kN)", color="white")
        ax.set_xlabel("Mx (kN.m)")
        ax.set_ylabel("My (kN.m)")
        ax.grid(True, linestyle='--', alpha=0.3)

        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.tab_results)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        # Add Toolbar
        toolbar_frame = ctk.CTkFrame(self.tab_results)
        toolbar_frame.grid(row=1, column=0, sticky="ew")
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()
        
        self.current_results_canvas = canvas