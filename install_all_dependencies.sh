#!/bin/bash
# Install all dependencies for both API server and GUI app

cd "$(dirname "$0")"

echo "Installing all dependencies..."

# Use venv's pip
if [ -f "venv/bin/pip3" ]; then
    PIP_CMD="venv/bin/pip3"
    PYTHON_CMD="venv/bin/python3"
elif [ -n "$VIRTUAL_ENV" ]; then
    PIP_CMD="$VIRTUAL_ENV/bin/pip3"
    PYTHON_CMD="$VIRTUAL_ENV/bin/python3"
else
    echo "Error: Virtual environment not found!"
    echo "Please run: source venv/bin/activate"
    exit 1
fi

echo "Using Python: $PYTHON_CMD"
echo "Using pip: $PIP_CMD"

# Upgrade pip
echo ""
echo "Upgrading pip..."
$PIP_CMD install --upgrade pip

# Install API server dependencies (using MediaPipe, not dlib)
echo ""
echo "Installing API server dependencies (MediaPipe)..."
$PIP_CMD install -r requirements-mediapipe.txt

# Install GUI app dependencies
echo ""
echo "Installing GUI app dependencies..."
$PIP_CMD install -r gui_app/requirements-gui.txt

# Install PyInstaller
echo ""
echo "Installing PyInstaller..."
$PIP_CMD install pyinstaller

echo ""
echo "✓ All dependencies installed!"
echo ""
echo "To start API server:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "To build GUI app:"
echo "  cd gui_app"
echo "  ./build_mac.sh"

