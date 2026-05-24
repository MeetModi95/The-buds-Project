"""
SONIC VOICE STUDIO II
======================
Production-grade voice command control software.
Powered by Vosk offline speech recognition.

Entry point — run this file to launch the application.
"""

import sys
import os

# --- PyInstaller frozen-bundle support ---
# When running from a PyInstaller --onefile bundle, the extracted temp dir
# is available as sys._MEIPASS.  We use it to locate bundled data such as
# the Vosk model and profile files.

def _get_base_path():
    """Return the base path for bundled resources."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

# Expose for other modules
BASE_PATH = _get_base_path()

# Ensure the project root is on the path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.main_window import MainWindow


def main():
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
