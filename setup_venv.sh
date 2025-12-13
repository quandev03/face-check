#!/bin/bash
# Setup virtual environment for GUI app

cd "$(dirname "$0")"

echo "Setting up virtual environment..."

# Remove old venv if broken
if [ -d "venv" ] && [ ! -f "venv/bin/python3" ]; then
    echo "Removing broken venv..."
    rm -rf venv
fi

# Create new venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating new virtual environment..."
    # Try Python 3.11 first (MediaPipe requirement), fallback to python3
    if command -v python3.11 &> /dev/null; then
        echo "Using Python 3.11 (required for MediaPipe)..."
        python3.11 -m venv venv
    elif command -v python3.10 &> /dev/null; then
        echo "Using Python 3.10 (required for MediaPipe)..."
        python3.10 -m venv venv
    else
        echo "Warning: Python 3.11 or 3.10 not found. Using python3 (MediaPipe may not work with Python 3.13+)"
        python3 -m venv venv
    fi
fi

# Use venv's pip directly
VENV_PIP="venv/bin/pip"
VENV_PYTHON="venv/bin/python"

# Check if venv was created successfully
if [ ! -f "$VENV_PIP" ]; then
    echo "Error: Virtual environment creation failed!"
    exit 1
fi

# Upgrade pip
echo "Upgrading pip..."
$VENV_PYTHON -m pip install --upgrade pip

# Install GUI dependencies
echo "Installing GUI dependencies..."
$VENV_PYTHON -m pip install -r gui_app/requirements-gui.txt

# Install PyInstaller
echo "Installing PyInstaller..."
$VENV_PYTHON -m pip install pyinstaller

echo ""
echo "✓ Virtual environment setup complete!"
echo ""
echo "To activate the venv, run:"
echo "  source venv/bin/activate"
echo ""
echo "Then you can build the app:"
echo "  cd gui_app"
echo "  ./build_mac.sh"







