> 🇧🇷 **Para a versão em Português**, [clique aqui](README_pt.md).

# Hyperion 🏛️

### **Computational Analysis for Arbitrary Reinforced Concrete Sections**
*A Tribute to Brazilian Engineering Genius*

![Cathedral of Brasília Columns](cathedral.jpg)
> *The iconic hyperboloid columns of the Cathedral of Brasília.*

---

## 📜 The Inspiration: Why "Cardozo"?

This software is named in honor of **Joaquim Cardozo** (1897–1978), the brilliant Brazilian structural engineer and poet who performed the calculations for Oscar Niemeyer's most iconic works.

While Niemeyer dreamt of the shapes, it was Cardozo who made the concrete float. The **Cathedral of Brasília** is a prime example: its columns are hyperboloids of revolution with variable cross-sections along their height—a geometric challenge that, in the 1950s, required immense mathematical prowess to solve without modern computers.

**This tool was developed to solve similar complexities today:** allowing engineers to analyze arbitrary, non-standard cross-sections extracted directly from CAD drawings, ensuring safety for complex architectural heritage.

## 🏗️ Overview

**Hyperion** is a specialized engineering tool designed to generate **Interaction Diagrams ($N-M_x-M_y$)** for reinforced concrete sections that do not fit into standard templates (rectangular/circular).

It leverages **Computational Geometry** to parse raw `.dxf` drawings, applies constitutive laws of materials (following **NBR 6118:2014**), and utilizes the Finite Element Method (Fiber Analysis) to integrate stresses and generate resistance envelopes.

## 🚀 Key Features

* **DXF Parsing Engine:** Automatically extracts concrete boundaries (including multiple voids) and steel bars directly from CAD layers.
* **Material Factory:** Generates stress-strain profiles for Concrete (Parabolic-Rectangular) and Steel (Elastic-Plastic) based on standard classes (e.g., C30, C50, CA-50).
* **Arbitrary Geometry:** Handles L-shaped, T-shaped, hollow, or completely irregular sections effortlessly.
* **Interactive GUI:** Modern desktop interface built with `CustomTkinter` for easy material selection and visualization.

## 🛠️ Architecture

The project follows a clean **Model-View-Controller (MVC)** structure:

```text
src/
├── backend/            # The "Engine Room" (Business Logic)
│   ├── dxf_parser.py       # Extracts geometry from CAD
│   ├── geometry_builder.py # Converts raw data into FEA objects
│   ├── materials.py        # Factory for NBR-6118 materials
│   └── column.py           # Analysis logic
│
├── frontend/           # The "User Interface"
│   └── app_window.py       # CustomTkinter GUI
│
└── main.py             # Application Entry Point
```
⚙️ Engineering Assumptions
    Bernoulli-Euler Hypothesis: Plane sections remain plane after deformation.

    Perfect Bonding: No slip between steel bars and concrete.

    Constitutive Models:

        Concrete: Idealized Parabola-Rectangle (NBR 6118). Tensile strength neglected for ULS.

        Steel: Elastic-perfectly plastic behavior.
    Second-Order Effects: The tool calculates Section Resistance (Rd​). Design moments (Md,tot​) must be input by the user containing global second-order effects.
    
💻 Installation & Usage

# 1. Clone the repository
git clone [https://github.com/](https://github.com/)[YOUR_USERNAME]/Cardozo.git

# 2. Enter directory
cd Cardozo

# 3. Create and Activate Virtual Env
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 4. Install Dependencies
pip install -r requirements.txt

# 5. Run the Application
cd src
python main.py
📐 Input Format (DXF)

To successfully import a section, your .dxf file must use the following layers:

    Layer concrete: Closed LWPOLYLINE entities. (Outer boundary + Voids).

    Layer steel bars: CIRCLE entities representing reinforcement.

📫 Feedback & Contact

This project is open-source and developed with passion for structural engineering. If you have suggestions, found a bug, or just want to chat about the project:

    Email: seu.email@exemplo.com

    LinkedIn: [Link do seu Perfil]

☕ Support the Project

If Cardozo helped you in your studies or projects, consider supporting the development!

    Pix: [Sua Chave Pix]

    PayPal: [Seu Link PayPal]


## 🎓 Credits & Team

**Author & Lead Developer:**

* **Tarso Bessa**
    * *Civil Engineering Student / Researcher*
    * *Independent Researcher*
    * *Contact: bessatarso@gmail.com*

**Technical & Scientific Advisory Board:**

This project was developed under the expert guidance of a team of senior structural engineers and researchers:

* **Prof. Marco Aurélio Bessa, PhD**
    * *Professor at University of Brasília (UnB)*
    * *Independent Structural Consultant*


* **Prof. José Humberto Matias, PhD**
    * *Professor at University of Brasília (UnB)*
    * *Independent Structural Consultant*
   

* **Prof. Lenildo dos Santos, PhD**
    * *Professor at University of Brasília (UnB)*
    * *Independent Structural Consultant*

---