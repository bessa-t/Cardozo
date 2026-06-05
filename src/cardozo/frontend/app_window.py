import customtkinter as ctk
from tkinter import filedialog, messagebox
import webbrowser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from cardozo.backend.dxf_parser import DXFParser
from cardozo.backend.geometry_builder import GeometryBuilder
from cardozo.backend.nbr6118 import NBR6118

GITHUB_REPO_URL = "https://github.com/bessa-t/Cardozo"
NEWTONS_PER_KGF = 9.80665
KNM_TO_KGFM = 1000.0 / NEWTONS_PER_KGF

TRANSLATIONS = {
    "en": {
        "window_title": "Cardozo - Biaxial Bending Analysis",
        "subtitle": "Structural Analysis v1.0",
        "fck": "fck:",
        "fy": "fy:",
        "gamma_c": "γc:",
        "gamma_s": "γs:",
        "normal_force": "Normal Force:",
        "geometry_dxf": "Geometry (DXF):",
        "select_dxf_placeholder": "Select .dxf file...",
        "browse_file": "Browse File",
        "run_analysis": "RUN ANALYSIS",
        "processing": "Processing...",
        "developed_by": "Developed by Tarso Bessa\nbessatarso@gmail.com",
        "support": "Support on GitHub",
        "language": "Language:",
        "tab_geometry": "Geometry Preview",
        "tab_results": "Interaction Diagram",
        "geometry_placeholder": "Geometry Preview will appear here.",
        "results_placeholder": "Interaction Diagram will appear here.",
        "help_title": "How to prepare your DXF",
        "help_text": (
            "DXF FILE REQUIREMENTS:\n\n"
            "1. UNITS: The file must be drawn with consistent units.\n"
            "   The software interprets coordinates directly.\n\n"
            "2. CONCRETE LAYER:\n"
            "   - Draw the concrete perimeter as a closed POLYLINE.\n"
            "   - Layer name must be exactly 'concrete'.\n\n"
            "3. STEEL LAYER:\n"
            "   - Draw rebars as CIRCLES.\n"
            "   - Layer name must be exactly 'steel bars'.\n\n"
            "4. ORIGIN: Center the section near (0,0) for better visualization."
        ),
        "file_dialog_title": "Select DXF Geometry",
        "dxf_files": "DXF Files",
        "all_files": "All Files",
        "input_error": "Input Error",
        "select_file_warning": "Please select a DXF file first.",
        "invalid_normal_force": "Normal Force must be a valid number.",
        "invalid_material_inputs": "fck, fy, γc and γs must be valid positive numbers.",
        "calculation_error": "Calculation Error",
        "calculation_error_message": "An error occurred during analysis:\n{error}",
        "geometry_plot_title": "Cross Section View",
        "diagram_title": "Interaction Diagram (N = {n_val:g} kgf)",
    },
    "pt": {
        "window_title": "Cardozo - Análise de Flexão Biaxial",
        "subtitle": "Análise Estrutural v1.0",
        "fck": "fck:",
        "fy": "fy:",
        "gamma_c": "γc:",
        "gamma_s": "γs:",
        "normal_force": "Força normal:",
        "geometry_dxf": "Geometria (DXF):",
        "select_dxf_placeholder": "Selecione o arquivo .dxf...",
        "browse_file": "Buscar arquivo",
        "run_analysis": "EXECUTAR ANÁLISE",
        "processing": "Processando...",
        "developed_by": "Desenvolvido por Tarso Bessa\nbessatarso@gmail.com",
        "support": "Apoiar no GitHub",
        "language": "Idioma:",
        "tab_geometry": "Prévia da geometria",
        "tab_results": "Diagrama de interação",
        "geometry_placeholder": "A prévia da geometria aparecerá aqui.",
        "results_placeholder": "O diagrama de interação aparecerá aqui.",
        "help_title": "Como preparar seu DXF",
        "help_text": (
            "REQUISITOS DO ARQUIVO DXF:\n\n"
            "1. UNIDADES: O arquivo deve ser desenhado com unidades consistentes.\n"
            "   O software interpreta as coordenadas diretamente.\n\n"
            "2. LAYER DO CONCRETO:\n"
            "   - Desenhe o perímetro do concreto como uma POLYLINE fechada.\n"
            "   - O nome da layer deve ser exatamente 'concrete'.\n\n"
            "3. LAYER DO AÇO:\n"
            "   - Desenhe as barras como CIRCLES.\n"
            "   - O nome da layer deve ser exatamente 'steel bars'.\n\n"
            "4. ORIGEM: Centralize a seção perto de (0,0) para melhor visualização."
        ),
        "file_dialog_title": "Selecionar geometria DXF",
        "dxf_files": "Arquivos DXF",
        "all_files": "Todos os arquivos",
        "input_error": "Erro de entrada",
        "select_file_warning": "Selecione um arquivo DXF primeiro.",
        "invalid_normal_force": "A força normal deve ser um número válido.",
        "invalid_material_inputs": "fck, fy, γc e γs devem ser números positivos válidos.",
        "calculation_error": "Erro de cálculo",
        "calculation_error_message": "Ocorreu um erro durante a análise:\n{error}",
        "geometry_plot_title": "Vista da seção transversal",
        "diagram_title": "Diagrama de interação (N = {n_val:g} kgf)",
    },
}

