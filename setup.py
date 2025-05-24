from setuptools import setup, find_packages
import sys
import subprocess
import os

def check_tesseract():
    """Check if Tesseract is installed"""
    try:
        subprocess.run(['tesseract', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_tesseract():
    """Attempt to install Tesseract using Homebrew"""
    try:
        # Check if Homebrew is installed
        subprocess.run(['brew', '--version'], capture_output=True, check=True)
        
        print("Installing Tesseract OCR via Homebrew...")
        result = subprocess.run(['brew', 'install', 'tesseract'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Tesseract installed successfully!")
            return True
        else:
            print(f"❌ Failed to install Tesseract: {result.stderr}")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Homebrew is not installed.")
        return False

def pre_install_checks():
    """Run pre-installation checks"""
    if sys.platform == 'darwin':  # macOS
        if not check_tesseract():
            print("\n" + "="*60)
            print("⚠️  Tesseract OCR is not installed!")
            print("="*60)
            print("\nCursor-resumer requires Tesseract OCR to function properly.")
            
            # Try to install automatically
            response = input("\nWould you like to install Tesseract automatically? [Y/n]: ").strip().lower()
            
            if response in ['', 'y', 'yes']:
                if install_tesseract():
                    print("\nTesseract has been installed successfully!")
                else:
                    print("\nAutomatic installation failed.")
                    print("Please install manually with: brew install tesseract")
                    print("\nIf you don't have Homebrew, install it first:")
                    print("  /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            else:
                print("\nPlease install Tesseract manually:")
                print("  brew install tesseract")
            
            print("="*60 + "\n")
    
    # Check for external managed environment
    if sys.version_info >= (3, 11) and sys.platform == 'darwin':
        if os.path.exists('/opt/homebrew') or os.path.exists('/usr/local/Homebrew'):
            print("\n" + "="*60)
            print("ℹ️  IMPORTANT: macOS External Environment Detected")
            print("="*60)
            print("\nIf you encounter an 'externally-managed-environment' error,")
            print("you have several options:\n")
            print("1. Use a virtual environment (recommended):")
            print("   python3 -m venv venv")
            print("   source venv/bin/activate")
            print("   pip install cursor-resumer\n")
            print("2. Use pipx for isolated installation:")
            print("   brew install pipx")
            print("   pipx install cursor-resumer\n")
            print("3. Force installation (not recommended):")
            print("   pip install --break-system-packages cursor-resumer")
            print("="*60 + "\n")

# Run pre-installation checks
pre_install_checks()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cursor-resumer",
    version="1.0.0",
    author="khaterdev",
    author_email="mostafa@khater.dev",
    description="Automatically clicks resume button when Cursor AI hits 25 tool call limit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/khaterdev/cursor-resumer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: MacOS :: MacOS X",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pyautogui>=0.9.54",
        "opencv-python>=4.9.0.80",
        "Pillow>=10.2.0",
        "pytesseract>=0.3.10",
        "numpy>=1.26.4",
    ],
    entry_points={
        "console_scripts": [
            "cursor-resumer=cursor_resumer.main:main",
        ],
    },
    keywords="cursor ai automation resume tool-limit",
    project_urls={
        "Bug Reports": "https://github.com/khaterdev/cursor-resumer/issues",
        "Source": "https://github.com/khaterdev/cursor-resumer",
    },
)