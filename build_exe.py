"""PyInstaller build script for IFC Coordinator."""

import os
import sys
import shutil
import subprocess
from PyInstaller.__main__ import run


def build():
    print("=" * 60)
    print("Building IFC Coordinator Standalone Executable")
    print("=" * 60)

    work_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(work_dir)

    icon_path = os.path.join(work_dir, "resources", "icon.ico")

    # Arguments for PyInstaller
    args = [
        "main.py",
        "--name=IFC_Coordinator",
        "--noconsole",  # GUI app, no black terminal window
        "--onefile",    # Single standalone .exe file
        f"--icon={icon_path}",
        "--add-data=resources;resources",
        "--collect-all=ifcopenshell",
        "--collect-all=ifcpatch",
        "--hidden-import=ifcopenshell",
        "--hidden-import=ifcopenshell.util.shape",
        "--hidden-import=ifcopenshell.util.placement",
        "--hidden-import=ifcopenshell.util.unit",
        "--hidden-import=numpy",
        "--hidden-import=PySide6",
        "--clean",
        "--noconfirm",
    ]

    print("Running PyInstaller with arguments:")
    for a in args:
        print(" ", a)

    run(args)

    dist_exe = os.path.join(work_dir, "dist", "IFC_Coordinator.exe")
    if os.path.exists(dist_exe):
        size_mb = os.path.getsize(dist_exe) / (1024 * 1024)
        print("=" * 60)
        print(f"BUILD SUCCESSFUL!")
        print(f"Standalone executable created at: {dist_exe}")
        print(f"File size: {size_mb:.2f} MB")
        print("=" * 60)
    else:
        print("ERROR: Output executable not found in dist/!")
        sys.exit(1)


if __name__ == "__main__":
    build()