LANGUAGE_OPTIONS = {
    "English": "en",
    "Português": "pt",
}

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.language = "en"
        self.tab_geometry_name = self.tr("tab_geometry")
        self.tab_results_name = self.tr("tab_results")

        # 1. Main Window Setup
        self.title(self.tr("window_title"))
        self.geometry("1200x800")
        self.minsize(980, 620)
        
        # Grid Configuration: Fixed Sidebar (0), Expandable Content (1)
        self.grid_columnconfigure(0, minsize=250)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Variables to store chart canvases (references for clearing later)
        self.current_results_canvas = None
        self.current_geometry_canvas = None

        # 2. UI Initialization
        self.create_sidebar()
        self.create_main_area()

    def tr(self, key):
        """Returns the translated text for the active language."""
        return TRANSLATIONS[self.language][key]

    def change_language(self, selected_language):
        """Updates visible UI text when the language selector changes."""
        self.language = LANGUAGE_OPTIONS[selected_language]
        self.apply_language()

    def apply_language(self):
        """Applies the selected language to all visible static text."""
        self.title(self.tr("window_title"))
        self.sub_label.configure(text=self.tr("subtitle"))
        self.lbl_fck.configure(text=self.tr("fck"))
        self.lbl_fy.configure(text=self.tr("fy"))
        self.lbl_gamma_c.configure(text=self.tr("gamma_c"))
        self.lbl_gamma_s.configure(text=self.tr("gamma_s"))
        self.lbl_n_force.configure(text=self.tr("normal_force"))
        self.lbl_file.configure(text=self.tr("geometry_dxf"))
        self.path_entry.configure(placeholder_text=self.tr("select_dxf_placeholder"))
        self.btn_browse.configure(text=self.tr("browse_file"))
        self.btn_calculate.configure(text=self.tr("run_analysis"))
        self.lbl_credits.configure(text=self.tr("developed_by"))
        self.btn_support.configure(text=self.tr("support"))
        self.lbl_language.configure(text=self.tr("language"))

        selected_tab = self.tab_view.get()
        new_geometry_name = self.tr("tab_geometry")
        new_results_name = self.tr("tab_results")
        if self.tab_geometry_name != new_geometry_name:
            self.tab_view.rename(self.tab_geometry_name, new_geometry_name)
        if self.tab_results_name != new_results_name:
            self.tab_view.rename(self.tab_results_name, new_results_name)

        if selected_tab == self.tab_geometry_name:
            self.tab_view.set(new_geometry_name)
        elif selected_tab == self.tab_results_name:
            self.tab_view.set(new_results_name)

        self.tab_geometry_name = new_geometry_name
        self.tab_results_name = new_results_name

        if self.lbl_placeholder_geo:
            self.lbl_placeholder_geo.configure(text=self.tr("geometry_placeholder"))
        if self.lbl_placeholder_res:
            self.lbl_placeholder_res.configure(text=self.tr("results_placeholder"))

    def create_sidebar(self):
        """Creates the left sidebar menu with input controls and credits."""
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        
        # Push footer to the bottom using row weights
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        # --- Header ---
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="CARDOZO",
                                       font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 5))
        
        self.sub_label = ctk.CTkLabel(self.sidebar_frame, text=self.tr("subtitle"),
                                       text_color="gray", font=ctk.CTkFont(size=12))
        self.sub_label.grid(row=1, column=0, padx=20, pady=(0, 14))

        # --- Section 1: Materials ---
        self.material_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.material_frame.grid(row=2, column=0, padx=18, pady=(4, 0), sticky="ew")

        self.lbl_fck, self.entry_fck = self.create_value_row(
            self.material_frame,
            row=0,
            label_text=self.tr("fck"),
            placeholder_text="30",
            unit_text="MPa",
        )
        self.entry_fck.insert(0, "30")

        self.lbl_fy, self.entry_fy = self.create_value_row(
            self.material_frame,
            row=1,
            label_text=self.tr("fy"),
            placeholder_text="500",
            unit_text="MPa",
        )
        self.entry_fy.insert(0, "500")

        self.lbl_gamma_c, self.entry_gamma_c = self.create_value_row(
            self.material_frame,
            row=2,
            label_text=self.tr("gamma_c"),
            placeholder_text="1.4",
        )
        self.entry_gamma_c.insert(0, "1.4")

        self.lbl_gamma_s, self.entry_gamma_s = self.create_value_row(
            self.material_frame,
            row=3,
            label_text=self.tr("gamma_s"),
            placeholder_text="1.15",
        )
        self.entry_gamma_s.insert(0, "1.15")

        # --- Section 2: Loading Inputs ---
        self.load_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.load_frame.grid(row=3, column=0, padx=18, pady=(12, 0), sticky="ew")
        self.lbl_n_force, self.entry_n_force = self.create_value_row(
            self.load_frame,
            row=0,
            label_text=self.tr("normal_force"),
            placeholder_text="0.0",
            unit_text="kgf",
            entry_width=82,
        )

        # --- Section 3: File Input with Help Button ---
        # A small frame to align the label and the help button horizontally
        file_label_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        file_label_frame.grid(row=4, column=0, padx=20, pady=(16, 0), sticky="ew")
        
        self.lbl_file = ctk.CTkLabel(file_label_frame, text=self.tr("geometry_dxf"), anchor="w")
        self.lbl_file.pack(side="left")

        # Help Button (?)
        self.btn_help = ctk.CTkButton(file_label_frame, text="?", width=20, height=20,
                                      fg_color="gray", hover_color="gray40",
                                      command=self.show_dxf_help)
        self.btn_help.pack(side="right")

        self.path_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text=self.tr("select_dxf_placeholder"))
        self.path_entry.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        self.btn_browse = ctk.CTkButton(self.sidebar_frame, text=self.tr("browse_file"),
                                        fg_color="transparent", border_width=2,
                                        text_color=("gray10", "#DCE4EE"),
                                        command=self.open_dxf_file)
        self.btn_browse.grid(row=6, column=0, padx=20, pady=5, sticky="ew")

        # --- Main Action Button ---
        self.btn_calculate = ctk.CTkButton(self.sidebar_frame, text=self.tr("run_analysis"),
                                           height=50,
                                           fg_color="#106A43", hover_color="#148F5C",
                                           font=ctk.CTkFont(size=14, weight="bold"),
                                           command=self.calculate_event)
        self.btn_calculate.grid(row=7, column=0, padx=20, pady=(18, 14), sticky="ew")

        # --- Language Selector ---
        self.lbl_language = ctk.CTkLabel(self.sidebar_frame, text=self.tr("language"), anchor="w")
        self.lbl_language.grid(row=8, column=0, padx=20, pady=(0, 0), sticky="w")

        self.language_option = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=list(LANGUAGE_OPTIONS.keys()),
            command=self.change_language,
        )
        self.language_option.set("English")
        self.language_option.grid(row=9, column=0, padx=20, pady=5, sticky="ew")

        # --- Footer: Credits & Support ---
        self.separator = ctk.CTkFrame(self.sidebar_frame, height=2, fg_color="gray30")
        self.separator.grid(row=11, column=0, sticky="ew", padx=20, pady=(8, 8))

        self.lbl_credits = ctk.CTkLabel(self.sidebar_frame, 
                                        text=self.tr("developed_by"),
                                        font=ctk.CTkFont(size=10), text_color="gray60")
        self.lbl_credits.grid(row=12, column=0, padx=20, pady=(0, 5))

        self.btn_support = ctk.CTkButton(self.sidebar_frame, text=self.tr("support"),
                                         height=30, fg_color="#24292F", text_color="white",
                                         hover_color="#3B424A",
                                         command=self.open_support_link)
        self.btn_support.grid(row=13, column=0, padx=20, pady=(0, 14), sticky="ew")

    def create_value_row(
        self,
        parent,
        row,
        label_text,
        placeholder_text,
        unit_text="",
        entry_width=76,
    ):
        """Creates a compact label + value + unit row."""
        parent.grid_columnconfigure(1, weight=1)
        label = ctk.CTkLabel(parent, text=label_text, anchor="w")
        label.grid(row=row, column=0, padx=(0, 8), pady=4, sticky="w")

        entry = ctk.CTkEntry(parent, placeholder_text=placeholder_text, width=entry_width)
        entry.grid(row=row, column=1, padx=(0, 6), pady=4, sticky="e")

        unit_label = ctk.CTkLabel(
            parent,
            text=unit_text,
            width=34,
            text_color="gray70",
            anchor="w",
        )
        unit_label.grid(row=row, column=2, padx=(0, 0), pady=4, sticky="w")

        return label, entry

    def create_main_area(self):
        """Creates the right main area with Tabs for Geometry and Results."""
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.tab_geometry = self.tab_view.add(self.tab_geometry_name)
        self.tab_results = self.tab_view.add(self.tab_results_name)
        
        # Configure internal grid weights
        self.tab_results.grid_columnconfigure(0, weight=1)
        self.tab_results.grid_rowconfigure(0, weight=1)
        self.tab_geometry.grid_columnconfigure(0, weight=1)
        self.tab_geometry.grid_rowconfigure(0, weight=1)

        # Initial Placeholders
        self.lbl_placeholder_res = ctk.CTkLabel(self.tab_results, 
                                            text=self.tr("results_placeholder"),
                                            font=ctk.CTkFont(size=16))
        self.lbl_placeholder_res.grid(row=0, column=0)

        self.lbl_placeholder_geo = ctk.CTkLabel(self.tab_geometry, 
                                            text=self.tr("geometry_placeholder"),
                                            font=ctk.CTkFont(size=16))
        self.lbl_placeholder_geo.grid(row=0, column=0)

    # --- EVENT HANDLERS ---

    def show_dxf_help(self):
        """Displays a popup with DXF instructions."""
        messagebox.showinfo(self.tr("help_title"), self.tr("help_text"))

    def open_support_link(self):
        """Opens the support URL in the default browser."""
        webbrowser.open(GITHUB_REPO_URL)
    
    def open_dxf_file(self):
        """Opens system file dialog to select the DXF."""
        filename = filedialog.askopenfilename(
            title=self.tr("file_dialog_title"),
            filetypes=((self.tr("dxf_files"), "*.dxf"), (self.tr("all_files"), "*.*")),
        )
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
        fck_str = self.entry_fck.get()
        fy_str = self.entry_fy.get()
        gamma_c_str = self.entry_gamma_c.get()
        gamma_s_str = self.entry_gamma_s.get()
        n_force_str = self.entry_n_force.get()

        if not filepath:
            messagebox.showwarning(self.tr("input_error"), self.tr("select_file_warning"))
            return

        # Handle Normal Force Input (String to Float conversion)
        try:
            if n_force_str.strip() == "":
                n_force_kgf = 0.0
            else:
                n_force_kgf = float(n_force_str)
        except ValueError:
            messagebox.showerror(self.tr("input_error"), self.tr("invalid_normal_force"))
            return

        try:
            fck = float(fck_str)
            fy = float(fy_str)
            gamma_c = float(gamma_c_str)
            gamma_s = float(gamma_s_str)
            if fck <= 0 or fy <= 0 or gamma_c <= 0 or gamma_s <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(self.tr("input_error"), self.tr("invalid_material_inputs"))
            return

        # Convert kgf to Newtons for the analysis engine.
        n_force_newtons = n_force_kgf * NEWTONS_PER_KGF

        # UI Feedback
        self.btn_calculate.configure(text=self.tr("processing"), state="disabled")
        self.update()

        try:
            print(f"--- Starting Analysis ---")
            
            # 2. Instantiate Parser and Builder
            parser = DXFParser(filepath)
            builder = GeometryBuilder()

            # 3. Create NBR 6118 materials from user-defined inputs
            design_code = NBR6118(gamma_c=gamma_c, gamma_s=gamma_s)
            mat_concrete = design_code.create_concrete_material(fck=fck)
            mat_steel = design_code.create_steel_material(fy=fy)

            # 4. Build Section
            section = builder.build_section(parser.parse(), mat_concrete, mat_steel)
            design_code.assign_concrete_section(section)

            # --- Plot Geometry (Immediate Feedback) ---
            print("Plotting geometry preview...")
            self.plot_geometry_embedded(section)
            self.update()

            # 5. Execute Heavy Calculation
            print(f"Calculating interaction diagram for N = {n_force_kgf} kgf...")
            bb_results, _phis = design_code.biaxial_bending_diagram(
                n_design=n_force_newtons,
                n_points=24,
                progress_bar=False,
            )

            # 6. Display Results
            self.plot_results_embedded(bb_results, n_force_kgf)
            
            # Switch tab to show results
            self.tab_view.set(self.tab_results_name)
            print("Analysis completed successfully.")

        except Exception as e:
            messagebox.showerror(
                self.tr("calculation_error"),
                self.tr("calculation_error_message").format(error=str(e)),
            )
            print(f"ERROR: {e}")

        finally:
            # Restore Button State
            self.btn_calculate.configure(text=self.tr("run_analysis"), state="normal")

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
        section_obj.plot_section(ax=ax, title=self.tr("geometry_plot_title"))
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

        m_x_list, m_y_list = results_obj.get_results_lists()
        m_x_kgfm = [m_x * KNM_TO_KGFM for m_x in m_x_list]
        m_y_kgfm = [m_y * KNM_TO_KGFM for m_y in m_y_list]
        ax.plot(m_x_kgfm, m_y_kgfm, "o-", color="#4EA3F1", linewidth=1.8, markersize=4)
        ax.axhline(0, color="white", linewidth=0.8, alpha=0.35)
        ax.axvline(0, color="white", linewidth=0.8, alpha=0.35)

        # Customize Chart
        ax.set_title(self.tr("diagram_title").format(n_val=n_val), color="white")
        ax.set_xlabel("Mx (kgf.m)")
        ax.set_ylabel("My (kgf.m)")
        ax.set_aspect("equal", adjustable="datalim")
        ax.grid(True, linestyle='--', alpha=0.3)
        fig.tight_layout()

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
