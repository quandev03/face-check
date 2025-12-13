#!/bin/bash
# Rebuild script with proper cleanup

echo "Cleaning previous build..."
rm -rf build dist __pycache__
# Don't delete build.spec, we need it

echo "Rebuilding with updated spec..."
cd "$(dirname "$0")"

# Detect Python
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

# Check dependencies first
echo "Checking dependencies..."
$PYTHON_CMD check_dependencies.py
if [ $? -ne 0 ]; then
    echo ""
    echo "Please install missing dependencies first!"
    exit 1
fi

# Ensure PyInstaller is installed
if ! $PYTHON_CMD -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    $PIP_CMD install pyinstaller
fi

# Build with verbose output
# Note: --collect-all is not allowed with .spec files, but build.spec already includes collect_all logic
echo "Building executable..."
echo "This may take several minutes..."
$PYTHON_CMD -m PyInstaller --clean --log-level=INFO build.spec

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Build completed successfully!"
    echo "Executable: dist/FaceRecognitionApp"
    echo ""
    echo "To test, run: ./dist/FaceRecognitionApp"
else
    echo ""
    echo "✗ Build failed. Check the output above for errors."
    exit 1
fi







