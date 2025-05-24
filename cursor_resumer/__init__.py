"""
Cursor Resumer - Automatically clicks resume button when Cursor AI hits 25 tool call limit
"""

__version__ = "1.0.0"
__author__ = "Cursor Resumer Contributors"

import sys
import subprocess
import warnings

def check_dependencies():
    """Check if all required dependencies are available"""
    # Check Tesseract
    try:
        subprocess.run(['tesseract', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        warnings.warn(
            "\n\nWARNING: Tesseract OCR is not installed!\n"
            "Cursor-resumer requires Tesseract to function properly.\n"
            "Install it with: brew install tesseract\n",
            RuntimeWarning,
            stacklevel=2
        )

# Run dependency check on import
check_dependencies()

from .main import CursorResumer, main

__all__ = ["CursorResumer", "main"]