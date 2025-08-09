# src/main.py
import tkinter as tk
from gui import AppGUI

if __name__ == "__main__":
    """Main entry point that launches the GUI."""
    try:
        AppGUI(tk.Tk(), "Compliment Chaos Mirror")
    except Exception as e:
        print(f"💥 A critical error occurred: {e}")