"""
Hyperion - Biaxial Bending Analysis Software
Application Entry Point.

This script initializes the environment, configures system paths,
sets up the GUI theme, and launches the main application loop.

Author: Tarso [Your Last Name]
Date: 2024
License: MIT
"""

import sys
import os
import customtkinter as ctk

# ==============================================================================
# 1. ENVIRONMENT CONFIGURATION
# ==============================================================================
# Ensures that the 'src' directory is added to the system path.
# This allows 'frontend' to import 'backend' and 'data' modules seamlessly,
# regardless of where the script is executed from.

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Now we can safely import the App class from the frontend package
try:
    from frontend.app_window import App
except ImportError as e:
    print("CRITICAL ERROR: Failed to import application modules.")
    print(f"Details: {e}")
    print("Please ensure you are running the script from the correct directory.")
    sys.exit(1)

# ==============================================================================
# 2. APPLICATION LAUNCHER
# ==============================================================================

def main():
    """
    Main execution function.
    Sets up the visual theme and starts the GUI event loop.
    """
    
    # --- GUI Appearance Settings ---
    # Modes: "System" (standard), "Dark", "Light"
    ctk.set_appearance_mode("Dark")  
    
    # Themes: "blue" (standard), "green", "dark-blue"
    ctk.set_default_color_theme("dark-blue")  

    # --- Initialize Application ---
    print("--- Starting Hyperion System ---")
    try:
        app = App()
        
        # Optional: Set icon if available (Windows only)
        # app.iconbitmap(os.path.join(current_dir, "frontend", "assets", "icon.ico"))
        
        # --- Start Event Loop ---
        # The code halts here and waits for user interaction
        app.mainloop()
        
    except Exception as e:
        print(f"An unexpected error occurred during execution: {e}")
    finally:
        print("--- Hyperion System Shutdown ---")

if __name__ == "__main__":
    main()