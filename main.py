"""
main.py
-------
Application entry point for the Smart Parking Multi-MCU
Distribution Pipeline Workflow simulation.

Run this file to launch the SCADA HMI dashboard:

    python main.py
"""

import tkinter as tk

from dashboard_gui import SmartParkingDistributionWorkflowGUI


def main():
    root = tk.Tk()
    SmartParkingDistributionWorkflowGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
