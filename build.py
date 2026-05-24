"""
SONIC VOICE STUDIO II - Build Script
=====================================
Compiles the application into a single standalone .exe using PyInstaller.

Usage:
    python build.py

The output will be in  dist/SonicVoiceStudio.exe
"""

import os
import sys
import subprocess
import shutil

# Fix Windows console encoding for Unicode output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def ensure_pyinstaller():
    """Make sure PyInstaller is installed."""
    try:
        subprocess.check_call(
            [sys.executable, "-c", "import PyInstaller"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print("[OK] PyInstaller is available.")
    except subprocess.CalledProcessError:
        print("[..] Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("[OK] PyInstaller installed.")


def find_customtkinter_path():
    """Return the customtkinter package directory so we can bundle its assets."""
    result = subprocess.run(
        [sys.executable, "-c", "import customtkinter; import os; print(os.path.dirname(customtkinter.__file__))"],
        capture_output=True, text=True
    )
    path = result.stdout.strip()
    if not path or not os.path.isdir(path):
        raise RuntimeError("Could not locate customtkinter package directory.")
    return path


def build():
    project_root = os.path.dirname(os.path.abspath(__file__))
    entry_point = os.path.join(project_root, "sonic_studio.py")
    ctk_path = find_customtkinter_path()

    # Collect data directories
    data_dirs = []

    # Vosk model - do not bundle internally to keep EXE size small and startup instantaneous.
    # Instead, we will copy it next to the compiled EXE in dist/
    model_dir = os.path.join(project_root, "model")
    copy_model_externally = False
    if os.path.isdir(model_dir):
        copy_model_externally = True
        print("[OK] Will copy model folder to dist/ output directory for zero-decompression fast startup.")
    else:
        print("[WARN] 'model/' directory not found - you must place it adjacent to the EXE at runtime.")

    # Data (profiles, defaults)
    data_dir = os.path.join(project_root, "data")
    if os.path.isdir(data_dir):
        data_dirs.append((data_dir, "data"))
        print("[OK] Bundling data directory (%s)" % data_dir)

    # CustomTkinter assets
    data_dirs.append((ctk_path, "customtkinter"))
    print("[OK] Bundling customtkinter assets (%s)" % ctk_path)

    # Bundle the logo image inside the executable
    logo_file = os.path.join(project_root, "sonic logo.png")
    if os.path.isfile(logo_file):
        data_dirs.append((logo_file, "."))
        print("[OK] Bundling sonic logo.png")

    # Build the --add-data arguments
    separator = ";" if sys.platform == "win32" else ":"
    add_data_args = []
    for src, dest in data_dirs:
        add_data_args.extend(["--add-data", "%s%s%s" % (src, separator, dest)])

    exclude_modules = [
        "matplotlib", "scipy", "pandas", "IPython", "ipykernel", "notebook",
        "PyQt5", "PyQt6", "PySide2", "PySide6", "sqlite3", "tkinter.test",
        "unittest", "pydoc"
    ]

    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "SonicVoiceStudio",
        "--clean",
        "--noupx",  # Decompressing at startup adds latency; disable UPX for instant launches
        # Collect all binaries and data for specific packages
        "--collect-all", "vosk",
        "--hidden-import", "sounddevice",
        "--hidden-import", "pynput",
        "--hidden-import", "pynput.keyboard",
        "--hidden-import", "pynput.keyboard._win32",
        "--hidden-import", "pynput.mouse",
        "--hidden-import", "pynput.mouse._win32",
        "--hidden-import", "customtkinter",
        "--hidden-import", "numpy",
        "--hidden-import", "PIL",
    ]

    # Add exclusions
    for mod in exclude_modules:
        cmd.extend(["--exclude-module", mod])

    # Add data files
    cmd.extend(add_data_args)
    cmd.append(entry_point)

    print()
    print("=" * 60)
    print("  Building SonicVoiceStudio.exe ...")
    print("=" * 60)
    print()
    print("Command:")
    print("  " + " ".join(cmd))
    print()

    result = subprocess.run(cmd, cwd=project_root)

    if result.returncode == 0:
        exe_path = os.path.join(project_root, "dist", "SonicVoiceStudio.exe")
        dist_dir = os.path.join(project_root, "dist")
        
        # Copy model folder externally to dist/model/
        if copy_model_externally:
            dest_model_dir = os.path.join(dist_dir, "model")
            print("[..] Copying 'model/' folder to dist/model/ ...")
            try:
                if os.path.exists(dest_model_dir):
                    shutil.rmtree(dest_model_dir)
                shutil.copytree(model_dir, dest_model_dir)
                print("[OK] 'model/' folder copied adjacent to executable.")
            except Exception as e:
                print("[WARN] Failed to copy model folder: %s" % e)

        # Copy logo adjacent as reference
        if os.path.isfile(logo_file):
            try:
                shutil.copy2(logo_file, os.path.join(dist_dir, "sonic logo.png"))
            except Exception:
                pass

        print()
        print("=" * 60)
        print("  BUILD SUCCESSFUL")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print("  Output: %s" % exe_path)
            print("  Size:   %.1f MB" % size_mb)
        print("=" * 60)
    else:
        print()
        print("=" * 60)
        print("  BUILD FAILED - see errors above.")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    ensure_pyinstaller()
    build()
