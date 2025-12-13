#!/bin/bash
# Build script for macOS

echo "Building Face Recognition App for macOS..."

# Detect Python and pip commands
# Always use python3 and pip3 to be safe
if [ -n "$VIRTUAL_ENV" ]; then
    # Use venv's python3 directly
    PYTHON_CMD="$VIRTUAL_ENV/bin/python3"
    PIP_CMD="$VIRTUAL_ENV/bin/pip3"
    echo "Using virtual environment: $VIRTUAL_ENV"
    
    # Verify venv python exists
    if [ ! -f "$PYTHON_CMD" ]; then
        echo "Error: Python not found in venv at $PYTHON_CMD"
        echo "Please recreate venv or check venv path"
        exit 1
    fi
else
    # Try to find venv in parent directory
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    PARENT_VENV="$SCRIPT_DIR/../venv/bin/python3"
    if [ -f "$PARENT_VENV" ]; then
        PYTHON_CMD="$PARENT_VENV"
        PIP_CMD="$SCRIPT_DIR/../venv/bin/pip3"
        echo "Found venv in parent directory, using: $PYTHON_CMD"
    else
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
        echo "Using system Python"
    fi
fi

# Check if PyInstaller is installed
if ! $PYTHON_CMD -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller not found. Installing..."
    $PIP_CMD install pyinstaller
fi

# Create build directories
mkdir -p dist
mkdir -p build

# Check dependencies first
echo "Checking dependencies..."
$PYTHON_CMD check_dependencies.py
if [ $? -ne 0 ]; then
    echo ""
    echo "Please install missing dependencies first!"
    echo "Run: pip install -r requirements-gui.txt"
    exit 1
fi

# Build executable with verbose output
# Note: --collect-all is not allowed with .spec files, but build.spec already includes collect_all logic
echo "Running PyInstaller..."
echo "This may take several minutes..."
$PYTHON_CMD -m PyInstaller --clean --log-level=INFO build.spec

if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi

echo ""
echo "Build completed successfully!"
echo "Executable is in: dist/FaceRecognitionApp"
echo ""
echo "To create a .app bundle, you may need to use additional tools like py2app or create a bundle manually."

